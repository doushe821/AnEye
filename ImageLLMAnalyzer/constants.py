from pathlib import Path

DOCS_EXTENSIONS = [".pdf"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", "webp"]
TECHNICAL_PROMPT =  "ON THE FIRST LINE OF YOUR ANSWER PLACE THE OFFICIAL NAME OF THE DEVICE. " \
"IF YOU DON'T KNOW THE DEVICE, LET THE FIRST LINE BE 'UNKNOW DEVICE'" \
"I need technical information about what is on photo. " \
"You need to provide valuable information for an engineer." \

"Then start your technical answer."
IMAGE_DIR = Path("images/")
DOCS_DIR = Path("docs/")
MODEL_NAME="text-embedding-3-small"
