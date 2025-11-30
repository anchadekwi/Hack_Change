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
├── pipeline.py             # Основной запускаемый файл
├── mws_client.py           # Клиент MWS Tables API
├── data_collector.py       # YouTube Data API клиент
├── vk_parser.py            # VK Data API клиент
├── tg_parser.py            # Tg Data API клиент
├── requirements.txt        # Зависимости Python
└── README.md               # Документация
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
| Поле | Тип | Описание | Пример |
|:-----|:----|:----------|:-------|
| **Пост** | `SingleText` | Описание контента | `"Обзор нового автомобиля"` |
| **Ссылка** | `URL` | Прямая ссылка | `https://youtube.com/watch?v=...` |
| **Соц. сеть** | `SingleSelect` | Платформа | **Ютуб / ВК / Телеграмм** |
| **Название** | `Text` | Заголовок | *Полное название видео* |
| **Просмотры** | `Number` | Количество | `1,226,809` |
| **Лайки** | `Number` | Лайки | `63,081` |
| **Комментарии** | `Number` | Комментарии | `5,271` |
| **Дата** | `DateTime` | Публикации | `28/11/2025` |

📄 Техническое задание
Проект реализует требования MTS Hack&Change 2025:

Основные функции:
✅ Подключение к внешним API (YouTube Data API)

✅ Автоматический сбор статистики

✅ Интеграция с MWS Tables

✅ Визуализация данных

# 🤝 Команда разработки
# Команда "безымянный" - участники MTS Hack&Change 2025
* Константин Никонов - backend-разработчик
* Алёна Поминова - аналитик данных
* Анна Федорова - backend-разработчик 
* Артём Хорев - backend-разработчик

# Инструкция по запуску
```
pip install -r requirements.txt
python3 pipeline.py
```
Это скрипт экспорта данных в MWS. Рекомендуется запускать его по расписанию или в отдельном процессе

# MWS
Таблица с тестовыми данными:
https://tables.mws.ru/invite/link?token=9245b0a225274ea4b9a4630b36960802 От MWS Tables: 79278543399 пригласил вас присоединиться к пространству "Реестр".
https://tables.mws.ru/template/tpcprivate/tplYjhZvQmrRY