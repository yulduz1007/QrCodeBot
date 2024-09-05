import asyncio
import logging
import sys
from aiogram.types import KeyboardButton
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup
from PIL import Image
from sqlalchemy import select, insert, update, delete

from Db.config import QrCode, session, User, engine

dp = Dispatcher()


class QrCodeState(StatesGroup):
    fullname = State()
    phone_number = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    qrcode_id = message.text.split()[-1]
    query1 = select(QrCode).where(QrCode.id == qrcode_id)
    qr_code = session.execute(query1).scalar()
    print(qr_code.is_active)
    if qr_code.is_active=="true":
        await message.answer(f"Hello {message.from_user.full_name} Please, enter your name: ")
        await state.set_state(QrCodeState.fullname)
        query = (
            update(QrCode).
            where(QrCode.id == qrcode_id).
            values(is_active=False)
        )
        with engine.connect() as connection:
            connection.execute(query)
            connection.commit()

    else:
        await message.answer(f"Sorry, this qr_code already entered, {html.bold(message.from_user.full_name)}!")


@dp.message(QrCodeState.fullname)
async def fullname_handler(message: Message, state: FSMContext) -> None:
    phone_button = KeyboardButton(text="Send phone number", request_contact=True)
    keyboard_markup = ReplyKeyboardMarkup(
        keyboard=[[phone_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    full_name = message.text
    await state.update_data({"full_name": full_name})
    await state.set_state(QrCodeState.phone_number)
    await message.answer(f"Enter your phone number", reply_markup=keyboard_markup)


@dp.message(QrCodeState.phone_number)
async def fullname_handler(message: Message, state: FSMContext) -> None:
    phone_number = message.contact.phone_number
    await state.update_data({"phone_number": phone_number})
    data = await state.get_data()
    query = insert(User).values(full_name=data["full_name"], phone_number=phone_number)
    session.execute(query)
    session.commit()
    await message.answer("Saved")



async def main() -> None:
    bot = Bot(token="Your bot token",
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

