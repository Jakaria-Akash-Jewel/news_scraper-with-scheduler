from flask import Flask, render_template_string, send_file
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import io
import threading
import schedule
import time

app = Flask(__name__)

def get_headlines():
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://edition.cnn.com/world"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    headlines = []

    for tag in soup.find_all("a"):
        title = tag.get_text(strip=True)
        link = tag.get("href")
        if title and link and "/202" in link:
            full_link = f"https://edition.cnn.com{link}" if link.startswith("/") else link
            if (title, full_link) not in headlines:
                headlines.append((title, full_link))

    return headlines

def save_headlines_to_csv(headlines):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Headline', 'URL'])
    for title, link in headlines:
        writer.writerow([title, link])
    output.seek(0)
    return output

@app.route('/')
def home():
    headlines = get_headlines()
    return render_template_string(template, headlines=headlines)

@app.route('/download')
def download_csv():
    headlines = get_headlines()
    csv_file = save_headlines_to_csv(headlines)
    date = datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f"cnn_headlines_{date}.csv"
    return send_file(io.BytesIO(csv_file.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=filename)

template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CNN News Headlines</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 30px;
        }
        h1 {
            color: #cc0000;
            text-align: center;
        }
        ul {
            max-width: 800px;
            margin: auto;
            padding: 0;
            list-style: none;
        }
        li {
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-left: 6px solid #cc0000;
            font-size: 18px;
        }
        a {
            text-decoration: none;
            color: #222;
        }
        a:hover {
            text-decoration: underline;
            color: #cc0000;
        }
        .buttons {
            text-align: center;
            margin: 30px;
        }
        .btn {
            background: #cc0000;
            color: white;
            padding: 10px 20px;
            margin: 5px;
            text-decoration: none;
            font-size: 16px;
            border-radius: 5px;
        }
        .btn:hover {
            background: #990000;
        }
    </style>
</head>
<body>
    <h1>CNN News Headlines with Links</h1>

    <div class="buttons">
        <a href="/" class="btn">🔁 Refresh</a>
        <a href="/download" class="btn">💾 Download CSV</a>
    </div>

    <ul>
        {% for title, link in headlines %}
            <li><a href="{{ link }}" target="_blank">{{ title }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
'''

def run_scheduler():
    def job():
        print(f"🕒 Scheduler ran at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        get_headlines()

    schedule.every(1).hour.do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(debug=True)
