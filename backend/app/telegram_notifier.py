import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .config import settings
from .schemas import LeadRecord
from .storage import (
    cleanup_old_archived_leads,
    list_active_leads,
    list_archived_leads,
    mark_lead_done,
    read_prices,
    set_tg_message_id,
    update_service_price,
)

bot = Bot(token=settings.bot_token)
dispatcher = Dispatcher()
PAGE_SIZE = 5
pending_price_updates: dict[int, tuple[str, str]] = {}


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


def _menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Заказы"), KeyboardButton(text="Архив заказов")],
            [KeyboardButton(text="Настройки")],
        ],
        resize_keyboard=True,
    )


def _lead_line(lead: LeadRecord) -> str:
    created = lead.created_at.astimezone().strftime("%d.%m %H:%M")
    return f"• {created} | {lead.name} | {lead.phone} | id: {lead.id[:8]}"


def _orders_page_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if page > 1:
        keyboard.button(text="⬅️ Назад", callback_data=f"orders:page:{page - 1}")
    if page < total_pages:
        keyboard.button(text="Вперед ➡️", callback_data=f"orders:page:{page + 1}")
    return keyboard.as_markup()


def _archive_page_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if page > 1:
        keyboard.button(text="⬅️ Назад", callback_data=f"archive:page:{page - 1}")
    if page < total_pages:
        keyboard.button(text="Вперед ➡️", callback_data=f"archive:page:{page + 1}")
    return keyboard.as_markup()


async def _send_orders_page(message: Message, page: int = 1) -> None:
    leads = list_active_leads()
    if not leads:
        await message.answer("Активных заказов нет.")
        return
    total_pages = (len(leads) + PAGE_SIZE - 1) // PAGE_SIZE
    safe_page = max(1, min(page, total_pages))
    start = (safe_page - 1) * PAGE_SIZE
    chunk = leads[start : start + PAGE_SIZE]
    lines = ["📋 Незавершенные заказы:\n"] + [_lead_line(lead) for lead in chunk]
    text = "\n".join(lines) + f"\n\nСтраница {safe_page}/{total_pages}"
    await message.answer(text, reply_markup=_orders_page_keyboard(safe_page, total_pages))


async def _send_archive_page(message: Message, page: int = 1) -> None:
    leads = list_archived_leads()
    if not leads:
        await message.answer("Архив пуст.")
        return
    total_pages = (len(leads) + PAGE_SIZE - 1) // PAGE_SIZE
    safe_page = max(1, min(page, total_pages))
    start = (safe_page - 1) * PAGE_SIZE
    chunk = leads[start : start + PAGE_SIZE]
    lines = ["🗂 Архив заказов:\n"] + [_lead_line(lead) for lead in chunk]
    text = "\n".join(lines) + f"\n\nСтраница {safe_page}/{total_pages}"
    await message.answer(text, reply_markup=_archive_page_keyboard(safe_page, total_pages))


def _settings_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for category in read_prices():
        keyboard.button(text=category.title, callback_data=f"settings:cat:{category.key}")
    keyboard.adjust(1)
    return keyboard.as_markup()


def _category_items_keyboard(category_key: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    category = next((cat for cat in read_prices() if cat.key == category_key), None)
    if category is None:
        return keyboard.as_markup()
    for item in category.items:
        keyboard.button(
            text=f"{item.title} ({item.price_from} ₽)",
            callback_data=f"settings:item:{category.key}:{item.title}",
        )
    keyboard.adjust(1)
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
    await message.answer("Панель заказов ClearSpace активна.", reply_markup=_menu_keyboard())


@dispatcher.message(F.text == "Заказы")
async def on_orders_menu(message: Message) -> None:
    await _send_orders_page(message, page=1)


@dispatcher.message(F.text == "Архив заказов")
async def on_archive_menu(message: Message) -> None:
    await _send_archive_page(message, page=1)


@dispatcher.message(F.text == "Настройки")
async def on_settings_menu(message: Message) -> None:
    await message.answer("Выберите категорию для редактирования цен:", reply_markup=_settings_keyboard())


@dispatcher.callback_query(F.data.startswith("orders:page:"))
async def on_orders_page(callback: CallbackQuery) -> None:
    if callback.data is None or callback.message is None:
        return
    page = int(callback.data.split(":")[-1])
    leads = list_active_leads()
    if not leads:
        await callback.message.edit_text("Активных заказов нет.")
        await callback.answer()
        return
    total_pages = (len(leads) + PAGE_SIZE - 1) // PAGE_SIZE
    safe_page = max(1, min(page, total_pages))
    start = (safe_page - 1) * PAGE_SIZE
    chunk = leads[start : start + PAGE_SIZE]
    lines = ["📋 Незавершенные заказы:\n"] + [_lead_line(lead) for lead in chunk]
    text = "\n".join(lines) + f"\n\nСтраница {safe_page}/{total_pages}"
    await callback.message.edit_text(text, reply_markup=_orders_page_keyboard(safe_page, total_pages))
    await callback.answer()


@dispatcher.callback_query(F.data.startswith("archive:page:"))
async def on_archive_page(callback: CallbackQuery) -> None:
    if callback.data is None or callback.message is None:
        return
    page = int(callback.data.split(":")[-1])
    leads = list_archived_leads()
    if not leads:
        await callback.message.edit_text("Архив пуст.")
        await callback.answer()
        return
    total_pages = (len(leads) + PAGE_SIZE - 1) // PAGE_SIZE
    safe_page = max(1, min(page, total_pages))
    start = (safe_page - 1) * PAGE_SIZE
    chunk = leads[start : start + PAGE_SIZE]
    lines = ["🗂 Архив заказов:\n"] + [_lead_line(lead) for lead in chunk]
    text = "\n".join(lines) + f"\n\nСтраница {safe_page}/{total_pages}"
    await callback.message.edit_text(text, reply_markup=_archive_page_keyboard(safe_page, total_pages))
    await callback.answer()


@dispatcher.callback_query(F.data.startswith("settings:cat:"))
async def on_settings_category(callback: CallbackQuery) -> None:
    if callback.data is None or callback.message is None:
        return
    category_key = callback.data.split(":")[-1]
    await callback.message.edit_text(
        "Выберите услугу для изменения цены:",
        reply_markup=_category_items_keyboard(category_key),
    )
    await callback.answer()


@dispatcher.callback_query(F.data.startswith("settings:item:"))
async def on_settings_item(callback: CallbackQuery) -> None:
    if callback.data is None or callback.message is None or callback.from_user is None:
        return
    _, _, category_key, item_title = callback.data.split(":", 3)
    pending_price_updates[callback.from_user.id] = (category_key, item_title)
    await callback.message.answer(
        f"Введите новую цену для '{item_title}' только числом, например: 3200",
    )
    await callback.answer()


@dispatcher.message(F.text.regexp(r"^\d+$"))
async def on_new_price_value(message: Message) -> None:
    if message.from_user is None:
        return
    pending = pending_price_updates.get(message.from_user.id)
    if pending is None:
        return
    category_key, item_title = pending
    new_price = int(message.text or "0")
    if new_price <= 0:
        await message.answer("Цена должна быть больше 0.")
        return
    ok = update_service_price(category_key, item_title, new_price)
    if not ok:
        await message.answer("Не удалось обновить цену: услуга не найдена.")
        return
    pending_price_updates.pop(message.from_user.id, None)
    await message.answer(f"Цена обновлена: {item_title} -> {new_price} ₽")


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
    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
            await dispatcher.start_polling(bot, drop_pending_updates=False)
            return
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            await asyncio.sleep(5)


async def close_bot() -> None:
    await bot.session.close()


async def cleanup_archived_daily() -> None:
    while True:
        cleanup_old_archived_leads()
        await asyncio.sleep(86400)
