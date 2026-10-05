async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || "Không thể kết nối máy chủ.");
    return payload;
}

function showMessage(element, text, success = false) {
    element.textContent = text;
    element.classList.toggle("is-success", success);
}

function initAuthPage() {
    const loginForm = document.getElementById("login-form");
    if (!loginForm) return;

    const registerForm = document.getElementById("register-form");
    const isRegister = new URLSearchParams(location.search).get("view") === "register";
    document.getElementById("form-title").textContent = isRegister ? "Tạo tài khoản học viên" : "Chào mừng trở lại";
    document.getElementById("form-intro").textContent = isRegister
        ? "Đăng ký miễn phí để bắt đầu hành trình học tập."
        : "Đăng nhập để vào không gian học tập của bạn.";
    loginForm.hidden = isRegister;
    registerForm.hidden = !isRegister;
    document.getElementById("login-footer").hidden = isRegister;
    document.getElementById("register-footer").hidden = !isRegister;
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = document.getElementById("login-message");
        const submitButton = loginForm.querySelector("button[type='submit']");
        submitButton.disabled = true;
        try {
            const account = await apiRequest("/api/auth/login", {
                method: "POST",
                body: JSON.stringify({
                    email: loginForm.elements.email.value.trim(),
                    password: loginForm.elements.password.value,
                }),
            });
            location.href = account.role === "admin" ? "admin.html" : "user.html";
        } catch (error) {
            showMessage(message, error.message);
        } finally {
            submitButton.disabled = false;
        }
    });

    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = document.getElementById("register-message");
        const submitButton = registerForm.querySelector("button[type='submit']");
        submitButton.disabled = true;
        try {
            await apiRequest("/api/auth/register", {
                method: "POST",
                body: JSON.stringify({
                    name: registerForm.elements.name.value.trim(),
                    email: registerForm.elements.email.value.trim(),
                    password: registerForm.elements.password.value,
                }),
            });
            location.replace("user.html");
        } catch (error) {
            showMessage(message, error.message);
        } finally {
            submitButton.disabled = false;
        }
    });
}

async function requireRole(requiredRole) {
    try {
        const account = await apiRequest("/api/auth/me");
        if (account.role !== requiredRole) {
            location.replace("auth.html");
            return;
        }
        document.querySelectorAll("[data-account-name]").forEach((element) => {
            element.textContent = account.name;
        });
        document.querySelectorAll("[data-account-email]").forEach((element) => {
            element.textContent = account.email;
        });

        document.getElementById("logout-button")?.addEventListener("click", async () => {
            await apiRequest("/api/auth/logout", { method: "POST" });
            location.replace("auth.html");
        });

        if (requiredRole === "admin") {
            await Promise.all([renderUsersTable(), initAdminForms(), renderCourseTable()]);
        }
    } catch {
        location.replace("auth.html");
    }
}

async function renderUsersTable() {
    const tableBody = document.getElementById("users-table-body");
    if (!tableBody) return;
    try {
        const users = await apiRequest("/api/admin/users");
        document.getElementById("user-count").textContent = String(users.filter((user) => user.role === "user").length);
        tableBody.replaceChildren();
        users.forEach((user, index) => {
            const row = document.createElement("tr");
            [String(index + 1), user.name, user.email, user.role === "admin" ? "Quản trị viên" : "Học viên"].forEach((value) => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.append(cell);
            });
            tableBody.append(row);
        });
    } catch (error) {
        tableBody.replaceChildren();
        addEmptyRow(tableBody, 4, error.message);
    }
}

async function initAdminForms() {
    const form = document.getElementById("admin-create-form");
    if (!form) return;
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = document.getElementById("admin-create-message");
        const button = form.querySelector("button[type='submit']");
        button.disabled = true;
        try {
            await apiRequest("/api/admin/users", {
                method: "POST",
                body: JSON.stringify({
                    name: form.elements.name.value.trim(),
                    email: form.elements.email.value.trim(),
                    password: form.elements.password.value,
                }),
            });
            form.reset();
            showMessage(message, "Đã tạo tài khoản quản trị viên.", true);
            await renderUsersTable();
        } catch (error) {
            showMessage(message, error.message);
        } finally {
            button.disabled = false;
        }
    });

    const courseForm = document.getElementById("course-form");
    const imageInput = document.getElementById("course-image-file");
    imageInput.addEventListener("change", async () => {
        const file = imageInput.files[0];
        if (!file) return;
        const status = document.getElementById("course-image-status");
        const submitButton = courseForm.querySelector("button[type='submit']");
        if (file.size > 5 * 1024 * 1024) {
            imageInput.value = "";
            showMessage(status, "Ảnh không được vượt quá 5 MB.");
            return;
        }

        const formData = new FormData();
        formData.set("image", file);
        submitButton.disabled = true;
        showMessage(status, "Đang tải ảnh lên...");
        try {
            const response = await fetch("/api/admin/uploads", {
                method: "POST",
                credentials: "same-origin",
                body: formData,
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(result.error || "Không thể tải ảnh lên.");
            courseForm.elements.image_url.value = result.image_url;
            updateImagePreview(result.image_url);
            showMessage(status, "Đã tải ảnh lên.", true);
        } catch (error) {
            imageInput.value = "";
            showMessage(status, error.message);
        } finally {
            submitButton.disabled = false;
        }
    });

    courseForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = document.getElementById("course-message");
        const button = courseForm.querySelector("button[type='submit']");
        const courseId = courseForm.elements.id.value;
        const data = {
            title: courseForm.elements.title.value.trim(),
            description: courseForm.elements.description.value.trim(),
            image_url: courseForm.elements.image_url.value.trim(),
            course_url: courseForm.elements.course_url.value.trim(),
        };
        button.disabled = true;
        try {
            await apiRequest(courseId ? `/api/courses/${courseId}` : "/api/courses", {
                method: courseId ? "PUT" : "POST",
                body: JSON.stringify(data),
            });
            resetCourseForm();
            showMessage(message, courseId ? "Đã cập nhật khóa học." : "Đã thêm khóa học.", true);
            await renderCourseTable();
        } catch (error) {
            showMessage(message, error.message);
        } finally {
            button.disabled = false;
        }
    });

    document.getElementById("course-form-reset").addEventListener("click", resetCourseForm);
    document.getElementById("course-image-clear").addEventListener("click", () => {
        courseForm.elements.image_url.value = "";
        imageInput.value = "";
        updateImagePreview("");
        showMessage(document.getElementById("course-image-status"), "Đã bỏ ảnh.", true);
    });
    document.getElementById("courses-table-body").addEventListener("click", handleCourseAction);
}

function updateImagePreview(imageUrl) {
    const preview = document.getElementById("course-image-preview");
    const image = document.getElementById("course-image-preview-img");
    preview.hidden = !imageUrl;
    image.src = imageUrl || "";
}

function resetCourseForm() {
    const form = document.getElementById("course-form");
    form.reset();
    document.getElementById("course-id").value = "";
    document.getElementById("course-form-title").textContent = "Thêm khóa học";
    document.getElementById("course-submit-label").textContent = "Thêm khóa học";
    showMessage(document.getElementById("course-message"), "");
    showMessage(document.getElementById("course-image-status"), "PNG, JPG, GIF hoặc WebP, tối đa 5 MB.");
    updateImagePreview("");
}

async function renderCourseTable() {
    const tableBody = document.getElementById("courses-table-body");
    if (!tableBody) return;
    try {
        const courses = await apiRequest("/api/courses");
        document.getElementById("course-count").textContent = String(courses.length);
        tableBody.replaceChildren();
        if (courses.length === 0) addEmptyRow(tableBody, 3, "Chưa có khóa học.");
        courses.forEach((course) => {
            const row = document.createElement("tr");
            const titleCell = document.createElement("td");
            titleCell.textContent = course.title;
            const descriptionCell = document.createElement("td");
            descriptionCell.textContent = course.description;
            const actionsCell = document.createElement("td");
            actionsCell.className = "table-actions";
            const editButton = makeActionButton("Sửa", "edit", course.id);
            const deleteButton = makeActionButton("Xóa", "delete", course.id);
            actionsCell.append(editButton, deleteButton);
            row.append(titleCell, descriptionCell, actionsCell);
            tableBody.append(row);
        });
    } catch (error) {
        tableBody.replaceChildren();
        addEmptyRow(tableBody, 3, error.message);
    }
}

function makeActionButton(label, action, id) {
    const button = document.createElement("button");
    button.className = "text-button";
    button.type = "button";
    button.dataset.action = action;
    button.dataset.id = String(id);
    button.textContent = label;
    return button;
}

async function handleCourseAction(event) {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const message = document.getElementById("course-message");
    try {
        if (button.dataset.action === "delete") {
            if (!window.confirm("Bạn có chắc muốn xóa khóa học này?")) return;
            await apiRequest(`/api/courses/${button.dataset.id}`, { method: "DELETE" });
            showMessage(message, "Đã xóa khóa học.", true);
            await renderCourseTable();
            return;
        }
        const course = (await apiRequest("/api/courses")).find((item) => String(item.id) === button.dataset.id);
        if (!course) throw new Error("Không tìm thấy khóa học.");
        const form = document.getElementById("course-form");
        form.elements.id.value = course.id;
        form.elements.title.value = course.title;
        form.elements.description.value = course.description;
        form.elements.image_url.value = course.image_url;
        document.getElementById("course-image-file").value = "";
        updateImagePreview(course.image_url);
        showMessage(document.getElementById("course-image-status"), course.image_url ? "Ảnh hiện tại. Chọn file mới để thay." : "PNG, JPG, GIF hoặc WebP, tối đa 5 MB.");
        form.elements.course_url.value = course.course_url;
        document.getElementById("course-form-title").textContent = "Sửa khóa học";
        document.getElementById("course-submit-label").textContent = "Lưu thay đổi";
        form.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
        showMessage(message, error.message);
    }
}

function addEmptyRow(tableBody, columnCount, text) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = columnCount;
    cell.className = "empty-row";
    cell.textContent = text;
    row.append(cell);
    tableBody.append(row);
}

document.addEventListener("DOMContentLoaded", () => {
    initAuthPage();
    const requiredRole = document.body.dataset.protectedRole;
    if (requiredRole) requireRole(requiredRole);
});