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
    mark_lead_active,
    mark_lead_done,
    read_prices,
    set_tg_message_id,
    update_service_price,
)

bot = Bot(token=settings.bot_token)
dispatcher = Dispatcher()
PAGE_SIZE = 5
pending_price_updates: dict[int, tuple[str, str, str]] = {}


def _sticker_number(index: int) -> str:
    stickers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    if 1 <= index <= len(stickers):
        return stickers[index - 1]
    return f"{index}."


def _build_message(lead: LeadRecord) -> str:
    local_time = lead.created_at.astimezone().strftime("%d.%m.%Y, %H:%M")
    comment = lead.comment.strip() or "Без комментария"
    return (
        "📦 Новая заявка\n\n"
        f"👤 {lead.name}\n"
        f"📞 {lead.phone}\n"
        f"💬 \"{comment}\"\n"
        f"🕒 {local_time}"
    )


def _done_keyboard(lead_id: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Завершить", callback_data=f"done:{lead_id}")
    return keyboard.as_markup()


def _menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Заявки")],
            [KeyboardButton(text="⚙️ Настройки")],
            [KeyboardButton(text="🗂 Архив заявок")],
        ],
        resize_keyboard=True,
    )


def _active_orders_text(leads: list[LeadRecord], page: int, total_pages: int) -> str:
    lines = [f"📥 Активные заказы • Страница {page}/{total_pages}", ""]
    for index, lead in enumerate(leads, start=1):
        created = lead.created_at.astimezone().strftime("%d.%m.%Y, %H:%M")
        comment = lead.comment.strip() or "Без комментария"
        marker = _sticker_number(index)
        lines.append(
            f"{marker} 👤 {lead.name}\n"
            f"📞 {lead.phone}\n"
            f"💬 \"{comment}\"\n"
            f"🕒 {created}"
        )
    return "\n\n".join(lines)


def _orders_page_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    leads = list_active_leads()
    start = (page - 1) * PAGE_SIZE
    chunk = leads[start : start + PAGE_SIZE]
    for idx, lead in enumerate(chunk, start=1):
        keyboard.button(text=f"{_sticker_number(idx)} Завершить", callback_data=f"done:{lead.id}")

    if page > 1:
        keyboard.button(text="⬅️ Назад", callback_data=f"orders:page:{page - 1}")
    if page < total_pages:
        keyboard.button(text="Вперед ➡️", callback_data=f"orders:page:{page + 1}")

    keyboard.adjust(1)
    return keyboard.as_markup()


def _archive_page_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    leads = list_archived_leads()
    start = (page - 1) * PAGE_SIZE
    chunk = leads[start : start + PAGE_SIZE]
    for idx, lead in enumerate(chunk, start=1):
        keyboard.button(text=f"{_sticker_number(idx)} В активные", callback_data=f"restore:{lead.id}")
    if page > 1:
        keyboard.button(text="⬅️ Назад", callback_data=f"archive:page:{page - 1}")
    if page < total_pages:
        keyboard.button(text="Вперед ➡️", callback_data=f"archive:page:{page + 1}")
    keyboard.adjust(1)
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
    text = _active_orders_text(chunk, safe_page, total_pages)
    await message.answer(
        text,
        reply_markup=_orders_page_keyboard(safe_page, total_pages),
    )


def _archive_page_text(leads: list[LeadRecord], page: int, total_pages: int) -> str:
    lines = [f"🗂 Архив заказов • Страница {page}/{total_pages}", ""]
    for index, lead in enumerate(leads, start=1):
        created = lead.created_at.astimezone().strftime("%d.%m.%Y, %H:%M")
        done = lead.done_at.astimezone().strftime("%d.%m.%Y, %H:%M") if lead.done_at else "—"
        comment = lead.comment.strip() or "Без комментария"
        marker = _sticker_number(index)
        lines.append(
            f"{marker} 👤 {lead.name}\n"
            f"📞 {lead.phone}\n"
            f"💬 \"{comment}\"\n"
            f"🕒 Создан: {created}\n"
            f"✅ Завершен: {done}"
        )
    return "\n\n".join(lines)


async def _send_archive_page(message: Message, page: int = 1) -> None:
    leads = list_archived_leads()
    if not leads:
        await message.answer("Архив пуст.")
        return
    total_pages = (len(leads) + PAGE_SIZE - 1) // PAGE_SIZE
    safe_page = max(1, min(page, total_pages))
    start = (safe_page - 1) * PAGE_SIZE
    chunk = leads[start : start + PAGE_SIZE]
    await message.answer(
        _archive_page_text(chunk, safe_page, total_pages),
        reply_markup=_archive_page_keyboard(safe_page, total_pages),
    )


def _services_prices() -> tuple[str, dict[str, tuple[str, int]]]:
    category = next((cat for cat in read_prices() if cat.key == "services"), None)
    if category is None:
        raise RuntimeError("Category 'services' not found in prices.json")

    mapped: dict[str, tuple[str, int]] = {}
    for item in category.items:
        mapped[item.key] = (item.title, item.price_from)
    return category.key, mapped


def _settings_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    category_key, services = _services_prices()
    for item_key, (title, price) in services.items():
        keyboard.button(text=f"{title} ({price} ₽)", callback_data=f"settings:item:{category_key}:{item_key}")
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
    await message.answer(
        "Добро пожаловать в панель ClearSpace.\nВыберите действие в меню ниже.",
        reply_markup=_menu_keyboard(),
    )


@dispatcher.message(F.text == "📥 Заявки")
async def on_orders_menu(message: Message) -> None:
    await _send_orders_page(message, page=1)


@dispatcher.message(F.text == "🗂 Архив заявок")
async def on_archive_menu(message: Message) -> None:
    await _send_archive_page(message, page=1)


@dispatcher.message(F.text == "⚙️ Настройки")
async def on_settings_menu(message: Message) -> None:
    await message.answer("Выберите услугу для изменения цены на сайте:", reply_markup=_settings_keyboard())


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
    text = _active_orders_text(chunk, safe_page, total_pages)
    await callback.message.edit_text(
        text,
        reply_markup=_orders_page_keyboard(safe_page, total_pages),
    )
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
    await callback.message.edit_text(
        _archive_page_text(chunk, safe_page, total_pages),
        reply_markup=_archive_page_keyboard(safe_page, total_pages),
    )
    await callback.answer()


@dispatcher.callback_query(F.data.startswith("settings:item:"))
async def on_settings_item(callback: CallbackQuery) -> None:
    if callback.data is None or callback.message is None or callback.from_user is None:
        return
    _, _, category_key, item_key = callback.data.split(":", 3)
    _, services = _services_prices()
    service = services.get(item_key)
    if service is None:
        await callback.answer("Услуга не найдена", show_alert=True)
        return
    item_title, old_price = service
    pending_price_updates[callback.from_user.id] = (category_key, item_key, item_title)
    await callback.message.answer(
        f"Текущая цена: {item_title} — {old_price} ₽\nВведите новую цену (только число):"
    )
    await callback.answer()


@dispatcher.message(F.text.regexp(r"^\d+$"))
async def on_new_price_value(message: Message) -> None:
    if message.from_user is None:
        return
    pending = pending_price_updates.get(message.from_user.id)
    if pending is None:
        return
    category_key, item_key, item_title = pending
    new_price = int(message.text or "0")
    if new_price <= 0:
        await message.answer("Цена должна быть больше 0.")
        return
    ok = update_service_price(category_key, item_key, new_price)
    if not ok:
        await message.answer("Не удалось обновить цену: услуга не найдена.")
        return
    pending_price_updates.pop(message.from_user.id, None)
    await message.answer(
        f"Цена обновлена: {item_title} -> {new_price} ₽",
        reply_markup=_settings_keyboard(),
    )


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


@dispatcher.callback_query(F.data.startswith("restore:"))
async def on_restore(callback: CallbackQuery) -> None:
    if callback.data is None or callback.message is None:
        return
    lead_id = callback.data.split(":", 1)[1]
    lead = mark_lead_active(lead_id)
    if lead is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    # Refresh current archive page after restore.
    page = 1
    if callback.message.reply_markup:
        # Try to derive current page from message text.
        text = callback.message.text or ""
        marker = "Страница "
        if marker in text:
            try:
                page = int(text.split(marker, 1)[1].split("/", 1)[0])
            except Exception:  # noqa: BLE001
                page = 1
    leads = list_archived_leads()
    if not leads:
        await callback.message.edit_text("Архив пуст.")
        await callback.answer("Перенесено в активные")
        return
    total_pages = (len(leads) + PAGE_SIZE - 1) // PAGE_SIZE
    safe_page = max(1, min(page, total_pages))
    start = (safe_page - 1) * PAGE_SIZE
    chunk = leads[start : start + PAGE_SIZE]
    await callback.message.edit_text(
        _archive_page_text(chunk, safe_page, total_pages),
        reply_markup=_archive_page_keyboard(safe_page, total_pages),
    )
    await callback.answer("Перенесено в активные")


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
