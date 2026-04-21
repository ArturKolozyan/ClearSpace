from aiogram import Bot

from .config import settings
from .schemas import LeadRecord


def _build_message(lead: LeadRecord) -> str:
    local_time = lead.created_at.astimezone().strftime("%H:%M")
    comment = lead.comment.strip() or "Без комментария"
    return (
        "📦 НОВЫЙ ЗАКАЗ: ClearSpace\n\n"
        f"👤 Клиент: {lead.name}\n"
        f"📞 Связь: {lead.phone}\n"
        f"💬 Пожелания: {comment}\n\n"
        f"🕒 Время заявки: {local_time}"
    )


async def notify_owner(lead: LeadRecord) -> None:
    bot = Bot(token=settings.bot_token)
    try:
        try:
            await bot.send_message(
                chat_id=settings.owner_chat_id,
                text=_build_message(lead),
            )
        except Exception:  # noqa: BLE001
            # Telegram delivery failure must not break lead creation flow.
            return
    finally:
        await bot.session.close()
