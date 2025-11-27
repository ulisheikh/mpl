# bot/states.py
# FSM holatlari: qo'shimcha holatlar keyinchalik kengaytiriladi.
from aiogram.fsm.state import State, StatesGroup

class StartStates(StatesGroup):
    choosing_language = State()
    choosing_mode = State()  # global or local

class EditDictStates(StatesGroup):
    waiting_for_lang = State()
    waiting_for_action = State()
    waiting_for_key = State()
    waiting_for_value = State()

class AdminStates(StatesGroup):
    waiting_for_command = State()
