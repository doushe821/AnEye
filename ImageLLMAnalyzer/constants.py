from pathlib import Path

DOCS_EXTENSIONS = [".pdf"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", "webp"]

TECHNICAL_PROMPT = """
Let's play a guessing game! What do you think this electronic component might be?

Make an educated guess based on:
- What it resembles
- Your electronics knowledge
- Similar things you've seen

Format your answer however you like. Just have fun with it!

Examples of what you could say:
"Hmm, this looks like it could be an Arduino Nano to me - small size, lots of pins, USB connector."

"I'm seeing something that reminds me of a Wi-Fi module. Maybe an ESP8266 or similar?"

"If I had to guess, I'd say this is some kind of power MOSFET in a TO-220 package."

"On the first line - leave your best guess in capital letters like this: [DEVICE]"
"""
IMAGE_DIR = Path("images/")
DOCS_DIR = Path("docs/")
MODEL_NAME="text-embedding-3-small"
