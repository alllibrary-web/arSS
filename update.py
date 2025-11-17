import requests
from bs4 import BeautifulSoup
from github import Github
import json
import os

# ================= 1. ПАРСИНГ ВСЕХ СТРАНИЦ =================

base_url = "https://byrutgame.org"  # сайт
items = []

try:
    # 1. Получаем главную страницу (или категорию с торрентами)
    html = requests.get(base_url).text
    soup = BeautifulSoup(html, "html.parser")

    # 2. Ищем все ссылки на страницы с торрентами
    # Меняем селектор под сайт, пример: все ссылки с "/torrent/"
    torrent_pages = [a['href'] for a in soup.select('a[href*="/torrent/"]')]

    # 3. Проходим по каждой странице с торрентом
    for page in torrent_pages:
        if not page.startswith("http"):
            page = base_url + page
        page_html = requests.get(page).text
        page_soup = BeautifulSoup(page_html, "html.parser")

        # 4. Ищем все ссылки на файлы .torrent на странице
        for link in page_soup.select("a[href$='.torrent']"):
            title = link.text.strip()
            torrent_link = link['href']
            if not torrent_link.startswith("http"):
                torrent_link = base_url + torrent_link

            items.append({
                "name": title,
                "magnet": torrent_link  # можно позже конвертировать в magnet
            })

except Exception as e:
    print("Ошибка при парсинге сайта:", e)

# ================= 2. ПОДКЛЮЧЕНИЕ К GITHUB =================

g = Github(os.getenv("GITHUB_TOKEN"))

repo = g.get_repo("alllibrary-web/arSS")
file_path = "arSS for Hydra.json"
file = repo.get_contents(file_path)

# ================= 3. ЧИТАЕМ JSON =================

data = json.loads(file.decoded_content.decode())

# ================= 4. ДОБАВЛЯЕМ НОВЫЕ ТОРРЕНТЫ =================

data.extend(items)

# ================= 5. СОХРАНЯЕМ НА GITHUB =================

repo.update_file(
    path=file_path,
    message="Auto update: all torrents from byrutgame.org",
    content=json.dumps(data, indent=4, ensure_ascii=False),
    sha=file.sha
)
