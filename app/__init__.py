from flask import Flask


def create_app():
    """
    Flask 앱 생성 함수

    역할:
    - Flask 앱 객체 생성
    - 라우트(Blueprint) 등록
    - 나중에 config, DB, 확장기능 연결 시 이 함수 안에서 확장 가능
    """
    app = Flask(__name__)

    # routes.py에 정의한 Blueprint 연결
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app