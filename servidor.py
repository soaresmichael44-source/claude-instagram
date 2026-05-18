import os, time, tempfile
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import cloudinary, cloudinary.uploader, requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__)
CORS(app)

ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
API_VERSION = os.getenv("META_API_VERSION", "v19.0")
GRAPH = f"https://graph.facebook.com/{API_VERSION}"

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

HTML = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>Publicador Instagram</title><style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:-apple-system,sans-serif;background:#0f0f0f;color:#e0e0e0;padding:20px;max-width:700px;margin:0 auto}h1{font-size:18px;margin-bottom:20px}label{font-size:11px;color:#888;display:block;margin-bottom:5px;text-transform:uppercase}textarea,input{width:100%;padding:10px;background:#1a1a1a;border:1px solid #333;border-radius:8px;color:#e0e0e0;font-size:14px;font-family:inherit;margin-bottom:12px}textarea{resize:vertical}.slide{background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:12px;margin-bottom:10px}.sh{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}.sh span{font-size:12px;color:#888}.rb{background:none;border:none;color:#888;cursor:pointer;font-size:20px}.add{width:100%;padding:10px;background:none;border:1px dashed #444;border-radius:8px;color:#888;cursor:pointer;margin:10px 0;font-size:14px}.pub{width:100%;padding:12px;background:linear-gradient(135deg,#C13584,#E1306C);color:white;border:none;border-radius:8px;font-size:16px;font-weight:600;cursor:pointer;margin-top:10px}.pub:disabled{opacity:.5}.st{margin-top:15px;padding:12px;border-radius:8px;font-size:14px;display:none}.ok{background:#0d2e1a;color:#4caf50;border:1px solid #1e5c32}.er{background:#2e0d0d;color:#f44336;border:1px solid #5c1e1e}</style></head><body><h1>Publicador Instagram</h1><label>Legenda</label><textarea id="cap" rows="4" placeholder="Legenda com hashtags..."></textarea><label>Slides</label><div id="slides"></div><button class="add" onclick="addSlide('','')">+ Adicionar slide</button><button class="pub" id="btn" onclick="pub()">Publicar no Instagram</button><div class="st" id="st"></div><script>let n=0;function addSlide(t,c){n++;const id=n;const d=document.createElement('div');d.className='slide';d.id='sl'+id;d.innerHTML=`<div class="sh"><span>Slide ${id}</span><button class="rb" onclick="document.getElementById('sl${id}').remove()">x</button></div><input type="text" id="t${id}" placeholder="Titulo" value="${t}"><textarea id="c${id}" rows="2" placeholder="Conteudo">${c}</textarea>`;document.getElementById('slides').appendChild(d);}function msg(m,tp){const e=document.getElementById('st');e.style.display='block';e.className='st '+tp;e.innerHTML=m;}async function pub(){const cap=document.getElementById('cap').value.trim();const slides=[];for(let i=1;i<=n;i++){const t=document.getElementById('t'+i);const c=document.getElementById('c'+i);if(t&&c)slides.push({titulo:t.value.trim(),conteudo:c.value.trim()});}if(!cap)return msg('Preencha a legenda.','er');if(slides.length<2)return msg('Adicione pelo menos 2 slides.','er');const btn=document.getElementById('btn');btn.disabled=true;btn.textContent='Publicando...';msg('Gerando e enviando...','ok');try{const r=await fetch('/publicar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({caption:cap,dados:slides})});const d=await r.json();if(d.status==='ok'){msg('Publicado! Post ID: '+d.post_id,'ok');}else{msg('Erro: '+(d.erro||JSON.stringify(d)),'er');}}catch(e){msg('Erro: '+e.message,'er');}btn.disabled=false;btn.textContent='Publicar no Instagram';}addSlide('','');addSlide('','');</script></body></html>"""

def gerar_slide(titulo, conteudo, index):
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = int(220-(y/H)*60); g = int(180-(y/H)*80); b = int(190-(y/H)*60)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    draw.rectangle([20,20,W-20,H-20], outline="#D4AF37", width=4)
    try:
        ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
    except:
        ft = fb = ImageFont.load_default()
    draw.text((W//2, 280), titulo, font=ft, fill="#D4AF37", anchor="mm")
    words = conteudo.split()
    lines, line = [], ""
    for w in words:
        if len(line+w) < 32: line += w+" "
        else: lines.append(line.strip()); line = w+" "
    lines.append(line.strip())
    y = 460
    for l in lines:
        draw.text((W//2, y), l, font=fb, fill="white", anchor="mm"); y += 62
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(tmp.name, "JPEG", quality=95)
    return tmp.name

def upload(path):
    r = cloudinary.uploader.upload(path, folder="instagram_carrossel", resource_type="image",
        api_key=os.getenv("CLOUDINARY_API_KEY"), api_secret=os.getenv("CLOUDINARY_API_SECRET"))
    return r["secure_url"]

def aguardar(cid):
    for _ in range(15):
        r = requests.get(f"{GRAPH}/{cid}", params={"fields":"status_code","access_token":ACCESS_TOKEN})
        if r.json().get("status_code") == "FINISHED": return
        time.sleep(2)

@app.route("/")
def index():
    return HTML

@app.route("/publicar", methods=["POST"])
def publicar():
    data = request.get_json()
    caption = data.get("caption","")
    slides = data.get("dados",[])
    urls = []
    for i, s in enumerate(slides):
        path = gerar_slide(s.get("titulo",""), s.get("conteudo",""), i)
        url = upload(path); os.unlink(path); urls.append(url)
    cids = []
    for url in urls:
        r = requests.post(f"{GRAPH}/{ACCOUNT_ID}/media", data={"image_url":url,"is_carousel_item":"true","access_token":ACCESS_TOKEN})
        cids.append(r.json()["id"])
    for cid in cids: aguardar(cid)
    r = requests.post(f"{GRAPH}/{ACCOUNT_ID}/media", data={"media_type":"CAROUSEL","children":",".join(cids),"caption":caption,"access_token":ACCESS_TOKEN})
    carousel_id = r.json()["id"]
    r2 = requests.post(f"{GRAPH}/{ACCOUNT_ID}/media_publish", data={"creation_id":carousel_id,"access_token":ACCESS_TOKEN})
    return jsonify({"status":"ok","post_id":r2.json().get("id"),"image_urls":urls})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
