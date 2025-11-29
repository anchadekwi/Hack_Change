# 🎯 Умный реестр контента | MTS Hack&Change 2025

Автоматизированная система сбора и анализа статистики контента для медиа-компаний и контент-менеджеров. Интеграция с YouTube, MWS Tables и AI-аналитикой.

# 📊 Текущая функциональность
✅ Сбор данных YouTube - автоматический парсинг статистики каналов

✅ Интеграция с MWS Tables - запись данных в реальном времени

✅ Мультиплатформенность - поддержка YouTube, VK, Telegram

🔄 AI-аналитика - в разработке (чат-бот и прогнозирование)

# 🚀 Быстрый старт
1. Клонирование и настройка
bash
<pre><code id="codeBlock">
git clone https://github.com/anchadekwi/Hack_Change.git
cd Hack_Change
pip install -r requirements.txt
</code></pre>
<button onclick="copyCode()">
2. Настройка окружения
Создайте .env файл:

<pre><code id="codeBlock">
MWS Tables API
MWS_API_KEY=uskNd4PAf4ND1FODa1n4XQZ
MWS_SPACE_ID=dstEPg0bL9lD8jiDmt
MWS_VIEW_ID=viwBSnap01TEa

YouTube Data API
YOUTUBE_API_KEY=AIzaSyBB1nT_RE1FVHTvzcdF1e2FxBta7i7GFh8

OpenRouter AI
OPENROUTER_API_KEY=your_key_here
</code></pre>
<button onclick="copyCode()">

# 🏗 Архитектура проекта
<pre><code id="codeBlock">
Hack_Change/
├── main.py                 # Основной запускаемый файл
├── mws.py                  # Клиент MWS Tables API
├── youtube.py              # YouTube Data API клиент
├── test.py                 # Тесты и валидация
├── requirements.txt        # Зависимости Python
├── Dockerfile             # Контейнеризация приложения
├── static/                # Статические файлы (CSS, JS)
├── templates/             # HTML шаблоны
└── README.md              # Документация
</code></pre>
<button onclick="copyCode()">

# Пример использования
Сбор статистики: просмотры, лайки, комментарии

Метаданные: заголовки, описания, даты публикации

Автоматическое обновление: по расписанию или запросу

Автоматическое создание записей

Поддержка всех типов полей MWS

Обработка ошибок и валидация

Прогнозирование вовлеченности

📈 Структура данных в MWS Tables
<pre><code id="codeBlock">
Поле	Тип	Описание	Пример
Пост	SingleText	Описание контента	"Обзор нового автомобиля"
Ссылка	URL	Прямая ссылка	https://youtube.com/watch?v=...
Соц. сеть	SingleSelect	Платформа	Ютуб / ВК / Телеграмм
Название	Text	Заголовок	Полное название видео
Просмотры	Number	Количество	1,226,809
Лайки	Number	Лайки	63,081
Комментарии	Number	Комментарии	5,271
Дата	DateTime	Публикации	28/11/2025
</code></pre>
<button onclick="copyCode()">

📄 Техническое задание
Проект реализует требования MTS Hack&Change 2025:

Основные функции:
✅ Подключение к внешним API (YouTube Data API)

✅ Автоматический сбор статистики

✅ Интеграция с MWS Tables

✅ Визуализация данных

# 🤝 Команда разработки
# Команда "безымянный" - участники MTS Hack&Change 2025
