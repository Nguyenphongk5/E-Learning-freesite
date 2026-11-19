import re
import random
import sqlite3
import json
from pathlib import Path
from urllib.parse import urlsplit

from flask import current_app, g
from werkzeug.security import check_password_hash, generate_password_hash


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

DEFAULT_BOOKS = [
    (
        "Clean Code: A Handbook of Agile Software Craftsmanship",
        "Robert C. Martin (Uncle Bob)",
        "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80",
        "Khác / Best Practices",
        "Cuốn sách kinh điển hướng dẫn cách viết mã nguồn sạch, dễ đọc, dễ bảo trì và tối ưu cho lập trình viên.",
        "https://www.oreilly.com/library/view/clean-code-a/9780132350884/",
    ),
    (
        "The C++ Programming Language (4th Edition)",
        "Bjarne Stroustrup",
        "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80",
        "C++",
        "Cuốn sách đầy đủ và chính thống nhất về ngôn ngữ C++ do chính cha đẻ Bjarne Stroustrup biên soạn.",
        "https://www.stroustrup.com/4th.html",
    ),
    (
        "Python Crash Course: A Hands-On, Project-Based Introduction to Programming",
        "Eric Matthes",
        "https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80",
        "Python",
        "Cuốn sách bán chạy nhất thế giới dành cho người mới bắt đầu học Python qua các dự án thực tế.",
        "https://nostarch.com/pythoncrashcourse2e",
    ),
    (
        "Effective Java (3rd Edition)",
        "Joshua Bloch",
        "https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=600&q=80",
        "Java",
        "Cẩm nang không thể thiếu dành cho các Java Developer muốn nâng cao tư duy thiết kế và tối ưu mã nguồn Java.",
        "https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/",
    ),
    (
        "Eloquent JavaScript: A Modern Introduction to Programming",
        "Marijn Haverbeke",
        "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80",
        "Web Development",
        "Cuốn sách tuyệt vời về ngôn ngữ JavaScript hiện đại, từ tư duy lập trình căn bản đến các ứng dụng web phức tạp.",
        "https://eloquentjavascript.net/",
    ),
    (
        "Head First Design Patterns",
        "Eric Freeman & Elisabeth Robson",
        "https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=600&q=80",
        "Khác / Architecture",
        "Hướng dẫn trực quan, sinh động về các mẫu thiết kế phần mềm (Design Patterns) phổ biến trong công nghiệp.",
        "https://www.oreilly.com/library/view/head-first-design/9781492077992/",
    ),
]


def seed_books(connection):
    if connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] != 0:
        return
    connection.executemany(
        "INSERT INTO books (title, author, cover_image, category, description, document_url) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        DEFAULT_BOOKS,
    )


def seed_quiz_data(connection):
    if connection.execute("SELECT COUNT(*) FROM quiz_exams").fetchone()[0]:
        return
    exams = [
        ("html-foundations", "Nền tảng HTML & CSS", "HTML & CSS", "Cơ bản", 12, "Cấu trúc trang, semantic HTML và các nguyên tắc CSS."),
        ("javascript-basics", "JavaScript căn bản", "JavaScript", "Cơ bản", 15, "Biến, kiểu dữ liệu, hàm và các thao tác với mảng."),
        ("programming-logic", "Tư duy lập trình", "Lập trình", "Trung bình", 15, "Thuật toán, vòng lặp, độ phức tạp và tư duy giải quyết vấn đề."),
    ]
    connection.executemany(
        "INSERT OR IGNORE INTO quiz_exams "
        "(id, title, subject, difficulty, duration, description) VALUES (?, ?, ?, ?, ?, ?)",
        exams,
    )
    questions = {
        "html-foundations": [
            ("Thẻ HTML nào biểu thị nội dung độc lập, có thể tái sử dụng như một bài viết?", ["<section>", "<article>", "<aside>", "<span>"], 1, "<article> dùng cho nội dung độc lập."),
            ("Thuộc tính CSS nào điều khiển khoảng trống bên trong đường viền?", ["margin", "gap", "padding", "spacing"], 2, "padding là khoảng đệm bên trong."),
            ("Selector nào chọn phần tử có id là \"menu\"?", [".menu", "#menu", "menu#", "*menu"], 1, "Selector id bắt đầu bằng ký tự #."),
            ("Thuộc tính nào giúp ảnh giữ tỷ lệ khi vừa khung chứa?", ["object-fit: cover", "display: inline", "position: fixed", "float: left"], 0, "object-fit: cover giữ tỷ lệ ảnh."),
            ("Vai trò chính của thuộc tính alt trên ảnh là gì?", ["Tạo viền", "Đặt kích thước", "Cung cấp mô tả thay thế", "Tải ảnh nhanh hơn"], 2, "alt cung cấp mô tả thay thế."),
        ],
        "javascript-basics": [
            ("Từ khóa nào khai báo biến có phạm vi khối và có thể gán lại?", ["var", "let", "const", "static"], 1, "let có phạm vi khối."),
            ("Kết quả của typeof null trong JavaScript là gì?", ['"null"', '"undefined"', '"object"', '"boolean"'], 2, "typeof null trả về \"object\"."),
            ("Phương thức nào tạo mảng mới bằng cách biến đổi từng phần tử?", ["filter()", "map()", "find()", "reduceRight()"], 1, "map() biến đổi từng phần tử."),
            ("Toán tử === kiểm tra điều gì?", ["Chỉ giá trị", "Chỉ kiểu", "Giá trị và kiểu", "Giá trị sau ép kiểu"], 2, "=== so sánh cả giá trị và kiểu."),
            ("Sự kiện nào phản hồi thao tác nhấn nút?", ["submit", "change", "click", "load"], 2, "Sự kiện click phát khi nhấn."),
            ("Promise.resolve(5) tạo ra trạng thái nào?", ["pending", "fulfilled", "rejected", "cancelled"], 1, "Promise.resolve tạo Promise fulfilled."),
        ],
        "programming-logic": [
            ("Cấu trúc nào lặp khi điều kiện còn đúng?", ["if/else", "while", "switch", "return"], 1, "while lặp khi điều kiện đúng."),
            ("Độ phức tạp tìm kiếm tuyến tính trên n phần tử là gì?", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 2, "Tìm kiếm tuyến tính là O(n)."),
            ("Tìm kiếm nhị phân yêu cầu mảng ở trạng thái nào?", ["Số phần tử chẵn", "Đã được sắp xếp", "Không có số âm", "Không trùng giá trị"], 1, "Mảng phải được sắp xếp."),
            ("Biến đếm thường dùng để làm gì?", ["Đếm lặp hoặc phần tử", "Sắp xếp dữ liệu", "Lưu toàn bộ chương trình", "Dừng mọi hàm"], 0, "Biến đếm theo dõi số lần lặp."),
            ("Bước đầu tiên khi giải bài toán lập trình là gì?", ["Viết mã", "Hiểu đầu vào và yêu cầu", "Chọn ngôn ngữ phức tạp", "Tối ưu trước"], 1, "Xác định yêu cầu trước."),
        ],
    }
    for exam_id, exam_questions in questions.items():
        for position, (text, options, answer_index, explanation) in enumerate(exam_questions):
            connection.execute(
                "INSERT INTO quiz_questions "
                "(exam_id, text, options_json, answer_index, explanation, position) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (exam_id, text, json.dumps(options, ensure_ascii=False), answer_index, explanation, position),
            )
    connection.execute(
        "UPDATE quiz_exams SET status = 'published', published_at = COALESCE(published_at, CURRENT_TIMESTAMP)"
    )


def get_database():
    if "database" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.database = connection
    return g.database


def initialize_database(app):
    admin_email = app.config["BOOTSTRAP_ADMIN_EMAIL"]
    admin_password = app.config["BOOTSTRAP_ADMIN_PASSWORD"]
    is_production = str(app.config.get("APP_ENV", "")).lower() == "production"
    if is_production and (not admin_email or not admin_password):
        raise RuntimeError(
            "Set ADMIN_EMAIL and ADMIN_PASSWORD to bootstrap the first admin in production."
        )
    if is_production and admin_password == "admin123":
        raise RuntimeError("ADMIN_PASSWORD must not use the insecure default in production.")
    if is_production and len(admin_password) < 12:
        raise RuntimeError("ADMIN_PASSWORD must be at least 12 characters in production.")
    if bool(admin_email) != bool(admin_password):
        raise RuntimeError("Set both ADMIN_EMAIL and ADMIN_PASSWORD to bootstrap the first admin.")

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
            details TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            cover_image TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            details TEXT NOT NULL DEFAULT '',
            document_url TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            exam_id TEXT NOT NULL,
            exam_title TEXT NOT NULL,
            subject TEXT NOT NULL,
            correct_count INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            score INTEGER NOT NULL,
            duration_seconds INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS quiz_exams (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            difficulty TEXT NOT NULL DEFAULT 'Cơ bản',
            duration INTEGER NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
            due_at TEXT,
            published_at TEXT,
            shuffle_questions INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id TEXT NOT NULL REFERENCES quiz_exams(id) ON DELETE CASCADE,
            text TEXT NOT NULL,
            options_json TEXT NOT NULL,
            answer_index INTEGER NOT NULL,
            explanation TEXT NOT NULL DEFAULT '',
            question_type TEXT NOT NULL DEFAULT 'single_choice',
            correct_answers_json TEXT NOT NULL DEFAULT '[]',
            answer_key TEXT NOT NULL DEFAULT '',
            points INTEGER NOT NULL DEFAULT 1,
            required_answer INTEGER NOT NULL DEFAULT 1,
            position INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS quiz_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id TEXT NOT NULL REFERENCES quiz_exams(id) ON DELETE CASCADE,
            student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            due_at TEXT,
            UNIQUE(exam_id, student_id)
        );
        CREATE TABLE IF NOT EXISTS quiz_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id TEXT NOT NULL REFERENCES quiz_exams(id) ON DELETE CASCADE,
            student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            answers_json TEXT NOT NULL,
            auto_score INTEGER NOT NULL DEFAULT 0,
            manual_score INTEGER,
            score INTEGER,
            status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('draft', 'submitted', 'graded')),
            submitted_at TEXT,
            graded_at TEXT,
            teacher_comment TEXT NOT NULL DEFAULT '',
            UNIQUE(exam_id, student_id)
        );
        CREATE TABLE IF NOT EXISTS quiz_monthly_aggregates (
            period_month TEXT NOT NULL,
            exam_id TEXT NOT NULL,
            exam_title TEXT NOT NULL,
            subject TEXT NOT NULL,
            attempts INTEGER NOT NULL,
            score_total INTEGER NOT NULL,
            correct_count INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            best_score INTEGER NOT NULL,
            PRIMARY KEY (period_month, exam_id, exam_title, subject)
        );
        CREATE TABLE IF NOT EXISTS auth_rate_limit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            client_key TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_auth_rate_limit_events_client
            ON auth_rate_limit_events(action, client_key, created_at);
        CREATE INDEX IF NOT EXISTS idx_auth_rate_limit_events_created_at
            ON auth_rate_limit_events(created_at);
        CREATE INDEX IF NOT EXISTS idx_quiz_attempts_created_at
            ON quiz_attempts(created_at DESC, id DESC);
        CREATE INDEX IF NOT EXISTS idx_quiz_attempts_exam_id
            ON quiz_attempts(exam_id);
        """
    )
    course_columns = {row["name"] for row in connection.execute("PRAGMA table_info(courses)")}
    if "details" not in course_columns:
        connection.execute("ALTER TABLE courses ADD COLUMN details TEXT NOT NULL DEFAULT ''")
    book_columns = {row["name"] for row in connection.execute("PRAGMA table_info(books)")}
    if "details" not in book_columns:
        connection.execute("ALTER TABLE books ADD COLUMN details TEXT NOT NULL DEFAULT ''")
    exam_columns = {row["name"] for row in connection.execute("PRAGMA table_info(quiz_exams)") }
    if "status" not in exam_columns:
        connection.execute("ALTER TABLE quiz_exams ADD COLUMN status TEXT NOT NULL DEFAULT 'draft'")
    if "due_at" not in exam_columns:
        connection.execute("ALTER TABLE quiz_exams ADD COLUMN due_at TEXT")
    if "published_at" not in exam_columns:
        connection.execute("ALTER TABLE quiz_exams ADD COLUMN published_at TEXT")
    if "shuffle_questions" not in exam_columns:
        connection.execute("ALTER TABLE quiz_exams ADD COLUMN shuffle_questions INTEGER NOT NULL DEFAULT 0")
    question_columns = {row["name"] for row in connection.execute("PRAGMA table_info(quiz_questions)") }
    if "question_type" not in question_columns:
        connection.execute("ALTER TABLE quiz_questions ADD COLUMN question_type TEXT NOT NULL DEFAULT 'single_choice'")
    if "correct_answers_json" not in question_columns:
        connection.execute("ALTER TABLE quiz_questions ADD COLUMN correct_answers_json TEXT NOT NULL DEFAULT '[]'")
    if "points" not in question_columns:
        connection.execute("ALTER TABLE quiz_questions ADD COLUMN points INTEGER NOT NULL DEFAULT 1")
    if "answer_key" not in question_columns:
        connection.execute("ALTER TABLE quiz_questions ADD COLUMN answer_key TEXT NOT NULL DEFAULT ''")
    if "required_answer" not in question_columns:
        connection.execute("ALTER TABLE quiz_questions ADD COLUMN required_answer INTEGER NOT NULL DEFAULT 1")
    connection.execute(
        "UPDATE quiz_exams SET status = 'published', "
        "published_at = COALESCE(published_at, CURRENT_TIMESTAMP) "
        "WHERE id IN ('html-foundations', 'javascript-basics', 'programming-logic')"
    )
    for row in connection.execute(
        "SELECT id, answer_index, correct_answers_json FROM quiz_questions"
    ).fetchall():
        if row["correct_answers_json"] in {"", "[]"}:
            connection.execute(
                "UPDATE quiz_questions SET correct_answers_json = ? WHERE id = ?",
                (json.dumps([row["answer_index"]], ensure_ascii=False), row["id"]),
            )
    if connection.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
        connection.executemany(
            "INSERT INTO courses (title, description, image_url, course_url) VALUES (?, ?, ?, ?)",
            DEFAULT_COURSES,
        )
    seed_books(connection)
    seed_quiz_data(connection)

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
            print(f"Admin account initialized: {admin_email}")
    connection.execute(
        "INSERT INTO quiz_assignments (exam_id, student_id, due_at) "
        "SELECT e.id, u.id, e.due_at FROM quiz_exams e "
        "JOIN users u ON u.role = 'user' WHERE e.status = 'published' "
        "ON CONFLICT(exam_id, student_id) DO NOTHING"
    )
    connection.commit()
    connection.close()


def normalize_email(value):
    return str(value).strip().lower()


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def valid_email(email):
    return len(email) <= 254 and re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) is not None


def public_account(user):
    return {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}


def validate_course(data):
    fields = ("title", "description", "details", "image_url", "course_url")
    if any(not isinstance(data.get(field, ""), str) for field in fields):
        return None, "Các trường khóa học phải có giá trị dạng chuỗi."

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    details = data.get("details", "").strip()
    image_url = data.get("image_url", "").strip()
    course_url = data.get("course_url", "").strip()
    if not title or len(title) > 150:
        return None, "Tên khóa học cần có từ 1 đến 150 ký tự."
    if len(description) > 1200:
        return None, "Mô tả không được vượt quá 1200 ký tự."
    if len(details) > 5000:
        return None, "Nội dung chi tiết không được vượt quá 5000 ký tự."
    try:
        parsed_course_url = urlsplit(course_url)
        _ = parsed_course_url.port
    except ValueError:
        return None, "Liên kết khóa học không hợp lệ."
    if parsed_course_url.scheme not in {"http", "https"} or not parsed_course_url.hostname:
        return None, "Liên kết khóa học phải bắt đầu bằng http:// hoặc https://."
    if image_url:
        is_local_image = image_url.startswith("images/") and ".." not in Path(image_url).parts
        is_uploaded_image = re.fullmatch(r"/uploads/[a-f0-9]{32}\.(?:png|jpg|gif|webp)", image_url) is not None
        try:
            parsed_image_url = urlsplit(image_url)
            _ = parsed_image_url.port
            is_external_image = (
                parsed_image_url.scheme in {"http", "https"}
                and bool(parsed_image_url.hostname)
            )
        except ValueError:
            is_external_image = False
        if not (is_local_image or is_uploaded_image or is_external_image):
            return None, "Ảnh cần là đường dẫn images/ hoặc URL http(s)."
    return {
        "title": title,
        "description": description,
        "details": details,
        "image_url": image_url,
        "course_url": course_url,
    }, None


def find_user_by_email(email):
    return get_database().execute(
        "SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email,)
    ).fetchone()


def get_user_by_id(user_id):
    return get_database().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_user(name, email, password_hash, role):
    database = get_database()
    cursor = database.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, role),
    )
    if role == "user":
        database.execute(
            "INSERT INTO quiz_assignments (exam_id, student_id, due_at) "
            "SELECT id, ?, due_at FROM quiz_exams WHERE status = 'published' "
            "ON CONFLICT(exam_id, student_id) DO NOTHING",
            (cursor.lastrowid,),
        )
    database.commit()
    return cursor.lastrowid


def list_accounts():
    return get_database().execute(
        "SELECT id, name, email, role, created_at FROM users ORDER BY role DESC, id"
    ).fetchall()


def count_admin_accounts():
    return get_database().execute(
        "SELECT COUNT(*) FROM users WHERE role = 'admin'"
    ).fetchone()[0]


def get_account_data(user_id):
    database = get_database()
    account = database.execute(
        "SELECT id, name, email, role, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    attempts = database.execute(
        "SELECT exam_title, subject, correct_count, total_questions, score, "
        "duration_seconds, created_at FROM quiz_attempts "
        "WHERE user_id = ? ORDER BY created_at DESC, id DESC",
        (user_id,),
    ).fetchall()
    return {"account": dict(account), "quiz_attempts": [dict(row) for row in attempts]}


def _archive_quiz_attempts(database, where_clause, parameters):
    grouped_attempts = database.execute(
        "SELECT strftime('%Y-%m', created_at) AS period_month, exam_id, exam_title, "
        "subject, COUNT(*) AS attempts, SUM(score) AS score_total, "
        "SUM(correct_count) AS correct_count, SUM(total_questions) AS total_questions, "
        "MAX(score) AS best_score FROM quiz_attempts WHERE "
        + where_clause
        + " GROUP BY period_month, exam_id, exam_title, subject",
        parameters,
    ).fetchall()
    for row in grouped_attempts:
        database.execute(
            "INSERT INTO quiz_monthly_aggregates "
            "(period_month, exam_id, exam_title, subject, attempts, score_total, "
            "correct_count, total_questions, best_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(period_month, exam_id, exam_title, subject) DO UPDATE SET "
            "attempts = attempts + excluded.attempts, "
            "score_total = score_total + excluded.score_total, "
            "correct_count = correct_count + excluded.correct_count, "
            "total_questions = total_questions + excluded.total_questions, "
            "best_score = MAX(best_score, excluded.best_score)",
            tuple(row),
        )
    return database.execute(
        "DELETE FROM quiz_attempts WHERE " + where_clause, parameters
    ).rowcount


def archive_expired_quiz_attempts(cutoff):
    database = get_database()
    deleted = _archive_quiz_attempts(database, "created_at < ?", (cutoff,))
    database.commit()
    return deleted


def delete_user_and_archive_attempts(user_id):
    database = get_database()
    archived_attempts = _archive_quiz_attempts(database, "user_id = ?", (user_id,))
    database.execute("DELETE FROM users WHERE id = ?", (user_id,))
    database.commit()
    return archived_attempts


def _question_dict(row, include_answer=True):
    question = {
        "id": row["id"],
        "text": row["text"],
        "options": json.loads(row["options_json"]),
        "explanation": row["explanation"],
        "position": row["position"],
        "type": row["question_type"],
        "points": row["points"],
        "answer_key": row["answer_key"],
        "required": bool(row["required_answer"]),
    }
    if include_answer:
        if row["question_type"] in {"multiple_choice"}:
            question["answers"] = json.loads(row["correct_answers_json"])
        else:
            question["answer"] = row["answer_index"]
    return question


def list_quiz_exams(include_questions=False):
    database = get_database()
    rows = database.execute(
        "SELECT id, title, subject, difficulty, duration, description, status, due_at, published_at, shuffle_questions "
        "FROM quiz_exams ORDER BY created_at DESC"
    ).fetchall()
    exams = []
    for row in rows:
        exam = dict(row)
        question_rows = database.execute(
            "SELECT id, text, options_json, answer_index, explanation, position, "
            "question_type, correct_answers_json, answer_key, points, required_answer "
            "FROM quiz_questions WHERE exam_id = ? ORDER BY position, id",
            (exam["id"],),
        ).fetchall()
        exam["questionCount"] = len(question_rows)
        if include_questions:
            exam["questions"] = [_question_dict(question) for question in question_rows]
        else:
            exam["questions"] = [
                {
                    "id": question["id"],
                    "text": question["text"],
                    "options": json.loads(question["options_json"]),
                    "type": question["question_type"],
                    "points": question["points"],
                    "required": bool(question["required_answer"]),
                }
                for question in question_rows
            ]
        exams.append(exam)
    return exams


def get_quiz_exam(exam_id, include_answers=False):
    database = get_database()
    row = database.execute(
        "SELECT id, title, subject, difficulty, duration, description, status, due_at, published_at, shuffle_questions "
        "FROM quiz_exams WHERE id = ?",
        (exam_id,),
    ).fetchone()
    if not row:
        return None
    exam = dict(row)
    question_rows = database.execute(
        "SELECT id, text, options_json, answer_index, explanation, position, "
        "question_type, correct_answers_json, answer_key, points, required_answer "
        "FROM quiz_questions WHERE exam_id = ? ORDER BY position, id",
        (exam_id,),
    ).fetchall()
    exam["questionCount"] = len(question_rows)
    exam["questions"] = [
        _question_dict(question, include_answer=include_answers)
        if include_answers
        else {
            "id": question["id"],
            "text": question["text"],
            "options": json.loads(question["options_json"]),
            "type": question["question_type"],
            "points": question["points"],
            "required": bool(question["required_answer"]),
        }
        for question in question_rows
    ]
    if not include_answers and exam.get("shuffle_questions"):
        random.shuffle(exam["questions"])
    return exam


def create_quiz_exam(data):
    database = get_database()
    cursor = database.execute(
        "INSERT INTO quiz_exams "
        "(id, title, subject, difficulty, duration, description, status, due_at, published_at, shuffle_questions) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["id"], data["title"], data["subject"],
            data.get("difficulty", "Cơ bản"), data["duration"], data.get("description", ""),
            data.get("status", "draft"), data.get("due_at"),
            data.get("published_at"), 1 if data.get("shuffle_questions") else 0,
        ),
    )
    database.commit()
    return cursor


def update_quiz_exam(exam_id, data):
    database = get_database()
    published_at = data.get("published_at")
    if published_at is None:
        existing = database.execute(
            "SELECT published_at FROM quiz_exams WHERE id = ?", (exam_id,)
        ).fetchone()
        published_at = existing["published_at"] if existing else None
    cursor = database.execute(
        "UPDATE quiz_exams SET title = ?, subject = ?, difficulty = ?, duration = ?, "
        "description = ?, status = ?, due_at = ?, published_at = ?, shuffle_questions = ? "
        "WHERE id = ?",
        (
            data["title"], data["subject"], data.get("difficulty", "Cơ bản"),
            data["duration"], data.get("description", ""), data.get("status", "draft"),
            data.get("due_at"), published_at, 1 if data.get("shuffle_questions") else 0, exam_id,
        ),
    )
    database.commit()
    return cursor.rowcount > 0


def delete_quiz_exam(exam_id):
    database = get_database()
    cursor = database.execute("DELETE FROM quiz_exams WHERE id = ?", (exam_id,))
    database.commit()
    return cursor.rowcount > 0


def create_quiz_question(exam_id, data):
    database = get_database()
    position = database.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 FROM quiz_questions WHERE exam_id = ?",
        (exam_id,),
    ).fetchone()[0]
    cursor = database.execute(
        "INSERT INTO quiz_questions "
        "(exam_id, text, options_json, answer_index, explanation, position, "
        "question_type, correct_answers_json, answer_key, points, required_answer) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            exam_id, data["text"], json.dumps(data["options"], ensure_ascii=False),
            data.get("answer", -1), data.get("explanation", ""), position,
            data["type"], json.dumps(data.get("answers", []), ensure_ascii=False),
            data.get("answer_key", ""), data["points"],
            1 if data.get("required", True) else 0,
        ),
    )
    database.commit()
    return cursor.lastrowid


def update_quiz_question(question_id, exam_id, data):
    database = get_database()
    cursor = database.execute(
        "UPDATE quiz_questions SET text = ?, options_json = ?, answer_index = ?, explanation = ?, "
        "question_type = ?, correct_answers_json = ?, answer_key = ?, points = ?, required_answer = ? "
        "WHERE id = ? AND exam_id = ?",
        (
            data["text"], json.dumps(data["options"], ensure_ascii=False),
            data.get("answer", -1), data.get("explanation", ""),
            data["type"], json.dumps(data.get("answers", []), ensure_ascii=False),
            data.get("answer_key", ""), data["points"],
            1 if data.get("required", True) else 0, question_id, exam_id,
        ),
    )
    database.commit()
    return cursor.rowcount > 0


def delete_quiz_question(question_id, exam_id):
    database = get_database()
    cursor = database.execute(
        "DELETE FROM quiz_questions WHERE id = ? AND exam_id = ?", (question_id, exam_id)
    )
    database.commit()
    return cursor.rowcount > 0


def publish_quiz_exam(exam_id, due_at=None, student_ids=None):
    database = get_database()
    exam = database.execute(
        "SELECT id, status FROM quiz_exams WHERE id = ?", (exam_id,)
    ).fetchone()
    if not exam:
        return False
    question_count = database.execute(
        "SELECT COUNT(*) AS count FROM quiz_questions WHERE exam_id = ?", (exam_id,)
    ).fetchone()["count"]
    if question_count < 1:
        raise ValueError("Đề thi cần ít nhất một câu hỏi trước khi xuất bản.")
    database.execute(
        "UPDATE quiz_exams SET status = 'published', due_at = ?, published_at = "
        "COALESCE(published_at, CURRENT_TIMESTAMP) WHERE id = ?",
        (due_at, exam_id),
    )
    if student_ids:
        for student_id in student_ids:
            database.execute(
                "INSERT INTO quiz_assignments (exam_id, student_id, due_at) "
                "VALUES (?, ?, ?) "
                "ON CONFLICT(exam_id, student_id) DO UPDATE SET due_at = excluded.due_at",
                (exam_id, student_id, due_at),
            )
    else:
        database.execute(
            "INSERT INTO quiz_assignments (exam_id, student_id, due_at) "
            "SELECT ?, id, ? FROM users WHERE role = 'user' "
            "ON CONFLICT(exam_id, student_id) DO UPDATE SET due_at = excluded.due_at",
            (exam_id, due_at),
        )
    database.commit()
    return True


def list_assigned_quiz_exams(student_id):
    database = get_database()
    rows = database.execute(
        "SELECT e.id, e.title, e.subject, e.difficulty, e.duration, e.description, "
        "e.status, COALESCE(a.due_at, e.due_at) AS due_at, e.published_at, "
        "s.status AS submission_status, s.score "
        "FROM quiz_assignments a "
        "JOIN quiz_exams e ON e.id = a.exam_id "
        "LEFT JOIN quiz_submissions s ON s.exam_id = e.id AND s.student_id = a.student_id "
        "WHERE a.student_id = ? AND e.status = 'published' "
        "ORDER BY e.published_at DESC",
        (student_id,),
    ).fetchall()
    exams = []
    for row in rows:
        exam = dict(row)
        exam["questionCount"] = database.execute(
            "SELECT COUNT(*) AS count FROM quiz_questions WHERE exam_id = ?",
            (exam["id"],),
        ).fetchone()["count"]
        exams.append(exam)
    return exams


def _grade_quiz_answers(question_rows, answers, validate_required=True):
    auto_score = 0
    correct_count = 0
    graded_count = 0
    review = []
    for question in question_rows:
        answer = answers.get(str(question["id"]))
        if validate_required and question["required_answer"] and (
            answer is None or answer == "" or answer == []
        ):
            return None, "Vui lòng trả lời tất cả câu hỏi bắt buộc."

        if question["question_type"] == "single_choice":
            correct_answers = [question["answer_index"]]
            is_correct = type(answer) is int and answer == question["answer_index"]
            graded_count += 1
        elif question["question_type"] == "multiple_choice":
            correct_answers = json.loads(question["correct_answers_json"])
            is_correct = (
                isinstance(answer, list)
                and all(type(value) is int for value in answer)
                and len(answer) == len(set(answer))
                and set(answer) == set(correct_answers)
            )
            graded_count += 1
        elif question["question_type"] == "true_false":
            correct_answers = [question["answer_index"]]
            is_correct = (
                type(answer) is bool and answer == (question["answer_index"] == 1)
            ) or (type(answer) is int and answer == question["answer_index"])
            graded_count += 1
        elif question["question_type"] == "essay":
            correct_answers = None
            is_correct = None
            if isinstance(answer, str) and question["answer_key"].strip():
                expected = " ".join(question["answer_key"].strip().lower().split())
                submitted = " ".join(answer.strip().lower().split())
                if submitted == expected:
                    auto_score += question["points"]
        else:
            raise ValueError(f"Unsupported quiz question type: {question['question_type']}")

        if is_correct:
            correct_count += 1
            if question["question_type"] != "essay":
                auto_score += question["points"]
        review.append({
            "question_id": question["id"],
            "correct": is_correct,
            "correct_answers": correct_answers,
            "explanation": question["explanation"],
        })
    return {
        "auto_score": auto_score,
        "correct_count": correct_count,
        "graded_count": graded_count,
        "review": review,
    }, None


def submit_quiz_submission(exam_id, student_id, answers):
    database = get_database()
    assignment = database.execute(
        "SELECT due_at FROM quiz_assignments WHERE exam_id = ? AND student_id = ?",
        (exam_id, student_id),
    ).fetchone()
    exam = database.execute(
        "SELECT id, status, due_at FROM quiz_exams WHERE id = ?", (exam_id,)
    ).fetchone()
    if not assignment or not exam or exam["status"] != "published":
        return None, "Bạn không được giao đề thi này."
    due_at = assignment["due_at"] or exam["due_at"]
    if due_at:
        due_row = database.execute("SELECT julianday(?) AS due", (due_at,)).fetchone()
        now_row = database.execute("SELECT julianday('now') AS now").fetchone()
        if due_row["due"] is not None and now_row["now"] > due_row["due"]:
            return None, "Đề thi đã quá hạn nộp."

    existing = database.execute(
        "SELECT id FROM quiz_submissions "
        "WHERE exam_id = ? AND student_id = ?",
        (exam_id, student_id),
    ).fetchone()
    question_rows = database.execute(
        "SELECT id, question_type, answer_index, correct_answers_json, answer_key, "
        "explanation, points, required_answer "
        "FROM quiz_questions WHERE exam_id = ? ORDER BY position, id",
        (exam_id,),
    ).fetchall()
    question_ids = {str(question["id"]) for question in question_rows}
    if not isinstance(answers, dict) or set(answers) != question_ids:
        return None, "Danh sách câu trả lời không hợp lệ."

    grading, error = _grade_quiz_answers(question_rows, answers)
    if error:
        return None, error
    auto_score = grading["auto_score"]

    if existing:
        database.execute(
            "UPDATE quiz_submissions SET answers_json = ?, auto_score = ?, "
            "manual_score = NULL, score = ?, status = 'submitted', "
            "submitted_at = CURRENT_TIMESTAMP, graded_at = NULL, teacher_comment = '' "
            "WHERE exam_id = ? AND student_id = ?",
            (json.dumps(answers, ensure_ascii=False), auto_score, auto_score,
             exam_id, student_id),
        )
    else:
        database.execute(
            "INSERT INTO quiz_submissions "
            "(exam_id, student_id, answers_json, auto_score, score, status, submitted_at) "
            "VALUES (?, ?, ?, ?, ?, 'submitted', CURRENT_TIMESTAMP)",
            (exam_id, student_id, json.dumps(answers, ensure_ascii=False),
             auto_score, auto_score),
        )
    database.commit()
    total_points = sum(question["points"] for question in question_rows)
    score = round(auto_score / total_points * 100) if total_points else 0
    return {
        "exam_id": exam_id,
        "auto_score": auto_score,
        "total_points": total_points,
        "score": score,
        "correct_count": grading["correct_count"],
        "graded_count": grading["graded_count"],
        "review": grading["review"],
        "answers": answers,
        "updated_existing": bool(existing),
        "status": "submitted",
    }, None


def list_quiz_submissions(exam_id):
    database = get_database()
    rows = database.execute(
        "SELECT s.id, s.exam_id, s.student_id, u.name, u.email, s.answers_json, "
        "s.auto_score, s.manual_score, s.score, s.status, s.submitted_at, s.graded_at, "
        "s.teacher_comment FROM quiz_submissions s "
        "JOIN users u ON u.id = s.student_id WHERE s.exam_id = ? "
        "ORDER BY s.submitted_at DESC",
        (exam_id,),
    ).fetchall()
    submissions = []
    for row in rows:
        item = dict(row)
        item["answers"] = json.loads(item.pop("answers_json"))
        submissions.append(item)
    return submissions


def grade_quiz_submission(submission_id, manual_score, comment=""):
    database = get_database()
    submission = database.execute(
        "SELECT id, auto_score FROM quiz_submissions WHERE id = ?", (submission_id,)
    ).fetchone()
    if not submission:
        return False
    if type(manual_score) is not int or manual_score < 0:
        return False
    total_score = submission["auto_score"] + manual_score
    database.execute(
        "UPDATE quiz_submissions SET manual_score = ?, score = ?, status = 'graded', "
        "graded_at = CURRENT_TIMESTAMP, teacher_comment = ? WHERE id = ?",
        (manual_score, total_score, str(comment).strip(), submission_id),
    )
    database.commit()
    return True


def create_quiz_attempt(data, user_id=None):
    score = round(data["correct_count"] / data["total_questions"] * 100)
    cursor = get_database().execute(
        "INSERT INTO quiz_attempts "
        "(user_id, exam_id, exam_title, subject, correct_count, total_questions, score, duration_seconds) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            user_id,
            data["exam_id"],
            data["exam_title"],
            data["subject"],
            data["correct_count"],
            data["total_questions"],
            score,
            data["duration_seconds"],
        ),
    )
    get_database().commit()
    return cursor.lastrowid


def get_quiz_statistics():
    database = get_database()
    live_summary = database.execute(
        "SELECT COUNT(*) AS attempts, COALESCE(SUM(score), 0) AS score_total, "
        "COALESCE(SUM(correct_count), 0) AS correct_count, "
        "COALESCE(SUM(total_questions), 0) AS total_questions "
        "FROM quiz_attempts"
    ).fetchone()
    archived_summary = database.execute(
        "SELECT COALESCE(SUM(attempts), 0) AS attempts, "
        "COALESCE(SUM(score_total), 0) AS score_total, "
        "COALESCE(SUM(correct_count), 0) AS correct_count, "
        "COALESCE(SUM(total_questions), 0) AS total_questions "
        "FROM quiz_monthly_aggregates"
    ).fetchone()
    assigned_rows = database.execute(
        "SELECT s.id, s.exam_id, s.student_id, u.name AS learner, e.title AS exam_title, "
        "e.subject, s.answers_json, s.auto_score, s.score, s.status, s.submitted_at "
        "FROM quiz_submissions s "
        "JOIN quiz_exams e ON e.id = s.exam_id "
        "JOIN users u ON u.id = s.student_id "
        "WHERE s.status IN ('submitted', 'graded') "
        "ORDER BY s.submitted_at DESC, s.id DESC"
    ).fetchall()
    questions_by_exam = {}
    assigned_attempts = []
    for row in assigned_rows:
        exam_id = row["exam_id"]
        if exam_id not in questions_by_exam:
            questions_by_exam[exam_id] = database.execute(
                "SELECT id, question_type, answer_index, correct_answers_json, answer_key, "
                "explanation, points, required_answer FROM quiz_questions "
                "WHERE exam_id = ? ORDER BY position, id",
                (exam_id,),
            ).fetchall()
        question_rows = questions_by_exam[exam_id]
        answers = json.loads(row["answers_json"])
        grading, _ = _grade_quiz_answers(
            question_rows, answers, validate_required=False
        )
        total_points = sum(question["points"] for question in question_rows)
        score_points = row["score"] if row["score"] is not None else row["auto_score"]
        score = round(score_points * 100 / total_points) if total_points else 0
        assigned_attempts.append({
            "exam_id": exam_id,
            "exam_title": row["exam_title"],
            "subject": row["subject"],
            "student_id": row["student_id"],
            "learner": row["learner"],
            "score": score,
            "correct_count": grading["correct_count"],
            "total_questions": grading["graded_count"],
            "created_at": row["submitted_at"],
        })

    assigned_count = len(assigned_attempts)
    attempt_count = (
        live_summary["attempts"] + archived_summary["attempts"] + assigned_count
    )
    score_total = (
        live_summary["score_total"]
        + archived_summary["score_total"]
        + sum(attempt["score"] for attempt in assigned_attempts)
    )
    learners = database.execute(
        "SELECT COUNT(*) FROM ("
        "SELECT user_id AS student_id FROM quiz_attempts WHERE user_id IS NOT NULL "
        "UNION "
        "SELECT student_id FROM quiz_submissions "
        "WHERE student_id IS NOT NULL AND status IN ('submitted', 'graded')"
        ")"
    ).fetchone()[0]
    summary = {
        "attempts": attempt_count,
        "average_score": int(score_total / attempt_count + 0.5) if attempt_count else 0,
        "learners": learners,
        "correct_count": (
            live_summary["correct_count"] + archived_summary["correct_count"]
            + sum(attempt["correct_count"] for attempt in assigned_attempts)
        ),
        "total_questions": (
            live_summary["total_questions"] + archived_summary["total_questions"]
            + sum(attempt["total_questions"] for attempt in assigned_attempts)
        ),
    }

    exam_rows = database.execute(
        "SELECT exam_id, exam_title, subject, COUNT(*) AS attempts, "
        "SUM(score) AS score_total, MAX(score) AS best_score "
        "FROM quiz_attempts GROUP BY exam_id, exam_title, subject "
        "UNION ALL "
        "SELECT exam_id, exam_title, subject, SUM(attempts) AS attempts, "
        "SUM(score_total) AS score_total, MAX(best_score) AS best_score "
        "FROM quiz_monthly_aggregates GROUP BY exam_id, exam_title, subject"
    ).fetchall()
    exams_by_key = {}
    for row in exam_rows:
        key = (row["exam_id"], row["exam_title"], row["subject"])
        exam = exams_by_key.setdefault(key, {
            "exam_id": row["exam_id"],
            "exam_title": row["exam_title"],
            "subject": row["subject"],
            "attempts": 0,
            "score_total": 0,
            "best_score": 0,
        })
        exam["attempts"] += row["attempts"]
        exam["score_total"] += row["score_total"]
        exam["best_score"] = max(exam["best_score"], row["best_score"])
    for attempt in assigned_attempts:
        key = (attempt["exam_id"], attempt["exam_title"], attempt["subject"])
        exam = exams_by_key.setdefault(key, {
            "exam_id": attempt["exam_id"],
            "exam_title": attempt["exam_title"],
            "subject": attempt["subject"],
            "attempts": 0,
            "score_total": 0,
            "best_score": 0,
        })
        exam["attempts"] += 1
        exam["score_total"] += attempt["score"]
        exam["best_score"] = max(exam["best_score"], attempt["score"])
    exams = [
        {
            "exam_id": exam["exam_id"],
            "exam_title": exam["exam_title"],
            "subject": exam["subject"],
            "attempts": exam["attempts"],
            "average_score": int(exam["score_total"] / exam["attempts"] + 0.5),
            "best_score": exam["best_score"],
        }
        for exam in exams_by_key.values()
    ]
    exams.sort(key=lambda exam: (-exam["attempts"], exam["exam_title"].casefold()))
    recent = [
        dict(attempt)
        for attempt in database.execute(
            "SELECT quiz_attempts.exam_title, quiz_attempts.subject, "
            "quiz_attempts.correct_count, quiz_attempts.total_questions, quiz_attempts.score, "
            "quiz_attempts.created_at, "
            "CASE WHEN quiz_attempts.user_id IS NULL THEN 'Khách' ELSE 'Học viên' END AS learner "
            "FROM quiz_attempts "
            "ORDER BY quiz_attempts.id DESC LIMIT 20"
        ).fetchall()
    ]
    recent.extend({
        "exam_title": attempt["exam_title"],
        "subject": attempt["subject"],
        "correct_count": attempt["correct_count"],
        "total_questions": attempt["total_questions"],
        "score": attempt["score"],
        "created_at": attempt["created_at"],
        "learner": attempt["learner"],
    } for attempt in assigned_attempts)
    recent.sort(key=lambda attempt: attempt["created_at"] or "", reverse=True)
    return {
        "summary": summary,
        "exams": exams,
        "recent": recent[:20],
    }


def list_courses():
    return get_database().execute("SELECT * FROM courses ORDER BY id ASC").fetchall()


def get_course_by_id(course_id):
    return get_database().execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()


def create_course(data):
    cursor = get_database().execute(
        "INSERT INTO courses (title, description, image_url, course_url, details) VALUES (?, ?, ?, ?, ?)",
        (data["title"], data["description"], data["image_url"], data["course_url"], data["details"]),
    )
    get_database().commit()
    return cursor.lastrowid


def update_course(course_id, data):
    cursor = get_database().execute(
        "UPDATE courses SET title = ?, description = ?, image_url = ?, course_url = ?, details = ? WHERE id = ?",
        (data["title"], data["description"], data["image_url"], data["course_url"], data["details"], course_id),
    )
    if cursor.rowcount:
        get_database().commit()
    return cursor.rowcount > 0


def delete_course(course_id):
    cursor = get_database().execute("DELETE FROM courses WHERE id = ?", (course_id,))
    if cursor.rowcount:
        get_database().commit()
    return cursor.rowcount > 0


def validate_book(data):
    title = str(data.get("title", "")).strip()
    author = str(data.get("author", "")).strip()
    cover_image = str(data.get("cover_image", "")).strip()
    category = str(data.get("category", "")).strip()
    description = str(data.get("description", "")).strip()
    details = str(data.get("details", "")).strip()
    document_url = str(data.get("document_url", "")).strip()

    if not title or len(title) > 200:
        return None, "Tên sách cần có từ 1 đến 200 ký tự."
    if not author or len(author) > 120:
        return None, "Tên tác giả cần có từ 1 đến 120 ký tự."
    if not category or len(category) > 80:
        return None, "Danh mục cần có từ 1 đến 80 ký tự."
    if len(description) > 2000:
        return None, "Mô tả không được vượt quá 2000 ký tự."
    if len(details) > 5000:
        return None, "Nội dung chi tiết không được vượt quá 5000 ký tự."
    try:
        parsed_document_url = urlsplit(document_url)
        parsed_document_url.port
    except ValueError:
        return None, "Liên kết tài liệu không hợp lệ."
    if parsed_document_url.scheme not in {"http", "https"} or not parsed_document_url.hostname:
        return None, "Liên kết tài liệu phải bắt đầu bằng http:// hoặc https://."
    if cover_image and not re.fullmatch(r"/static/uploads/books/[a-f0-9]{32}\.(?:png|jpg|gif|webp)", cover_image):
        return None, "Ảnh bìa không hợp lệ."

    return {
        "title": title,
        "author": author,
        "cover_image": cover_image,
        "category": category,
        "description": description,
        "details": details,
        "document_url": document_url,
    }, None


def list_books():
    return get_database().execute("SELECT * FROM books ORDER BY created_at DESC, id DESC").fetchall()


def count_books():
    return get_database().execute("SELECT COUNT(*) FROM books").fetchone()[0]


def get_book_by_id(book_id):
    return get_database().execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()


def create_book(data):
    cursor = get_database().execute(
        "INSERT INTO books (title, author, cover_image, category, description, details, document_url) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data["title"],
            data["author"],
            data["cover_image"],
            data["category"],
            data["description"],
            data.get("details", ""),
            data["document_url"],
        ),
    )
    get_database().commit()
    return cursor.lastrowid


def update_book(book_id, data):
    cursor = get_database().execute(
        "UPDATE books SET title = ?, author = ?, cover_image = ?, category = ?, "
        "description = ?, details = ?, document_url = ? WHERE id = ?",
        (
            data["title"],
            data["author"],
            data["cover_image"],
            data["category"],
            data["description"],
            data.get("details", ""),
            data["document_url"],
            book_id,
        ),
    )
    if cursor.rowcount:
        get_database().commit()
    return cursor.rowcount > 0


def delete_book(book_id):
    cursor = get_database().execute("DELETE FROM books WHERE id = ?", (book_id,))
    if cursor.rowcount:
        get_database().commit()
    return cursor.rowcount > 0
