import os, sys, json
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/Library/Fonts/Arial Bold.ttf"
FONT_REG  = "/System/Library/Fonts/SFNS.ttf"
OUTPUT_DIR = "/Users/michaelsoares/claude-instagram/slides"

BG        = "#0D1B2A"
ACCENT    = "#EBA020"
WHITE     = "#FFFFFF"
LIGHTGRAY = "#B0C4DE"
CARD      = "#1A2F45"
SIZE      = (1080, 1080)

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def new_canvas():
    img = Image.new("RGB", SIZE, BG)
    return img, ImageDraw.Draw(img)

def draw_accent_bar(draw, y=80, width=120, thick=6):
    draw.rectangle([(SIZE[0]//2 - width//2, y), (SIZE[0]//2 + width//2, y+thick)], fill=ACCENT)

def center_text(draw, text, y, font, color):
    for i, line in enumerate(text.split("\\n")):
        bbox = font.getbbox(line)
        w = bbox[2] - bbox[0]
        draw.text(((SIZE[0]-w)//2, y + i*int(font.size*1.3)), line, font=font, fill=color)

def draw_tag(draw, text, x, y):
    f = font(FONT_BOLD, 28)
    draw.rectangle([(x, y), (x+len(text)*17+20, y+44)], fill=ACCENT)
    draw.text((x+10, y+8), text, font=f, fill=WHITE)

def slide_capa(dados):
    img, draw = new_canvas()
    draw.ellipse([(540,200),(1140,800)], fill=CARD)
    draw.ellipse([(-60,300),(300,780)], fill=CARD)
    draw_tag(draw, dados.get("tag", "POST"), 80, 90)
    f_big = font(FONT_BOLD, 90)
    center_text(draw, dados.get("titulo", "Titulo"), 420, f_big, WHITE)
    f_sub = font(FONT_REG, 38)
    center_text(draw, dados.get("subtitulo", ""), 620, f_sub, LIGHTGRAY)
    draw_accent_bar(draw, y=970)
    f_handle = font(FONT_BOLD, 52)
    handle = dados.get("handle", "@usuario")
    bbox = f_handle.getbbox(handle)
    w = bbox[2] - bbox[0]
    draw.text(((SIZE[0]-w)//2, 985), handle, font=f_handle, fill=ACCENT)
    return img

def slide_conteudo(dados, num):
    img, draw = new_canvas()
    draw.ellipse([(800,50),(1150,400)], fill=CARD)
    f_num = font(FONT_BOLD, 160)
    draw.text((80, 60), str(num), font=f_num, fill=ACCENT)
    draw_accent_bar(draw, y=280)
    f_titulo = font(FONT_BOLD, 72)
    center_text(draw, dados.get("titulo", ""), 320, f_titulo, WHITE)
    f_corpo = font(FONT_REG, 42)
    center_text(draw, dados.get("corpo", ""), 520, f_corpo, LIGHTGRAY)
    draw_accent_bar(draw, y=970)
    f_handle = font(FONT_BOLD, 46)
    handle = dados.get("handle", "@usuario")
    bbox = f_handle.getbbox(handle)
    w = bbox[2] - bbox[0]
    draw.text(((SIZE[0]-w)//2, 985), handle, font=f_handle, fill=ACCENT)
    return img

def slide_cta(dados):
    img, draw = new_canvas()
    draw.ellipse([(540,200),(1140,800)], fill=CARD)
    draw.ellipse([(-60,300),(300,780)], fill=CARD)
    draw_accent_bar(draw, y=320)
    f_big = font(FONT_BOLD, 82)
    center_text(draw, dados.get("cta", "Siga para mais!"), 380, f_big, WHITE)
    f_sub = font(FONT_REG, 40)
    center_text(draw, dados.get("subtitulo", ""), 620, f_sub, LIGHTGRAY)
    draw_accent_bar(draw, y=970)
    f_handle = font(FONT_BOLD, 56)
    handle = dados.get("handle", "@usuario")
    bbox = f_handle.getbbox(handle)
    w = bbox[2] - bbox[0]
    draw.text(((SIZE[0]-w)//2, 985), handle, font=f_handle, fill=ACCENT)
    return img

def main():
    dados_raw = sys.argv[1] if len(sys.argv) > 1 else "{}"
    dados = json.loads(dados_raw)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    handle = dados.get("handle", "@usuario")
    slides_def = dados.get("slides", [])
    arquivos = []
    capa_dados = {"tag": dados.get("tag","POST"), "titulo": dados.get("titulo",""), "subtitulo": dados.get("subtitulo",""), "handle": handle}
    img = slide_capa(capa_dados)
    path = os.path.join(OUTPUT_DIR, "01_capa.jpg")
    img.save(path, "JPEG", quality=95)
    arquivos.append(path)
    print(f"Salvo: {path}")
    for i, slide in enumerate(slides_def):
        slide["handle"] = handle
        img = slide_conteudo(slide, i+1)
        path = os.path.join(OUTPUT_DIR, f"0{i+2}_slide.jpg")
        img.save(path, "JPEG", quality=95)
        arquivos.append(path)
        print(f"Salvo: {path}")
    cta_dados = {"cta": dados.get("cta","Siga para mais!"), "subtitulo": dados.get("cta_sub",""), "handle": handle}
    img = slide_cta(cta_dados)
    path = os.path.join(OUTPUT_DIR, f"0{len(slides_def)+2}_cta.jpg")
    img.save(path, "JPEG", quality=95)
    arquivos.append(path)
    print(f"Salvo: {path}")
    print(f"\nTotal: {len(arquivos)} slides em {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
