import logging
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Also print to console during development
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logger = logging.getLogger(__name__)
logger.addHandler(console)