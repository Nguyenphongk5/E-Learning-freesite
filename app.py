import os
import re
import secrets
import sqlite3
import uuid
from functools import wraps
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask, g, jsonify, request, send_from_directory, session
from PIL import Image, UnidentifiedImageError
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
STATIC_EXTENSIONS = {
    ".css", ".gif", ".html", ".ico", ".jpeg", ".jpg", ".jfif", ".js",
    ".png", ".svg", ".webmanifest", ".webp",
}
IMAGE_EXTENSIONS = {"PNG": ".png", "JPEG": ".jpg", "GIF": ".gif", "WEBP": ".webp"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000

DEFAULT_COURSES = [
    ("C++ From Basic To Advance", "Getting started with CPP", "images/picture/card-1.png", "https://www.youtube.com/watch?v=z9bZufPHFLU&list=PLfqMhTWNBTe0b2nM6JHVCnAkhQRGiZMSJ"),
    ("Java", "Kickstart your journey in Java", "images/picture/card-2.png", "https://www.youtube.com/watch?v=WOUpjal8ee4&list=PLsyeobzWxl7oZ-fxDYkOToURHhMuWD1BK"),
    ("C Programming", "Kickstart your coding journey with C", "images/picture/card-3.png", "https://www.youtube.com/watch?v=MoqYPc43ssk&list=PLXthElPLs7ZaGXGI-_ToQ670nr1RAtjRB"),
    ("Python Programming", "Getting started with Python", "images/picture/card-4.png", "https://www.youtube.com/watch?v=kqtD5dpn9C8"),
    ("Django Framework", "Master Django skills", "images/picture/card-5.png", "https://www.youtube.com/watch?v=UmljXZIypDc&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p"),
    ("HTML", "Learn HTML to create amazing web pages", "images/picture/card-6.png", "https://www.youtube.com/watch?v=dD2EISBDjWM&list=PLr6-GrHUlVf_ZNmuQSXdS197Oyr1L9sPB"),
    ("CSS", "Design amazing web pages with CSS", "images/picture/card-7.png", "https://www.youtube.com/watch?v=qKoajPPWpmo&list=PLr6-GrHUlVf8JIgLcu3sHigvQjTw_aC9C"),
    ("JavaScript", "Kickstart your coding journey in scripting", "images/picture/card-8.png", "https://www.youtube.com/watch?v=2md4HQNRqJA&list=PLRAV69dS1uWSxUIk5o3vQY2-_VKsOpXLD"),
    ("React JS", "Learn an amazing front-end framework", "images/picture/card-9.png", "https://www.youtube.com/watch?v=QFaFIcGhPoM&list=PLC3y8-rFHvwgg3vaYJgHGnModB54rxOk3"),
    ("Kotlin", "Kickstart your coding journey in Kotlin", "images/picture/card-11.png", "https://www.youtube.com/watch?v=VEqhzCFmEQI&list=PLlxmoA0rQ-LwgK1JsnMsakYNACYGa1cjR"),
    ("Angular", "Head for Google's framework", "images/picture/card-10.png", "https://www.youtube.com/watch?v=0eWrpsCLMJQ&list=PLC3y8-rFHvwhBRAgFinJR8KHIrCdTkZcZ"),
    ("SQL", "Start understanding databases", "images/picture/card-12.png", "https://www.youtube.com/watch?v=7GVFYt6_ZFM&list=PL08903FB7ACA1C2FB"),
    ("Flutter", "Kickstart your coding journey in Flutter", "images/picture/card-14.png", "https://www.youtube.com/watch?v=VPvVD8t02U8"),
    ("PyTorch", "Explore machine learning with PyTorch", "images/picture/card-13.jpg", "https://www.youtube.com/watch?v=V_xro1bcAuA"),
    ("PHP", "Create dynamic websites with PHP", "images/picture/card-15.jfif", "https://www.youtube.com/watch?v=7GVFYt6_ZFM&list=PL08903FB7ACA1C2FB"),
    ("Nest.js", "Create a REST API", "images/picture/card-16.jpg", "https://www.youtube.com/watch?v=GHTA143_b-s"),
    ("Tailwind CSS", "Responsive web designs with Tailwind CSS", "images/picture/card-17.png", "https://www.youtube.com/watch?v=lZp4salRFFc"),
    ("Bootstrap", "Create interactive websites with Bootstrap", "images/picture/card-18.png", "https://www.youtube.com/watch?v=-qfEOE4vtxE"),
]


def create_app(test_config=None):
    app = Flask(__name__, static_folder=None)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.environ.get("DATABASE_PATH", str(BASE_DIR / "instance" / "elearning.sqlite3")),
        UPLOAD_FOLDER=os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "instance" / "uploads")),
        MAX_CONTENT_LENGTH=6 * 1024 * 1024,
        BOOTSTRAP_ADMIN_EMAIL=os.environ.get("ADMIN_EMAIL", "").strip().lower(),
        BOOTSTRAP_ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD", ""),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "").lower() == "true",
    )
    if test_config:
        app.config.update(test_config)

    with app.app_context():
        initialize_database(app)

    @app.teardown_appcontext
    def close_database(_error=None):
        connection = g.pop("database", None)
        if connection is not None:
            connection.close()

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    @app.get("/api/auth/me")
    @login_required
    def current_account():
        return jsonify(public_account(g.current_user))

    @app.post("/api/auth/register")
    def register():
        data = json_payload()
        name = str(data.get("name", "")).strip()
        email = normalize_email(data.get("email", ""))
        password = str(data.get("password", ""))
        if not name or len(name) > 80:
            return api_error("Họ tên cần có từ 1 đến 80 ký tự.", 400)
        if not valid_email(email):
            return api_error("Email không hợp lệ.", 400)
        if len(password) < 8:
            return api_error("Mật khẩu cần có ít nhất 8 ký tự.", 400)

        try:
            cursor = get_database().execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'user')",
                (name, email, generate_password_hash(password)),
            )
            get_database().commit()
        except sqlite3.IntegrityError:
            return api_error("Email này đã được sử dụng.", 409)

        user = get_database().execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        session.clear()
        session["user_id"] = user["id"]
        return jsonify(public_account(user)), 201

    @app.post("/api/auth/login")
    def login():
        data = json_payload()
        email = normalize_email(data.get("email", ""))
        password = str(data.get("password", ""))
        user = get_database().execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email,)
        ).fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            return api_error("Email hoặc mật khẩu không chính xác.", 401)

        session.clear()
        session["user_id"] = user["id"]
        return jsonify(public_account(user))

    @app.post("/api/auth/logout")
    def logout():
        session.clear()
        return jsonify({"message": "Đã đăng xuất."})

    @app.get("/api/courses")
    def list_courses():
        courses = get_database().execute(
            "SELECT * FROM courses ORDER BY id ASC"
        ).fetchall()
        return jsonify([dict(course) for course in courses])

    @app.post("/api/admin/uploads")
    @admin_required
    def upload_course_image():
        uploaded_file = request.files.get("image")
        if uploaded_file is None or not uploaded_file.filename:
            return api_error("Chọn một file ảnh để tải lên.", 400)

        image_data = uploaded_file.stream.read(MAX_UPLOAD_SIZE + 1)
        if len(image_data) > MAX_UPLOAD_SIZE:
            return api_error("Ảnh không được vượt quá 5 MB.", 413)
        try:
            with Image.open(BytesIO(image_data)) as image:
                extension = IMAGE_EXTENSIONS.get(image.format)
                if extension is None:
                    return api_error("Chỉ hỗ trợ ảnh PNG, JPG, GIF hoặc WebP.", 400)
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    return api_error("Kích thước ảnh vượt quá giới hạn cho phép.", 400)
                image.verify()
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            return api_error("File tải lên không phải ảnh hợp lệ.", 400)

        upload_folder = Path(app.config["UPLOAD_FOLDER"])
        upload_folder.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4().hex}{extension}"
        (upload_folder / filename).write_bytes(image_data)
        return jsonify({"image_url": f"/uploads/{filename}"}), 201

    @app.post("/api/courses")
    @admin_required
    def create_course():
        data, error = validate_course(json_payload())
        if error:
            return api_error(error, 400)
        cursor = get_database().execute(
            "INSERT INTO courses (title, description, image_url, course_url) VALUES (?, ?, ?, ?)",
            (data["title"], data["description"], data["image_url"], data["course_url"]),
        )
        get_database().commit()
        course = get_database().execute(
            "SELECT * FROM courses WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return jsonify(dict(course)), 201

    @app.put("/api/courses/<int:course_id>")
    @admin_required
    def update_course(course_id):
        data, error = validate_course(json_payload())
        if error:
            return api_error(error, 400)
        cursor = get_database().execute(
            "UPDATE courses SET title = ?, description = ?, image_url = ?, course_url = ? WHERE id = ?",
            (data["title"], data["description"], data["image_url"], data["course_url"], course_id),
        )
        if cursor.rowcount == 0:
            return api_error("Không tìm thấy khóa học.", 404)
        get_database().commit()
        course = get_database().execute(
            "SELECT * FROM courses WHERE id = ?", (course_id,)
        ).fetchone()
        return jsonify(dict(course))

    @app.delete("/api/courses/<int:course_id>")
    @admin_required
    def delete_course(course_id):
        cursor = get_database().execute("DELETE FROM courses WHERE id = ?", (course_id,))
        if cursor.rowcount == 0:
            return api_error("Không tìm thấy khóa học.", 404)
        get_database().commit()
        return jsonify({"message": "Đã xóa khóa học."})

    @app.get("/api/admin/users")
    @admin_required
    def list_accounts():
        users = get_database().execute(
            "SELECT id, name, email, role, created_at FROM users ORDER BY role DESC, id"
        ).fetchall()
        return jsonify([dict(user) for user in users])

    @app.post("/api/admin/users")
    @admin_required
    def create_admin():
        data = json_payload()
        name = str(data.get("name", "")).strip()
        email = normalize_email(data.get("email", ""))
        password = str(data.get("password", ""))
        if not name or len(name) > 80:
            return api_error("Họ tên cần có từ 1 đến 80 ký tự.", 400)
        if not valid_email(email):
            return api_error("Email không hợp lệ.", 400)
        if len(password) < 8:
            return api_error("Mật khẩu cần có ít nhất 8 ký tự.", 400)
        try:
            cursor = get_database().execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
                (name, email, generate_password_hash(password)),
            )
            get_database().commit()
        except sqlite3.IntegrityError:
            return api_error("Email này đã được sử dụng.", 409)
        user = get_database().execute(
            "SELECT id, name, email, role, created_at FROM users WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return jsonify(dict(user)), 201

    @app.get("/")
    def homepage():
        return send_from_directory(BASE_DIR, "index.html")

    @app.get("/uploads/<path:filename>")
    def uploaded_image(filename):
        path = Path(filename)
        if path.name != filename or path.suffix.lower() not in set(IMAGE_EXTENSIONS.values()):
            return api_error("Không tìm thấy ảnh.", 404)
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, max_age=3600)

    @app.get("/<path:filename>")
    def static_file(filename):
        path = Path(filename)
        if any(part.startswith(".") for part in path.parts):
            return api_error("Không tìm thấy trang.", 404)
        if path.suffix.lower() not in STATIC_EXTENSIONS:
            return api_error("Không tìm thấy trang.", 404)
        return send_from_directory(BASE_DIR, filename)

    return app


def initialize_database(app):
    database_path = Path(app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('user', 'admin')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            image_url TEXT NOT NULL DEFAULT '',
            course_url TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    if connection.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
        connection.executemany(
            "INSERT INTO courses (title, description, image_url, course_url) VALUES (?, ?, ?, ?)",
            DEFAULT_COURSES,
        )

    admin_email = app.config["BOOTSTRAP_ADMIN_EMAIL"]
    admin_password = app.config["BOOTSTRAP_ADMIN_PASSWORD"]
    if bool(admin_email) != bool(admin_password):
        connection.close()
        raise RuntimeError("Set both ADMIN_EMAIL and ADMIN_PASSWORD to bootstrap the first admin.")
    if admin_email:
        existing = connection.execute(
            "SELECT role FROM users WHERE email = ? COLLATE NOCASE", (admin_email,)
        ).fetchone()
        if existing and existing["role"] != "admin":
            connection.close()
            raise RuntimeError("The bootstrap admin email already belongs to a user account.")
        if not existing:
            connection.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
                ("Quản trị viên", admin_email, generate_password_hash(admin_password)),
            )
    connection.commit()
    connection.close()


def get_database():
    if "database" not in g:
        connection = sqlite3.connect(current_app_config_database())
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.database = connection
    return g.database


def current_app_config_database():
    from flask import current_app

    return current_app.config["DATABASE"]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return api_error("Vui lòng đăng nhập.", 401)
        user = get_database().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            session.clear()
            return api_error("Vui lòng đăng nhập.", 401)
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if g.current_user["role"] != "admin":
            return api_error("Bạn không có quyền quản trị.", 403)
        return view(*args, **kwargs)

    return wrapped


def public_account(user):
    return {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}


def json_payload():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def normalize_email(value):
    return str(value).strip().lower()


def valid_email(email):
    return len(email) <= 254 and re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) is not None


def validate_course(data):
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    image_url = str(data.get("image_url", "")).strip()
    course_url = str(data.get("course_url", "")).strip()
    if not title or len(title) > 150:
        return None, "Tên khóa học cần có từ 1 đến 150 ký tự."
    if len(description) > 1200:
        return None, "Mô tả không được vượt quá 1200 ký tự."
    parsed_course_url = urlsplit(course_url)
    if parsed_course_url.scheme not in {"http", "https"} or not parsed_course_url.netloc:
        return None, "Liên kết khóa học phải bắt đầu bằng http:// hoặc https://."
    if image_url:
        parsed_image_url = urlsplit(image_url)
        is_local_image = image_url.startswith("images/") and ".." not in Path(image_url).parts
        is_uploaded_image = re.fullmatch(r"/uploads/[a-f0-9]{32}\.(?:png|jpg|gif|webp)", image_url) is not None
        is_external_image = parsed_image_url.scheme in {"http", "https"} and bool(parsed_image_url.netloc)
        if not (is_local_image or is_uploaded_image or is_external_image):
            return None, "Ảnh cần là đường dẫn images/ hoặc URL http(s)."
    return {
        "title": title,
        "description": description,
        "image_url": image_url,
        "course_url": course_url,
    }, None


def api_error(message, status):
    return jsonify({"error": message}), status


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)