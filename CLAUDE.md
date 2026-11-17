# smm-bot — ведение соцсетей через Claude

Пользователь пишет по-русски, отвечай по-русски, простым языком (он не программист).

## Площадки
- Instagram — `instagram.py` (готово). Токен: сетевой секрет окружения для `graph.instagram.com`
  (или переменная `IG_TOKEN`). Хост `graph.instagram.com` должен быть разрешён в сети окружения.
- Telegram, MAX — ещё не подключены.

## Правила
- Никогда не публикуй без явного «да» пользователя на конкретный текст и медиа.
- Медиа для постов клади в `media/`, коммить и пушь в `main`; публичная ссылка:
  `https://raw.githubusercontent.com/adamec1213-sketch/smm-bot/main/media/<файл>`.
- Перед созданием контента читай профиль продукта (навык `product-marketing`,
  файл `.agents/product-marketing.md`). Если его нет — сначала собери его
  (после подключения Instagram — по `python instagram.py profile`).
- Тексты: навыки `social`, `copywriting`, `content-strategy`; видео — `video`; картинки — `image`.
- Токен Instagram живёт 60 дней: продлевай `python instagram.py refresh`.
