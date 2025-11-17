import requests
from bs4 import BeautifulSoup
from github import Github
import json
import os

# ================= 1. ПАРСИНГ САЙТА =================

BASE_URL = "https://byrutgame.org"
items = []

try:
    print("Парсим сайт:", BASE_URL)
    html = requests.get(BASE_URL, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")

    # Ищем ссылки, содержащие "/torrent/"
    torrent_pages = [a['href'] for a in soup.select('a[href*="/torrent/"]')]

    print(f"Найдено страниц с торрентами: {len(torrent_pages)}")

    for page in torrent_pages:
        page_url = page if page.startswith("http") else BASE_URL + page

        try:
            page_html = requests.get(page_url, timeout=10).text
            page_soup = BeautifulSoup(page_html, "html.parser")

            # Ищем ссылки на .torrent файлы
            torrent_links = page_soup.select("a[href$='.torrent']")

            for link in torrent_links:
                title = link.text.strip() or "Без названия"
                torrent_url = link["href"]
                if not torrent_url.startswith("http"):
                    torrent_url = BASE_URL + torrent_url

                items.append({
                    "name": title,
                    "magnet": torrent_url
                })

        except Exception as e:
            print("Ошибка страницы:", page_url, "::", e)

except Exception as e:
    print("Ошибка при парсинге сайта:", e)


# ================= 2. ПОДКЛЮЧЕНИЕ К GITHUB =================

print("Подключаемся к GitHub...")

# ВАЖНО: именно GH_TOKEN !!!
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise SystemExit("ОШИБКА: GITHUB_TOKEN не получен! Проверь секрет GH_TOKEN в GitHub.")

g = Github(token)
repo = g.get_repo("alllibrary-web/arSS")
file_path = "arSS for Hydra.json"

file = repo.get_contents(file_path)

# ================= 3. ЧИТАЕМ ТЕКУЩИЙ JSON =================

try:
    data = json.loads(file.decoded_content.decode())
except Exception:
    data = []

# ================= 4. ДОБАВЛЯЕМ НОВЫЕ ТОРРЕНТЫ =================

print(f"Добавляем {len(items)} новых торрентов...")
data.extend(items)

# ================= 5. СОХРАНЯЕМ НА GITHUB =================

repo.update_file(
    path=file_path,
    message="Auto update from byrutgame.org",
    content=json.dumps(data, indent=4, ensure_ascii=False),
    sha=file.sha
)

print("Файл успешно обновлён!")
