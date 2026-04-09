from app import create_app

# Flask 앱 생성
app = create_app()

if __name__ == "__main__":
    """
    개발용 실행 진입점

    debug=True:
    - 코드 수정 시 자동 재시작
    - 에러 발생 시 디버그 화면 표시
    """
    app.run(host="127.0.0.1", port=5000, debug=True)