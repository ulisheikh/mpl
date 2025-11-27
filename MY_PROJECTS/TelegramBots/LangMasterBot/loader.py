# bot/loader.py
# Bot va Dispatcher yaratadi. Bu faylni boshqa modullarda import qilib ishlatasiz.
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot instance (use throughout the project)
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")

# Simple memory storage for FSM (for prototyping). For production use Redis/DB storage.
storage = MemoryStorage()

# Dispatcher
dp = Dispatcher(storage=storage)
