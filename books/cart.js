(function (global) {
  "use strict";

  const storageKey = "elearningBookCart";
  const cover = isbn => `https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg?default=false`;
  const books = [
    { id: 1, name: "C++ Primer (5th Edition)", author: "Stanley B. Lippman, Josée Lajoie, Barbara E. Moo", category: "C/C++", description: "Giáo trình toàn diện về ngôn ngữ C++ hiện đại, từ cú pháp nền tảng đến thư viện chuẩn.", price: 85000, cover: cover("9780321714114"), available: true, featured: true },
    { id: 2, name: "Python Crash Course (3rd Edition)", author: "Eric Matthes", category: "Python", description: "Lộ trình thực hành Python qua nền tảng ngôn ngữ và các dự án có thể tự xây dựng.", price: 99000, cover: cover("9781718502703"), available: true, featured: true },
    { id: 3, name: "JavaScript: The Good Parts", author: "Douglas Crockford", category: "JavaScript & Web", description: "Khám phá những đặc tính cốt lõi giúp viết JavaScript rõ ràng và nhất quán.", price: 120000, cover: cover("9780596517748"), available: true },
    { id: 4, name: "HTML and CSS: Design and Build Websites", author: "Jon Duckett", category: "HTML/CSS", description: "Nhập môn HTML và CSS bằng cách tiếp cận trực quan, dễ tra cứu khi thực hành web.", price: 75000, cover: cover("9781118008188"), available: true, featured: true },
    { id: 5, name: "Effective Java (3rd Edition)", author: "Joshua Bloch", category: "Java & OOP", description: "Các thực hành tốt để thiết kế API và viết chương trình Java an toàn, dễ bảo trì.", price: 189000, cover: cover("9780134685991"), available: true, featured: true },
    { id: 6, name: "Automate the Boring Stuff with Python (2nd Edition)", author: "Al Sweigart", category: "Python", description: "Dùng Python để tự động hóa các công việc thường ngày qua những ví dụ thực tế.", price: 159000, cover: cover("9781593279929"), available: true },
    { id: 7, name: "Eloquent JavaScript (3rd Edition)", author: "Marijn Haverbeke", category: "JavaScript & Web", description: "Tìm hiểu JavaScript từ nền tảng đến lập trình bất đồng bộ và ứng dụng trên trình duyệt.", price: 175000, cover: cover("9781593279509"), available: true },
    { id: 8, name: "Learning SQL (3rd Edition)", author: "Alan Beaulieu", category: "Cơ sở dữ liệu & SQL", description: "Thực hành truy vấn, kết hợp bảng và xử lý dữ liệu với SQL.", price: 169000, cover: cover("9781492057611"), available: true },
    { id: 9, name: "Grokking Algorithms", author: "Aditya Y. Bhargava", category: "Thuật toán & cấu trúc dữ liệu", description: "Giải thích các thuật toán phổ biến bằng ví dụ và hình minh họa dễ theo dõi.", price: 149000, cover: cover("9781617292231"), available: true },
    { id: 10, name: "Pro Git (2nd Edition)", author: "Scott Chacon, Ben Straub", category: "Git & GitHub", description: "Từ workflow Git cơ bản đến nhánh, remote và cộng tác trong dự án.", price: 129000, cover: cover("9781484200773"), available: true },
    { id: 11, name: "Node.js Design Patterns (2nd Edition)", author: "Mario Casciaro, Luciano Mammino", category: "Node.js & Backend", description: "Các mẫu thiết kế giúp xây dựng ứng dụng Node.js có cấu trúc và khả năng mở rộng.", price: 219000, cover: cover("9781785885587"), available: true },
    { id: 12, name: "Hands-On Machine Learning (3rd Edition)", author: "Aurélien Géron", category: "Machine Learning & AI", description: "Tiếp cận học máy và deep learning bằng các dự án với Python, Scikit-Learn và TensorFlow.", price: 249000, cover: cover("9781098125974"), available: true }
  ];
  const booksById = new Map(books.map(book => [book.id, book]));

  function getStockLimit(book) {
    return Number.isSafeInteger(book.stock) && book.stock >= 0 ? book.stock : Infinity;
  }

  function readCart() {
    let stored;
    try {
      stored = JSON.parse(global.localStorage.getItem(storageKey) || "[]");
    } catch {
      return [];
    }
    if (!Array.isArray(stored)) return [];

    const items = new Map();
    stored.forEach(item => {
      const book = item && booksById.get(Number(item.id));
      const quantity = Number(item && item.quantity);
      if (!book || book.available === false || !Number.isSafeInteger(quantity) || quantity < 1) return;
      const current = items.get(book.id) || 0;
      const next = Math.min(current + quantity, getStockLimit(book));
      if (Number.isSafeInteger(next) && next >= 1) items.set(book.id, next);
    });
    return Array.from(items, ([id, quantity]) => ({ id, quantity }));
  }

  function writeCart(items) {
    try {
      global.localStorage.setItem(storageKey, JSON.stringify(items));
      return true;
    } catch {
      return false;
    }
  }

  function getCount() {
    return readCart().reduce((total, item) => total + item.quantity, 0);
  }

  function add(id) {
    const book = booksById.get(Number(id));
    if (!book || book.available === false) {
      return { ok: false, message: "Sách không tồn tại hoặc hiện không khả dụng." };
    }

    const items = readCart();
    const existing = items.find(item => item.id === book.id);
    const nextQuantity = (existing ? existing.quantity : 0) + 1;
    if (nextQuantity > getStockLimit(book)) {
      return { ok: false, message: "Số lượng vượt quá tồn kho hiện có." };
    }
    if (!Number.isSafeInteger(nextQuantity)) {
      return { ok: false, message: "Số lượng sách không hợp lệ." };
    }
    if (existing) existing.quantity = nextQuantity;
    else items.push({ id: book.id, quantity: 1 });

    if (!writeCart(items)) {
      return { ok: false, message: "Không thể lưu giỏ hàng trên thiết bị này." };
    }
    return { ok: true, message: `Đã thêm "${book.name}" vào giỏ hàng.` };
  }

  function setQuantity(id, quantity) {
    const book = booksById.get(Number(id));
    if (!book || book.available === false) {
      return { ok: false, message: "Sách không tồn tại hoặc hiện không khả dụng." };
    }
    if (!Number.isSafeInteger(quantity) || quantity < 1) {
      return { ok: false, message: "Số lượng phải từ 1 trở lên." };
    }
    if (quantity > getStockLimit(book)) {
      return { ok: false, message: "Số lượng vượt quá tồn kho hiện có." };
    }

    const items = readCart();
    const existing = items.find(item => item.id === book.id);
    if (!existing) return { ok: false, message: "Sách không có trong giỏ hàng." };
    existing.quantity = quantity;
    if (!writeCart(items)) {
      return { ok: false, message: "Không thể lưu giỏ hàng trên thiết bị này." };
    }
    return { ok: true, message: "Đã cập nhật số lượng." };
  }

  function remove(id) {
    const items = readCart().filter(item => item.id !== Number(id));
    if (!writeCart(items)) {
      return { ok: false, message: "Không thể lưu thay đổi giỏ hàng." };
    }
    return { ok: true, message: "Đã xóa sách khỏi giỏ hàng." };
  }

  function getItems() {
    return readCart().map(item => {
      const book = booksById.get(item.id);
      return { book: { ...book }, quantity: item.quantity, lineTotal: book.price * item.quantity };
    });
  }

  function getTotal() {
    return getItems().reduce((total, item) => total + item.lineTotal, 0);
  }

  global.BookCart = {
    storageKey,
    getBooks: () => books.map(book => ({ ...book })),
    getItems,
    getCount,
    getTotal,
    add,
    setQuantity,
    remove
  };
})(window);