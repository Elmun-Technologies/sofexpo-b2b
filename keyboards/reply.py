from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.translations import (
    BTN_UZ, BTN_RU, BTN_EN,
    COUNTRIES, VISIT_DAYS, VISIT_PURPOSES,
    get_text
)

def get_language_keyboard() -> ReplyKeyboardMarkup:
    """Tilni tanlash tugmalari."""
    keyboard = [
        [KeyboardButton(text=BTN_UZ), KeyboardButton(text=BTN_RU), KeyboardButton(text=BTN_EN)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_start_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Boshlang'ich marketing va menyu tugmalari."""
    keyboard = [
        [KeyboardButton(text=get_text("btn_register", lang))],
        [KeyboardButton(text=get_text("btn_info", lang)), KeyboardButton(text=get_text("btn_change_lang", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_contact_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Telefon raqamni ulashish tugmasi."""
    keyboard = [
        [KeyboardButton(text=get_text("btn_share_contact", lang), request_contact=True)],
        [KeyboardButton(text=get_text("btn_cancel", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_country_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Mamlakatni tanlash tugmalari."""
    c_list = COUNTRIES.get(lang, COUNTRIES["uz"])
    keyboard = [
        [KeyboardButton(text=c_list[0]), KeyboardButton(text=c_list[1])],
        [KeyboardButton(text=c_list[2]), KeyboardButton(text=c_list[3])],
        [KeyboardButton(text=c_list[4]), KeyboardButton(text=c_list[5])],
        [KeyboardButton(text=c_list[6])],
        [KeyboardButton(text=get_text("btn_cancel", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_visit_days_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Ko'rgazmaga kelish kuni tugmalari."""
    d_list = VISIT_DAYS.get(lang, VISIT_DAYS["uz"])
    keyboard = [
        [KeyboardButton(text=d_list[0]), KeyboardButton(text=d_list[1])],
        [KeyboardButton(text=d_list[2]), KeyboardButton(text=d_list[3])],
        [KeyboardButton(text=get_text("btn_cancel", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_visit_purpose_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Tashrif maqsadi tugmalari."""
    p_list = VISIT_PURPOSES.get(lang, VISIT_PURPOSES["uz"])
    keyboard = [
        [KeyboardButton(text=p_list[0]), KeyboardButton(text=p_list[1])],
        [KeyboardButton(text=p_list[2])],
        [KeyboardButton(text=p_list[3]), KeyboardButton(text=p_list[4])],
        [KeyboardButton(text=get_text("btn_cancel", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_skip_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Ixtiyoriy bosqichlarni o'tkazib yuborish tugmasi."""
    keyboard = [
        [KeyboardButton(text=get_text("btn_skip", lang))],
        [KeyboardButton(text=get_text("btn_cancel", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_cancel_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Faqat bekor qilish tugmasi."""
    keyboard = [
        [KeyboardButton(text=get_text("btn_cancel", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
