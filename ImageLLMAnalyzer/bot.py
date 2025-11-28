import os
import asyncio
import shutil
from pathlib import Path
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# === Настройки из .env ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS_RAW = os.getenv("CHAT_IDS", "")
WATCH_DIR_STR = os.getenv("WATCH_DIR", "./prompts")
IMAGES_DIR_STR = os.getenv("IMAGES_DIR", "./processed/img")      # ← новая переменная
PROCESSED_DIR_STR = os.getenv("PROCESSED_DIR", "./prompt_succeed")
CHECK_INTERVAL = 5

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

def find_image_for_txt(txt_path: Path) -> Optional[Path]:
    """Ищет изображение с тем же stem в IMAGES_DIR."""
    stem = txt_path.stem  # например: capture_20251128_182611_response
    for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
        img_path = IMAGES_DIR / (stem + ext)
        if img_path.is_file():
            return img_path
    return None

def get_txt_files():
    return sorted(WATCH_DIR.glob("*.txt"))

async def send_file_pair(txt_path: Path, img_path: Path | None):
    """Отправляет .txt и (опционально) изображение из IMAGES_DIR."""
    try:
        content = txt_path.read_text(encoding='utf-8')
    except Exception as e:
        content = f"[Ошибка чтения {txt_path.name}]: {e}"

    successfully_sent_to_all = True

    for chat_id in CHAT_IDS:
        try:
            # Отправка текста
            if len(content) <= 4096:
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"📄 <b>{txt_path.name}</b>\n\n{content}",
                    parse_mode="HTML"
                )
            else:
                preview = content[:4000] + "\n\n[... полный текст во вложении]"
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"📄 <b>{txt_path.name}</b>\n\n{preview}",
                    parse_mode="HTML"
                )
                with open(txt_path, 'rb') as f:
                    await bot.send_document(chat_id=chat_id, document=f)

            # Отправка изображения, если найдено
            if img_path:
                with open(img_path, 'rb') as img_f:
                    await bot.send_photo(
                        chat_id=chat_id,
                        photo=img_f,
                        caption=f"🖼 {img_path.name}"
                    )

            print(f"✅ Отправлено в чат {chat_id}: {txt_path.name}" + (f" + {img_path.name}" if img_path else ""))
        except TelegramError as e:
            print(f"❌ Ошибка отправки в чат {chat_id}: {e}")
            successfully_sent_to_all = False

    return successfully_sent_to_all

async def process_and_move(txt_path: Path, img_path: Path | None):
    success = await send_file_pair(txt_path, img_path)

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
            await process_and_move(txt_file, img_file)
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    print("✅ Бот запущен.")
    print(f"📥 TXT из: {WATCH_DIR}")
    print(f"🖼 IMG из: {IMAGES_DIR}")
    print(f"📤 Всё в: {PROCESSED_DIR}")
    print(f"👥 Получатели: {CHAT_IDS}")
    await watch_folder()

if __name__ == "__main__":
    asyncio.run(main())
