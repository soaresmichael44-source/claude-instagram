import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
API_VERSION = os.getenv("META_API_VERSION", "v21.0")
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def criar_container_item(image_url: str) -> str:
    """Cria um container de imagem para uso em carrossel."""
    resp = requests.post(
        f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media",
        params={
            "image_url": image_url,
            "is_carousel_item": True,
            "access_token": ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    return resp.json()["id"]


def criar_container_carrossel(children_ids: list[str], caption: str) -> str:
    """Cria o container principal do carrossel com as imagens filhas."""
    resp = requests.post(
        f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media",
        params={
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
            "access_token": ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    return resp.json()["id"]


def aguardar_processamento(container_id: str, tentativas: int = 10, intervalo: int = 5):
    """Aguarda o container estar pronto antes de publicar."""
    for _ in range(tentativas):
        resp = requests.get(
            f"{BASE_URL}/{container_id}",
            params={"fields": "status_code", "access_token": ACCESS_TOKEN},
        )
        resp.raise_for_status()
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Erro no processamento do container {container_id}")
        time.sleep(intervalo)
    raise TimeoutError(f"Container {container_id} não ficou pronto a tempo")


def publicar_carrossel(container_id: str) -> str:
    """Publica o carrossel e retorna o ID da publicação."""
    resp = requests.post(
        f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media_publish",
        params={"creation_id": container_id, "access_token": ACCESS_TOKEN},
    )
    resp.raise_for_status()
    return resp.json()["id"]


def main(image_urls: list[str], caption: str):
    if not INSTAGRAM_ACCOUNT_ID or not ACCESS_TOKEN:
        print("Erro: defina INSTAGRAM_BUSINESS_ID e INSTAGRAM_ACCESS_TOKEN no arquivo .env")
        sys.exit(1)

    if len(image_urls) < 2 or len(image_urls) > 10:
        print("Erro: o carrossel precisa ter entre 2 e 10 imagens")
        sys.exit(1)

    print(f"Criando {len(image_urls)} containers de imagem...")
    children_ids = [criar_container_item(url) for url in image_urls]

    print("Criando container do carrossel...")
    carrossel_id = criar_container_carrossel(children_ids, caption)

    print("Aguardando processamento...")
    aguardar_processamento(carrossel_id)

    print("Publicando...")
    post_id = publicar_carrossel(carrossel_id)
    print(f"Carrossel publicado com sucesso! ID: {post_id}")


if __name__ == "__main__":
    # Edite as URLs e legenda abaixo ou adapte para receber como argumentos
    IMAGENS = [
        "https://example.com/imagem1.jpg",
        "https://example.com/imagem2.jpg",
        "https://example.com/imagem3.jpg",
    ]
    LEGENDA = "Meu carrossel publicado via API 🚀"

    main(IMAGENS, LEGENDA)
