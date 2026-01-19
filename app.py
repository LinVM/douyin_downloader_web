from flask import Flask, render_template, request, flash
import os, requests, re, json

app = Flask(__name__)
app.secret_key = "douyin_downloader_secret"

DOWNLOAD_FOLDER = "images"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def fetch_images_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        html = resp.text
        match = re.search(r'window\.__INIT_PROPS__=(.*?);\(function', html)
        if not match: return f"[ERROR] 未找到商品信息: {url}"
        data = json.loads(match.group(1))
        goods_name = data.get('goodsDetail', {}).get('basicInfo', {}).get('name', 'unknown_product')
        goods_name = re.sub(r'[\\/:*?"<>|]', '_', goods_name)
        images = data.get('goodsDetail', {}).get('images', [])
        if not images: return f"[ERROR] 未找到商品图片: {url}"
        folder_path = os.path.join(DOWNLOAD_FOLDER, goods_name)
        os.makedirs(folder_path, exist_ok=True)
        for i, img_url in enumerate(images, start=1):
            img_url = img_url.replace("http://", "https://")
            ext = img_url.split('.')[-1].split('?')[0]
            img_data = requests.get(img_url, headers=headers, timeout=10).content
            with open(os.path.join(folder_path, f"{i}.{ext}"), "wb") as f:
                f.write(img_data)
        return f"[OK] 下载完成: {goods_name} ({len(images)} 张图片)"
    except Exception as e:
        return f"[ERROR] 下载失败: {url} -> {e}"

@app.route("/", methods=["GET","POST"])
def index():
    results = []
    if request.method=="POST":
        urls_text = request.form.get("urls","").strip()
        urls = [line.strip() for line in urls_text.splitlines() if line.strip()]
        if not urls: flash("请至少输入一个商品链接","danger")
        else: results = [fetch_images_from_url(u) for u in urls]
    return render_template("index.html", results=results)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
