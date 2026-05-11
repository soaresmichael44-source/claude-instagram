import os, sys, json
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "/Users/michaelsoares/claude-instagram/slides"
SIZE = (1080, 1080)

BG      = "#1a0a0e"
BG2     = "#2d1420"
BG3     = "#3d1e2a"
GOLD    = "#C9A84C"
ROSE    = "#e8a0aa"
CREAM   = "#F5E6C8"
MUTED   = "#c8a090"

def font(size, bold=False):
    paths = [
        "/Library/Fonts/Georgia Bold.ttf" if bold else "/Library/Fonts/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except:
            continue
    return ImageFont.load_default()

def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def canvas():
    img = Image.new("RGB", SIZE, hex2rgb(BG))
    draw = ImageDraw.Draw(img)
    draw.ellipse([580, -100, 1280, 500], fill=hex2rgb(BG2))
    draw.ellipse([-200, 600, 500, 1200], fill=hex2rgb(BG2))
    return img, draw

def gold_line(draw, y, w=300):
    x = (1080 - w) // 2
    draw.rectangle([x, y, x+w, y+4], fill=hex2rgb(GOLD))

def handle_text(draw, h="@michaelsoares_"):
    gold_line(draw, 990, 300)
    f = font(40)
    bbox = f.getbbox(h)
    w = bbox[2] - bbox[0]
    draw.text(((1080-w)//2, 1020), h, font=f, fill=hex2rgb(GOLD))

def center(draw, text, y, size, color, bold=False):
    f = font(size, bold)
    for i, line in enumerate(text.split("\n")):
        bbox = f.getbbox(line)
        w = bbox[2] - bbox[0]
        draw.text(((1080-w)//2, y + i*int(size*1.35)), line, font=f, fill=hex2rgb(color))

def slide_capa(dados):
    img, draw = canvas()
    draw.ellipse([380, 280, 700, 600], fill=hex2rgb(BG3))
    draw.ellipse([390, 290, 690, 590], fill="#3d1e2a")
    draw.ellipse([420, 310, 660, 520], fill=(*hex2rgb(ROSE), 40))
    gold_line(draw, 380, 200)
    center(draw, dados.get("titulo",""), 430, 96, CREAM, bold=True)
    center(draw, dados.get("subtitulo",""), 580, 40, MUTED)
    for cx, cy, r, c in [(80,80,18,ROSE),(1000,400,14,GOLD),(60,700,12,ROSE),(980,900,10,GOLD)]:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=hex2rgb(c), width=2)
    handle_text(draw, dados.get("handle","@usuario"))
    return img

def slide_conteudo(dados, num):
    img, draw = canvas()
    f_big = font(200, bold=True)
    draw.text((60, 60), str(num), font=f_big, fill=(*hex2rgb(GOLD), 50))
    gold_line(draw, 360, 400)
    center(draw, dados.get("titulo",""), 400, 80, CREAM, bold=True)
    center(draw, dados.get("corpo",""), 540, 44, MUTED)
    draw.ellipse([480, 820, 600, 940], outline=hex2rgb(GOLD), width=3)
    draw.ellipse([510, 850, 570, 910], fill=(*hex2rgb(ROSE), 100))
    handle_text(draw, dados.get("handle","@usuario"))
    return img

def slide_cta(dados):
    img, draw = canvas()
    gold_line(draw, 360, 400)
    center(draw, dados.get("cta","Siga para mais!"), 420, 72, CREAM, bold=True)
    center(draw, dados.get("subtitulo",""), 560, 44, MUTED)
    gold_line(draw, 680, 400)
    for cx, cy, r, c in [(80,80,18,ROSE),(1000,400,14,GOLD),(60,700,12,ROSE),(980,900,10,GOLD)]:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=hex2rgb(c), width=2)
    handle_text(draw, dados.get("handle","@usuario"))
    return img

def main():
    dados_raw = sys.argv[1] if len(sys.argv) > 1 else "{}"
    dados = json.loads(dados_raw)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    handle = dados.get("handle", "@usuario")
    slides_def = dados.get("slides", [])

    img = slide_capa({**dados, "handle": handle})
    p = os.path.join(OUTPUT_DIR, "01_capa.jpg")
    img.save(p, "JPEG", quality=95)
    print(f"Salvo: {p}")

    for i, s in enumerate(slides_def):
        s["handle"] = handle
        img = slide_conteudo(s, i+1)
        p = os.path.join(OUTPUT_DIR, f"0{i+2}_slide.jpg")
        img.save(p, "JPEG", quality=95)
        print(f"Salvo: {p}")

    img = slide_cta({"cta": dados.get("cta",""), "subtitulo": dados.get("cta_sub",""), "handle": handle})
    p = os.path.join(OUTPUT_DIR, f"0{len(slides_def)+2}_cta.jpg")
    img.save(p, "JPEG", quality=95)
    print(f"Salvo: {p}")

if __name__ == "__main__":
    main()
