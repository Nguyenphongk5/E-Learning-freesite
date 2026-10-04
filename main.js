const backToTop = document.querySelector('.back-to-top');

document.querySelectorAll('[data-course-id][href="#"]').forEach(function (courseLink) {
  courseLink.setAttribute('aria-disabled', 'true');
  courseLink.title = 'Registration temporarily unavailable';
});

document.addEventListener('click', function (event) {
  const courseLink = event.target.closest('[data-course-id][href="#"]');
  if (courseLink) {
    event.preventDefault();
  }
});

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
