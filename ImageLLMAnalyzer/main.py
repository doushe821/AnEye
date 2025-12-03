from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import base64
from constants import *
# import chromadb
# from transformers import AutoModel
# from chromadb.config import Settings
# from chromadb.utils import embedding_functions
# from sentence_transformers import SentenceTransformer
# from pypdf import PdfReader
import time
import logging

import os
import questionary

# === Logging setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("NANO_BANANA_API_KEY")

# class RagAgent():
#         def __init__(self):
#             # self.model = SentenceTransformer(MODEL_NAME)
#             self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY,)
#             self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
#             sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
#             model_name="sentence-transformers/all-MiniLM-L6-v2")
#             # self.model = AutoModel.from_pretrained("jinaai/jina-embeddings-v3", trust_remote_code=True)
#             self.collection = self.chroma_client.create_collection(
#                 name="AnEyeCollection",
#                 embedding_function=sentence_transformer_ef
#                 )
#
#         def get_text(self, file_path: Path):
#             reader = PdfReader(file_path)
#             text = [page.extract_text() for page in reader.pages]
#             return " ".join(text)
#
#         def cut_into_chunks(self, text: str, chunk_size, chunk_overlap):
#             if (chunk_size < chunk_overlap):
#                 raise RagError("chunk_size < chunk_overlap (please try other values)")
#             text_array = []
#             text_length = len(text)
#
#             for i in range(0, text_length, chunk_size):
#                 if (i + chunk_size + chunk_overlap < text_length and i - chunk_overlap > 0):
#                     text_array.append(text[i-chunk_overlap:i+chunk_size+chunk_overlap])
#                 elif (i - chunk_overlap < 0 and i + chunk_size + chunk_overlap < text_length):
#                     text_array.append(text[0:i+chunk_size+chunk_overlap])
#                 elif (i + chunk_size + chunk_overlap >= text_length and i - chunk_overlap > 0):
#                     text_array.append(text[i-chunk_overlap:text_length])
#                 else:
#                     text_array.append(text)
#             return text_array
#
#         def load_to_db(self, path : Path):
#             if not Path(path).exists():
#                 return RagError("Not a path...")
#             try:
#                 for document in path.iterdir():
#                     file_text = self.get_text(document)
#                     chunked = self.cut_into_chunks(file_text, 1000, 100)
#                     ids = [f"{document.name}_{i}" for i in range(len(chunked))]
#                     self.collection.add(
#                         documents=chunked,
#                         ids=ids,
#
#                         )
#                 print("Successfully added documents to RAG")
#             except Exception as e:
#                 print(f"Got error {e} for {path}")
#
# class RagError(Exception):
#     def __init__(self, message):
#         self.message = message
#         super().__init__(self.message)
#

# ===========================================/


def get_docs(directory: Path):
    if not directory.exists():
        raise FileNotFoundError(f"dir not found {directory}")

    docs = [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in DOCS_EXTENSIONS]
    return docs


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
    model="google/gemini-3-pro-image-preview",
    messages=[
        {
            "role": "system",
            "content": "You are a hardware identification assistant that strictly follows formatting rules. You only identify components based on visible markings."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": TECHNICAL_PROMPT.strip()
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }
    ],
    temperature=0.0,
    max_tokens=500
    )
    return completion.choices[0].message.content

def process_new_images(image_dir: Path, processed_dir: Path, prompts: Path):
    images = get_img(image_dir)
    for img_path in images:
        try:
            logger.info(f"Processing image: {img_path}")
            response = get_ai_response(str(img_path))
            logger.info(f"AI Response for {img_path.name}: {response}")

            with open(prompts / f"{img_path.stem}_response.txt", "w") as f:
                f.write(response)

            new_path = processed_dir / img_path.name
            img_path.rename(new_path)
            logger.info(f"Moved {img_path} to {new_path}")
        except Exception as e:
            logger.error(f"Failed to process {img_path}: {e}")


if __name__ == "__main__":

    image_dir = Path("uploads")
    processed = Path("processed")
    prompts = Path("processed/prompts")
    processed_img = Path("processed/img")
    image_dir.mkdir(exist_ok=True)
    processed.mkdir(exist_ok=True)
    prompts.mkdir(exist_ok=True)
    processed_img.mkdir(exist_ok=True)

    # processed_dir =
    # agent = RagAgent()
    # agent.load_to_db(Path("docs"))
    # selected_image = choose_image()

    while True:
        process_new_images(image_dir, processed_img, prompts)
        time.sleep(1)  # Wait 10 seconds before next check

