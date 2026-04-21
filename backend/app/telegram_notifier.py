from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .config import settings
from .schemas import LeadRecord
from .storage import mark_lead_done, set_tg_message_id

bot = Bot(token=settings.bot_token)
dispatcher = Dispatcher()


def _build_message(lead: LeadRecord) -> str:
    local_time = lead.created_at.astimezone().strftime("%H:%M")
    comment = lead.comment.strip() or "Без комментария"
    return (
        "📦 НОВЫЙ ЗАКАЗ: ClearSpace\n\n"
        f"🆔 ID: {lead.id}\n"
        f"👤 Клиент: {lead.name}\n"
        f"📞 Связь: {lead.phone}\n"
        f"💬 Пожелания: {comment}\n\n"
        f"🕒 Время заявки: {local_time}"
    )


def _done_keyboard(lead_id: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Завершить", callback_data=f"done:{lead_id}")
    return keyboard.as_markup()


async def notify_owner(lead: LeadRecord) -> None:
    try:
        msg = await bot.send_message(
            chat_id=settings.owner_chat_id,
            text=_build_message(lead),
            reply_markup=_done_keyboard(lead.id),
        )
        set_tg_message_id(lead.id, msg.message_id)
    except Exception:  # noqa: BLE001
        return


@dispatcher.message(Command("start"))
async def on_start(message: Message) -> None:
    await message.answer("Панель заказов ClearSpace активна.")


@dispatcher.callback_query(F.data.startswith("done:"))
async def on_done(callback: CallbackQuery) -> None:
    if callback.data is None:
        return
    lead_id = callback.data.split(":", 1)[1]
    lead = mark_lead_done(lead_id)
    if lead is None:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    if callback.message:
        try:
            await callback.message.delete()
        except Exception:  # noqa: BLE001
            await callback.message.edit_text(
                f"✅ Заказ {lead.id} завершен",
            )
    await callback.answer("Готово")


async def run_polling() -> None:
    await dispatcher.start_polling(bot)


async def close_bot() -> None:
    await bot.session.close()
