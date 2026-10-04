const backToTop = document.querySelector('.back-to-top');

document.addEventListener('scroll', function () {
  if (window.scrollY > 500) {
    backToTop.style.display = 'inline-block';
  } else {
    backToTop.style.display = 'none';
  }
});

backToTop.addEventListener('click', () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  });
});

const bookGrid = document.querySelector('#book-grid');
const bookSearch = document.querySelector('#book-search');
const bookFilters = document.querySelectorAll('[data-book-filter]');
const bookResults = document.querySelector('#book-results');
const bookEmpty = document.querySelector('#book-empty');

if (bookGrid && bookSearch && bookResults && bookEmpty && bookFilters.length) {
  const bookCards = Array.from(bookGrid.querySelectorAll('.book-card'));
  let activeCategory = 'all';

  function filterBooks() {
    const searchTerm = bookSearch.value.trim().toLocaleLowerCase();
    let visibleCount = 0;

    bookCards.forEach((card) => {
      const matchesCategory =
        activeCategory === 'all' || card.dataset.category === activeCategory;
      const searchableText =
        `${card.dataset.title} ${card.dataset.author}`.toLocaleLowerCase();
      const matchesSearch = searchableText.includes(searchTerm);
      const isVisible = matchesCategory && matchesSearch;

      card.hidden = !isVisible;
      if (isVisible) visibleCount += 1;
    });

    bookResults.textContent = `Hiển thị ${visibleCount} trong ${bookCards.length} cuốn sách`;
    bookEmpty.hidden = visibleCount > 0;
  }

  bookFilters.forEach((filter) => {
    filter.addEventListener('click', () => {
      activeCategory = filter.dataset.bookFilter;
      bookFilters.forEach((button) => {
        const isActive = button === filter;
        button.classList.toggle('is-active', isActive);
        button.setAttribute('aria-pressed', String(isActive));
      });
      filterBooks();
    });
  });

  bookSearch.addEventListener('input', filterBooks);
  filterBooks();
}
