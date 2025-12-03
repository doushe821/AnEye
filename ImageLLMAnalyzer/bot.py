import os
import asyncio
import shutil
from pathlib import Path
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
from typing import Optional, List
import re
import html
from constants import *
from difflib import SequenceMatcher

load_dotenv()

# === Настройки из .env ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS_RAW = os.getenv("CHAT_IDS", "")
WATCH_DIR_STR = os.getenv("WATCH_DIR", "./prompts")
IMAGES_DIR_STR = os.getenv("IMAGES_DIR", "./processed/img")      # ← новая переменная
PROCESSED_DIR_STR = os.getenv("PROCESSED_DIR", "./prompt_succeed")
CHECK_INTERVAL = 5
FILENAME_THRESHOLD = float(0.4)

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не задан в .env")

CHAT_IDS = [int(cid.strip()) for cid in CHAT_IDS_RAW.split(",") if cid.strip()]
WATCH_DIR = Path(WATCH_DIR_STR).resolve()
IMAGES_DIR = Path(IMAGES_DIR_STR).resolve()             # ← новая директория
PROCESSED_DIR = Path(PROCESSED_DIR_STR).resolve()

# Создаём все нужные папки
WATCH_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

bot = Bot(token=BOT_TOKEN)


def similar(a: str, b: str) -> float:
    """Возвращает коэффициент схожести между двумя строками (0.0-1.0)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_image_for_txt(txt_path: Path) -> Optional[Path]:
    stem = txt_path.stem.rstrip("_response")
    print(stem)
    for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
        img_path = IMAGES_DIR / (stem + ext)
        print(img_path)
        if img_path.is_file():
            return img_path
    return None

def find_pdf_for_txt(txt_path: Path) -> Optional[Path]:
    """Находит PDF файл в директории docs по первой строке TXT файла"""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                return None
            component_names = []
            first_line = lines[0].strip()
            if not first_line:
                return None

            import re
            for line in lines:
                match = re.search(r'\[([^\]]+)\]', line)
                if match:
                    search_term = match.group(1).strip()
                    component_names.append(search_term)
                else:
                    search_term = first_line.strip()

            docs_dir = Path("docs")
            if not docs_dir.exists():
                print("docs_dir doesn't exist")
                return None
            pdf_paths = list()
            print(list(docs_dir.glob("*.pdf")))
            best_score = 0
            print("\n".join(lines))
            for component in component_names:
                for pdf_file in docs_dir.glob("*.pdf"):
                    pdf_name = pdf_file.stem
                    score = similar(component, pdf_name)
                    print(f"PDF_FILE - {pdf_name} => SCORE - {score}")

                    if score >= 0.95:
                        print(f"📕 FOUND APPROPRIATE DOCUMENT {pdf_name}")
                        pdf_paths.append([pdf_file, score])

                    if score > best_score and score > FILENAME_THRESHOLD:
                        best_score = score
                        best_match = pdf_file
                        pdf_paths.append([best_match, best_score])


            print(f"BEST_SCORE IS - {best_score}")
            print(f"BEST_MATCH IS - {best_match}")
            if best_score >= FILENAME_THRESHOLD:
                print(f"📕 Best Document found is {best_match}")
                pdf_paths.append([best_match, best_score])

        if (pdf_paths):
            return max(pdf_paths, key=lambda x: x[1])

    except Exception as e:
        print(f"Ошибка при поиске PDF для {txt_path}: {e}")

    return None

def get_txt_files():
    return sorted(WATCH_DIR.glob("*.txt"))

def escape_markdown_v2(text: str) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def send_file_pair(txt_path: Path, img_path: Optional[Path], pdf_path: Optional[Path]):
    try:
        content = txt_path.read_text(encoding='utf-8')
    except Exception as e:
        content = f"[Ошибка чтения {txt_path.name}]: {e}"

    successfully_sent_to_all = True

    for chat_id in CHAT_IDS:
        try:
            safe_name = html.escape(txt_path.name)
            safe_content = html.escape(content)
            if len(content) <= 4096:


                await bot.send_message(
                    chat_id=chat_id,
                    text=f"📄 <b>{safe_name}</b>\n\n{safe_content}",
                    parse_mode="HTML"
                )
            else:
                preview = safe_content[:4000] + "\n\n[... полный текст во вложении]"
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"📄 <b>{safe_name}</b>\n\n{preview}",
                    parse_mode="HTML"
                )
                with open(txt_path, 'rb') as f:
                    await bot.send_document(chat_id=chat_id, document=f)

            if img_path:
                with open(img_path, 'rb') as img_f:
                    await bot.send_photo(
                        chat_id=chat_id,
                        photo=img_f,
                        caption=f"🖼 {img_path.name}"
                    )
            if pdf_path:
                with open(pdf_path, 'rb') as pdf_f:
                    await bot.send_document(
                        chat_id=chat_id,
                        document=pdf_f,
                        filename=pdf_path.name,
                        caption=f"📄 {pdf_path.name}"
                        )
                    print(f"✅ PDF отправлен: {pdf_path.name}")

            print(f"✅ Отправлено в чат {chat_id}: {txt_path.name}" + (f" + {img_path.name}" if img_path else ""))
        except TelegramError as e:
            print(f"❌ Ошибка отправки в чат {chat_id}: {e} {content}")
            successfully_sent_to_all = False

    return successfully_sent_to_all


async def process_and_move(txt_path: Path, img_path: Optional[Path], pdf_file : Optional[Path]):
    success = await send_file_pair(txt_path, img_path, pdf_file)

    if success:
        # Перемещаем .txt из WATCH_DIR → PROCESSED_DIR
        shutil.move(str(txt_path), str(PROCESSED_DIR / txt_path.name))
        print(f"📁 Перемещён TXT: {txt_path.name}")

        # Перемещаем изображение из IMAGES_DIR → PROCESSED_DIR (если есть)
        if img_path:
            shutil.move(str(img_path), str(PROCESSED_DIR / img_path.name))
            print(f"🖼 Перемещено IMG: {img_path.name}")
    else:
        print(f"⚠️ Не перемещено: ошибка отправки для {txt_path.name}")

async def watch_folder():
    while True:
        for txt_file in get_txt_files():
            img_file = find_image_for_txt(txt_file)
            pdf_file = find_pdf_for_txt(txt_file)
            await process_and_move(txt_file, img_file, pdf_file)
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    print("✅ Бот запущен.")
    print(TECHNICAL_PROMPT)
    print(f"📥 TXT из: {WATCH_DIR}")
    print(f"🖼 IMG из: {IMAGES_DIR}")
    print(f"📤 Всё в: {PROCESSED_DIR}")
    print(f"👥 Получатели: {CHAT_IDS}")
    await asyncio.gather(
        watch_folder(),
    )

if __name__ == "__main__":
    asyncio.run(main())
