from flask import Flask, jsonify, render_template, request
from flask_login import current_user, login_required

from config import Config
from extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/"):
            return jsonify({"error": "Please log in."}), 401
        from flask import redirect, url_for
        return redirect(url_for("auth.login"))

    from routes.api import api_bp
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/")
    @login_required
    def dashboard():
        return render_template("dashboard.html", user=current_user,
                               currency=app.config["CURRENCY"])

    with app.app_context():
        db.create_all()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
