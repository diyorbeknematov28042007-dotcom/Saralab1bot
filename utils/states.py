from aiogram.fsm.state import State, StatesGroup

class AddChannel(StatesGroup):
    waiting_channel_id = State()
    waiting_channel_link = State()
    waiting_channel_name = State()

class NewProject(StatesGroup):
    waiting_name = State()
    waiting_post = State()
    waiting_channel_info = State()
    waiting_auto_link = State()
    waiting_threshold = State()
    waiting_auto_url = State()
    confirm = State()

class Broadcast(StatesGroup):
    waiting_content = State()
    confirm = State()
