import sys
import os
from loguru import logger

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Remove default handler
logger.remove()

# Add a file handler for detailed rotation logs
logger.add(
    "logs/writing_agent.log",
    rotation="10 MB",
    retention="1 week",
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Add standard error handler for warnings and above without cluttering standard CLI out
logger.add(sys.stderr, level="WARNING")

def get_logger():
    return logger
