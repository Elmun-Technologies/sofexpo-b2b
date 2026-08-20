import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.registration import RegistrationState
from keyboards.reply import (
    get_language_keyboard,
    get_start_keyboard,
    get_contact_keyboard,
    get_country_keyboard,
    get_visit_days_keyboard,
    get_visit_purpose_keyboard,
    get_skip_keyboard,
    get_cancel_keyboard
)
from utils.translations import (
    BTN_UZ, BTN_RU, BTN_EN,
    LANG_UZ, LANG_RU, LANG_EN,
    TEXTS, get_text
)
from database.db import save_registration
from services.sheets import append_to_google_sheet
from config import ADMIN_IDS, ADMIN_GROUP_ID

logger = logging.getLogger(__name__)
user_router = Router()

# List of cancel texts across languages
CANCEL_TEXTS = [
    TEXTS["btn_cancel"]["uz"],
    TEXTS["btn_cancel"]["ru"],
    TEXTS["btn_cancel"]["en"]
]

# List of info texts across languages
INFO_TEXTS = [
    TEXTS["btn_info"]["uz"],
    TEXTS["btn_info"]["ru"],
    TEXTS["btn_info"]["en"]
]

# List of register texts across languages
REGISTER_TEXTS = [
    TEXTS["btn_register"]["uz"],
    TEXTS["btn_register"]["ru"],
    TEXTS["btn_register"]["en"]
]

# List of change language texts
CHANGE_LANG_TEXTS = [
    TEXTS["btn_change_lang"]["uz"],
    TEXTS["btn_change_lang"]["ru"],
    TEXTS["btn_change_lang"]["en"]
]

# List of skip texts across languages
SKIP_TEXTS = [
    TEXTS["btn_skip"]["uz"],
    TEXTS["btn_skip"]["ru"],
    TEXTS["btn_skip"]["en"]
]

async def get_user_lang(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get("language", LANG_UZ)


@user_router.message(Command("cancel"))
@user_router.message(F.text.in_(CANCEL_TEXTS))
async def cancel_handler(message: Message, state: FSMContext):
    """Anketani bekor qilish handleri."""
    lang = await get_user_lang(state)
    await state.clear()
    await state.update_data(language=lang)
    await message.answer(
        get_text("cancel_msg", lang),
        parse_mode="Markdown",
        reply_markup=get_start_keyboard(lang)
    )


@user_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Botni boshlash - Birinchi bo'lib tilni tanlashni so'rash."""
    await state.clear()
    await state.set_state(RegistrationState.select_language)
    await message.answer(
        get_text("select_language", "uz"),
        reply_markup=get_language_keyboard()
    )


@user_router.message(RegistrationState.select_language, F.text.in_([BTN_UZ, BTN_RU, BTN_EN]))
@user_router.message(F.text.in_([BTN_UZ, BTN_RU, BTN_EN]))
async def language_selected_handler(message: Message, state: FSMContext):
    """Til tanlanganda ishlaydi."""
    lang_map = {
        BTN_UZ: LANG_UZ,
        BTN_RU: LANG_RU,
        BTN_EN: LANG_EN
    }
    selected_lang = lang_map.get(message.text, LANG_UZ)
    await state.update_data(language=selected_lang)
    
    welcome_text = get_text("welcome", selected_lang)
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_start_keyboard(selected_lang))


@user_router.message(F.text.in_(CHANGE_LANG_TEXTS))
async def change_language_handler(message: Message, state: FSMContext):
    """Tilni o'zgartirish tugmasi."""
    await state.set_state(RegistrationState.select_language)
    await message.answer(
        get_text("select_language", "uz"),
        reply_markup=get_language_keyboard()
    )


@user_router.message(F.text.in_(INFO_TEXTS))
async def info_handler(message: Message, state: FSMContext):
    """Ko'rgazma haqida ma'lumot."""
    lang = await get_user_lang(state)
    info_text = get_text("info", lang)
    await message.answer(info_text, parse_mode="Markdown", reply_markup=get_start_keyboard(lang))


@user_router.message(F.text.in_(REGISTER_TEXTS))
async def start_registration_handler(message: Message, state: FSMContext):
    """Ro'yxatdan o'tish anketasini boshlash."""
    lang = await get_user_lang(state)
    await state.update_data(language=lang)
    await state.set_state(RegistrationState.full_name)
    
    first_question = get_text("q1_full_name", lang)
    await message.answer(first_question, parse_mode="Markdown", reply_markup=get_cancel_keyboard(lang))


# 1. Full name
@user_router.message(RegistrationState.full_name)
async def process_full_name(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    if not message.text or message.text.startswith("/"):
        await message.answer(get_text("invalid_text", lang))
        return

    await state.update_data(full_name=message.text.strip())
    await state.set_state(RegistrationState.position)
    await message.answer(
        get_text("q2_position", lang),
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(lang)
    )


# 2. Position
@user_router.message(RegistrationState.position)
async def process_position(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    if not message.text or message.text.startswith("/"):
        await message.answer(get_text("invalid_text", lang))
        return

    await state.update_data(position=message.text.strip())
    await state.set_state(RegistrationState.company)
    await message.answer(
        get_text("q3_company", lang),
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(lang)
    )


# 3. Company
@user_router.message(RegistrationState.company)
async def process_company(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    if not message.text or message.text.startswith("/"):
        await message.answer(get_text("invalid_text", lang))
        return

    await state.update_data(company=message.text.strip())
    await state.set_state(RegistrationState.industry)
    await message.answer(
        get_text("q4_industry", lang),
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(lang)
    )


# 4. Industry
@user_router.message(RegistrationState.industry)
async def process_industry(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    if not message.text or message.text.startswith("/"):
        await message.answer(get_text("invalid_text", lang))
        return

    await state.update_data(industry=message.text.strip())
    await state.set_state(RegistrationState.country)
    await message.answer(
        get_text("q5_country", lang),
        parse_mode="Markdown",
        reply_markup=get_country_keyboard(lang)
    )


# 5. Country
@user_router.message(RegistrationState.country)
async def process_country(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    if not message.text or message.text.startswith("/"):
        await message.answer(get_text("invalid_text", lang))
        return

    await state.update_data(country=message.text.strip())
    await state.set_state(RegistrationState.city)
    await message.answer(
        get_text("q6_city", lang),
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(lang)
    )


# 6. City
@user_router.message(RegistrationState.city)
async def process_city(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    if not message.text or message.text.startswith("/"):
        await message.answer(get_text("invalid_text", lang))
        return

    await state.update_data(city=message.text.strip())
    await state.set_state(RegistrationState.phone)
    await message.answer(
        get_text("q7_phone", lang),
        parse_mode="Markdown",
        reply_markup=get_contact_keyboard(lang)
    )


# 7. Phone (Contact or Text)
@user_router.message(RegistrationState.phone)
async def process_phone(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    phone_number = None
    if message.contact:
        phone_number = message.contact.phone_number
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
    elif message.text and not message.text.startswith("/"):
        phone_number = message.text.strip()

    if not phone_number:
        await message.answer(
            get_text("q7_phone", lang),
            reply_markup=get_contact_keyboard(lang)
        )
        return

    await state.update_data(phone=phone_number)
    await state.set_state(RegistrationState.email)
    await message.answer(
        get_text("q8_email", lang),
        parse_mode="Markdown",
        reply_markup=get_skip_keyboard(lang)
    )


# 8. Email
@user_router.message(RegistrationState.email)
async def process_email(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    email_val = ""
    if message.text and message.text not in SKIP_TEXTS and not message.text.startswith("/"):
        email_val = message.text.strip()

    await state.update_data(email=email_val)
    await state.set_state(RegistrationState.visit_day)
    await message.answer(
        get_text("q9_visit_day", lang),
        parse_mode="Markdown",
        reply_markup=get_visit_days_keyboard(lang)
    )


# 9. Visit Day
@user_router.message(RegistrationState.visit_day)
async def process_visit_day(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    if not message.text or message.text.startswith("/"):
        await message.answer(get_text("invalid_text", lang))
        return

    await state.update_data(visit_day=message.text.strip())
    await state.set_state(RegistrationState.visit_purpose)
    await message.answer(
        get_text("q10_visit_purpose", lang),
        parse_mode="Markdown",
        reply_markup=get_visit_purpose_keyboard(lang)
    )


# 10. Visit Purpose
@user_router.message(RegistrationState.visit_purpose)
async def process_visit_purpose(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    if not message.text or message.text.startswith("/"):
        await message.answer(get_text("invalid_text", lang))
        return

    await state.update_data(visit_purpose=message.text.strip())
    await state.set_state(RegistrationState.comment)
    await message.answer(
        get_text("q11_comment", lang),
        parse_mode="Markdown",
        reply_markup=get_skip_keyboard(lang)
    )


# 11. Comment & Finish
@user_router.message(RegistrationState.comment)
async def process_comment(message: Message, state: FSMContext):
    lang = await get_user_lang(state)
    comment_val = ""
    if message.text and message.text not in SKIP_TEXTS and not message.text.startswith("/"):
        comment_val = message.text.strip()

    data = await state.get_data()
    data["comment"] = comment_val
    data["telegram_id"] = message.from_user.id
    data["username"] = message.from_user.username or ""
    if "language" not in data:
        data["language"] = lang

    # Database-ga saqlash
    row_id = await save_registration(data)

    # Google Sheets-ga saqlash (parallel/background)
    await append_to_google_sheet(data)

    # State holatini saqlash (faqat tilni saqlab qolamiz)
    await state.clear()
    await state.update_data(language=lang)

    # User-ga tasdiq xabari
    success_text = get_text("success_msg", lang)
    await message.answer(success_text, parse_mode="Markdown", reply_markup=get_start_keyboard(lang))

    # Adminlarga bildirishnoma yuborish
    comment_text = data.get('comment') or "Yo'q"
    email_text = data.get('email') or "Kiritilmadi"
    username_text = f"@{data.get('username')}" if data.get('username') else str(data.get('telegram_id'))

    admin_notify_text = (
        f"🆕 **Yangi B2B Ro'yxatdan o'tish (#{row_id})**\n\n"
        f"🌐 **Til:** {data.get('language', 'uz')}\n"
        f"👤 **Ism:** {data.get('full_name')}\n"
        f"💼 **Lavozim:** {data.get('position')}\n"
        f"🏢 **Kompaniya:** {data.get('company')}\n"
        f"🏭 **Soha:** {data.get('industry')}\n"
        f"🌍 **Mamlakat/Shahar:** {data.get('country')}, {data.get('city')}\n"
        f"📞 **Tel:** {data.get('phone')}\n"
        f"📧 **Email:** {email_text}\n"
        f"📅 **Kelish kuni:** {data.get('visit_day')}\n"
        f"🎯 **Maqsad:** {data.get('visit_purpose')}\n"
        f"💬 **Izoh:** {comment_text}\n"
        f"🔗 **Telegram:** {username_text}"
    )

    # Guruhga yuborish (ADMIN_GROUP_ID)
    if ADMIN_GROUP_ID:
        try:
            await message.bot.send_message(ADMIN_GROUP_ID, admin_notify_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Admin guruhiga ({ADMIN_GROUP_ID}) bildirishnoma yuborishda xato: {e}")

    # Adminlarga shaxsiyga yuborish
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(admin_id, admin_notify_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Admin {admin_id} ga bildirishnoma yuborishda xato: {e}")
