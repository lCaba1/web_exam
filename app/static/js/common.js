// Автоматическое скрытие уведомлений через 5 секунд
document.addEventListener('DOMContentLoaded', function() {
  // Скрытие всех алертов, кроме .alert-static
  setTimeout(() => {
    const alerts = document.querySelectorAll('.alert:not(.alert-static)');
    alerts.forEach(alert => {
      if (window.bootstrap && bootstrap.Alert) {
        new bootstrap.Alert(alert).close();
      } else {
        alert.style.display = 'none';
      }
    });
  }, 5000);

  // Подсветка активных ссылок в навигации
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav-link');

  navLinks.forEach(link => {
    const linkPath = link.getAttribute('href');
    if (linkPath === currentPath) {
      link.classList.add('active', 'fw-bold');
    }
  });
});