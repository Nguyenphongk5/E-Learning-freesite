(() => {
  "use strict";

  const results = document.getElementById("results");
  const summary = document.getElementById("summary");
  const cases = [];
  let passed = 0;
  let failed = 0;

  function test(name, callback) {
    cases.push({ name, callback });
  }

  function equal(actual, expected, message) {
    if (!Object.is(actual, expected)) {
      throw new Error(message || `Mong đợi ${String(expected)}, nhận ${String(actual)}`);
    }
  }

  function deepEqual(actual, expected, message) {
    const actualJson = JSON.stringify(actual);
    const expectedJson = JSON.stringify(expected);
    if (actualJson !== expectedJson) {
      throw new Error(message || `Mong đợi ${expectedJson}, nhận ${actualJson}`);
    }
  }

  function ok(value, message) {
    if (!value) throw new Error(message || "Mong đợi điều kiện đúng");
  }

  function reset() {
    window.localStorage.clear();
    window.setStorageFailure("read", false);
    window.setStorageFailure("write", false);
  }

  test("catalog có ID duy nhất và ít nhất 12 đầu sách", () => {
    const books = BookCart.getBooks();
    equal(books.length, 12);
    equal(new Set(books.map(book => book.id)).size, books.length);
    ok(books.every(book => book.name && book.author && book.price > 0));
  });

  test("thêm sách hợp lệ lưu ID/số lượng và trả thông báo thành công", () => {
    const result = BookCart.add(1);
    equal(result.ok, true);
    ok(result.message.includes("C++ Primer"));
    deepEqual(JSON.parse(window.localStorage.getItem(BookCart.storageKey)), [{ id: 1, quantity: 1 }]);
  });

  test("thêm cùng sách nhiều lần cộng số lượng, không tạo dòng trùng", () => {
    BookCart.add(1);
    BookCart.add("1");
    deepEqual(BookCart.getItems().map(item => ({ id: item.book.id, quantity: item.quantity })), [{ id: 1, quantity: 2 }]);
    equal(BookCart.getCount(), 2);
  });

  test("từ chối ID sách không tồn tại và giữ nguyên giỏ", () => {
    BookCart.add(1);
    const before = window.localStorage.getItem(BookCart.storageKey);
    const result = BookCart.add(999);
    equal(result.ok, false);
    equal(window.localStorage.getItem(BookCart.storageKey), before);
  });

  test("cập nhật số lượng hợp lệ và tính thành tiền", () => {
    BookCart.add(1);
    const result = BookCart.setQuantity(1, 3);
    equal(result.ok, true);
    equal(BookCart.getItems()[0].lineTotal, 255000);
    equal(BookCart.getTotal(), 255000);
    equal(BookCart.getCount(), 3);
  });

  test("từ chối số lượng nhỏ hơn 1, thập phân và vượt miền số nguyên an toàn", () => {
    BookCart.add(1);
    for (const quantity of [0, -1, 1.5, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1]) {
      equal(BookCart.setQuantity(1, quantity).ok, false, `Phải từ chối quantity=${String(quantity)}`);
    }
    equal(BookCart.getItems()[0].quantity, 1);
  });

  test("không tăng vượt miền số nguyên an toàn", () => {
    window.localStorage.setItem(BookCart.storageKey, JSON.stringify([{ id: 1, quantity: Number.MAX_SAFE_INTEGER }]));
    const result = BookCart.add(1);
    equal(result.ok, false);
    equal(BookCart.getItems()[0].quantity, Number.MAX_SAFE_INTEGER);
  });

  test("không cập nhật số lượng cho sách chưa có trong giỏ", () => {
    const result = BookCart.setQuantity(1, 2);
    equal(result.ok, false);
    equal(BookCart.getCount(), 0);
  });

  test("xóa một sách và giữ lại các sách còn lại", () => {
    BookCart.add(1);
    BookCart.add(2);
    const result = BookCart.remove(1);
    equal(result.ok, true);
    deepEqual(BookCart.getItems().map(item => item.book.id), [2]);
    equal(BookCart.getCount(), 1);
  });

  test("tổng tiền nhiều sách lấy đơn giá từ catalog, bỏ qua giá client lưu", () => {
    window.localStorage.setItem(BookCart.storageKey, JSON.stringify([
      { id: 1, quantity: 2, price: 1 },
      { id: 2, quantity: 1, price: 1 }
    ]));
    equal(BookCart.getTotal(), 269000);
    equal(BookCart.getItems()[0].book.price, 85000);
  });

  test("dữ liệu JSON hỏng được xem như giỏ rỗng và có thể thêm lại", () => {
    window.localStorage.setItem(BookCart.storageKey, "{khong-hop-le");
    equal(BookCart.getCount(), 0);
    equal(BookCart.add(2).ok, true);
    equal(BookCart.getTotal(), 99000);
  });

  test("lỗi đọc storage không làm API đọc giỏ bị văng lỗi", () => {
    window.setStorageFailure("read", true);
    equal(BookCart.getCount(), 0);
    deepEqual(BookCart.getItems(), []);
  });

  test("lỗi ghi storage được trả về dưới dạng kết quả thất bại", () => {
    window.setStorageFailure("write", true);
    const result = BookCart.add(1);
    equal(result.ok, false);
    ok(result.message.includes("Không thể lưu"));
  });

  test("xóa toàn bộ mặt hàng đưa số lượng và tổng tiền về 0", () => {
    BookCart.add(1);
    BookCart.add(2);
    BookCart.remove(1);
    BookCart.remove(2);
    equal(BookCart.getCount(), 0);
    equal(BookCart.getTotal(), 0);
    deepEqual(BookCart.getItems(), []);
  });

  cases.forEach(({ name, callback }) => {
    reset();
    const item = document.createElement("li");
    try {
      callback();
      passed += 1;
      item.className = "pass";
      item.textContent = `ĐẠT — ${name}`;
    } catch (error) {
      failed += 1;
      item.className = "fail";
      item.textContent = `LỖI — ${name}: ${error.message}`;
      console.error(name, error);
    }
    results.append(item);
  });

  summary.dataset.state = failed ? "failed" : "passed";
  summary.textContent = `Kết quả: ${passed}/${cases.length} đạt, ${failed} thất bại.`;
  document.title = `${failed ? "FAIL" : "PASS"} (${passed}/${cases.length}) — Unit test giỏ hàng`;
})();
