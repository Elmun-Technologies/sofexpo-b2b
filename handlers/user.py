import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from states.registration import RegistrationState
from keyboards.reply import (
    get_start_keyboard,
    get_contact_keyboard,
    get_country_keyboard,
    get_visit_days_keyboard,
    get_visit_purpose_keyboard,
    get_skip_keyboard,
    get_cancel_keyboard,
    REGISTER_TEXT,
    INFO_TEXT,
    SKIP_TEXT,
    CANCEL_TEXT
)
from database.db import save_registration
from services.sheets import append_to_google_sheet
from config import ADMIN_IDS, ADMIN_GROUP_ID

logger = logging.getLogger(__name__)
user_router = Router()

@user_router.message(Command("cancel"))
@user_router.message(F.text == CANCEL_TEXT)
async def cancel_handler(message: Message, state: FSMContext):
    """Anketani bekor qilish handleri."""
    current_state = await state.get_state()
    await state.clear()
    await message.answer(
        "Ro'yxatdan o'tish bekor qilindi.\nQayta ro'yxatdan o'tish uchun **'📝 Ro'yxatdan o'tish'** tugmasini bosing.",
        parse_mode="Markdown",
        reply_markup=get_start_keyboard()
    )

@user_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Botni boshlash - Jalb qiluvchi marketing xabari."""
    await state.clear()
    
    welcome_text = (
        "🏢 **SOF EXPO SAMARKAND — Xalqaro B2B Ko'rgazmasi!** 👋\n\n"
        "Samarqand shahridagi eng yirik **SOF EXPO B2B** ko'rgazmasining rasmiy botiga xush kelibsiz.\n\n"
        "Ko'rgazmada 100+ mahalliy va xalqaro kompaniyalar, yangi biznes imkoniyatlari hamda samarali hamkorliklar sizni kutmoqda!\n\n"
        "💡 **Nega ro'yxatdan o'tish kerak?**\n"
        "🔹 Yangi biznes hamkorlar va mijozlar topish\n"
        "🔹 Sohadagi eng so'nggi va innovatsion takliflar bilan tanishish\n"
        "🔹 Ko'rgazmaga navbatsiz va **bepul** kirish\n\n"
        "👇 Ro'yxatdan o'tish uchun quyidagi **'📝 Ro'yxatdan o'tish'** tugmasini bosing:"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_start_keyboard())

@user_router.message(F.text == INFO_TEXT)
async def info_handler(message: Message):
    """Ko'rgazma haqida ma'lumot."""
    info_text = (
        "ℹ️ **SOF EXPO SAMARKAND B2B Ko'rgazmasi haqida**\n\n"
        "📍 **Joylashuv:** Samarqand shahri, SOF EXPO ko'rgazmalar majmuasi\n"
        "🎯 **Maqsad:** Mahalliy va xalqaro tadbirkorlar o'rtasida B2B aloqalarni rivojlantirish hamda yangi shartnomalar tuzish.\n\n"
        "Qatnashish mutlaqo **bepul**! O'z biznesingizni rivojlantirish uchun hoziroq ro'yxatdan o'ting. 👇"
    )
    await message.answer(info_text, parse_mode="Markdown", reply_markup=get_start_keyboard())

@user_router.message(F.text == REGISTER_TEXT)
async def start_registration_handler(message: Message, state: FSMContext):
    """Ro'yxatdan o'tish anketasini boshlash."""
    await state.clear()
    await state.set_state(RegistrationState.full_name)
    
    first_question = (
        "Ajoyib! Anketa savollarini to'ldiramiz. ✨\n\n"
        "**1-savol:** Ismingiz va familiyangizni kiriting (Masalan: Alisher Navoiy):"
    )
    await message.answer(first_question, parse_mode="Markdown", reply_markup=get_cancel_keyboard())

# 1. Full name
@user_router.message(RegistrationState.full_name)
async def process_full_name(message: Message, state: FSMContext):
    if not message.text or message.text.startswith("/"):
        await message.answer("Iltimos, ismingiz va familiyangizni matn ko'rinishida kiriting:")
        return

    await state.update_data(full_name=message.text.strip())
    await state.set_state(RegistrationState.position)
    await message.answer(
        "**2-savol:** Tashkilotingizdagi lavozimingizni kiriting (Masalan: Bosh direktor, Sotuv bo'limi boshlig'i, Menecer):",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )

# 2. Position
@user_router.message(RegistrationState.position)
async def process_position(message: Message, state: FSMContext):
    if not message.text or message.text.startswith("/"):
        await message.answer("Iltimos, lavozimingizni matn ko'rinishida kiriting:")
        return

    await state.update_data(position=message.text.strip())
    await state.set_state(RegistrationState.company)
    await message.answer(
        "**3-savol:** Kompaniyangiz yoki tashkilotingiz nomini kiriting:",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )

# 3. Company
@user_router.message(RegistrationState.company)
async def process_company(message: Message, state: FSMContext):
    if not message.text or message.text.startswith("/"):
        await message.answer("Iltimos, kompaniyangiz nomini kiriting:")
        return

    await state.update_data(company=message.text.strip())
    await state.set_state(RegistrationState.industry)
    await message.answer(
        "**4-savol:** Kompaniyangizning faoliyat sohasini kiriting (Masalan: Qishloq xo'jaligi, Tekstil, IT, Qurilish):",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )

# 4. Industry
@user_router.message(RegistrationState.industry)
async def process_industry(message: Message, state: FSMContext):
    if not message.text or message.text.startswith("/"):
        await message.answer("Iltimos, faoliyat sohangizni kiriting:")
        return

    await state.update_data(industry=message.text.strip())
    await state.set_state(RegistrationState.country)
    await message.answer(
        "**5-savol:** Qaysi mamlakatdan kelayotganingizni tanlang yoki kiriting:",
        parse_mode="Markdown",
        reply_markup=get_country_keyboard()
    )

# 5. Country
@user_router.message(RegistrationState.country)
async def process_country(message: Message, state: FSMContext):
    if not message.text or message.text.startswith("/"):
        await message.answer("Iltimos, mamlakat nomini tanlang yoki kiriting:")
        return

    await state.update_data(country=message.text.strip())
    await state.set_state(RegistrationState.city)
    await message.answer(
        "**6-savol:** Siz yashaydigan yoki kompaniya joylashgan shaharni kiriting (Masalan: Toshkent, Samarqand, Olmata):",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )

# 6. City
@user_router.message(RegistrationState.city)
async def process_city(message: Message, state: FSMContext):
    if not message.text or message.text.startswith("/"):
        await message.answer("Iltimos, shahar nomini kiriting:")
        return

    await state.update_data(city=message.text.strip())
    await state.set_state(RegistrationState.phone)
    await message.answer(
        "**7-savol:** Telefon raqamingizni pastdagi tugma orqali ulashing yoki qo'lda kiriting (+998901234567):",
        parse_mode="Markdown",
        reply_markup=get_contact_keyboard()
    )

# 7. Phone (Contact or Text)
@user_router.message(RegistrationState.phone)
async def process_phone(message: Message, state: FSMContext):
    phone_number = None
    if message.contact:
        phone_number = message.contact.phone_number
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
    elif message.text and not message.text.startswith("/"):
        phone_number = message.text.strip()

    if not phone_number:
        await message.answer(
            "Iltimos, pastdagi '📱 Telefon raqamni ulashish' tugmasini bosing yoki raqamingizni kiriting:",
            reply_markup=get_contact_keyboard()
        )
        return

    await state.update_data(phone=phone_number)
    await state.set_state(RegistrationState.email)
    await message.answer(
        "**8-savol:** Elektron pochta manzilingizni (Email) kiriting (Ixtiyoriy):",
        parse_mode="Markdown",
        reply_markup=get_skip_keyboard()
    )

# 8. Email
@user_router.message(RegistrationState.email)
async def process_email(message: Message, state: FSMContext):
    email_val = ""
    if message.text and message.text != SKIP_TEXT and not message.text.startswith("/"):
        email_val = message.text.strip()

    await state.update_data(email=email_val)
    await state.set_state(RegistrationState.visit_day)
    await message.answer(
        "**9-savol:** Ko'rgazmaning qaysi kunida tashrif buyurishni rejalashtiryapsiz?",
        parse_mode="Markdown",
        reply_markup=get_visit_days_keyboard()
    )

# 9. Visit Day
@user_router.message(RegistrationState.visit_day)
async def process_visit_day(message: Message, state: FSMContext):
    if not message.text or message.text.startswith("/"):
        await message.answer("Iltimos, kelish kuningizni tanlang:")
        return

    await state.update_data(visit_day=message.text.strip())
    await state.set_state(RegistrationState.visit_purpose)
    await message.answer(
        "**10-savol:** Tashrifingizdan asosiy maqsad nima?",
        parse_mode="Markdown",
        reply_markup=get_visit_purpose_keyboard()
    )

# 10. Visit Purpose
@user_router.message(RegistrationState.visit_purpose)
async def process_visit_purpose(message: Message, state: FSMContext):
    if not message.text or message.text.startswith("/"):
        await message.answer("Iltimos, tashrif maqsadingizni tanlang:")
        return

    await state.update_data(visit_purpose=message.text.strip())
    await state.set_state(RegistrationState.comment)
    await message.answer(
        "**11-savol:** Qo'shimcha izoh yoki takliflaringiz bo'lsa kiriting (Ixtiyoriy):",
        parse_mode="Markdown",
        reply_markup=get_skip_keyboard()
    )

# 11. Comment & Finish
@user_router.message(RegistrationState.comment)
async def process_comment(message: Message, state: FSMContext):
    comment_val = ""
    if message.text and message.text != SKIP_TEXT and not message.text.startswith("/"):
        comment_val = message.text.strip()

    data = await state.get_data()
    data["comment"] = comment_val
    data["telegram_id"] = message.from_user.id
    data["username"] = message.from_user.username or ""

    # Database-ga saqlash
    row_id = await save_registration(data)

    # Google Sheets-ga saqlash (parallel/background)
    await append_to_google_sheet(data)

    # State tozalash
    await state.clear()

    # User-ga tasdiq xabari
    success_text = (
        "✅ **Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!**\n\n"
        "SOF EXPO SAMARKAND B2B ko'rgazmasida sizni kutib qolamiz.\n"
        "Tashrifingiz uchun tashakkur!"
    )
    await message.answer(success_text, parse_mode="Markdown", reply_markup=get_start_keyboard())

    # Adminlarga bildirishnoma yuborish
    comment_text = data.get('comment') or "Yo'q"
    email_text = data.get('email') or "Kiritilmadi"
    username_text = f"@{data.get('username')}" if data.get('username') else str(data.get('telegram_id'))

    admin_notify_text = (
        f"🆕 **Yangi B2B Ro'yxatdan o'tish (#{row_id})**\n\n"
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
