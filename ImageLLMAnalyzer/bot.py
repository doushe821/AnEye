import os
import time
import asyncio
import shutil  # ← добавили
from pathlib import Path
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv

load_dotenv()

# === НАСТРОЙКИ ИЗ .env ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS_RAW = os.getenv("CHAT_IDS", "")
WATCH_DIR_STR = os.getenv("WATCH_DIR", "./prompts")
PROCESSED_DIR_STR = os.getenv("PROCESSED_DIR", "./prompt_succeed")  # ← новая переменная
CHECK_INTERVAL = 5

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не задан в .env")

CHAT_IDS = [int(cid.strip()) for cid in CHAT_IDS_RAW.split(",") if cid.strip()]
WATCH_DIR = Path(WATCH_DIR_STR).resolve()
PROCESSED_DIR = Path(PROCESSED_DIR_STR).resolve()

# Создаём директории при старте
WATCH_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

bot = Bot(token=BOT_TOKEN)

def get_txt_files():
    return sorted(WATCH_DIR.glob("*.txt"))

async def send_file_content(file_path: Path):
    """Отправляет файл и перемещает его в PROCESSED_DIR после успеха."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        content = f"[Ошибка чтения файла {file_path.name}]: {e}"

    successfully_sent_to_all = True
    for chat_id in CHAT_IDS:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=f"📄 <b>{file_path.name}</b>\n\n{content}",
                parse_mode="HTML"
            )
            print(f"Отправлено в чат {chat_id}: {file_path.name}")
        except TelegramError as e:
            print(f"Ошибка отправки в чат {chat_id}: {e}")
            successfully_sent_to_all = False  # не отправлено хотя бы одному — не перемещаем

    # Перемещаем файл, только если он был успешно отправлен всем
    if successfully_sent_to_all:
        target_path = PROCESSED_DIR / file_path.name
        try:
            shutil.move(str(file_path), str(target_path))
            print(f"✅ Перемещено: {file_path} → {target_path}")
        except Exception as e:
            print(f"❌ Ошибка перемещения {file_path}: {e}")
    else:
        print(f"⚠️ Файл {file_path} не перемещён: не все получатели получили сообщение.")

async def watch_folder():
    """Проверяет папку каждые CHECK_INTERVAL секунд."""
    while True:
        files = get_txt_files()
        for f in files:
            await send_file_content(f)
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    print("✅ Бот запущен.")
    print(f"📥 Следим за: {WATCH_DIR}")
    print(f"📤 Обработанные: {PROCESSED_DIR}")
    print(f"👥 Получатели: {CHAT_IDS}")
    await watch_folder()

if __name__ == "__main__":
    asyncio.run(main())
