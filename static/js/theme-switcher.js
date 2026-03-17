/**
 * Theme Switcher for MusicRate
 * Обрабатывает переключение тем с плавным переходом и перезагрузкой
 */

(function() {
    // Функция для применения темы
    function applyTheme(themeData) {
        if (!themeData) return;

        const root = document.documentElement;

        // Применяем CSS переменные
        Object.entries(themeData.css_variables).forEach(([key, value]) => {
            root.style.setProperty(key, value);
        });

        // Обновляем класс dark/light
        if (themeData.theme_type === 'dark') {
            document.documentElement.classList.add('dark');
            document.documentElement.classList.remove('light');
        } else {
            document.documentElement.classList.add('light');
            document.documentElement.classList.remove('dark');
        }

        // Сохраняем в localStorage для анонимных пользователей
        localStorage.setItem('musicrate_theme', themeData.slug);
    }

    // Загрузка темы из localStorage для анонимных пользователей
    function loadStoredTheme() {
        const storedTheme = localStorage.getItem('musicrate_theme');
        if (storedTheme) {
            fetch('/themes/available/')
                .then(response => response.json())
                .then(data => {
                    const theme = data.themes.find(t => t.slug === storedTheme);
                    if (theme) {
                        applyTheme(theme);
                    }
                })
                .catch(console.error);
        }
    }

    // Обработка HTMX событий для переключения тем
    document.addEventListener('htmx:afterSwap', function(event) {
        // Если это ответ от переключателя тем, перезагружаем страницу
        if (event.detail.target.closest('[hx-post*="themes/set"]')) {
            // Небольшая задержка для плавного визуального эффекта
            setTimeout(() => {
                window.location.reload();
            }, 300);
        }
    });

    // Плавный переход при переключении темы
    document.addEventListener('DOMContentLoaded', function() {
        // Добавляем плавность для body
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';

        // Загружаем сохранённую тему для анонимных пользователей
        loadStoredTheme();
    });

    // Обработка формы переключения темы
    document.addEventListener('submit', function(event) {
        const form = event.target;
        if (form.classList.contains('theme-form')) {
            const themeSlug = form.querySelector('[name="theme_slug"]').value;

            // Находим название темы для отображения
            const themeName = form.querySelector('button').querySelector('.font-medium').textContent.trim();

            // Показываем индикатор загрузки
            const button = form.querySelector('button');
            const originalContent = button.innerHTML;
            button.innerHTML = '<span class="text-text-muted">Применение...</span>';
            button.disabled = true;

            // Восстанавливаем кнопку после получения ответа
            form.addEventListener('htmx:afterSwap', function() {
                button.innerHTML = originalContent;
                button.disabled = false;
            }, { once: true });
        }
    });
})();
