/*
|--------------------------------------------------------------------------
| 대한민국 전용 산불 위험·경보 지도 스크립트
|--------------------------------------------------------------------------
| 역할
| 1. Leaflet 지도를 초기화한다.
| 2. 대한민국 중심으로 확대해서 시작한다.
| 3. 위험도 마커 / 재난문자 마커를 표시한다.
| 4. 라이트/다크 모드가 바뀌어도 구조가 깨지지 않게 한다.
|--------------------------------------------------------------------------
*/

/*
|--------------------------------------------------------------------------
| 실제 API 데이터를 담을 전역 변수
|--------------------------------------------------------------------------
*/
let wildfireRiskData = [];
let disasterMessageData = [];

/*
|--------------------------------------------------------------------------
| 전역 변수
|--------------------------------------------------------------------------
*/
let map;
let riskLayerGroup;
let messageLayerGroup;

/*
|--------------------------------------------------------------------------
| 위험등급별 색상 반환 함수
|--------------------------------------------------------------------------
*/
function getRiskColor(level) {
    switch (level) {
        case "낮음":
            return "#4caf50";
        case "보통":
            return "#ffc107";
        case "높음":
            return "#ff7043";
        case "매우 높음":
            return "#e53935";
        default:
            return "#607d8b";
    }
}

/*
|--------------------------------------------------------------------------
| 안전한 문자열 반환
|--------------------------------------------------------------------------
*/
function safeText(value, fallback = "-") {
    if (value === null || value === undefined || value === "") {
        return fallback;
    }
    return value;
}

/*
|--------------------------------------------------------------------------
| 좌표 유효성 검사
|--------------------------------------------------------------------------
*/
function hasValidLatLng(item) {
    return (
        item &&
        typeof item.lat === "number" &&
        typeof item.lng === "number" &&
        !Number.isNaN(item.lat) &&
        !Number.isNaN(item.lng)
    );
}

/*
|--------------------------------------------------------------------------
| 지도 초기화
|--------------------------------------------------------------------------
*/
function initMap() {
    const koreaCenter = [36.35, 127.85];

    const koreaBounds = L.latLngBounds(
        L.latLng(32.8, 124.5),
        L.latLng(39.5, 132.0)
    );

    map = L.map("pulseMap", {
        center: koreaCenter,
        zoom: 7,
        minZoom: 6,
        maxZoom: 12,
        maxBounds: koreaBounds,
        maxBoundsViscosity: 1.0,
        zoomControl: true
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        noWrap: true
    }).addTo(map);

    riskLayerGroup = L.layerGroup().addTo(map);
    messageLayerGroup = L.layerGroup().addTo(map);
}

/*
|--------------------------------------------------------------------------
| 위험도 레이어 렌더링
|--------------------------------------------------------------------------
*/
function renderRiskLayer() {
    riskLayerGroup.clearLayers();

    const topRiskOnlyElement = document.getElementById("toggleTopRiskOnly");
    const topRiskOnly = topRiskOnlyElement ? topRiskOnlyElement.checked : false;

    wildfireRiskData.forEach((item) => {
        if (!hasValidLatLng(item)) {
            return;
        }

        if (topRiskOnly && !["높음", "매우 높음"].includes(item.risk_level)) {
            return;
        }

        const regionName = safeText(item.region_name || item.region);
        const riskLevel = safeText(item.risk_level);
        const riskScore = safeText(item.risk_score);
        const forecastTime = safeText(item.forecast_time);

        const circle = L.circleMarker([item.lat, item.lng], {
            radius: 14,
            color: getRiskColor(riskLevel),
            fillColor: getRiskColor(riskLevel),
            fillOpacity: 0.7,
            weight: 2
        });

        circle.bindPopup(`
            <div style="min-width:200px;">
                <strong>${regionName}</strong><br>
                위험등급: ${riskLevel}<br>
                위험점수: ${riskScore}<br>
                예보기준: ${forecastTime}
            </div>
        `);

        circle.on("click", () => {
            updateRegionDetail({
                region: regionName,
                risk_level: riskLevel,
                risk_score: riskScore,
                forecast_time: forecastTime,
                type: "risk"
            });
        });

        circle.addTo(riskLayerGroup);
    });
}

/*
|--------------------------------------------------------------------------
| 재난문자 레이어 렌더링
|--------------------------------------------------------------------------
*/
function renderMessageLayer() {
    messageLayerGroup.clearLayers();

    disasterMessageData.forEach((item) => {
        if (!hasValidLatLng(item)) {
            return;
        }

        const regionName = safeText(item.region_name || item.region);
        const sender = safeText(item.sender);
        const sentAt = safeText(item.sent_at);
        const messageText = safeText(item.message_text);

        const marker = L.marker([item.lat, item.lng]);

        marker.bindPopup(`
            <div style="min-width:220px;">
                <strong>${regionName}</strong><br>
                발송기관: ${sender}<br>
                발송시각: ${sentAt}<br>
                <hr>
                <div>${messageText}</div>
            </div>
        `);

        marker.on("click", () => {
            updateRegionDetail({
                region: regionName,
                sender: sender,
                sent_at: sentAt,
                message_text: messageText,
                type: "message"
            });
        });

        marker.addTo(messageLayerGroup);
    });
}

/*
|--------------------------------------------------------------------------
| 우측 패널 - 최근 재난문자 목록 렌더링
|--------------------------------------------------------------------------
*/
function renderMessageList() {
    const container = document.getElementById("messageList");
    const countElement = document.getElementById("messageCount");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    disasterMessageData.forEach((item) => {
        const regionName = safeText(item.region_name || item.region);
        const sender = safeText(item.sender);
        const sentAt = safeText(item.sent_at);
        const messageText = safeText(item.message_text);

        const div = document.createElement("div");
        div.className = "message-item";
        div.innerHTML = `
            <div class="message-region">${regionName}</div>
            <div class="message-text">${messageText}</div>
            <div class="message-text">${sentAt} · ${sender}</div>
        `;
        container.appendChild(div);
    });

    if (countElement) {
        countElement.textContent = disasterMessageData.length;
    }
}

/*
|--------------------------------------------------------------------------
| 우측 패널 - 위험도 TOP 지역 렌더링
|--------------------------------------------------------------------------
*/
function renderTopRiskList() {
    const container = document.getElementById("topRiskList");
    const highRiskCountElement = document.getElementById("highRiskCount");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    const sorted = [...wildfireRiskData].sort((a, b) => {
        const aScore = Number(a.risk_score) || 0;
        const bScore = Number(b.risk_score) || 0;
        return bScore - aScore;
    });

    sorted.slice(0, 5).forEach((item) => {
        const regionName = safeText(item.region_name || item.region);
        const riskLevel = safeText(item.risk_level);
        const riskScore = safeText(item.risk_score);

        const div = document.createElement("div");
        div.className = "top-risk-item";
        div.innerHTML = `
            <div class="top-risk-region">${regionName}</div>
            <div class="top-risk-meta">
                위험등급: ${riskLevel} / 점수: ${riskScore}
            </div>
        `;
        container.appendChild(div);
    });

    const highRiskCount = wildfireRiskData.filter((item) =>
        ["높음", "매우 높음"].includes(item.risk_level)
    ).length;

    if (highRiskCountElement) {
        highRiskCountElement.textContent = highRiskCount;
    }
}

/*
|--------------------------------------------------------------------------
| 상세 패널 업데이트
|--------------------------------------------------------------------------
*/
function updateRegionDetail(data) {
    const box = document.getElementById("regionDetailBox");
    const selectedRegionName = document.getElementById("selectedRegionName");

    if (selectedRegionName) {
        selectedRegionName.textContent = data.region || "없음";
    }

    if (!box) {
        return;
    }

    if (data.type === "risk") {
        box.innerHTML = `
            <strong>${safeText(data.region)}</strong><br>
            위험등급: ${safeText(data.risk_level)}<br>
            위험점수: ${safeText(data.risk_score)}<br>
            예보기준시각: ${safeText(data.forecast_time)}
        `;
    } else {
        box.innerHTML = `
            <strong>${safeText(data.region)}</strong><br>
            발송기관: ${safeText(data.sender)}<br>
            발송시각: ${safeText(data.sent_at)}<br>
            <hr>
            ${safeText(data.message_text)}
        `;
    }
}

/*
|--------------------------------------------------------------------------
| 레이어 토글 이벤트 연결
|--------------------------------------------------------------------------
*/
function bindLayerToggleEvents() {
    const riskCheckbox = document.getElementById("toggleRiskLayer");
    const messageCheckbox = document.getElementById("toggleMessageLayer");
    const topRiskOnlyCheckbox = document.getElementById("toggleTopRiskOnly");
    const resetMapBtn = document.getElementById("resetMapBtn");

    if (riskCheckbox) {
        riskCheckbox.addEventListener("change", function () {
            if (this.checked) {
                map.addLayer(riskLayerGroup);
            } else {
                map.removeLayer(riskLayerGroup);
            }
        });
    }

    if (messageCheckbox) {
        messageCheckbox.addEventListener("change", function () {
            if (this.checked) {
                map.addLayer(messageLayerGroup);
            } else {
                map.removeLayer(messageLayerGroup);
            }
        });
    }

    if (topRiskOnlyCheckbox) {
        topRiskOnlyCheckbox.addEventListener("change", function () {
            renderRiskLayer();
        });
    }

    if (resetMapBtn) {
        resetMapBtn.addEventListener("click", function () {
            map.setView([36.35, 127.85], 7);
        });
    }
}

/*
|--------------------------------------------------------------------------
| 테스트용 샘플 데이터
|--------------------------------------------------------------------------
| 아직 Flask API 연결 전이면 이 데이터로 화면 먼저 확인 가능
|--------------------------------------------------------------------------
*/
function loadSampleData() {
    wildfireRiskData = [
        {
            id: 1,
            region_name: "강원특별자치도 강릉시",
            risk_level: "매우 높음",
            risk_score: 82.5,
            forecast_time: "2026-04-10 09:00:00",
            lat: 37.7519,
            lng: 128.8761
        },
        {
            id: 2,
            region_name: "경상북도 안동시",
            risk_level: "높음",
            risk_score: 74.2,
            forecast_time: "2026-04-10 09:00:00",
            lat: 36.5684,
            lng: 128.7294
        },
        {
            id: 3,
            region_name: "서울특별시 종로구",
            risk_level: "보통",
            risk_score: 45.8,
            forecast_time: "2026-04-10 09:00:00",
            lat: 37.5735,
            lng: 126.9788
        }
    ];

    disasterMessageData = [
        {
            id: 1,
            region_name: "강원특별자치도 강릉시",
            sender: "행정안전부",
            sent_at: "2026-04-10 08:30:00",
            message_text: "[산불] 강릉시 산불 확산 우려 지역 주민은 안전한 장소로 대피 바랍니다.",
            lat: 37.7519,
            lng: 128.8761
        }
    ];
}

/*
|--------------------------------------------------------------------------
| 초기 실행
|--------------------------------------------------------------------------
*/
document.addEventListener("DOMContentLoaded", function () {
    initMap();
    loadSampleData();
    renderRiskLayer();
    renderMessageLayer();
    renderMessageList();
    renderTopRiskList();
    bindLayerToggleEvents();
});