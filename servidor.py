#!/usr/bin/env python3
"""
Servidor local porta 3000.
POST /publicar  → gera slides, faz upload para catbox.moe, publica carrossel no Instagram.
GET  /status    → saúde do servidor.
"""

import json, os, sys, time, threading, subprocess, http.server
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

PROJECT_DIR  = Path(__file__).parent
SLIDES_DIR   = PROJECT_DIR / "slides"
LOG_FILE     = PROJECT_DIR / "servidor.log"
API_PORT = int(os.environ.get("PORT", 3000))

ACCOUNT_ID      = os.getenv("INSTAGRAM_BUSINESS_ID")
ACCESS_TOKEN    = os.getenv("INSTAGRAM_ACCESS_TOKEN")
API_VERSION     = os.getenv("META_API_VERSION", "v19.0")
IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
IMGBB_API_KEY   = os.getenv("IMGBB_API_KEY")
GRAPH           = f"https://graph.facebook.com/{API_VERSION}"

_lock = threading.Lock()

CAPTION_PADRAO = """🏠 Consórcio: o jeito inteligente de realizar seus sonhos!

✅ Sem juros
✅ Parcelas acessíveis
✅ Pode usar FGTS
✅ Carta de crédito = poder de compra à vista

Me chame no Direct e vamos encontrar o consórcio ideal para você! 👇

#consórcio #consorcioilumine #realizeseusonho #imóveis #automóvel #planejamentofinanceiro #investimento #michaelsoares #finançaspessoais"""


def log(msg):
    linha = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(linha, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(linha + "\n")


def gerar_slides():
    log("Gerando slides...")
    r = subprocess.run([sys.executable, str(PROJECT_DIR / "gerar_carrossel.py")],
                       capture_output=True, text=True, cwd=PROJECT_DIR)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    log("Slides gerados.")


def upload_imgbb(path: Path) -> str:
    log(f"  Enviando {path.name} → imgbb")
    import base64
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    r = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": IMGBB_API_KEY, "image": b64},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("success"):
        raise RuntimeError(f"imgbb erro: {data}")
    url = data["data"]["url"]
    log(f"    ✓ {url}")
    return url


def aguardar(cid, label=""):
    for i in range(15):
        r = requests.get(f"{GRAPH}/{cid}",
                         params={"fields": "status_code", "access_token": ACCESS_TOKEN})
        r.raise_for_status()
        status = r.json().get("status_code", "?")
        log(f"  [{label}] {status} ({i+1})")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Container {cid} em ERROR")
        time.sleep(5)
    raise TimeoutError(cid)


def publicar_carrossel(urls: list, caption: str) -> str:
    # Cria item por item
    children = []
    for url in urls:
        r = requests.post(f"{GRAPH}/{ACCOUNT_ID}/media",
                          params={"image_url": url, "is_carousel_item": "true",
                                  "access_token": ACCESS_TOKEN})
        r.raise_for_status()
        cid = r.json()["id"]
        log(f"  Item criado: {cid}")
        children.append(cid)

    for cid in children:
        aguardar(cid, cid[:8])

    # Cria container do carrossel
    r = requests.post(f"{GRAPH}/{ACCOUNT_ID}/media",
                      params={"media_type": "CAROUSEL", "children": ",".join(children),
                              "caption": caption, "access_token": ACCESS_TOKEN})
    r.raise_for_status()
    carrossel_id = r.json()["id"]
    log(f"  Carrossel: {carrossel_id}")
    aguardar(carrossel_id, "carrossel")

    # Publica
    r = requests.post(f"{GRAPH}/{ACCOUNT_ID}/media_publish",
                      params={"creation_id": carrossel_id, "access_token": ACCESS_TOKEN})
    r.raise_for_status()
    post_id = r.json()["id"]
    log(f"✅ Post ID: {post_id}")
    return post_id


def pipeline(caption: str, dados: dict = None) -> dict:
    import json as _json
    dados_str = _json.dumps(dados or {})
    import subprocess as _sp, sys as _sys
    r = _sp.run([_sys.executable, str(PROJECT_DIR / "gerar_carrossel.py"), dados_str],
                capture_output=True, text=True, cwd=PROJECT_DIR)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    arquivos = sorted(SLIDES_DIR.glob("*.jpg"))
    urls = [upload_imgbb(p) for p in arquivos]
    post_id = publicar_carrossel(urls, caption)
    return {"status": "ok", "post_id": post_id, "image_urls": urls}


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        log(f"{self.client_address[0]} {fmt % args}")

    def _json(self, code, data):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/status":
            self._json(200, {"status": "online", "porta": API_PORT, "conta": ACCOUNT_ID})
        else:
            self._json(404, {"erro": "não encontrado"})

    def do_POST(self):
        if self.path != "/publicar":
            self._json(404, {"erro": "não encontrado"})
            return

        caption = CAPTION_PADRAO
        n = int(self.headers.get("Content-Length", 0))
        if n:
            try:
                body = json.loads(self.rfile.read(n))
                caption = body.get("caption", CAPTION_PADRAO)
                dados = body.get("dados", {})
            except json.JSONDecodeError:
                self._json(400, {"erro": "JSON inválido"})
                return

        if not _lock.acquire(blocking=False):
            self._json(409, {"erro": "publicação em andamento"})
            return

        try:
            log("=== POST /publicar ===")
            self._json(200, pipeline(caption, dados))
        except Exception as e:
            log(f"ERRO: {e}")
            self._json(500, {"erro": str(e)})
        finally:
            _lock.release()


if __name__ == "__main__":
    if not ACCOUNT_ID or not ACCESS_TOKEN:
        sys.exit("Erro: INSTAGRAM_BUSINESS_ID e INSTAGRAM_ACCESS_TOKEN não definidos no .env")
    server = http.server.HTTPServer(("0.0.0.0", API_PORT), Handler)
    log(f"Servidor em http://localhost:{API_PORT}  |  POST /publicar  |  GET /status")
    server.serve_forever()
