# QuizBot Flask (с таймером)

Минимальное веб‑приложение на Flask для тестов с ограничением по времени.

## Локальный запуск
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export FLASK_SECRET_KEY="замени-на-случайный"
export TEST_DURATION_SECONDS=120  # сек на весь тест (опционально)
python app.py
```
Открой `http://127.0.0.1:5000`.

## Вопросы
Редактируй `questions.json`. Поля:
```json
[
  {"question": "Текст", "options": ["A","B","C","D"], "answer": 1}
]
```
`answer` — индекс верного ответа, начиная с 0.

## Деплой на Render
1. Создай репозиторий на GitHub и залей код.
2. На https://render.com → New → Web Service → подключи репо.
3. Runtime: Python 3; Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Env Vars: `FLASK_SECRET_KEY=<случайная_строка>`, `TEST_DURATION_SECONDS=120`
6. Открой выданный URL, чтобы проходить тест из браузера.

## Замечания
- Результаты пишутся в SQLite (`quiz.db`), можно выгружать с сервера.
- Таймер — на весь тест; при 0 секунд страница автоматически завершает попытку.
- Для продакшна добавь авторизацию/ограничение попыток/экспорт результатов.
