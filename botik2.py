import asyncio, json, os, random, time, logging, aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "9284760662:AAEGgZYrk4sVkOG0cq5S75zqLio-eEQcAmM"
SUBGRAM_KEY = "1b56f1e4c0b4bc273720f359a82c28cbf1edbea02167ecedb11d9b1086c2218e"
GRAMADS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Mzg1MSIsImp0aSI6IjM1MmE5MzZiLTg4MWItNDY3Mi04YzczLTE5MGMyNjE5MGVhYiIsIm5hbWUiOiJTdGFuZG9mZiBnb2xkIiwiYm90aWQiOiIzMzMzMiIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWVpZGVudGlmaWVyIjoiNjM4NTEiLCJuYmYiOjE3OTU3MDc5MjIsImV4cCI6MTc5NTkxNjcyMiwiaXNzIjoiU3R1Z25vdiIsImF1ZCI6IlVzZXJzIn0.WUBhAAZXvH7-dSOsM5eGKHMHGta84nDkFl6fM3RmHCo"
DATA_FILE = "/tmp/so2_save.json"

log = logging.getLogger("adverts")
bot = Bot(token=TOKEN)
dp = Dispatcher()
from fastapi import FastAPI, Request
from aiogram.types import Update
app = FastAPI()

class BotStates(StatesGroup):
    waiting_code = State()
    waiting_support = State()

ADMINS = (7608157300,8685735427)
BASE_PROMOS = {"STANDOFF": 500.0, "GOLD2026": 1500.0, "KNIFE": 2500.0}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "promos": {}, "total_opens": 0}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

db = load_data()

def get_user(uid, name="Игрок"):
    s = str(uid)
    start_gold = 100000.0 if uid in ADMINS else 100.0
    if s not in db["users"]:
        db["users"][s] = {"name": name, "gold": start_gold, "inv": [], "last_bonus": 0, "opened": 0, "knives": 0, "promos": []}
        save_data()
    else:
        db["users"][s]["name"] = name
        if "last_bonus" not in db["users"][s]:
            db["users"][s]["last_bonus"] = 0
    return db["users"][s]

EMOJIS = {"Common": "⬜️", "Uncommon": "🟦", "Rare": "🔷", "Epic": "🟪", "Legendary": "🟥", "Arcane": "🟨"}
W_DEF = {"Common": 65.0, "Uncommon": 20.0, "Rare": 10.0, "Epic": 4.0, "Legendary": 0.8, "Arcane": 0.2}
W_KNIFE = {"Arcane": 100.0}

CONTAINERS = {
    "b_orig": {"name": "📦 Origin Box", "price": 10.0, "cat": "boxes", "w": W_DEF, "skins": {"Common": [("G22 Pattern", 0.5), ("P350 Savannah", 0.4)], "Uncommon": [("USP Pisces", 1.5), ("MP7 Thorn", 1.0)], "Rare": [("Deagle Morgan", 6.0), ("AWM Sport", 8.0)], "Epic": [("AKR Carbon", 25.0), ("P90 Ghoul", 20.0)], "Legendary": [("M4A1 Bubblegum", 110.0), ("AWM Genesis", 140.0)], "Arcane": [("AKR Treasure Hunter", 950.0), ("AWM Sport V2", 1200.0)]}},
    "b_fab": {"name": "📦 Fable Box", "price": 10.0, "cat": "boxes", "w": W_DEF, "skins": {"Common": [("MP5 Project Z9", 0.4), ("M40 Quake", 0.4)], "Uncommon": [("MAC10 Argo", 1.2), ("TEC-9 Fable", 1.6)], "Rare": [("FS Tactical", 5.5), ("G22 Starfall", 9.0)], "Epic": [("AKR Worm", 22.0), ("AWM Scratch", 35.0)], "Legendary": [("Deagle Dragon Glass", 150.0), ("M4A1 King", 120.0)], "Arcane": [("M4 Samurai", 650.0), ("AKR Necromancer", 720.0)]}},
    "b_emp": {"name": "📦 Empire Box", "price": 10.0, "cat": "boxes", "w": W_DEF, "skins": {"Common": [("P350 Blizzard", 0.4), ("G22 Monster", 0.5)], "Uncommon": [("M110 Cyber", 1.3), ("MP7 Lich", 1.4)], "Rare": [("AKR12 4 Years", 6.5), ("M4A1 Kitsune", 8.5)], "Epic": [("Deagle Orochi", 30.0), ("P90 Samurai", 24.0)], "Legendary": [("AKR Tag King", 160.0), ("M16 Triumphant", 135.0)], "Arcane": [("M4A1 Bubblegum Pro", 580.0), ("AWM Boom", 810.0)]}},
    "b_riv": {"name": "📦 Rival Box", "price": 10.0, "cat": "boxes", "w": W_DEF, "skins": {"Common": [("SM1014 Faceless", 0.4), ("P350 Neon", 0.5)], "Uncommon": [("MP7 Offroad", 1.2), ("TEC-9 Aurora", 1.4)], "Rare": [("M40 Monster", 6.0), ("FAMAS Beagle", 7.5)], "Epic": [("AWM Gear", 25.0), ("AKR Sport", 32.0)], "Legendary": [("G22 Nest", 130.0), ("USP Genesis", 175.0)], "Arcane": [("AKR Rival", 690.0), ("M4 Night Wolf", 620.0)]}},
    "c_orig": {"name": "💼 Origin Case", "price": 100.0, "cat": "cases", "w": W_DEF, "skins": {"Common": [("G22 Pattern", 2.0)], "Uncommon": [("USP Pisces", 6.0)], "Rare": [("AWM Sport", 30.0)], "Epic": [("AKR Carbon", 95.0)], "Legendary": [("AWM Genesis", 480.0)], "Arcane": [("M9 Universe", 4800.0), ("Karambit Gold", 15000.0)]}},
    "c_fab": {"name": "💼 Fable Case", "price": 100.0, "cat": "cases", "w": W_DEF, "skins": {"Common": [("MP5 Project Z9", 2.0)], "Uncommon": [("TEC-9 Fable", 6.5)], "Rare": [("G22 Starfall", 35.0)], "Epic": [("AWM Scratch", 120.0)], "Legendary": [("Deagle Dragon Glass", 520.0)], "Arcane": [("Butterfly Legacy", 4100.0), ("Butterfly Dragon Glass", 6500.0)]}},
    "c_scor": {"name": "💼 Scorpion Case", "price": 100.0, "cat": "cases", "w": W_DEF, "skins": {"Common": [("M40 Cursed", 2.1)], "Uncommon": [("MP7 Banana", 6.0)], "Rare": [("AKR12 Aurora", 28.0)], "Epic": [("Deagle Yakuza", 115.0)], "Legendary": [("AKR Dragon", 540.0)], "Arcane": [("Kunai Poison", 3500.0), ("Kunai Luxury", 4900.0)]}},
    "k_case": {"name": "🔪 Knife Case", "price": 2500.0, "cat": "knives", "w": W_KNIFE, "skins": {"Arcane": [("Kunai Bone", 1800.0), ("Dual Daggers Acid", 2100.0), ("Butterfly Legacy", 3800.0), ("M9 Dragon Glass", 5200.0), ("Karambit Claw", 6400.0), ("Karambit Gold", 15000.0)]}}
}
ALL_SKINS = [dict(name=n, price=p, rar=r, emoji=EMOJIS[r]) for c in CONTAINERS.values() for r, sl in c["skins"].items() for n, p in sl]

async def check_subgram(user_id: int, first_name: str):
    if user_id in ADMINS or not SUBGRAM_KEY:
        return []
    url = "https://subgram.ru"
    headers = {"Auth": SUBGRAM_KEY, "Content-Type": "application/json"}
    payload = {"UserId": user_id, "ChatId": user_id, "first_name": first_name}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=5) as resp:
                data = await resp.json()
                if data.get("status") == "ok":
                    return []
                return data.get("links", [])
    except Exception:
        return []

async def show_advert(user_id: int):
    if user_id in ADMINS or not GRAMADS_TOKEN:
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://gramads.net",
                headers={"Authorization": f"Bearer {GRAMADS_TOKEN}", "Content-Type": "application/json"},
                json={"SendToChatId": user_id},
                timeout=5
            ) as response:
                if not response.ok:
                    log.error("Gramads: %s" % str(await response.json()))
    except Exception:
        pass

def sub_lock_kb(links):
    btns = [[InlineKeyboardButton(text=f"📢 Подписаться на канал #{i}", url=link)] for i, link in enumerate(links, 1)]
    btns.append([InlineKeyboardButton(text="✅ Я подписался — Начать игру!", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=btns)

async def verify_sub(target, uid: int, fname: str):
    links = await check_subgram(uid, fname)
    if links:
        txt = "🔒 ДОСТУП К ИГРЕ ЗАКРЫТ!\n━━━━━━━━━━━━━━\nЧтобы открывать кейсы и играть, подпишись на всех спонсоров ниже, затем нажми кнопку проверки:"
        if isinstance(target, Message):
            await target.answer(txt, reply_markup=sub_lock_kb(links))
        elif isinstance(target, CallbackQuery):
            await target.message.edit_text(txt, reply_markup=sub_lock_kb(links))
            await target.answer("❌ Сначала подпишись на все каналы!", show_alert=True)
        return False
    return True

def roll(ckey):
    c = CONTAINERS[ckey]
    rar = random.choices(list(c["w"].keys()), weights=list(c["w"].values()), k=1).pop()
    name, price = random.choice(c["skins"][rar])
    return rar, name, price

def kb_main():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Магазин кейсов", callback_data="shop")],
        [InlineKeyboardButton(text="⚒ Контракт (5 в 1)", callback_data="craft"), InlineKeyboardButton(text="⚡️ Апгрейд", callback_data="upg")],
        [InlineKeyboardButton(text="⚔️ Дуэль с ботом", callback_data="duel"), InlineKeyboardButton(text="🏆 Топ игроков", callback_data="top")],
        [InlineKeyboardButton(text="🎒 Инвентарь", callback_data="inv"), InlineKeyboardButton(text="👤 Профиль", callback_data="prof")],
        [InlineKeyboardButton(text="🎁 Бонус (+100 G / 24ч)", callback_data="bonus"), InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")]
    ])

def main_text(u, fname):
    inv_val = sum(i.get("price", 0) for i in u["inv"])
    return (
        f"╔══════════════════╗\n"
        f"   🔫 STANDOFF 2 SIMULATOR\n"
        f"╚══════════════════╝\n\n"
        f"👤 Боец: {fname}\n"
        f"💰 Баланс: {u['gold']:.2f} G\n"
        f"🎒 Инвентарь: {len(u['inv'])} шт. ({inv_val:.1f} G)\n"
        f"📦 Открыто кейсов: {u['opened']} | 🔪 Ножей: {u['knives']}\n\n"
        f"👇 Выбери режим игры в меню:"
    )

@dp.message(Command("start"))
async def start_cmd(m: Message, state: FSMContext):
    await state.clear()
    if not await verify_sub(m, m.from_user.id, m.from_user.first_name):
        return
    u = get_user(m.from_user.id, m.from_user.first_name)
    await m.answer(main_text(u, m.from_user.first_name), reply_markup=kb_main())
    await show_advert(m.from_user.id)

@dp.callback_query(F.data == "check_sub")
async def check_sub_cb(c: CallbackQuery):
    if not await verify_sub(c, c.from_user.id, c.from_user.first_name):
        return
    u = get_user(c.from_user.id, c.from_user.first_name)
    await c.message.edit_text(main_text(u, c.from_user.first_name), reply_markup=kb_main())
    await show_advert(c.from_user.id)
@dp.message(Command("addpromo"))
async def add_promo_cmd(m: Message):
    if ADMINS and m.from_user.id not in ADMINS:
        return
    parts = m.text.split()
    if len(parts) != 3:
        return await m.answer("Пиши так: /addpromo НАЗВАНИЕ СУММА\nПример: /addpromo BONUS500 500")
    _, code_raw, amt_raw = parts
    db.setdefault("promos", {})[code_raw.upper()] = float(amt_raw)
    save_data()
    await m.answer(f"✅ Промокод {code_raw.upper()} на {amt_raw} G создан!")

@dp.message(Command("backup"))
async def backup_cmd(m: Message):
    if ADMINS and m.from_user.id not in ADMINS:
        return
    if os.path.exists(DATA_FILE):
        await m.answer_document(FSInputFile(DATA_FILE), caption="💾 Резервная копия базы.")

@dp.message(F.document)
async def restore_doc(m: Message):
    if ADMINS and m.from_user.id not in ADMINS:
        return
    if m.document.file_name == DATA_FILE:
        file = await bot.get_file(m.document.file_id)
        await bot.download_file(file.file_path, DATA_FILE)
        global db
        db = load_data()
        await m.answer("✅ База игроков восстановлена!")

@dp.callback_query(F.data == "home")
async def home_cb(c: CallbackQuery, state: FSMContext):
    await state.clear()
    if not await verify_sub(c, c.from_user.id, c.from_user.first_name):
        return
    u = get_user(c.from_user.id, c.from_user.first_name)
    await c.message.edit_text(main_text(u, c.from_user.first_name), reply_markup=kb_main())

@dp.callback_query(F.data == "support")
async def support_ask(c: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.waiting_support)
    await c.message.edit_text("🆘 СЛУЖБА ПОДДЕРЖКИ\n━━━━━━━━━━━━━━\nНапиши свой вопрос одним сообщением — оно отправится админам:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="home")]]))

@dp.message(BotStates.waiting_support)
async def support_send(m: Message, state: FSMContext):
    await state.clear()
    if not ADMINS:
        return await m.answer("⚠️ Админы не настроены в коде бота.", reply_markup=kb_main())
    uname = f"@{m.from_user.username}" if m.from_user.username else "без юзернейма"
    txt = f"📩 СООБЩЕНИЕ В ПОДДЕРЖКУ\n━━━━━━━━━━━━━━\n👤 От: {m.from_user.first_name} ({uname})\n🆔 ID: {m.from_user.id}\n\n💬 Текст:\n{m.text}"
    sent = 0
    for aid in ADMINS:
        try:
            await bot.send_message(aid, txt)
            sent += 1
        except Exception:
            pass
    await m.answer("✅ Сообщение отправлено админам!" if sent else "❌ Админы еще не запустили бота (/start).", reply_markup=kb_main())

@dp.callback_query(F.data == "shop")
async def shop_cb(c: CallbackQuery):
    if not await verify_sub(c, c.from_user.id, c.from_user.first_name):
        return
    u = get_user(c.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Боксы (10 G | без ножей)", callback_data="cat:boxes")],
        [InlineKeyboardButton(text="💼 Кейсы (100 G | шанс ножа)", callback_data="cat:cases")],
        [InlineKeyboardButton(text="🔪 Ножевой кейс (2500 G | 100% нож)", callback_data="open:k_case")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="home")]
    ])
    await c.message.edit_text(f"🛒 МАГАЗИН КОНТЕЙНЕРОВ\n━━━━━━━━━━━━━━\n💰 Твой баланс: {u['gold']:.2f} G", reply_markup=kb)

@dp.callback_query(F.data.startswith("cat:"))
async def cat_cb(c: CallbackQuery):
    if not await verify_sub(c, c.from_user.id, c.from_user.first_name):
        return
    _, cat = c.data.split(":")
    u = get_user(c.from_user.id)
    btns = [[InlineKeyboardButton(text=f"{v['name']} — {v['price']:.0f} G", callback_data=f"open:{k}")] for k, v in CONTAINERS.items() if v["cat"] == cat]
    btns.append([InlineKeyboardButton(text="🔙 К категориям", callback_data="shop")])
    await c.message.edit_text(f"📦 ВЫБОР КОНТЕЙНЕРА\n━━━━━━━━━━━━━━\n💰 Твой баланс: {u['gold']:.2f} G", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))

@dp.callback_query(F.data.startswith("open:"))
async def open_cb(c: CallbackQuery):
    if not await verify_sub(c, c.from_user.id, c.from_user.first_name):
        return
    _, ckey = c.data.split(":")
    cont = CONTAINERS[ckey]
    u = get_user(c.from_user.id)
    if u["gold"] < cont["price"]:
        return await c.answer("❌ Недостаточно голды!", show_alert=True)
    u["gold"] -= cont["price"]
    u["opened"] += 1
    db["total_opens"] = db.get("total_opens", 0) + 1
    msg = await c.message.edit_text(f"🔄 Открываем {cont['name']}...")
    for s in range(1, 4):
        tr, tn, _ = roll(ckey)
        await asyncio.sleep(0.45)
        await msg.edit_text(f"🎰 Прокрутка ({s}/3)...\n\n➡️ {EMOJIS[tr]} {tn} ({tr})")
    fr, fn, fp = roll(ckey)
    if any(k in fn for k in ["Karambit", "M9", "Butterfly", "Kunai", "Daggers"]):
        u["knives"] += 1
    u["inv"].append({"name": fn, "price": fp, "emoji": EMOJIS[fr], "rar": fr})
    save_data()
    if ADMINS and db["total_opens"] % 25 == 0 and os.path.exists(DATA_FILE):
        for aid in ADMINS:
            try:
                await bot.send_document(aid, FSInputFile(DATA_FILE), caption="🔄 Авто-бэкап базы")
            except Exception:
                pass
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔄 Открыть еще ({cont['price']:.0f} G)", callback_data=f"open:{ckey}")],
        [InlineKeyboardButton(text="⚡️ Апгрейд этого скина", callback_data=f"upg_go:{len(u['inv'])-1}:2")],
        [InlineKeyboardButton(text="🎒 Инвентарь", callback_data="inv"), InlineKeyboardButton(text="🛒 Магазин", callback_data="shop")]
    ])
    await asyncio.sleep(0.35)
    await msg.edit_text(f"🎉 ТЕБЕ ВЫПАЛО:\n━━━━━━━━━━━━━━\n{EMOJIS[fr]} {fn}\n🏷 Редкость: {fr}\n💵 Цена: {fp} G\n━━━━━━━━━━━━━━\n💰 Баланс: {u['gold']:.2f} G", reply_markup=kb)
    if u["opened"] % 3 == 0:
        await show_advert(c.from_user.id)
@dp.callback_query(F.data == "craft")
async def craft_cb(c: CallbackQuery):
    if not await verify_sub(c, c.from_user.id, c.from_user.first_name):
        return
    u = get_user(c.from_user.id)
    if len(u["inv"]) < 5:
        return await c.answer("❌ Нужно минимум 5 скинов для контракта!", show_alert=True)
    u["inv"].sort(key=lambda x: x.get("price", 0))
    s5 = u["inv"][:5]
    tot = sum(i.get("price", 0) for i in s5)
    txt = "\n".join([f"• {i['emoji']} {i['name']} ({i['price']} G)" for i in s5])
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔥 Скрафтить (5 в 1)", callback_data="craft_do")], [InlineKeyboardButton(text="🔙 В меню", callback_data="home")]])
    await c.message.edit_text(f"⚒ КОНТРАКТ (5 В 1)\n━━━━━━━━━━━━━━\nСпишутся 5 дешевых скинов ({tot:.2f} G):\n\n{txt}", reply_markup=kb)

@dp.callback_query(F.data == "craft_do")
async def craft_do_cb(c: CallbackQuery):
    u = get_user(c.from_user.id)
    if len(u["inv"]) < 5:
        return await c.answer("Не хватает скинов!", show_alert=True)
    u["inv"].sort(key=lambda x: x.get("price", 0))
    tot = sum(i.get("price", 0) for i in u["inv"][:5])
    del u["inv"][:5]
    best = min(ALL_SKINS, key=lambda x: abs(x["price"] - tot * random.uniform(0.9, 2.2)))
    if any(k in best["name"] for k in ["Karambit", "M9", "Butterfly", "Kunai", "Daggers"]):
        u["knives"] += 1
    u["inv"].append(dict(best))
    save_data()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⚒ Еще контракт", callback_data="craft")], [InlineKeyboardButton(text="🔙 В меню", callback_data="home")]])
    await c.message.edit_text(f"✨ КОНТРАКТ ВЫПОЛНЕН!\n━━━━━━━━━━━━━━\nТы получил: {best['emoji']} {best['name']} ({best['price']} G)", reply_markup=kb)

@dp.callback_query(F.data == "upg")
async def upg_menu_cb(c: CallbackQuery):
    if not await verify_sub(c, c.from_user.id, c.from_user.first_name):
        return
    u = get_user(c.from_user.id)
    if not u["inv"]:
        return await c.answer("Инвентарь пуст!", show_alert=True)
    u["inv"].sort(key=lambda x: x.get("price", 0), reverse=True)
    btns = [[InlineKeyboardButton(text=f"{item['emoji']} {item['name']} ({item['price']} G)", callback_data=f"upg_sel:{idx}")] for idx, item in enumerate(u["inv"][:8])]
    btns.append([InlineKeyboardButton(text="🔙 Назад", callback_data="home")])
    await c.message.edit_text("⚡️ АПГРЕЙД СКИНА\n━━━━━━━━━━━━━━\nВыбери скин для прокачки:", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))

@dp.callback_query(F.data.startswith("upg_sel:"))
async def upg_sel_cb(c: CallbackQuery):
    _, idx_s = c.data.split(":")
    idx = int(idx_s)
    u = get_user(c.from_user.id)
    if idx >= len(u["inv"]):
        return await upg_menu_cb(c)
    item = u["inv"][idx]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 x2 (45%)", callback_data=f"upg_go:{idx}:2"), InlineKeyboardButton(text="🟡 x3 (28%)", callback_data=f"upg_go:{idx}:3")],
        [InlineKeyboardButton(text="🔴 x5 (15%)", callback_data=f"upg_go:{idx}:5")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="upg")]
    ])
    await c.message.edit_text(f"⚡️ НАСТРОЙКА АПГРЕЙДА\n━━━━━━━━━━━━━━\nСкин: {item['emoji']} {item['name']} ({item['price']} G)\nПри неудаче скин сгорит!", reply_markup=kb)

@dp.callback_query(F.data.startswith("upg_go:"))
async def upg_go_cb(c: CallbackQuery):
    _, idx_s, mult_s = c.data.split(":")
    idx, mult = int(idx_s), int(mult_s)
    u = get_user(c.from_user.id)
    if idx >= len(u["inv"]):
        return await upg_menu_cb(c)
    item = u["inv"].pop(idx)
    win = random.randint(1, 100) <= {2: 45, 3: 28, 5: 15}[mult]
    if win:
        prize = min(ALL_SKINS, key=lambda x: abs(x["price"] - item["price"] * mult))
        if any(k in prize["name"] for k in ["Karambit", "M9", "Butterfly", "Kunai", "Daggers"]):
            u["knives"] += 1
        u["inv"].append(dict(prize))
        res = f"✅ УСПЕШНЫЙ АПГРЕЙД (x{mult})!\nНовый скин: {prize['emoji']} {prize['name']} ({prize['price']} G)"
    else:
        res = f"💥 НЕУДАЧА!\nСкин {item['emoji']} {item['name']} сгорел..."
    save_data()
    await c.message.edit_text(res, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⚡️ Еще раз", callback_data="upg")], [InlineKeyboardButton(text="🔙 В меню", callback_data="home")]]))

@dp.callback_query(F.data == "duel")
async def duel_cb(c: CallbackQuery):
    if not await verify_sub(c, c.from_user.id, c.from_user.first_name):
        return
    u = get_user(c.from_user.id)
    if not u["inv"]:
        return await c.answer("Сначала выбей хотя бы 1 скин!", show_alert=True)
    my_skin = random.choice(u["inv"])
    u["inv"].remove(my_skin)
    bot_skin = min(ALL_SKINS, key=lambda x: abs(x["price"] - my_skin["price"] * random.uniform(0.6, 1.5)))
    if my_skin["price"] >= bot_skin["price"]:
        u["inv"].extend([my_skin, dict(bot_skin)])
        header = "🏆 ТЫ ПОБЕДИЛ В ДУЭЛИ!"
    else:
        header = "💀 БОТ ЗАБРАЛ ТВОЙ СКИН!"
    save_data()
    await c.message.edit_text(f"{header}\n━━━━━━━━━━━━━━\n👤 Ты: {my_skin['emoji']} {my_skin['name']} ({my_skin['price']} G)\n🤖 Бот: {bot_skin['emoji']} {bot_skin['name']} ({bot_skin['price']} G)", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⚔️ Новая дуэль", callback_data="duel")], [InlineKeyboardButton(text="🔙 В меню", callback_data="home")]]))

@dp.callback_query(F.data == "top")
async def top_cb(c: CallbackQuery):
    ranking = sorted([(d.get("name", "Игрок"), d.get("gold", 0) + sum(i.get("price", 0) for i in d.get("inv", []))) for d in db["users"].values()], key=lambda x: x, reverse=True)
    lines = [f"{['🥇', '🥈', '🥉'][i] if i < 3 else '🏅'} {n} — {v:.1f} G" for i, (n, v) in enumerate(ranking[:10])]
    await c.message.edit_text("🏆 ТОП-10 БОГАЧЕЙ СЕРВЕРА\n━━━━━━━━━━━━━━\n" + "\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="home")]]))

@dp.callback_query(F.data == "inv")
async def inv_cb(c: CallbackQuery):
    u = get_user(c.from_user.id)
    if not u["inv"]:
        return await c.message.edit_text("🎒 Инвентарь пуст", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="home")]]))
    u["inv"].sort(key=lambda x: x.get("price", 0), reverse=True)
    tot = sum(i.get("price", 0) for i in u["inv"])
    txt = "\n".join([f"{i['emoji']} {i['name']} — {i['price']} G" for i in u["inv"][:15]])
    await c.message.edit_text(f"🎒 ИНВЕНТАРЬ ({len(u['inv'])} шт.) | {tot:.2f} G\n━━━━━━━━━━━━━━\n{txt}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"💸 Продать всё (+{tot:.1f} G)", callback_data="sell")], [InlineKeyboardButton(text="🔙 Назад", callback_data="home")]]))

@dp.callback_query(F.data == "sell")
async def sell_cb(c: CallbackQuery):
    u = get_user(c.from_user.id)
    tot = sum(i.get("price", 0) for i in u["inv"])
    u["gold"] += tot
    u["inv"].clear()
    save_data()
    await c.answer(f"✅ Продано за {tot:.2f} G!", show_alert=True)
    await inv_cb(c)

@dp.callback_query(F.data == "prof")
async def prof_cb(c: CallbackQuery):
    u = get_user(c.from_user.id, c.from_user.first_name)
    inv_val = sum(i.get("price", 0) for i in u["inv"])
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎟 Ввести промокод", callback_data="promo")], [InlineKeyboardButton(text="🔙 Назад", callback_data="home")]])
    await c.message.edit_text(f"👤 ПРОФИЛЬ БОЙЦА\n━━━━━━━━━━━━━━\n🆔 ID: {c.from_user.id}\n📛 Ник: {c.from_user.first_name}\n💰 Баланс: {u['gold']:.2f} G\n🎒 Инвентарь: {len(u['inv'])} шт. ({inv_val:.1f} G)\n📦 Кейсов: {u['opened']} | 🔪 Ножей: {u['knives']}", reply_markup=kb)

@dp.callback_query(F.data == "promo")
async def promo_ask(c: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.waiting_code)
    await c.message.edit_text("🎟 ВВЕДИ ПРОМОКОД В ЧАТ:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="home")]]))

@dp.message(BotStates.waiting_code)
async def promo_check(m: Message, state: FSMContext):
    code = m.text.strip().upper()
    u = get_user(m.from_user.id, m.from_user.first_name)
    await state.clear()
    all_p = {**BASE_PROMOS, **db.get("promos", {})}
    if code in all_p and code not in u["promos"]:
        u["gold"] += all_p[code]
        u["promos"].append(code)
        save_data()
        await m.answer(f"✅ Промокод {code} активирован! +{all_p[code]} G.", reply_markup=kb_main())
    else:
        await m.answer("❌ Неверный или уже использованный промокод.", reply_markup=kb_main())

@dp.callback_query(F.data == "bonus")
async def bonus_cb(c: CallbackQuery):
    if not await verify_sub(c, c.from_user.id, c.from_user.first_name):
        return
    u = get_user(c.from_user.id, c.from_user.first_name)
    now = time.time()
    passed = now - u.get("last_bonus", 0)
    if passed < 86400:
        rem = int(86400 - passed)
        return await c.answer(f"⏳ Бонус раз в 24 часа!\nОсталось: {rem // 3600} ч. {(rem % 3600) // 60} мин.", show_alert=True)
    u["gold"] += 100.0
    u["last_bonus"] = now
    save_data()
    await c.answer("🎁 Ежедневный бонус +100 G начислен!", show_alert=True)
    await home_cb(c, None)
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def index():
    return {"status": "Bot is running"}

