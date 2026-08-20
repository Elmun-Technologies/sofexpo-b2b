from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    full_name = State()      # 1. Ism va familiya
    position = State()       # 2. Lavozim
    company = State()        # 3. Kompaniya nomi
    industry = State()       # 4. Faoliyat sohasi
    country = State()        # 5. Mamlakat
    city = State()           # 6. Shahar
    phone = State()          # 7. Telefon raqami
    email = State()          # 8. Email
    visit_day = State()      # 9. Ko'rgazmaning qaysi kunida kelishi
    visit_purpose = State()  # 10. Tashrif maqsadi
    comment = State()        # 11. Qo'shimcha izoh
