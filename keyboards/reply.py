from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

REGISTER_TEXT = "📝 Ro'yxatdan o'tish"
INFO_TEXT = "ℹ️ Ko'rgazma haqida"
SKIP_TEXT = "⏭ O'tkazib yuborish"
CANCEL_TEXT = "❌ Bekor qilish"

def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Boshlang'ich marketing tugmalari."""
    keyboard = [
        [KeyboardButton(text=REGISTER_TEXT)],
        [KeyboardButton(text=INFO_TEXT)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni ulashish tugmasi."""
    keyboard = [
        [KeyboardButton(text="📱 Telefon raqamni ulashish", request_contact=True)],
        [KeyboardButton(text=CANCEL_TEXT)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_country_keyboard() -> ReplyKeyboardMarkup:
    """Mamlakatni tanlash tugmalari."""
    keyboard = [
        [KeyboardButton(text="O'zbekiston"), KeyboardButton(text="Qozog'iston")],
        [KeyboardButton(text="Qirg'iziston"), KeyboardButton(text="Tojikiston")],
        [KeyboardButton(text="Rossiya"), KeyboardButton(text="Turkiya")],
        [KeyboardButton(text="Boshqa mamlakat")],
        [KeyboardButton(text=CANCEL_TEXT)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_visit_days_keyboard() -> ReplyKeyboardMarkup:
    """Ko'rgazmaga kelish kuni tugmalari."""
    keyboard = [
        [KeyboardButton(text="1-kun"), KeyboardButton(text="2-kun")],
        [KeyboardButton(text="3-kun"), KeyboardButton(text="Barcha kunlar")],
        [KeyboardButton(text=CANCEL_TEXT)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_visit_purpose_keyboard() -> ReplyKeyboardMarkup:
    """Tashrif maqsadi tugmalari."""
    keyboard = [
        [KeyboardButton(text="🤝 Hamkor topish"), KeyboardButton(text="📈 Mijoz topish")],
        [KeyboardButton(text="📦 Mahsulotlar va xizmatlar bilan tanishish")],
        [KeyboardButton(text="🌐 Tajriba almashish"), KeyboardButton(text="Boshqa")],
        [KeyboardButton(text=CANCEL_TEXT)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_skip_keyboard() -> ReplyKeyboardMarkup:
    """Ixtiyoriy bosqichlarni o'tkazib yuborish tugmasi."""
    keyboard = [
        [KeyboardButton(text=SKIP_TEXT)],
        [KeyboardButton(text=CANCEL_TEXT)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Faqat bekor qilish tugmasi."""
    keyboard = [
        [KeyboardButton(text=CANCEL_TEXT)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
