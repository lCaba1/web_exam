document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('image');
    if (!fileInput) return;

    const fileNameDisplay = document.createElement('span');
    fileNameDisplay.className = 'text-muted ms-2';
    fileNameDisplay.id = 'file-name';
      
    const label = fileInput.previousElementSibling;
    if (label && label.tagName === 'LABEL') {
        label.appendChild(fileNameDisplay);
    }
      
    fileInput.addEventListener('change', function(e) {
        const fileName = e.target.files[0]?.name || 'Файл не выбран';
        fileNameDisplay.textContent = fileName;
    });
      
    fileNameDisplay.textContent = fileInput.files[0]?.name || 'Файл не выбран';
});