#!/usr/bin/env python3
"""Отправка постов из telegram/outbox/*.json в Telegram-канал (запускается в GitHub Actions).

Формат файла:
  {"text": "текст поста", "photos": ["https://.../01.jpg", ...]}   # photos необязательно, до 10
Токен бота — секрет TELEGRAM_BOT_TOKEN, канал — переменная TELEGRAM_CHAT_ID (например @spbpokoleniya).
После успешной отправки файл переносится в telegram/sent/.
"""
import glob, json, os, shutil, sys, urllib.request, urllib.parse

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ["TELEGRAM_CHAT_ID"]
API = f"https://api.telegram.org/bot{TOKEN}/"


def call(method, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(API + method, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        res = json.loads(e.read().decode() or "{}")
    if not res.get("ok"):
        sys.exit(f"Telegram ошибка в {method}: {res.get('description')}")
    return res["result"]


def link(msg):
    m = msg[0] if isinstance(msg, list) else msg
    u = m["chat"].get("username")
    return f"https://t.me/{u}/{m['message_id']}" if u else f"message_id={m['message_id']}"


def send(post):
    text, photos = post.get("text", ""), post.get("photos", [])
    if not photos:
        return call("sendMessage", {"chat_id": CHAT, "text": text})
    if len(text) > 1024:  # подпись к фото ограничена 1024 символами
        call("sendMediaGroup", {"chat_id": CHAT, "media": [{"type": "photo", "media": p} for p in photos[:10]]})
        return call("sendMessage", {"chat_id": CHAT, "text": text})
    if len(photos) == 1:
        return call("sendPhoto", {"chat_id": CHAT, "photo": photos[0], "caption": text})
    media = [{"type": "photo", "media": p} for p in photos[:10]]
    media[0]["caption"] = text
    return call("sendMediaGroup", {"chat_id": CHAT, "media": media})


if __name__ == "__main__":
    files = sorted(glob.glob("telegram/outbox/*.json"))
    if os.environ.get("TEST_MESSAGE"):
        print("✅", link(call("sendMessage", {"chat_id": CHAT, "text": os.environ["TEST_MESSAGE"]})))
    for f in files:
        msg = send(json.load(open(f, encoding="utf-8")))
        print("✅", f, "→", link(msg))
        shutil.move(f, "telegram/sent/" + os.path.basename(f))
