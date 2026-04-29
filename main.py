#!/usr/bin/env python3
"""
Telegram Account Manager Bot – Full Featured (getUpdates)
Supports: Import/Export ZIP, Check, Refresh, 2FA, Remove Devices, Reports, etc.

GitHub: https://github.com/i7rvn
"""

import asyncio, base64, hashlib, json, logging, os, sqlite3, io, zipfile, re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

import aiohttp
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    UserDeactivatedBanError, AuthKeyUnregisteredError, FloodWaitError
)
from telethon.tl.functions.auth import ResetAuthorizationsRequest

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID", "0")) 
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler('telegram_manager.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


COUNTRY_PREFIXES = {
    "93": ("🇦🇫", "Afghanistan"), "355": ("🇦🇱", "Albania"), "213": ("🇩🇿", "Algeria"),
    "1": ("🇺🇸/🇨🇦", "USA/Canada"), "44": ("🇬🇧", "UK"), "33": ("🇫🇷", "France"),
    "49": ("🇩🇪", "Germany"), "7": ("🇷🇺/🇰🇿", "Russia/Kazakhstan"), "90": ("🇹🇷", "Turkey"),
    "966": ("🇸🇦", "Saudi Arabia"), "20": ("🇪🇬", "Egypt"), "971": ("🇦🇪", "UAE"),
    "98": ("🇮🇷", "Iran"), "964": ("🇮🇶", "Iraq"), "963": ("🇸🇾", "Syria"),
    "962": ("🇯🇴", "Jordan"), "961": ("🇱🇧", "Lebanon"), "965": ("🇰🇼", "Kuwait"),
    "974": ("🇶🇦", "Qatar"), "967": ("🇾🇪", "Yemen"), "249": ("🇸🇩", "Sudan"),
    "212": ("🇲🇦", "Morocco"), "216": ("🇹🇳", "Tunisia"), "218": ("🇱🇾", "Libya"),
    "380": ("🇺🇦", "Ukraine"), "92": ("🇵🇰", "Pakistan"), "91": ("🇮🇳", "India"),
    "62": ("🇮🇩", "Indonesia"), "55": ("🇧🇷", "Brazil"), "52": ("🇲🇽", "Mexico"),
    "34": ("🇪🇸", "Spain"), "39": ("🇮🇹", "Italy"), "31": ("🇳🇱", "Netherlands"),
    "48": ("🇵🇱", "Poland"), "46": ("🇸🇪", "Sweden"), "41": ("🇨🇭", "Switzerland"),
    "81": ("🇯🇵", "Japan"), "82": ("🇰🇷", "South Korea"), "86": ("🇨🇳", "China"),
    "66": ("🇹🇭", "Thailand"), "84": ("🇻🇳", "Vietnam"), "63": ("🇵🇭", "Philippines"),
    "60": ("🇲🇾", "Malaysia"), "65": ("🇸🇬", "Singapore"), "27": ("🇿🇦", "South Africa"),
    "234": ("🇳🇬", "Nigeria"), "254": ("🇰🇪", "Kenya"), "256": ("🇺🇬", "Uganda"),
}

def detect_country(phone: str) -> Tuple[str, str]:
    phone = phone.strip().replace("+", "")
    for prefix_len in range(4, 0, -1):
        prefix = phone[:prefix_len]
        if prefix in COUNTRY_PREFIXES:
            return COUNTRY_PREFIXES[prefix]
    return ("🌍", "Unknown")

def estimate_year(uid: int) -> int:
    if uid < 10_000_000: return 2013
    elif uid < 100_000_000: return 2014
    elif uid < 300_000_000: return 2015
    elif uid < 600_000_000: return 2016
    elif uid < 900_000_000: return 2017
    elif uid < 1_200_000_000: return 2018
    elif uid < 1_500_000_000: return 2019
    elif uid < 2_000_000_000: return 2020
    elif uid < 4_000_000_000: return 2021
    elif uid < 5_500_000_000: return 2022
    elif uid < 7_000_000_000: return 2023
    else: return 2024

def split_text(text: str, limit=4000):
    chunks, while_text = [], text
    while len(while_text) > limit:
        cut = while_text.rfind("\n", 0, limit)
        if cut == -1: cut = limit
        chunks.append(while_text[:cut])
        while_text = while_text[cut:]
    chunks.append(while_text)
    return [c for c in chunks if c.strip()]

# ── قاعدة البيانات المطورة ──────────────────────────────────
class DatabaseManager:
    def __init__(self, db_path="telegram_manager.db"):
        self.db_path = db_path
        self.init_db()

    def conn(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def init_db(self):
        db = self.conn()
        c = db.cursor()
        c.executescript('''
        CREATE TABLE IF NOT EXISTS sessions (
            phone TEXT PRIMARY KEY,
            session_data TEXT,
            session_type TEXT DEFAULT 'telethon',
            status TEXT DEFAULT 'unknown',
            country TEXT,
            creation_year INTEGER,
            api_id TEXT,
            api_hash TEXT,
            has_2fa INTEGER DEFAULT 0,
            tfa_password TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checked_at TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        db.commit()
        db.close()


    def add_session(self, phone, session_data, session_type="telethon", api_id=None, api_hash=None, tfa_password=None):
        db = self.conn()
        db.execute('''
            INSERT OR REPLACE INTO sessions
            (phone, session_data, session_type, api_id, api_hash, tfa_password, has_2fa)
            VALUES (?,?,?,?,?,?,?)
        ''', (phone, session_data, session_type, api_id, api_hash, tfa_password, 1 if tfa_password else 0))
        db.commit(); db.close()

    def get_all_sessions(self):
        db = self.conn()
        rows = db.execute("SELECT * FROM sessions").fetchall()
        db.close(); return rows

    def get_session(self, phone):
        db = self.conn()
        row = db.execute("SELECT * FROM sessions WHERE phone=?", (phone,)).fetchone()
        db.close(); return row

    def get_sessions_by_status(self, status):
        db = self.conn()
        rows = db.execute("SELECT * FROM sessions WHERE status=?", (status,)).fetchall()
        db.close(); return rows

    def update_status(self, phone, status, country=None, year=None, has_2fa=None):
        db = self.conn()
        db.execute('''
            UPDATE sessions SET status=?, country=?, creation_year=?, checked_at=CURRENT_TIMESTAMP
            WHERE phone=?
        ''', (status, country, year, phone))
        if has_2fa is not None:
            db.execute("UPDATE sessions SET has_2fa=? WHERE phone=?", (int(has_2fa), phone))
        db.commit(); db.close()

    def update_2fa(self, phone, has_2fa: bool, password: str = None):
        db = self.conn()
        db.execute("UPDATE sessions SET has_2fa=?, tfa_password=? WHERE phone=?", (int(has_2fa), password, phone))
        db.commit(); db.close()

    def delete_session(self, phone):
        db = self.conn()
        db.execute("DELETE FROM sessions WHERE phone=?", (phone,))
        db.commit(); db.close()

    def count_by_status(self, status):
        db = self.conn()
        n = db.execute("SELECT COUNT(*) FROM sessions WHERE status=?", (status,)).fetchone()[0]
        db.close(); return n

    def total_sessions(self):
        db = self.conn()
        n = db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        db.close(); return n


    def get_setting(self, key, default=None):
        db = self.conn()
        row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        db.close()
        return row["value"] if row else default

    def set_setting(self, key, value):
        db = self.conn()
        db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, value))
        db.commit(); db.close()


    def add_user(self, uid, username, first_name, last_name):
        db = self.conn()
        db.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?,?,?,?)",
                   (uid, username, first_name, last_name))
        db.commit(); db.close()

class TelegramAccountManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def check_session(self, phone, session_data, api_id, api_hash):
        """فحص جلسة واحدة وإرجاع (status, country, year, has_2fa)"""
        try:
            client = TelegramClient(StringSession(session_data), int(api_id), api_hash)
            await client.connect()
            if await client.is_user_authorized():
                me = await client.get_me()
                status = "valid"
                year = estimate_year(me.id)
                has_2fa = False
                try:
                    pwd = await client.get_password_settings()
                    has_2fa = pwd.has_password
                except: pass
                await client.disconnect()
                return status, year, has_2fa
            else:
                await client.disconnect()
                return "invalid", None, False
        except (UserDeactivatedBanError, AuthKeyUnregisteredError):
            return "banned", None, False
        except FloodWaitError as e:
            await asyncio.sleep(min(e.seconds, 10))
            return "error", None, False
        except Exception:
            return "error", None, False

    async def apply_2fa(self, phone, session_data, api_id, api_hash, action, new_pass=None, old_pass=None):
        try:
            client = TelegramClient(StringSession(session_data), int(api_id), api_hash)
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                return False
            if action == "enable":
                await client.edit_2fa(new_password=new_pass)
            elif action == "disable":
                await client.edit_2fa(current_password=old_pass, new_password=None)
            elif action == "change":
                await client.edit_2fa(current_password=old_pass, new_password=new_pass)
            await client.disconnect()
            return True
        except Exception as e:
            logger.error(f"2FA error {phone}: {e}")
            return False

    async def remove_devices(self, phone, session_data, api_id, api_hash):
        try:
            client = TelegramClient(StringSession(session_data), int(api_id), api_hash)
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                return False
            await client(ResetAuthorizationsRequest())
            await client.disconnect()
            return True
        except Exception:
            return False


class TelegramBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.manager = TelegramAccountManager(self.db)
        self.user_states = {}      # state لكل مستخدم
        self.offset = 0
        self.session = None
        self.admin_id = OWNER_ID


    async def send_msg(self, chat_id, text, reply_markup=None):
        data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        if reply_markup: data['reply_markup'] = json.dumps(reply_markup)
        async with self.session.post(f"{API_URL}/sendMessage", json=data) as resp:
            return await resp.json()

    async def edit_msg(self, chat_id, msg_id, text, reply_markup=None):
        data = {'chat_id': chat_id, 'message_id': msg_id, 'text': text, 'parse_mode': 'HTML'}
        if reply_markup: data['reply_markup'] = json.dumps(reply_markup)
        async with self.session.post(f"{API_URL}/editMessageText", json=data) as resp:
            return await resp.json()

    async def answer_cb(self, cb_id, text=""):
        data = {'callback_query_id': cb_id, 'text': text}
        async with self.session.post(f"{API_URL}/answerCallbackQuery", json=data) as resp:
            return await resp.json()

    async def download_file(self, file_id):
        async with self.session.post(f"{API_URL}/getFile", json={'file_id': file_id}) as resp:
            result = await resp.json()
        if result['ok']:
            path = result['result']['file_path']
            url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{path}"
            async with self.session.get(url) as resp2:
                return await resp2.read()
        return None


    def main_menu_keyboard(self):
        btn = lambda txt, cb: {'text': txt, 'callback_data': cb}
        return {'inline_keyboard': [
            [btn("📥 Import ZIP", "m_import"), btn("📤 Export ZIP", "m_export")],
            [btn("✅ Check Sessions", "m_check"), btn("🔄 Refresh", "m_refresh")],
            [btn("🚫 Remove Devices", "m_remove"), btn("🔐 2FA", "m_2fa")],
            [btn("📅 Years", "m_years"), btn("🌍 Country", "m_country")],
            [btn("📆 Group by Year", "m_gyear"), btn("💾 Export JSON", "m_exjson")],
            [btn("⚙️ Set API", "m_api"), btn("📊 Stats", "m_stats")],
        ]}

    def simple_back(self, cb="back_main"):
        return {'inline_keyboard': [[{'text': '🔙 Back', 'callback_data': cb}]]}


    async def handle_start(self, msg):
        uid = msg['from']['id']
        if OWNER_ID and uid != OWNER_ID:
            return await self.send_msg(msg['chat']['id'], "⛔ Unauthorized.")
        self.db.add_user(uid, msg['from'].get('username'),
                         msg['from'].get('first_name'), msg['from'].get('last_name'))
        await self.send_msg(msg['chat']['id'],
            "🔐 <b>Account Manager</b> – full featured.\nChoose an action:",
            self.main_menu_keyboard())


    async def handle_callback(self, cb):
        uid = cb['from']['id']
        if OWNER_ID and uid != OWNER_ID: return
        data = cb['data']
        chat_id = cb['message']['chat']['id']
        msg_id = cb['message']['message_id']
        await self.answer_cb(cb['id'])

        if data == "back_main":
            await self.edit_msg(chat_id, msg_id, "🔐 Main Menu", self.main_menu_keyboard())

        elif data == "m_import":
            self.user_states[uid] = "import_zip"
            await self.send_msg(chat_id, "📦 Send a ZIP file with .json/.telethon sessions inside.")

        elif data == "m_export":
            await self.export_zip(chat_id)

        elif data == "m_check":
            await self.check_sessions(chat_id)

        elif data == "m_refresh":
            await self.refresh_sessions(chat_id)

        elif data == "m_remove":
            await self.remove_devices(chat_id)

        elif data == "m_2fa":
            kb = {
                'inline_keyboard': [
                    [{'text': "🔐 Enable 2FA", 'callback_data': "2fa_enable"},
                     {'text': "🔓 Disable 2FA", 'callback_data': "2fa_disable"}],
                    [{'text': "✏️ Change 2FA", 'callback_data': "2fa_change"}],
                    [{'text': "🔙 Back", 'callback_data': "back_main"}]
                ]
            }
            await self.edit_msg(chat_id, msg_id, "🔐 2FA Management", kb)

        elif data == "m_years":
            await self.show_years(chat_id)

        elif data == "m_country":
            await self.show_country(chat_id)

        elif data == "m_gyear":
            await self.show_group_year(chat_id)

        elif data == "m_exjson":
            await self.export_valid_json(chat_id)

        elif data == "m_api":
            self.user_states[uid] = "api_id"
            await self.send_msg(chat_id, "🔑 Enter default api_id:")

        elif data == "m_stats":
            total = self.db.total_sessions()
            v = self.db.count_by_status("valid")
            b = self.db.count_by_status("banned")
            e = self.db.count_by_status("error")
            db2 = self.db.conn()
            tfa = db2.execute("SELECT COUNT(*) FROM sessions WHERE has_2fa=1").fetchone()[0]
            db2.close()
            await self.edit_msg(chat_id, msg_id,
                f"📊 <b>Stats:</b>\n🔢 Total: {total}\n✅ Valid: {v}\n❌ Banned: {b}\n⚠️ Errors: {e}\n🔐 2FA: {tfa}",
                self.simple_back())

        elif data in ("2fa_enable", "2fa_disable", "2fa_change"):
            self.user_states[uid] = data
            if data == "2fa_enable":
                await self.send_msg(chat_id, "🔑 Send the <b>new</b> 2FA password:")
            elif data == "2fa_disable":
                await self.send_msg(chat_id, "🔑 Send the <b>current</b> 2FA password to disable:")
            else:
                self.user_states[uid] = "2fa_change_old"
                await self.send_msg(chat_id, "🔑 Send the <b>old</b> 2FA password first:")


    async def handle_text(self, msg):
        uid = msg['from']['id']
        if OWNER_ID and uid != OWNER_ID: return
        text = msg['text']
        chat_id = msg['chat']['id']
        state = self.user_states.get(uid)

        if not state: return


        if state == "api_id":
            self.user_states[uid] = "api_hash"
            self.db.set_setting("tmp_api_id", text)
            await self.send_msg(chat_id, "🔑 Now enter api_hash:")

        elif state == "api_hash":
            api_id = self.db.get_setting("tmp_api_id", "")
            self.db.set_setting("api_id", api_id)
            self.db.set_setting("api_hash", text)
            del self.user_states[uid]
            await self.send_msg(chat_id, f"✅ API saved:\n<code>{api_id}</code>\n<code>{text}</code>", self.main_menu_keyboard())


        elif state == "2fa_enable":
            del self.user_states[uid]
            await self.run_2fa(chat_id, "enable", new_pass=text)

        elif state == "2fa_disable":
            del self.user_states[uid]
            await self.run_2fa(chat_id, "disable", old_pass=text)

        elif state == "2fa_change_old":
            self.user_states[uid] = "2fa_change_new"
            self.db.set_setting("tmp_2fa_old", text)
            await self.send_msg(chat_id, "🔑 Now enter the <b>new</b> 2FA password:")

        elif state == "2fa_change_new":
            old = self.db.get_setting("tmp_2fa_old", "")
            del self.user_states[uid]
            await self.run_2fa(chat_id, "change", old_pass=old, new_pass=text)


    async def handle_document(self, msg):
        uid = msg['from']['id']
        if OWNER_ID and uid != OWNER_ID: return
        if self.user_states.get(uid) != "import_zip": return
        del self.user_states[uid]

        file_id = msg['document']['file_id']
        fname = msg['document'].get('file_name', 'file')
        data = await self.download_file(file_id)
        if not data:
            return await self.send_msg(msg['chat']['id'], "❌ Failed to download file.")

        count = 0
        default_api = self.db.get_setting("api_id") or API_ID
        default_hash = self.db.get_setting("api_hash") or API_HASH

        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for name in zf.namelist():
                    raw = zf.read(name).decode("utf-8", errors="ignore").strip()
                    phone = os.path.splitext(os.path.basename(name))[0]
                    if name.endswith((".session", ".telethon")):
                        self.db.add_session(phone, raw, "telethon", default_api, default_hash)
                        count += 1
                    elif name.endswith(".json"):
                        try:
                            content = json.loads(raw)
                            if isinstance(content, list):
                                for item in content:
                                    p = item.get("phone", "")
                                    s = item.get("session", item.get("session_string", ""))
                                    if p and s:
                                        self.db.add_session(p, s, "json",
                                                            item.get("api_id", default_api),
                                                            item.get("api_hash", default_hash),
                                                            item.get("tfa_password"))
                                        count += 1
                            else:
                                p = content.get("phone", phone)
                                s = content.get("session", content.get("session_string", raw))
                                if p and s:
                                    self.db.add_session(p, s, "json", default_api, default_hash,
                                                        content.get("tfa_password"))
                                    count += 1
                        except: pass
            await self.send_msg(msg['chat']['id'], f"✅ Imported {count} sessions.")
        except Exception as e:
            await self.send_msg(msg['chat']['id'], f"❌ Import failed: {e}")


    async def export_zip(self, chat_id):
        sessions = self.db.get_all_sessions()
        if not sessions: return await self.send_msg(chat_id, "❌ No sessions.")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for s in sessions:
                ext = ".session" if s["session_type"] == "telethon" else ".json"
                zf.writestr(f"{s['phone']}{ext}", s["session_data"])
        buf.seek(0)
        form = aiohttp.FormData()
        form.add_field('chat_id', str(chat_id))
        form.add_field('document', buf, filename='sessions.zip')
        async with self.session.post(f"{API_URL}/sendDocument", data=form) as resp:
            pass

    async def check_sessions(self, chat_id):
        sessions = self.db.get_all_sessions()
        if not sessions: return await self.send_msg(chat_id, "❌ No sessions.")
        msg = await self.send_msg(chat_id, f"🔍 Checking {len(sessions)} sessions...")
        msg_id = msg['result']['message_id']
        valid = banned = error = tfa = 0
        default_api = self.db.get_setting("api_id") or API_ID
        default_hash = self.db.get_setting("api_hash") or API_HASH
        for s in sessions:
            aid = s["api_id"] or default_api
            ahash = s["api_hash"] or default_hash
            country_flag, country_name = detect_country(s["phone"])
            status, year, has2fa = await self.manager.check_session(s["phone"], s["session_data"], aid, ahash)
            if status == "valid": valid += 1
            elif status == "banned": banned += 1
            else: error += 1
            if has2fa: tfa += 1
            self.db.update_status(s["phone"], status, f"{country_flag} {country_name}", year, has2fa)
        await self.edit_msg(chat_id, msg_id,
            f"✅ Check done:\n✅ Valid: {valid}\n❌ Banned: {banned}\n⚠️ Errors: {error}\n🔐 2FA: {tfa}")

    async def refresh_sessions(self, chat_id):
        invalid = self.db.get_sessions_by_status("invalid")
        if not invalid: return await self.send_msg(chat_id, "✅ No invalid sessions.")
        msg = await self.send_msg(chat_id, f"🔄 Refreshing {len(invalid)}...")
        msg_id = msg['result']['message_id']
        default_api = self.db.get_setting("api_id") or API_ID
        default_hash = self.db.get_setting("api_hash") or API_HASH
        refreshed = 0
        for s in invalid:
            aid = s["api_id"] or default_api; ahash = s["api_hash"] or default_hash
            status, year, has2fa = await self.manager.check_session(s["phone"], s["session_data"], aid, ahash)
            if status == "valid": refreshed += 1
            self.db.update_status(s["phone"], status, s["country"], year, has2fa)
        await self.edit_msg(chat_id, msg_id, f"✅ Refreshed {refreshed} sessions.")

    async def remove_devices(self, chat_id):
        valid = self.db.get_sessions_by_status("valid")
        if not valid: return await self.send_msg(chat_id, "❌ No valid sessions.")
        msg = await self.send_msg(chat_id, f"🚫 Removing devices from {len(valid)}...")
        msg_id = msg['result']['message_id']
        default_api = self.db.get_setting("api_id") or API_ID
        default_hash = self.db.get_setting("api_hash") or API_HASH
        done = 0
        for s in valid:
            aid = s["api_id"] or default_api; ahash = s["api_hash"] or default_hash
            if await self.manager.remove_devices(s["phone"], s["session_data"], aid, ahash):
                done += 1
        await self.edit_msg(chat_id, msg_id, f"✅ Removed devices from {done} accounts.")

    async def run_2fa(self, chat_id, action, new_pass=None, old_pass=None):
        valid = self.db.get_sessions_by_status("valid")
        if not valid: return await self.send_msg(chat_id, "❌ No valid sessions.")
        msg = await self.send_msg(chat_id, "⏳ Processing 2FA...")
        msg_id = msg['result']['message_id']
        default_api = self.db.get_setting("api_id") or API_ID
        default_hash = self.db.get_setting("api_hash") or API_HASH
        done = 0
        for s in valid:
            aid = s["api_id"] or default_api; ahash = s["api_hash"] or default_hash
            if await self.manager.apply_2fa(s["phone"], s["session_data"], aid, ahash, action, new_pass, old_pass):
                if action == "enable":
                    self.db.update_2fa(s["phone"], True, new_pass)
                elif action == "disable":
                    self.db.update_2fa(s["phone"], False, None)
                elif action == "change":
                    self.db.update_2fa(s["phone"], True, new_pass)
                done += 1
        await self.edit_msg(chat_id, msg_id, f"✅ 2FA {action}d on {done} accounts.")

    async def show_years(self, chat_id):
        sessions = self.db.get_all_sessions()
        if not sessions:
            return await self.send_msg(chat_id, "❌ No sessions.")
        txt = "📅 Creation Years:\n"
        for s in sessions:
            yr = s["creation_year"] or "?"
            tfa = " 🔐" if s["has_2fa"] else ""
            txt += f"📱 {s['phone']} → 📅 {yr}{tfa}\n"
        for chunk in split_text(txt):
            await self.send_msg(chat_id, chunk)

    async def show_country(self, chat_id):
        sessions = self.db.get_all_sessions()
        if not sessions:
            return await self.send_msg(chat_id, "❌ No sessions.")
        groups = defaultdict(list)
        for s in sessions:
            country = s["country"] or detect_country(s["phone"])[0] + " " + detect_country(s["phone"])[1]
            groups[country].append(s["phone"])
        txt = "🌍 Country Groups:\n"
        for country, phones in sorted(groups.items()):
            txt += f"\n{country} ({len(phones)}):\n"
            for p in phones:
                txt += f"  • {p}\n"
        for chunk in split_text(txt):
            await self.send_msg(chat_id, chunk)

    async def show_group_year(self, chat_id):
        sessions = self.db.get_all_sessions()
        if not sessions:
            return await self.send_msg(chat_id, "❌ No sessions.")
        groups = defaultdict(list)
        for s in sessions:
            yr = s["creation_year"] or "Unknown"
            groups[yr].append(s["phone"])
        txt = "📆 Group by Year:\n"
        for yr, phones in sorted(groups.items(), key=lambda x: str(x[0])):
            txt += f"\n📅 {yr} ({len(phones)}):\n"
            for p in phones:
                txt += f"  • {p}\n"
        for chunk in split_text(txt):
            await self.send_msg(chat_id, chunk)

    async def export_valid_json(self, chat_id):
        valid = self.db.get_sessions_by_status("valid")
        if not valid:
            return await self.send_msg(chat_id, "❌ No valid sessions.")
        output = []
        for s in valid:
            output.append({
                "phone": s["phone"],
                "session": s["session_data"],
                "session_type": s["session_type"],
                "country": s["country"],
                "creation_year": s["creation_year"],
                "has_2fa": bool(s["has_2fa"]),
                "tfa_password": s["tfa_password"] or "",
                "api_id": s["api_id"],
                "api_hash": s["api_hash"]
            })
        json_str = json.dumps(output, ensure_ascii=False, indent=2)
        buf = io.BytesIO(json_str.encode())
        form = aiohttp.FormData()
        form.add_field('chat_id', str(chat_id))
        form.add_field('document', buf, filename='valid_sessions.json')
        async with self.session.post(f"{API_URL}/sendDocument", data=form):
            pass

    
    async def get_updates(self):
        params = {'offset': self.offset, 'timeout': 30,
                  'allowed_updates': ['message', 'callback_query']}
        try:
            async with self.session.get(f"{API_URL}/getUpdates", params=params) as resp:
                data = await resp.json()
                if data['ok']:
                    return data['result']
                else:
                    logger.error(f"getUpdates error: {data}")
                    return []
        except Exception as e:
            logger.error(f"Exception: {e}")
            return []

    async def process_update(self, update):
        try:
            self.offset = update['update_id'] + 1
            if 'message' in update:
                msg = update['message']
                if msg['chat']['type'] != 'private':
                    return
                if 'text' in msg:
                    text = msg['text']
                    if text.startswith('/start'):
                        await self.handle_start(msg)
                    elif text.startswith('/help'):
                        await self.send_msg(msg['chat']['id'], "🔐 Use buttons to manage sessions.")
                    else:
                        await self.handle_text(msg)
                elif 'document' in msg:
                    await self.handle_document(msg)
            elif 'callback_query' in update:
                await self.handle_callback(update['callback_query'])
        except Exception as e:
            logger.error(f"process update error: {e}")

    async def run(self):
        self.session = aiohttp.ClientSession()
        logger.info("Bot started with getUpdates...")
        try:
            while True:
                updates = await self.get_updates()
                for upd in updates:
                    await self.process_update(upd)
                if not updates:
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped")
        finally:
            await self.session.close()


async def main():
    os.makedirs("sessions", exist_ok=True)
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Set BOT_TOKEN in .env"); return
    if not API_ID or API_HASH == "YOUR_API_HASH_HERE":
        print("❌ Set API_ID/API_HASH"); return
    bot = TelegramBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
