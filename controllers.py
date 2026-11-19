import hashlib
import hmac
import re
import secrets
import sqlite3
import time
import uuid
import warnings
from functools import wraps
from io import BytesIO
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from PIL import Image, UnidentifiedImageError
from models import (
    create_course,
    create_book,
    create_quiz_exam,
    create_quiz_question,
    create_user,
    count_books,
    count_admin_accounts,
    create_quiz_attempt,
    delete_book,
    delete_course,
    delete_quiz_exam,
    delete_quiz_question,
    delete_user_and_archive_attempts,
    find_user_by_email,
    get_account_data,
    get_book_by_id,
    get_course_by_id,
    get_database,
    get_quiz_statistics,
    get_quiz_exam,
    list_quiz_exams,
    list_assigned_quiz_exams,
    submit_quiz_submission,
    list_quiz_submissions,
    grade_quiz_submission,
    publish_quiz_exam,
    get_user_by_id,
    hash_password,
    list_accounts,
    list_books,
    list_courses,
    normalize_email,
    public_account,
    update_book,
    update_course,
    update_quiz_exam,
    update_quiz_question,
    valid_email,
    validate_book,
    validate_course,
    verify_password,
)


page_routes = Blueprint("pages", __name__)
api_routes = Blueprint("api", __name__)
STATIC_EXTENSIONS = {
    ".css", ".gif", ".html", ".ico", ".jpeg", ".jpg", ".jfif", ".js",
    ".png", ".svg", ".webmanifest", ".webp",
}
IMAGE_EXTENSIONS = {"PNG": ".png", "JPEG": ".jpg", "GIF": ".gif", "WEBP": ".webp"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000


def auth_rate_limited(action, limit_config, window_config):
    """Apply a persistent rolling-window limit keyed by action and client IP."""
    def decorate(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if request.method != "POST":
                return view(*args, **kwargs)
            now = int(time.time())
            window = int(current_app.config[window_config])
            limit = int(current_app.config[limit_config])
            client_ip = request.remote_addr or "unknown"
            client_key = hmac.new(
                str(current_app.config["SECRET_KEY"]).encode("utf-8"),
                client_ip.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            database = get_database()
            database.execute("BEGIN IMMEDIATE")
            database.execute(
                "DELETE FROM auth_rate_limit_events WHERE created_at <= ?",
                (now - max(window, 24 * 60 * 60),),
            )
            rows = database.execute(
                "SELECT created_at FROM auth_rate_limit_events "
                "WHERE action = ? AND client_key = ? AND created_at > ? "
                "ORDER BY created_at ASC",
                (action, client_key, now - window),
            ).fetchall()
            if len(rows) >= limit:
                retry_after = max(1, rows[0]["created_at"] + window - now)
                database.commit()
                if request.path == "/login":
                    flash("Bạn đã thử đăng nhập quá nhiều lần. Vui lòng thử lại sau.", "error")
                    response = render_template("admin_login.html"), 429
                    response = current_app.make_response(response)
                else:
                    response = current_app.make_response(
                        api_error("Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau.", 429)
                    )
                response.headers["Retry-After"] = str(retry_after)
                return response

            database.execute(
                "INSERT INTO auth_rate_limit_events (action, client_key, created_at) "
                "VALUES (?, ?, ?)",
                (action, client_key, now),
            )
            database.commit()
            return view(*args, **kwargs)
        return wrapped
    return decorate


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return api_error("Vui lòng đăng nhập.", 401)
        user = get_user_by_id(user_id)
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


def admin_page_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("pages.login_page"))
        user = get_user_by_id(user_id)
        if not user:
            session.clear()
            return redirect(url_for("pages.login_page"))
        if user["role"] != "admin":
            abort(403)
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


@page_routes.route("/login", methods=["GET", "POST"])
@auth_rate_limited("login", "AUTH_LOGIN_RATE_LIMIT", "AUTH_LOGIN_RATE_WINDOW")
def login_page():
    if request.method == "GET":
        user_id = session.get("user_id")
        user = get_user_by_id(user_id) if user_id else None
        if user and user["role"] == "admin":
            return redirect(url_for("pages.admin_books"))
        return render_template("admin_login.html")

    email = normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    user = find_user_by_email(email)
    if (
        not user
        or user["role"] != "admin"
        or not verify_password(user["password_hash"], password)
    ):
        flash("Email hoặc mật khẩu không chính xác.", "error")
        return render_template("admin_login.html"), 401

    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    return redirect(url_for("pages.admin_books"))


@page_routes.post("/logout")
@admin_page_required
def admin_logout():
    session.clear()
    return redirect(url_for("pages.login_page"))


@page_routes.get("/admin/books")
@admin_page_required
def admin_books():
    return render_template("admin_books.html", books=list_books(), admin=g.current_user)


def validate_image_upload(uploaded_file):
    image_data = uploaded_file.stream.read(MAX_UPLOAD_SIZE + 1)
    if len(image_data) > MAX_UPLOAD_SIZE:
        return None, None, "Ảnh không được vượt quá 5 MB.", 413

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(image_data)) as image:
                extension = IMAGE_EXTENSIONS.get(image.format)
                if extension is None:
                    return None, None, "Chỉ hỗ trợ ảnh PNG, JPG, GIF hoặc WebP.", 400
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    return None, None, "Kích thước ảnh vượt quá giới hạn cho phép.", 400
                image.verify()

            with Image.open(BytesIO(image_data)) as image:
                image.load()
    except (
        UnidentifiedImageError,
        OSError,
        SyntaxError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ):
        return None, None, "File tải lên không phải ảnh hợp lệ.", 400

    return image_data, extension, None, None


def save_uploaded_image(image_data, extension, folder):
    filename = f"{uuid.uuid4().hex}{extension}"
    upload_folder = Path(folder)
    upload_folder.mkdir(parents=True, exist_ok=True)
    (upload_folder / filename).write_bytes(image_data)
    return filename


@page_routes.route("/admin/books/add", methods=["GET", "POST"])
@admin_page_required
def add_book():
    if request.method == "GET":
        return render_template("admin_book_form.html", book=None, admin=g.current_user)

    data, error = validate_book(request.form)
    if error:
        flash(error, "error")
        return render_template("admin_book_form.html", book=request.form, admin=g.current_user), 400

    cover_file = request.files.get("cover_image")
    if not cover_file or not cover_file.filename:
        flash("Vui lòng chọn ảnh bìa cho sách.", "error")
        return render_template("admin_book_form.html", book=request.form, admin=g.current_user), 400

    image_data, extension, error, status_code = validate_image_upload(cover_file)
    if error:
        flash(error, "error")
        return render_template("admin_book_form.html", book=request.form, admin=g.current_user), status_code

    filename = save_uploaded_image(image_data, extension, current_app.config["BOOK_UPLOAD_FOLDER"])
    data["cover_image"] = f"/static/uploads/books/{filename}"

    create_book(data)
    flash("Đã thêm sách mới.", "success")
    return redirect(url_for("pages.admin_books"))


@page_routes.route("/admin/books/edit/<int:book_id>", methods=["GET", "POST"])
@admin_page_required
def edit_book(book_id):
    book = get_book_by_id(book_id)
    if not book:
        abort(404)
    if request.method == "GET":
        return render_template("admin_book_form.html", book=book, admin=g.current_user)

    data, error = validate_book(request.form)
    if error:
        flash(error, "error")
        return render_template("admin_book_form.html", book={**dict(book), **request.form}, admin=g.current_user), 400

    cover_file = request.files.get("cover_image")
    image_data = None
    extension = None
    if cover_file and cover_file.filename:
        image_data, extension, error, status_code = validate_image_upload(cover_file)
        if error:
            flash(error, "error")
            return render_template("admin_book_form.html", book={**dict(book), **request.form}, admin=g.current_user), status_code

    old_cover = book["cover_image"]
    if image_data is not None and extension is not None:
        filename = save_uploaded_image(image_data, extension, current_app.config["BOOK_UPLOAD_FOLDER"])
        data["cover_image"] = f"/static/uploads/books/{filename}"
    else:
        data["cover_image"] = old_cover

    update_book(book_id, data)
    if data["cover_image"] != old_cover:
        remove_book_cover(old_cover)
    flash("Đã cập nhật thông tin sách.", "success")
    return redirect(url_for("pages.admin_books"))


@page_routes.post("/admin/books/delete/<int:book_id>")
@admin_page_required
def remove_book(book_id):
    book = get_book_by_id(book_id)
    if not book:
        abort(404)
    delete_book(book_id)
    remove_book_cover(book["cover_image"])
    flash("Đã xóa sách.", "success")
    return redirect(url_for("pages.admin_books"))


def remove_book_cover(cover_image):
    filename = re.fullmatch(
        r"/static/uploads/books/([a-f0-9]{32}\.(?:png|jpg|gif|webp))",
        str(cover_image or ""),
    )
    if filename:
        (Path(current_app.config["BOOK_UPLOAD_FOLDER"]) / filename.group(1)).unlink(missing_ok=True)


@api_routes.get("/api/auth/me")
@login_required
def current_account():
    return jsonify(public_account(g.current_user))


@api_routes.get("/api/csrf-token")
def csrf_token():
    token_key = current_app.config["CSRF_TOKEN_SESSION_KEY"]
    token = session.get(token_key)
    if not token:
        token = secrets.token_urlsafe(32)
        session[token_key] = token
    return jsonify({"csrf_token": token})


@api_routes.get("/api/auth/me/data")
@login_required
def current_account_data():
    return jsonify(get_account_data(g.current_user["id"]))


@api_routes.delete("/api/auth/me")
@login_required
def delete_current_account():
    user = g.current_user
    if user["role"] == "admin":
        if user["email"] == current_app.config["BOOTSTRAP_ADMIN_EMAIL"]:
            return api_error(
                "Hãy đổi cấu hình BOOTSTRAP_ADMIN_EMAIL trước khi xóa tài khoản bootstrap.",
                409,
            )
        if count_admin_accounts() <= 1:
            return api_error(
                "Cần có ít nhất một quản trị viên khác trước khi xóa tài khoản này.",
                409,
            )

    archived_attempts = delete_user_and_archive_attempts(user["id"])
    session.clear()
    return jsonify({
        "message": "Tài khoản đã được xóa; kết quả quiz đã chuyển thành số liệu tổng hợp.",
        "archived_attempts": archived_attempts,
    })


@api_routes.post("/api/auth/register")
@auth_rate_limited("register", "AUTH_REGISTER_RATE_LIMIT", "AUTH_REGISTER_RATE_WINDOW")
def register():
    data = json_payload()
    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")
    if not all(isinstance(value, str) for value in (name, email, password)):
        return api_error("Họ tên, email và mật khẩu phải có giá trị dạng chuỗi.", 400)
    name = name.strip()
    email = normalize_email(email)
    if not name or len(name) > 80:
        return api_error("Họ tên cần có từ 1 đến 80 ký tự.", 400)
    if not valid_email(email):
        return api_error("Email không hợp lệ.", 400)
    if len(password) < 8:
        return api_error("Mật khẩu cần có ít nhất 8 ký tự.", 400)

    try:
        user_id = create_user(name, email, hash_password(password), "user")
    except sqlite3.IntegrityError:
        return api_error("Email này đã được sử dụng.", 409)

    user = get_user_by_id(user_id)
    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    return jsonify(public_account(user)), 201


@api_routes.post("/api/auth/login")
@auth_rate_limited("login", "AUTH_LOGIN_RATE_LIMIT", "AUTH_LOGIN_RATE_WINDOW")
def login():
    data = json_payload()
    email = data.get("email", "")
    password = data.get("password", "")
    if not isinstance(email, str) or not isinstance(password, str):
        return api_error("Email và mật khẩu phải có giá trị dạng chuỗi.", 400)
    email = normalize_email(email)
    if not email or not password or not valid_email(email):
        return api_error("Email hoặc mật khẩu không hợp lệ.", 400)
    user = find_user_by_email(email)
    if not user or not verify_password(user["password_hash"], password):
        return api_error("Email hoặc mật khẩu không chính xác.", 401)

    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    return jsonify(public_account(user))


@api_routes.post("/api/auth/logout")
def logout():
    session.clear()
    return jsonify({"message": "Đã đăng xuất."})


@api_routes.get("/api/courses")
def courses():
    return jsonify([dict(course) for course in list_courses()])


@api_routes.post("/api/admin/uploads")
@admin_required
def upload_course_image():
    uploaded_file = request.files.get("image")
    if uploaded_file is None or not uploaded_file.filename:
        return api_error("Chọn một file ảnh để tải lên.", 400)

    image_data, extension, error, status_code = validate_image_upload(uploaded_file)
    if error:
        return api_error(error, status_code)

    filename = save_uploaded_image(image_data, extension, current_app.config["UPLOAD_FOLDER"])
    return jsonify({"image_url": f"/uploads/{filename}"}), 201


@api_routes.post("/api/courses")
@admin_required
def create_course_route():
    data, error = validate_course(json_payload())
    if error:
        return api_error(error, 400)
    course_id = create_course(data)
    return jsonify(dict(get_course_by_id(course_id))), 201


@api_routes.put("/api/courses/<int:course_id>")
@admin_required
def update_course_route(course_id):
    data, error = validate_course(json_payload())
    if error:
        return api_error(error, 400)
    if not update_course(course_id, data):
        return api_error("Không tìm thấy khóa học.", 404)
    return jsonify(dict(get_course_by_id(course_id)))


@api_routes.delete("/api/courses/<int:course_id>")
@admin_required
def delete_course_route(course_id):
    if not delete_course(course_id):
        return api_error("Không tìm thấy khóa học.", 404)
    return jsonify({"message": "Đã xóa khóa học."})


@api_routes.get("/api/admin/users")
@admin_required
def admin_accounts():
    return jsonify([dict(user) for user in list_accounts()])


@api_routes.get("/api/admin/books/count")
@admin_required
def admin_book_count():
    return jsonify({"count": count_books()})


@api_routes.get("/api/admin/quiz/statistics")
@admin_required
def admin_quiz_statistics():
    return jsonify(get_quiz_statistics())


@api_routes.get("/api/quiz/exams")
def public_quiz_exams():
    return jsonify([
        exam for exam in list_quiz_exams()
        if exam.get("status") == "published"
    ])


@api_routes.get("/api/quiz/exams/<exam_id>")
def public_quiz_exam(exam_id):
    exam = get_quiz_exam(exam_id)
    if not exam:
        return api_error("Không tìm thấy đề thi.", 404)
    if exam.get("status") != "published":
        return api_error("Đề thi chưa được xuất bản.", 403)
    if not exam["questions"]:
        return api_error("Đề thi chưa có câu hỏi.", 400)
    return jsonify(exam)


@api_routes.get("/api/admin/quiz/exams")
@admin_required
def admin_quiz_exams():
    return jsonify(list_quiz_exams(include_questions=True))


def validate_quiz_exam_payload(data):
    if not isinstance(data, dict):
        return None, "Dữ liệu đề thi không hợp lệ."
    title = data.get("title", "")
    subject = data.get("subject", "")
    difficulty = data.get("difficulty", "Cơ bản")
    duration = data.get("duration")
    description = data.get("description", "")
    due_at = data.get("due_at")
    status = data.get("status", "draft")
    shuffle_questions = data.get("shuffle_questions", False)
    if not all(isinstance(value, str) for value in (title, subject, difficulty, description)):
        return None, "Thông tin đề thi phải có giá trị dạng chuỗi."
    if status not in {"draft", "published"}:
        return None, "Trạng thái đề thi không hợp lệ."
    if due_at is not None and not isinstance(due_at, str):
        return None, "Hạn nộp không hợp lệ."
    if type(shuffle_questions) is not bool:
        return None, "Tùy chọn xáo trộn không hợp lệ."
    title = title.strip()
    subject = subject.strip()
    description = description.strip()
    difficulty = difficulty.strip()
    if not title or len(title) > 100 or not subject or len(subject) > 60:
        return None, "Tên đề thi hoặc môn học không hợp lệ."
    if type(duration) is not int or not 1 <= duration <= 300:
        return None, "Thời lượng đề thi không hợp lệ."
    if len(description) > 500:
        return None, "Mô tả đề thi không được vượt quá 500 ký tự."
    return {
        "title": title,
        "subject": subject,
        "difficulty": difficulty or "Cơ bản",
        "duration": duration,
        "description": description,
        "status": status,
        "due_at": due_at.strip() if isinstance(due_at, str) and due_at.strip() else None,
        "shuffle_questions": shuffle_questions,
    }, None


@api_routes.post("/api/admin/quiz/exams")
@admin_required
def create_quiz_exam_route():
    data = json_payload()
    exam, error = validate_quiz_exam_payload(data)
    if error:
        return api_error(error, 400)
    exam_id = str(data.get("id", "")).strip()
    if not exam_id:
        exam_id = uuid.uuid4().hex
    if len(exam_id) > 100:
        return api_error("Mã đề thi không hợp lệ.", 400)
    exam["id"] = exam_id
    try:
        create_quiz_exam(exam)
    except sqlite3.IntegrityError:
        return api_error("Mã đề thi đã tồn tại.", 409)
    return jsonify(get_quiz_exam(exam_id)), 201


@api_routes.put("/api/admin/quiz/exams/<exam_id>")
@admin_required
def update_quiz_exam_route(exam_id):
    exam, error = validate_quiz_exam_payload(json_payload())
    if error:
        return api_error(error, 400)
    if not update_quiz_exam(exam_id, exam):
        return api_error("Không tìm thấy đề thi.", 404)
    return jsonify(get_quiz_exam(exam_id))


@api_routes.delete("/api/admin/quiz/exams/<exam_id>")
@admin_required
def delete_quiz_exam_route(exam_id):
    if not delete_quiz_exam(exam_id):
        return api_error("Không tìm thấy đề thi.", 404)
    return jsonify({"message": "Đã xóa đề thi."})


@api_routes.post("/api/admin/quiz/exams/<exam_id>/publish")
@admin_required
def publish_quiz_exam_route(exam_id):
    data = json_payload()
    due_at = data.get("due_at")
    student_ids = data.get("student_ids")
    if due_at is not None and not isinstance(due_at, str):
        return api_error("Hạn nộp không hợp lệ.", 400)
    if student_ids is not None:
        if not isinstance(student_ids, list) or any(type(student_id) is not int for student_id in student_ids):
            return api_error("Danh sách học sinh không hợp lệ.", 400)
    try:
        published = publish_quiz_exam(exam_id, due_at or None, student_ids)
    except ValueError as error:
        return api_error(str(error), 400)
    if not published:
        return api_error("Không tìm thấy đề thi.", 404)
    return jsonify(get_quiz_exam(exam_id))


def validate_quiz_question_payload(data):
    if not isinstance(data, dict):
        return None, "Dữ liệu câu hỏi không hợp lệ."
    text = data.get("text", "")
    options = data.get("options")
    answer = data.get("answer")
    answers = data.get("answers")
    answer_key = data.get("answer_key", "")
    explanation = data.get("explanation", "")
    question_type = data.get("type", "single_choice")
    points = data.get("points", 1)
    required = data.get("required", True)
    if question_type not in {"single_choice", "multiple_choice", "true_false", "essay"}:
        return None, "Loại câu hỏi không hợp lệ."
    if type(points) is not int or not 1 <= points <= 100:
        return None, "Điểm câu hỏi không hợp lệ."
    if type(required) is not bool:
        return None, "Thiết lập bắt buộc không hợp lệ."
    if not isinstance(text, str) or not isinstance(explanation, str):
        return None, "Nội dung câu hỏi phải có giá trị dạng chuỗi."
    if not isinstance(answer_key, str) or len(answer_key) > 2000:
        return None, "Đáp án tự luận không hợp lệ."
    answer_key = answer_key.strip()
    if question_type == "essay" and not answer_key:
        return None, "Câu tự luận cần đáp án mẫu để tự chấm."
    text = text.strip()
    explanation = explanation.strip()
    if not text or len(text) > 1000:
        return None, "Nội dung câu hỏi không hợp lệ."
    if question_type in {"essay"}:
        options = options if isinstance(options, list) else []
    elif not isinstance(options, list) or not 2 <= len(options) <= 6:
        return None, "Câu hỏi cần từ 2 đến 6 đáp án."
    if question_type != "essay" and any(not isinstance(option, str) or not option.strip() or len(option.strip()) > 500 for option in options):
        return None, "Các đáp án không hợp lệ."
    if question_type == "single_choice" and (type(answer) is not int or not 0 <= answer < len(options)):
        return None, "Đáp án đúng không hợp lệ."
    if question_type == "multiple_choice":
        if not isinstance(answers, list) or not answers or any(type(value) is not int or value < 0 or value >= len(options) for value in answers):
            return None, "Các đáp án đúng không hợp lệ."
        if len(set(answers)) != len(answers):
            return None, "Các đáp án đúng không được trùng."
    if question_type == "true_false" and type(answer) is not int or answer not in {0, 1}:
        return None, "Đáp án đúng/sai không hợp lệ."
    if len(explanation) > 1000:
        return None, "Giải thích không được vượt quá 1000 ký tự."
    return {
        "text": text,
        "options": [option.strip() for option in options],
        "answer": answer,
        "explanation": explanation,
        "type": question_type,
        "answers": answers if isinstance(answers, list) else [],
        "points": points,
        "answer_key": answer_key,
        "required": required,
    }, None


@api_routes.post("/api/admin/quiz/exams/<exam_id>/questions")
@admin_required
def create_quiz_question_route(exam_id):
    if not get_quiz_exam(exam_id):
        return api_error("Không tìm thấy đề thi.", 404)
    question, error = validate_quiz_question_payload(json_payload())
    if error:
        return api_error(error, 400)
    question_id = create_quiz_question(exam_id, question)
    return jsonify({"id": question_id, "message": "Đã thêm câu hỏi."}), 201


@api_routes.put("/api/admin/quiz/exams/<exam_id>/questions/<int:question_id>")
@admin_required
def update_quiz_question_route(exam_id, question_id):
    question, error = validate_quiz_question_payload(json_payload())
    if error:
        return api_error(error, 400)
    if not update_quiz_question(question_id, exam_id, question):
        return api_error("Không tìm thấy câu hỏi.", 404)
    return jsonify({"id": question_id, "message": "Đã cập nhật câu hỏi."})


@api_routes.delete("/api/admin/quiz/exams/<exam_id>/questions/<int:question_id>")
@admin_required
def delete_quiz_question_route(exam_id, question_id):
    if not delete_quiz_question(question_id, exam_id):
        return api_error("Không tìm thấy câu hỏi.", 404)
    return jsonify({"message": "Đã xóa câu hỏi."})


@api_routes.post("/api/quiz/exams/<exam_id>/submit")
@login_required
def submit_assigned_quiz_exam(exam_id):
    if g.current_user["role"] != "user":
        return api_error("Chỉ học sinh mới được nộp bài thi.", 403)
    data = json_payload()
    submission, error = submit_quiz_submission(
        exam_id, g.current_user["id"], data.get("answers")
    )
    if error:
        status = 409 if "đã được nộp" in error or "quá hạn" in error else 403
        return api_error(error, status)
    return jsonify(submission), 201


@api_routes.get("/api/admin/quiz/exams/<exam_id>/submissions")
@admin_required
def admin_quiz_submissions(exam_id):
    if not get_quiz_exam(exam_id):
        return api_error("Không tìm thấy đề thi.", 404)
    submissions = list_quiz_submissions(exam_id)
    return jsonify(submissions)


@api_routes.put("/api/admin/quiz/submissions/<int:submission_id>/grade")
@admin_required
def grade_quiz_submission_route(submission_id):
    data = json_payload()
    manual_score = data.get("manual_score")
    comment = data.get("comment", "")
    if type(manual_score) is not int or manual_score < 0:
        return api_error("Điểm chấm không hợp lệ.", 400)
    if not grade_quiz_submission(submission_id, manual_score, comment):
        return api_error("Không tìm thấy bài nộp.", 404)
    return jsonify({"message": "Đã chấm bài.", "manual_score": manual_score})


@api_routes.post("/api/quiz/attempts")
def save_quiz_attempt():
    data = json_payload()
    exam_id = str(data.get("examId", "")).strip()
    duration_seconds = data.get("duration")
    submitted_answers = data.get("answers")

    if not exam_id or len(exam_id) > 100:
        return api_error("Mã đề thi không hợp lệ.", 400)
    if type(duration_seconds) is not int or not 0 <= duration_seconds <= 18000:
        return api_error("Thời gian làm bài không hợp lệ.", 400)
    exam = get_quiz_exam(exam_id, include_answers=True)
    if not exam:
        return api_error("Không tìm thấy đề thi.", 404)
    if not exam["questions"]:
        return api_error("Đề thi chưa có câu hỏi.", 400)
    if not isinstance(submitted_answers, list) or len(submitted_answers) != len(exam["questions"]):
        return api_error("Danh sách đáp án không hợp lệ.", 400)

    correct_count = 0
    for question, submitted_answer in zip(exam["questions"], submitted_answers):
        if submitted_answer is not None:
            if type(submitted_answer) is not int:
                return api_error("Đáp án không hợp lệ.", 400)
            if not 0 <= submitted_answer < len(question["options"]):
                return api_error("Đáp án không hợp lệ.", 400)
            if submitted_answer == question["answer"]:
                correct_count += 1

    exam_title = exam["title"]
    subject = exam["subject"]
    total_questions = len(exam["questions"])

    user_id = session.get("user_id")
    if user_id and not get_user_by_id(user_id):
        user_id = None
    attempt_id = create_quiz_attempt({
        "exam_id": exam_id,
        "exam_title": exam_title,
        "subject": subject,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "duration_seconds": duration_seconds,
    }, user_id)
    score = round(correct_count / total_questions * 100)
    review = []
    for question, submitted_answer in zip(exam["questions"], submitted_answers):
        selected = submitted_answer if type(submitted_answer) is int else None
        review.append({
            "text": question["text"],
            "options": question["options"],
            "selected": selected,
            "answer": question["answer"],
            "explanation": question["explanation"],
        })
    return jsonify({
        "id": attempt_id,
        "message": "Đã lưu kết quả bài thi.",
        "correct": correct_count,
        "total": total_questions,
        "score": score,
        "duration": duration_seconds,
        "review": review,
    }), 201


@api_routes.post("/api/admin/users")
@admin_required
def create_admin():
    data = json_payload()
    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")
    if not all(isinstance(value, str) for value in (name, email, password)):
        return api_error("Họ tên, email và mật khẩu phải có giá trị dạng chuỗi.", 400)
    name = name.strip()
    email = normalize_email(email)
    if not name or len(name) > 80:
        return api_error("Họ tên cần có từ 1 đến 80 ký tự.", 400)
    if not valid_email(email):
        return api_error("Email không hợp lệ.", 400)
    if len(password) < 8:
        return api_error("Mật khẩu cần có ít nhất 8 ký tự.", 400)
    try:
        user_id = create_user(name, email, hash_password(password), "admin")
    except sqlite3.IntegrityError:
        return api_error("Email này đã được sử dụng.", 409)
    return jsonify(public_account(get_user_by_id(user_id))), 201


@page_routes.get("/")
def homepage():
    return render_template("index.html", books=list_books())


@page_routes.get("/courses/<int:course_id>")
def course_detail_page(course_id):
    course = get_course_by_id(course_id)
    if not course:
        abort(404)
    return render_template("course-detail.html", course=course)


@page_routes.get("/books/<int:book_id>")
def book_detail_page(book_id):
    book = get_book_by_id(book_id)
    if not book:
        abort(404)
    return render_template("book-detail.html", book=book)


@page_routes.get("/uploads/<path:filename>")
def uploaded_image(filename):
    if re.fullmatch(r"[a-f0-9]{32}\.(?:png|jpg|gif|webp)", filename) is None:
        return api_error("Không tìm thấy ảnh.", 404)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename, max_age=3600)


@page_routes.get("/static/uploads/books/<path:filename>")
def uploaded_book_cover(filename):
    if re.fullmatch(r"[a-f0-9]{32}\.(?:png|jpg|gif|webp)", filename) is None:
        return api_error("Không tìm thấy ảnh bìa.", 404)
    return send_from_directory(current_app.config["BOOK_UPLOAD_FOLDER"], filename, max_age=3600)


@page_routes.get("/<path:filename>")
def view_or_static_file(filename):
    path = Path(filename)
    if any(part.startswith(".") for part in path.parts):
        return api_error("Không tìm thấy trang.", 404)
    if path.suffix.lower() not in STATIC_EXTENSIONS:
        return api_error("Không tìm thấy trang.", 404)
    if path.suffix.lower() == ".html":
        if path.as_posix() == "index.html":
            return render_template("index.html", books=list_books())
        return render_template(filename)
    return send_from_directory(current_app.config["PROJECT_ROOT"], filename)


def json_payload():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def api_error(message, status):
    return jsonify({"error": message}), status
