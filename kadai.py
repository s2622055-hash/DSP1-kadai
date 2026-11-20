import json
import requests
import sqlite3
import time
from bs4 import BeautifulSoup

conn = sqlite3.connect("google_repos.db")
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        language TEXT,
        stars INTEGER
    )
""")

cur.execute("DELETE FROM repositories")
conn.commit()

url = "https://github.com/orgs/google/repositories"
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

page_num = 1

while True:
    print(f"{page_num}ページ目を取得中...")

    param = {
        'page': page_num
    }

    res = requests.get(url, params=param, headers=header)
    time.sleep(1)

    if res.status_code != 200:
        print(f"アクセス終了（ステータスコード: {res.status_code}）")
        break

    soup = BeautifulSoup(res.content, 'html.parser')
    script_tag = soup.find('script', {'data-target': 'react-app.embeddedData'})

    if script_tag is None:
        print("データの取得に失敗しました。")
        break

    data = json.loads(script_tag.string)
    route_data = data['payload']['orgReposPageRoute']
    repos = route_data['repositories']
    page_count = route_data['pageCount']

    if not repos:
        break

    for repo in repos:
        name = repo['name']
        if repo['primaryLanguage'] is not None:
            language = repo['primaryLanguage']['name']
        else:
            language = "None"
        stars = repo['starsCount']

        cur.execute(
            "INSERT INTO repositories (name, language, stars) VALUES (?, ?, ?)",
            (name, language, stars)
        )

    conn.commit()

    if page_num >= page_count:
        print("全ページの取得が完了しました。")
        break

    page_num += 1

print("\n=== データベースに保存されたデータ一覧 ===")
cur.execute("SELECT * FROM repositories")
rows = cur.fetchall()

for row in rows:
    print(row)

print(f"\n合計取得件数: {len(rows)}件")

conn.close()