#!/usr/bin/env python3
"""Публикация в Instagram через Instagram API с входом через Instagram (graph.instagram.com).

Токен берётся из переменной IG_TOKEN. Если её нет, запрос уходит с заглушкой,
и сетевой прокси облачной сессии подставляет сохранённый токен сам.

Команды:
  python instagram.py profile                     — аккаунт и последние посты
  python instagram.py photo URL "подпись"          — пост с одним фото
  python instagram.py carousel URL1 URL2 ... -c "подпись"  — карусель (2–10 фото/видео)
  python instagram.py reel URL "подпись" [--cover URL]     — Reels
  python instagram.py insights [N]                — статистика последних N постов
  python instagram.py refresh                     — продлить токен ещё на 60 дней

Медиа должны лежать по публичной ссылке (например, папка media/ этого репозитория:
https://raw.githubusercontent.com/<логин>/smm-bot/main/media/<файл>).
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.instagram.com/v21.0"
TOKEN = os.environ.get("IG_TOKEN", "proxy-injected")
VIDEO_EXT = (".mp4", ".mov")


def call(method, path, **params):
    params = {k: v for k, v in params.items() if v is not None}
    url = f"{API}/{path}"
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {TOKEN}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body)["error"]
            msg = f"{err.get('message')} (код {err.get('code')}, {err.get('error_subcode', '-')})"
        except Exception:
            msg = body
        sys.exit(f"Ошибка Instagram API: HTTP {e.code}: {msg}")


def me():
    return call("GET", "me", fields="user_id,username")["user_id"]


def wait_ready(container_id, timeout=600):
    """Видео обрабатывается на стороне Instagram — ждём статуса FINISHED."""
    start = time.time()
    while True:
        st = call("GET", container_id, fields="status_code,status")
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            sys.exit(f"Instagram не смог обработать медиа: {st.get('status')}")
        if time.time() - start > timeout:
            sys.exit("Обработка медиа заняла слишком долго")
        time.sleep(5)


def publish(uid, container_id):
    wait_ready(container_id)
    media_id = call("POST", f"{uid}/media_publish", creation_id=container_id)["id"]
    link = call("GET", media_id, fields="permalink").get("permalink")
    print(f"✅ Опубликовано: {link or media_id}")


def is_video(url):
    return urllib.parse.urlparse(url).path.lower().endswith(VIDEO_EXT)


def cmd_profile(_):
    p = call("GET", "me", fields="user_id,username,name,biography,website,"
             "followers_count,follows_count,media_count,account_type")
    print(json.dumps(p, ensure_ascii=False, indent=2))
    media = call("GET", "me/media", limit=25,
                 fields="caption,media_type,permalink,timestamp,like_count,comments_count")
    for m in media.get("data", []):
        print("\n---", m.get("timestamp", "")[:10], m.get("media_type"), m.get("permalink"),
              f"❤ {m.get('like_count', '?')} 💬 {m.get('comments_count', '?')}")
        print(m.get("caption", ""))


def cmd_photo(a):
    uid = me()
    c = call("POST", f"{uid}/media", image_url=a.url, caption=a.caption)["id"]
    publish(uid, c)


def cmd_carousel(a):
    if not 2 <= len(a.urls) <= 10:
        sys.exit("В карусели должно быть от 2 до 10 элементов")
    uid = me()
    children = []
    for u in a.urls:
        kw = {"media_type": "VIDEO", "video_url": u} if is_video(u) else {"image_url": u}
        cid = call("POST", f"{uid}/media", is_carousel_item="true", **kw)["id"]
        wait_ready(cid)
        children.append(cid)
    c = call("POST", f"{uid}/media", media_type="CAROUSEL",
             children=",".join(children), caption=a.caption)["id"]
    publish(uid, c)


def cmd_reel(a):
    uid = me()
    c = call("POST", f"{uid}/media", media_type="REELS", video_url=a.url,
             caption=a.caption, cover_url=a.cover, share_to_feed="true")["id"]
    publish(uid, c)


def cmd_insights(a):
    media = call("GET", "me/media", limit=a.n,
                 fields="id,caption,media_type,permalink,timestamp,like_count,comments_count")
    for m in media.get("data", []):
        metrics = "reach,saved,shares,total_interactions"
        if m["media_type"] == "VIDEO":
            metrics += ",views"
        ins = call("GET", f"{m['id']}/insights", metric=metrics)
        vals = {i["name"]: i["values"][0]["value"] for i in ins.get("data", [])}
        cap = (m.get("caption") or "").replace("\n", " ")[:60]
        print(m["timestamp"][:10], m["media_type"], f"❤{m.get('like_count')} 💬{m.get('comments_count')}",
              vals, "|", cap)


def cmd_refresh(_):
    r = call("GET", "refresh_access_token", grant_type="ig_refresh_token", access_token=TOKEN)
    days = r.get("expires_in", 0) // 86400
    print(f"Токен продлён на {days} дней. Новый токен нужно сохранить заново, если он изменился.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("profile").set_defaults(f=cmd_profile)
    p = sub.add_parser("photo"); p.add_argument("url"); p.add_argument("caption", nargs="?", default="")
    p.set_defaults(f=cmd_photo)
    p = sub.add_parser("carousel"); p.add_argument("urls", nargs="+"); p.add_argument("-c", "--caption", default="")
    p.set_defaults(f=cmd_carousel)
    p = sub.add_parser("reel"); p.add_argument("url"); p.add_argument("caption", nargs="?", default="")
    p.add_argument("--cover"); p.set_defaults(f=cmd_reel)
    p = sub.add_parser("insights"); p.add_argument("n", nargs="?", type=int, default=10)
    p.set_defaults(f=cmd_insights)
    sub.add_parser("refresh").set_defaults(f=cmd_refresh)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
