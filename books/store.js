(function () {
  "use strict";

  const books = BookCart.getBooks();
  const featuredBooks = books.filter(book => book.featured);
  const categories = [...new Set(books.map(book => book.category))];
  const elements = {
    search: document.getElementById("book-search"),
    categoryList: document.getElementById("category-list"),
    featured: document.getElementById("featured-books"),
    list: document.getElementById("book-list"),
    resultCount: document.getElementById("result-count"),
    emptyResults: document.getElementById("empty-results"),
    sort: document.getElementById("sort-books"),
    clearFilters: document.getElementById("clear-filters"),
    dialog: document.getElementById("book-dialog"),
    toast: document.getElementById("toast"),
    badge: document.getElementById("cart-count")
  };
  const filters = { category: "Tất cả", query: "", sort: "featured" };
  let toastTimer;

  function formatPrice(price) {
    return `${price.toLocaleString("vi-VN")} ₫`;
  }

  function coverMarkup(book, className) {
    return `<div class="${className}">
      <img src="${book.cover}" alt="Bìa sách ${book.name}" loading="lazy">
      <div class="cover-fallback" hidden><span>${book.category}</span><strong>${book.name}</strong><small>${book.author}</small></div>
      <span class="stock-badge ${book.available ? "in-stock" : "out-stock"}">${book.available ? "Còn hàng" : "Tạm hết hàng"}</span>
    </div>`;
  }

  function cardMarkup(book) {
    return `<article class="book-card">
      ${coverMarkup(book, "book-cover")}
      <div class="book-card-body">
        <div class="book-meta"><span>${book.category}</span></div>
        <h3>${book.name}</h3>
        <p class="book-author">${book.author}</p>
        <p class="book-description">${book.description}</p>
        <div class="book-card-bottom"><strong class="book-price">${formatPrice(book.price)}</strong><button class="detail-button" type="button" data-action="details" data-book-id="${book.id}">Chi tiết</button></div>
        <button class="add-button" type="button" data-action="add" data-book-id="${book.id}" ${book.available ? "" : "disabled"}>${book.available ? "Thêm vào giỏ" : "Tạm hết hàng"}</button>
      </div>
    </article>`;
  }

  function renderCategories() {
    elements.categoryList.innerHTML = ["Tất cả", ...categories].map(category => `
      <button class="category-chip ${filters.category === category ? "is-active" : ""}" type="button" data-category="${category}" aria-pressed="${filters.category === category}">
        ${category === "Tất cả" ? "Tất cả chủ đề" : category}<span>${category === "Tất cả" ? books.length : books.filter(book => book.category === category).length}</span>
      </button>`).join("");
  }

  function normalized(value) {
    return value.toLocaleLowerCase("vi").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  function getFilteredBooks() {
    const query = normalized(filters.query.trim());
    const filtered = books.filter(book => {
      const matchesCategory = filters.category === "Tất cả" || book.category === filters.category;
      const matchesQuery = !query || normalized(book.name).includes(query);
      return matchesCategory && matchesQuery;
    });
    if (filters.sort === "price-asc") filtered.sort((first, second) => first.price - second.price);
    if (filters.sort === "price-desc") filtered.sort((first, second) => second.price - first.price);
    return filtered;
  }

  function renderBooks() {
    const filtered = getFilteredBooks();
    elements.list.innerHTML = filtered.map(cardMarkup).join("");
    elements.resultCount.textContent = `${filtered.length} đầu sách`;
    elements.emptyResults.hidden = filtered.length !== 0;
    elements.clearFilters.hidden = filters.category === "Tất cả" && !filters.query;
    document.querySelector(".featured-section").hidden = Boolean(filters.query || filters.category !== "Tất cả");
  }

  function updateBadge() {
    elements.badge.textContent = BookCart.getCount();
  }

  function notify(message, isError) {
    window.clearTimeout(toastTimer);
    elements.toast.textContent = message;
    elements.toast.classList.toggle("toast-error", Boolean(isError));
    elements.toast.classList.add("is-visible");
    toastTimer = window.setTimeout(() => elements.toast.classList.remove("is-visible"), 2800);
  }

  function addBook(id) {
    const result = BookCart.add(id);
    updateBadge();
    notify(result.message, !result.ok);
  }

  function openDetails(id) {
    const book = books.find(item => item.id === id);
    if (!book) return;
    elements.dialog.innerHTML = `
      <button class="dialog-close" type="button" aria-label="Đóng chi tiết" data-action="close">×</button>
      ${coverMarkup(book, "dialog-cover")}
      <div class="dialog-copy">
        <p class="eyebrow">${book.category}</p>
        <h2 id="dialog-title">${book.name}</h2>
        <p class="dialog-author">Tác giả: ${book.author}</p>
        <p class="dialog-description">${book.description}</p>
        <div class="dialog-purchase"><strong>${formatPrice(book.price)}</strong><span class="stock-copy ${book.available ? "" : "out-stock-copy"}">${book.available ? "Còn hàng" : "Tạm hết hàng"}</span></div>
        <button class="add-button" type="button" data-action="add" data-book-id="${book.id}" ${book.available ? "" : "disabled"}>${book.available ? "Thêm vào giỏ" : "Tạm hết hàng"}</button>
      </div>`;
    elements.dialog.showModal();
  }

  document.addEventListener("error", event => {
    const image = event.target;
    if (!(image instanceof HTMLImageElement) || (!image.closest(".book-cover, .dialog-cover, .cover") && image.id !== "hero-cover")) return;
    image.hidden = true;
    const fallback = image.parentElement.querySelector(".cover-fallback");
    if (fallback) fallback.hidden = false;
  }, true);

  elements.categoryList.addEventListener("click", event => {
    const button = event.target.closest("[data-category]");
    if (!button) return;
    filters.category = button.dataset.category;
    renderCategories();
    renderBooks();
  });

  document.addEventListener("click", event => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    if (button.dataset.action === "add") addBook(Number(button.dataset.bookId));
    if (button.dataset.action === "details") openDetails(Number(button.dataset.bookId));
    if (button.dataset.action === "close") elements.dialog.close();
  });

  elements.search.addEventListener("input", () => {
    filters.query = elements.search.value;
    renderBooks();
  });

  elements.sort.addEventListener("change", () => {
    filters.sort = elements.sort.value;
    renderBooks();
  });

  elements.clearFilters.addEventListener("click", () => {
    filters.category = "Tất cả";
    filters.query = "";
    elements.search.value = "";
    renderCategories();
    renderBooks();
  });

  elements.dialog.addEventListener("click", event => {
    if (event.target === elements.dialog) elements.dialog.close();
  });

  elements.search.addEventListener("keydown", event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      elements.search.focus();
    }
  });

  window.addEventListener("storage", event => {
    if (event.key === BookCart.storageKey) updateBadge();
  });

  elements.featured.innerHTML = featuredBooks.map(cardMarkup).join("");
  renderCategories();
  renderBooks();
  updateBadge();
})();