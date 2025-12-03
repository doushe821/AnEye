from pathlib import Path

DOCS_EXTENSIONS = [".pdf"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", "webp"]

TECHNICAL_PROMPT =  "\n".join(["ON THE FIRST LINE OF YOUR ANSWER PLACE THE OFFICIAL NAME OF THE DEVICE IN FORMAT [NAME_OF_THE_DEVICE].",
"IF THE DEVICE CANNOT BE IDENTIFIED WITH HIGH CONFIDENCE FROM VISIBLE MARKINGS (e.g., part numbers, logos, clear labels), OUTPUT [UNKNOW DEVICE].",
"You are an expert hardware engineer. Analyze ONLY visible, legible text, symbols, or standardized markings on the component.",
"- DO NOT speculate based on shape, size, color, or 'appearance'.",
"- DO NOT assume type (e.g., 'likely RAM', 'probably a sensor').",
"- If clear part numbers (e.g., 'MT40A512M16', 'STM32F407VGT6') or manufacturer logos (e.g., Intel, TI, Samsung) are visible, identify the exact component.",
"- Provide:",
"  • Full part number",
"  • Manufacturer",
"  • Package type (if visible)",
"  • Key specs ONLY if decodable from markings (e.g., 'DDR4-3200', '3.3V', 'QFN-48')",
"- If no legible markings exist → [UNKNOW DEVICE] and stop."])

IMAGE_DIR = Path("images/")
DOCS_DIR = Path("docs/")
MODEL_NAME="text-embedding-3-small"
