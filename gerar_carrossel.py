"""Gera 5 slides de carrossel sobre consórcio para Instagram (1080x1080)."""
import os
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD   = "/Library/Fonts/Arial Bold.ttf"
FONT_REG    = "/System/Library/Fonts/SFNS.ttf"
OUTPUT_DIR  = "/Users/michaelsoares/claude-instagram/slides"

# Paleta
BG        = "#0D1B2A"
ACCENT    = "#E8A020"
WHITE     = "#FFFFFF"
LIGHTGRAY = "#B0C4DE"
CARD      = "#1A2F45"
SIZE      = (1080, 1080)


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def new_canvas():
    img = Image.new("RGB", SIZE, BG)
    return img, ImageDraw.Draw(img)


def draw_accent_bar(draw, y=80, width=120, thick=6):
    draw.rectangle([(SIZE[0]//2 - width//2, y), (SIZE[0]//2 + width//2, y + thick)], fill=ACCENT)


def center_text(draw, text, y, fnt, color=WHITE, line_spacing=10):
    lines = text.split("\n")
    total_h = sum(fnt.getbbox(l)[3] - fnt.getbbox(l)[1] for l in lines) + line_spacing * (len(lines) - 1)
    cur_y = y - total_h // 2
    for line in lines:
        bbox = fnt.getbbox(line)
        w = bbox[2] - bbox[0]
        draw.text(((SIZE[0] - w) // 2, cur_y), line, font=fnt, fill=color)
        cur_y += bbox[3] - bbox[1] + line_spacing


def draw_tag(draw, text, x, y):
    f = font(FONT_BOLD, 28)
    bbox = f.getbbox(text)
    w, h = bbox[2] - bbox[0] + 32, bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=ACCENT)
    draw.text((x + 16, y + 8), text, font=f, fill=BG)


def slide1_capa():
    img, draw = new_canvas()

    # Círculo decorativo de fundo
    draw.ellipse([(540, 200), (1140, 800)], fill=CARD)
    draw.ellipse([(-60, 300), (300, 780)], fill=CARD)

    # Topo
    draw_tag(draw, "CONSÓRCIO", 80, 90)

    # Título principal
    f_big = font(FONT_BOLD, 108)
    center_text(draw, "Realize\nseu sonho\nsem juros", 500, f_big, WHITE)

    # Subtítulo
    f_sub = font(FONT_REG, 40)
    center_text(draw, "O jeito inteligente de conquistar\nbens e serviços", 820, f_sub, LIGHTGRAY)

    # Rodapé
    draw_accent_bar(draw, y=970)
    f_handle = font(FONT_BOLD, 32)
    bbox = f_handle.getbbox("@michaelsoaares_")
    w = bbox[2] - bbox[0]
    draw.text(((SIZE[0] - w) // 2, 985), "@michaelsoaares_", font=f_handle, fill=ACCENT)

    return img


def slide2_oque_e():
    img, draw = new_canvas()

    # Número do slide
    draw_tag(draw, "01", 60, 60)

    # Título
    f_title = font(FONT_BOLD, 70)
    draw.text((60, 160), "O QUE É", font=f_title, fill=ACCENT)
    draw.text((60, 240), "CONSÓRCIO?", font=f_title, fill=WHITE)
    draw.rectangle([(60, 340), (200, 348)], fill=ACCENT)

    # Definição em card
    card_y = 390
    draw.rounded_rectangle([(60, card_y), (1020, card_y + 180)], radius=16, fill=CARD)
    f_body = font(FONT_REG, 38)
    draw.text((90, card_y + 30), "Um grupo de pessoas que contribuem\nmensalmente para um fundo comum\ncom o objetivo de adquirir bens.", font=f_body, fill=WHITE)

    # Destaques
    items = [
        ("💰", "Sem juros", "Apenas taxa de administração"),
        ("🏆", "Regulamentado", "Pelo Banco Central do Brasil"),
        ("📋", "Planejamento", "Ideal para objetivos de médio e longo prazo"),
    ]
    y = 620
    for icon, title, desc in items:
        draw.rounded_rectangle([(60, y), (1020, y + 100)], radius=12, fill=CARD)
        f_icon = font(FONT_REG, 44)
        draw.text((90, y + 28), icon, font=f_icon, fill=WHITE)
        f_it = font(FONT_BOLD, 36)
        draw.text((160, y + 16), title, font=f_it, fill=ACCENT)
        f_id = font(FONT_REG, 30)
        draw.text((160, y + 56), desc, font=f_id, fill=LIGHTGRAY)
        y += 120

    return img


def slide3_como_funciona():
    img, draw = new_canvas()

    draw_tag(draw, "02", 60, 60)

    f_title = font(FONT_BOLD, 70)
    draw.text((60, 160), "COMO", font=f_title, fill=WHITE)
    draw.text((60, 240), "FUNCIONA?", font=f_title, fill=ACCENT)
    draw.rectangle([(60, 340), (200, 348)], fill=ACCENT)

    passos = [
        ("1", "Entre em um grupo", "Escolha o valor da carta de crédito"),
        ("2", "Pague a parcela mensal", "Valor fixo e acessível, sem juros"),
        ("3", "Seja contemplado", "Por sorteio ou dando um lance"),
        ("4", "Use a carta de crédito", "Compre à vista e negocie desconto"),
    ]

    y = 380
    for num, titulo, desc in passos:
        # Número em círculo
        cx, cy = 100, y + 50
        draw.ellipse([(cx - 40, cy - 40), (cx + 40, cy + 40)], fill=ACCENT)
        f_num = font(FONT_BOLD, 42)
        bbox = f_num.getbbox(num)
        nw = bbox[2] - bbox[0]
        draw.text((cx - nw // 2, cy - 28), num, font=f_num, fill=BG)

        # Linha conectora
        if num != "4":
            draw.rectangle([(cx - 2, cy + 40), (cx + 2, cy + 100)], fill=ACCENT)

        f_t = font(FONT_BOLD, 36)
        draw.text((165, y + 18), titulo, font=f_t, fill=WHITE)
        f_d = font(FONT_REG, 30)
        draw.text((165, y + 60), desc, font=f_d, fill=LIGHTGRAY)
        y += 150

    return img


def slide4_vantagens():
    img, draw = new_canvas()

    draw_tag(draw, "03", 60, 60)

    f_title = font(FONT_BOLD, 70)
    draw.text((60, 160), "VANTAGENS DO", font=f_title, fill=WHITE)
    draw.text((60, 240), "CONSÓRCIO", font=f_title, fill=ACCENT)
    draw.rectangle([(60, 340), (200, 348)], fill=ACCENT)

    vantagens = [
        ("✅", "SEM JUROS",         "Economia real comparado ao financiamento"),
        ("✅", "PARCELAS MENORES",   "Até 60% mais barato que o financiamento"),
        ("✅", "USA O FGTS",         "Pode usar para dar lances ou amortizar"),
        ("✅", "CARTA COMO DINHEIRO","Poder de compra à vista na negociação"),
        ("✅", "VÁRIOS SEGMENTOS",   "Imóvel, automóvel, serviços e muito mais"),
    ]

    y = 390
    for icon, titulo, desc in vantagens:
        f_i = font(FONT_REG, 38)
        draw.text((60, y + 8), icon, font=f_i, fill=ACCENT)
        f_t = font(FONT_BOLD, 34)
        draw.text((120, y), titulo, font=f_t, fill=WHITE)
        f_d = font(FONT_REG, 28)
        draw.text((120, y + 42), desc, font=f_d, fill=LIGHTGRAY)
        draw.rectangle([(60, y + 95), (1020, y + 97)], fill=CARD)
        y += 115

    return img


def slide5_cta():
    img, draw = new_canvas()

    # Círculos decorativos
    draw.ellipse([(-100, -100), (400, 400)], fill=CARD)
    draw.ellipse([(680, 680), (1200, 1200)], fill=CARD)

    # Destaque central
    draw.rounded_rectangle([(80, 200), (1000, 540)], radius=24, fill=CARD)

    f_q = font(FONT_BOLD, 62)
    center_text(draw, "PRONTO PARA\nREALIZAR SEU\nSONHO?", 380, f_q, WHITE)

    # Linha dourada
    draw.rectangle([(200, 560), (880, 566)], fill=ACCENT)

    # CTA
    f_cta = font(FONT_REG, 42)
    center_text(draw, "Me chame no Direct!\nVou te ajudar a escolher\no melhor consórcio para você.", 700, f_cta, LIGHTGRAY)

    # Handle
    f_handle = font(FONT_BOLD, 58)
    center_text(draw, "@michaelsoaares_", 900, f_handle, ACCENT)

    draw_accent_bar(draw, y=970)

    return img


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    slides = [
        ("01_capa.jpg",        slide1_capa()),
        ("02_oque_e.jpg",      slide2_oque_e()),
        ("03_como_funciona.jpg", slide3_como_funciona()),
        ("04_vantagens.jpg",   slide4_vantagens()),
        ("05_cta.jpg",         slide5_cta()),
    ]
    for nome, img in slides:
        path = os.path.join(OUTPUT_DIR, nome)
        img.save(path, "JPEG", quality=95)
        print(f"  Salvo: {path}")
    print(f"\nTotal: {len(slides)} slides em {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
