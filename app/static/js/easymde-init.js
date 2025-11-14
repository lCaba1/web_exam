// Инициализация EasyMDE для Markdown-редактора
document.addEventListener('DOMContentLoaded', function() {
  const descriptionElement = document.getElementById('description');
  if (descriptionElement) {
    const easyMDE = new EasyMDE({
      element: descriptionElement,
      spellChecker: false,
      autosave: { enabled: false },
      toolbar: [
        "bold", "italic", "heading", "|",
        "quote", "unordered-list", "ordered-list", "|",
        "link", "image", "|", "preview"
      ]
    });
  }
});