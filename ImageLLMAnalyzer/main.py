from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import base64

import os
import questionary


load_dotenv()

API_KEY = os.getenv("NANO_BANANA_API_KEY")
IMAGE_DIR = Path("images/")
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", "webp"]

TECHNICAL_PROMPT = "I need technical information about what is on photo. You need to provide valuable information for an engineer."


def get_img(directory: Path):
    if not directory.exists():
        raise FileNotFoundError(f"dir not found {directory}")

    images = [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]

    return sorted(images)

def choose_image():
    images = get_img(IMAGE_DIR)
    images_str = [str(f.relative_to(IMAGE_DIR)) for f in images]
    image_select = questionary.select("choose an image from images dir",
                               choices=images_str).ask()
    if not image_select:
        return []
    for img_path in images:
        if img_path.name == image_select:
            return str(img_path.resolve())

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        mime_type = "image/jpeg"
        if image_path.lower().endswith(".png"):
            mime_type = "image/png"
        elif image_path.lower().endswith(".webp"):
            mime_type = "image/webp"

        encoded = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:{mime_type};base64,{encoded}"



def get_ai_response(image_path):

    image_url = encode_image(image_path)

    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    )
    completion = client.chat.completions.create(

    extra_body={},
    model="google/gemini-2.5-flash-image",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": TECHNICAL_PROMPT
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"{image_url}"
            }
            }
        ]
        }
    ]
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    selected_image = choose_image()
    response = get_ai_response(selected_image)
    print(response)
