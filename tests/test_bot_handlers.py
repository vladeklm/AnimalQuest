# tests/test_bot_handlers.py

import pytest
from aiogram import types
from aiogram.types import Message, CallbackQuery

from bot.handlers.start import cmd_start
from bot.handlers.quiz import start_quiz, QUESTIONS
from bot.handlers.sharing import share_callback
from bot.handlers.feedback import start_feedback, receive_feedback
from bot.handlers.contact import contact_user

# Фейковый контекст состояний вместо реального FSMContext
class DummyState:
    def __init__(self):
        self.data = {}
        self.state = None

    async def clear(self):
        self.data = {}
        self.state = None

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return self.data

    async def set_state(self, state):
        self.state = state

@pytest.fixture
def fake_state():
    return DummyState()

@pytest.mark.asyncio
async def test_cmd_start(monkeypatch):
    responses = []

    async def fake_answer(self, text, reply_markup=None):
        responses.append(text)

    # Подменяем Message.answer
    monkeypatch.setattr(Message, "answer", fake_answer, raising=False)

    msg = Message(
        message_id=1,
        from_user=types.User(id=1, is_bot=False, first_name="Test"),
        chat=types.Chat(id=1, type="private"),
        date=0,
        text="/start",
    )
    await cmd_start(msg)

    assert responses, "Нет ответа на /start"
    # Проверяем, что в ответе содержится приветствие
    assert "Привет" in responses[0], f"Ожидалось 'Привет' в ответе, получили: {responses[0]}"

@pytest.mark.asyncio
async def test_quiz_start(fake_state, monkeypatch):
    sent = []
    async def fake_msg_answer(self, text, reply_markup=None):
        sent.append(text)
    async def fake_cb_answer(self, *args, **kwargs):
        # stub for callback.answer()
        pass

    # Мокаем методы Message.answer и CallbackQuery.answer
    monkeypatch.setattr(Message, "answer", fake_msg_answer, raising=False)
    monkeypatch.setattr(CallbackQuery, "answer", fake_cb_answer, raising=False)

    cb = CallbackQuery(
        id="1",
        from_user=types.User(id=1, is_bot=False, first_name="Test"),
        chat_instance="x",
        data="start_quiz",
        message=Message(
            message_id=2,
            from_user=types.User(id=1, is_bot=False, first_name="Test"),
            chat=types.Chat(id=1, type="private"),
            date=0,
            text=""
        )
    )
    await start_quiz(cb, fake_state)
    assert sent and QUESTIONS[0]["question"] in sent[0]

@pytest.mark.asyncio
async def test_share_callback(monkeypatch):
    out = []
    async def fake_msg_answer(self, text, parse_mode=None, reply_markup=None):
        out.append(text)
    async def fake_cb_answer(self, *args, **kwargs):
        pass

    # Мокаем методы Message.answer и CallbackQuery.answer
    monkeypatch.setattr(Message, "answer", fake_msg_answer, raising=False)
    monkeypatch.setattr(CallbackQuery, "answer", fake_cb_answer, raising=False)

    cb = CallbackQuery(
        id="2",
        from_user=types.User(id=1, is_bot=False, first_name="Test"),
        chat_instance="y",
        data="share_тигр",
        message=Message(
            message_id=3,
            from_user=types.User(id=1, is_bot=False, first_name="Test"),
            chat=types.Chat(id=1, type="private"),
            date=0,
            text=""
        )
    )
    await share_callback(cb)
    assert out and "Я прошёл викторину" in out[0]

@pytest.mark.asyncio
async def test_feedback_flow(fake_state, monkeypatch):
    received = []
    async def fake_answer(self, text, reply_markup=None):
        received.append(text)
    async def fake_cb_answer(self, *args, **kwargs):
        # заглушка для callback.answer()
        pass

    # Мокаем Message.answer
    monkeypatch.setattr(Message, "answer", fake_answer, raising=False)
    # Мокаем CallbackQuery.answer
    monkeypatch.setattr(CallbackQuery, "answer", fake_cb_answer, raising=False)

    # Старт флоу отзыв
    cb = CallbackQuery(
        id="3",
        from_user=types.User(id=1, is_bot=False, first_name="Test"),
        chat_instance="z",
        data="feedback",
        message=Message(
            message_id=4,
            from_user=types.User(id=1, is_bot=False, first_name="Test"),
            chat=types.Chat(id=1, type="private"),
            date=0,
            text=""
        )
    )
    await start_feedback(cb, fake_state)
    assert received and "Напишите" in received[0]

    # Завершение флоу отзыв
    msg = Message(
        message_id=5,
        from_user=types.User(id=1, is_bot=False, first_name="Test"),
        chat=types.Chat(id=1, type="private"),
        date=0,
        text="Отлично!"
    )
    await receive_feedback(msg, fake_state)
    assert any("Спасибо за ваш отзыв" in t for t in received)

@pytest.mark.asyncio
async def test_contact_user(monkeypatch):
    out = []
    async def fake_answer(self, text, reply_markup=None):
        out.append(text)
    async def fake_cb_answer(self, *args, **kwargs):
        # заглушка для callback.answer()
        pass

    # Мокаем Message.answer
    monkeypatch.setattr(Message, "answer", fake_answer, raising=False)
    # Мокаем CallbackQuery.answer
    monkeypatch.setattr(CallbackQuery, "answer", fake_cb_answer, raising=False)

    cb = CallbackQuery(
        id="4",
        from_user=types.User(id=1, is_bot=False, first_name="Test"),
        chat_instance="w",
        data="contact_тигр",
        message=Message(
            message_id=6,
            from_user=types.User(id=1, is_bot=False, first_name="Test"),
            chat=types.Chat(id=1, type="private"),
            date=0,
            text=""
        )
    )
    await contact_user(cb)
    # Проверяем обновлённый текст из bot/handlers/contact.py
    assert out, "Нет ответа на контакт"
    assert "Ваш запрос отправлен сотруднику зоопарка" in out[0], (
        f"Ожидалось упоминание 'Ваш запрос отправлен сотруднику зоопарка', получили: {out[0]}"
    )
