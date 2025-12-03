from pathlib import Path

DOCS_EXTENSIONS = [".pdf"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", "webp"]

TECHNICAL_PROMPT = "\n".join([
    "Please analyze this electronic component and identify it based on visible markings.",
    "If you can clearly see part numbers, manufacturer logos, or other identifying marks, provide:",
    "1. The official device name in brackets on the first line: [DEVICE_NAME]",
    "2. Details about the component",
    "",
    "If you cannot confidently identify the device from visible markings, start with the most suitable device.",
    "",
    "Guidelines for analysis:",
    "- Focus on visible text, symbols, and standardized markings",
    "- Avoid speculation based on appearance alone",
    "- If part numbers or manufacturer logos are visible, try to identify the specific component",
    "",
    "When you identify a device, please include:",
    "• Full part number (if visible)",
    "• Manufacturer (if identifiable)",
    "• Package type (if discernible)",
    "• Key specifications that can be determined from markings",
    "",
    "Example format when a device is identified:",
    "[STM32F407VGT6]",
    "• Full part number: STM32F407VGT6",
    "• Manufacturer: STMicroelectronics",
    "• Package type: LQFP-100",
    "• Key specs: ARM Cortex-M4, 168 MHz, 1MB Flash"
])
IMAGE_DIR = Path("images/")
DOCS_DIR = Path("docs/")
MODEL_NAME="text-embedding-3-small"
