<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:000000,50:3b1d78,100:ff4fd8&height=260&section=header&text=Telegram%20Account%0AManager%20Bot&fontSize=48&fontColor=ffffff&animation=fadeIn&fontAlignY=38&descSize=22&descAlignY=60&desc=Bulk%20check%20%7C%202FA%20%7C%20Import/Export%20%7C%20Devices" />
</p>

<!-- Typing Animation -->
<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=24&duration=3500&pause=800&color=AE00FF&center=true&vCenter=true&width=900&lines=Session+Checker;2FA+Manager;Bulk+Account+Tools;Remove+All+Devices;Import+and+Export+ZIP;Country+and+Year+Reports" alt="Typing SVG" />
</p>

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=000000&color=6A0DAD" />
  <img src="https://img.shields.io/badge/Library-Telethon-26A5E4?style=for-the-badge&logo=telegram&logoColor=white&labelColor=000000&color=BD5FFF" />
  <img src="https://img.shields.io/badge/DB-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white&labelColor=000000&color=AE00FF" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge&logo=github&logoColor=white&labelColor=000000&color=6A0DAD" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge&logo=statuspal&logoColor=white&labelColor=000000&color=BD5FFF" />
  <img src="https://komarev.com/ghpvc/?username=i7rvn&label=Profile%20Views&color=AE00FF&style=for-the-badge&abbreviated=true" />
</p>

<!-- Neon Divider -->
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=4&section=header&text=&fontSize=0" width="100%" />

<!-- About Section -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=70&section=header&text=About%20the%20Bot&fontSize=28&fontColor=ffffff&animation=fadeIn" />
</p>

<p align="center">
  <strong style="color: #BD5FFF;">A full‑featured Telegram bot that manages Telegram account sessions.</strong><br/>
  Check validity, detect country and creation year, apply 2FA, remove other devices, and import/export sessions via ZIP – all from a private chat with the bot. Built with <code>Telethon</code> and <code>getUpdates</code> polling, ready to run locally or on a server.
</p>

<!-- Features -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=70&section=header&text=Key%20Features&fontSize=28&fontColor=ffffff&animation=fadeIn" />
</p>

- ✅ **Check sessions** – verify if an account is `valid`, `banned`, or `error`  
- 🔐 **2FA Management** – enable, disable, or change two‑factor passwords in bulk  
- 🚫 **Remove Devices** – call `auth.resetAuthorizations` to log out all other sessions  
- 📥 **Import ZIP** – accept `.zip` files containing `.session`, `.telethon`, or `.json` files with session strings  
- 📤 **Export ZIP** – download all stored sessions as a clean ZIP archive  
- 💾 **Export Valid JSON** – dump only working sessions into a structured JSON file  
- 🌍 **Country Detection** – map phone numbers to flags and country names  
- 📅 **Creation Year** – estimate the account’s creation year from its Telegram ID  
- 📊 **Stats & Reports** – group sessions by status, year, or country with one tap  
- 🔄 **Refresh** – re‑check sessions that were previously marked as `invalid`  
- 🛡️ **Single Owner** – restrict the bot to only one user (`OWNER_ID`)

<!-- Neon Divider -->
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=4&section=header&text=&fontSize=0" width="100%" />

<!-- Setup -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=70&section=header&text=Setup%20%26%20Installation&fontSize=28&fontColor=ffffff&animation=fadeIn" />
</p>

### Getting Credentials

#### Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the instructions.
3. Copy the generated **Bot Token**.
4. Paste it into the `.env` file as `BOT_TOKEN`.

#### API Credentials
1. Go to [my.telegram.org](https://my.telegram.org/auth) and log in.
2. Click **API development tools**.
3. Note your **api_id** and **api_hash**.
4. Add them to `.env` as `API_ID` and `API_HASH`.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/i7rvn/telegram-account-manager.git
   cd telegram-account-manager
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Required packages: `aiohttp`, `python-dotenv`, `telethon` (SQLite3 is built-in).

3. **Configure environment variables**
   Copy `.env.example` to `.env` and fill in your credentials:
   ```ini
   BOT_TOKEN=123456:ABC-DEF...
   API_ID=123456
   API_HASH=your_api_hash_here
   OWNER_ID=your_user_id   # optional – leave 0 to allow anyone
   ```
   > Keep `.env` secure – never commit it to version control.

4. **Run the bot**
   ```bash
   python manager.py
   ```
   The bot starts polling via `getUpdates`. Logs are written to `telegram_manager.log` and printed to the console.

<!-- Neon Divider -->
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=4&section=header&text=&fontSize=0" width="100%" />

<!-- Usage -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=70&section=header&text=Usage&fontSize=28&fontColor=ffffff&animation=fadeIn" />
</p>

### Bot Commands

| Command   | Description |
|-----------|-------------|
| `/start`  | Show the main inline menu |
| `/help`   | Display a short help message |

All other interactions are handled through **inline buttons** in the main menu.

### Inline Menu Options

| Button              | Description |
|---------------------|-------------|
| 📥 Import ZIP       | Upload a ZIP file with `.session`, `.telethon`, or `.json` files |
| 📤 Export ZIP       | Download all stored sessions as a ZIP |
| ✅ Check Sessions   | Validate every account, detect country, year, and 2FA |
| 🔄 Refresh          | Re‑check sessions that were previously `invalid` |
| 🚫 Remove Devices   | Log out all other devices from valid accounts (auth.resetAuthorizations) |
| 🔐 2FA              | Submenu to enable, disable, or change 2FA passwords |
| 📅 Years            | List all accounts with their estimated creation year |
| 🌍 Country          | Group accounts by detected country |
| 📆 Group by Year    | Group accounts by creation year |
| 💾 Export JSON      | Download a JSON file containing only `valid` sessions |
| ⚙️ Set API          | Change the default `api_id` / `api_hash` on the fly |
| 📊 Stats            | Show total, valid, banned, error, and 2FA counts |

For 2FA operations, the bot guides you step‑by‑step to enter the required passwords.

<!-- Neon Divider -->
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=4&section=header&text=&fontSize=0" width="100%" />

<!-- File Structure -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=70&section=header&text=File%20Structure&fontSize=28&fontColor=ffffff&animation=fadeIn" />
</p>

```
telegram-account-manager/
├── manager.py                # Main bot script
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── sessions/                 # Created automatically at runtime
```

<!-- Neon Divider -->
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=4&section=header&text=&fontSize=0" width="100%" />

<!-- Database Schema -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=70&section=header&text=Database%20Schema&fontSize=28&fontColor=ffffff&animation=fadeIn" />
</p>

All data is stored in an SQLite database (`telegram_manager.db`).

**`sessions` table**

| Column         | Type    | Description |
|----------------|---------|-------------|
| `phone`        | TEXT PK | Account phone number |
| `session_data` | TEXT    | Telethon session string |
| `session_type` | TEXT    | `telethon` or `json` |
| `status`       | TEXT    | `valid`, `banned`, `invalid`, `error` |
| `country`      | TEXT    | Flag + country name |
| `creation_year`| INTEGER | Estimated creation year |
| `api_id`       | TEXT    | Custom API ID (if set) |
| `api_hash`     | TEXT    | Custom API hash (if set) |
| `has_2fa`      | INTEGER | 1 if 2FA is enabled |
| `tfa_password` | TEXT    | Stored 2FA password |
| `added_at`     | TIMESTAMP | Date added |
| `checked_at`   | TIMESTAMP | Last check timestamp |

**`settings` table**

| Column  | Type    | Description |
|---------|---------|-------------|
| `key`   | TEXT PK | Setting name |
| `value` | TEXT    | Setting value |

**`users` table**

| Column       | Type    | Description |
|--------------|---------|-------------|
| `user_id`    | INTEGER PK | Telegram user ID |
| `username`   | TEXT    | @username |
| `first_name` | TEXT    | First name |
| `last_name`  | TEXT    | Last name |
| `created_at` | TIMESTAMP | First interaction |

<!-- Neon Divider -->
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=4&section=header&text=&fontSize=0" width="100%" />

<!-- Security Notes -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=70&section=header&text=Security%20Notes&fontSize=28&fontColor=ffffff&animation=fadeIn" />
</p>

- 🔒 **Never share your `.env` file** – it contains sensitive API credentials and bot tokens.
- 🛡️ **Restrict access** – set `OWNER_ID` in `.env` to your own Telegram user ID so only you can interact with the bot.
- 🗄️ **Database protection** – the `telegram_manager.db` file stores session strings; keep it in a safe location and avoid exposing it publicly.
- 🧹 **2FA passwords** – the bot stores 2FA passwords in plain text inside the database. Only store them if absolutely necessary, and handle the database with care.
- 🔄 **Use trusted networks** – when running the bot on a server, ensure it is behind a firewall and only accessible to you.

<!-- Neon Divider -->
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=4&section=header&text=&fontSize=0" width="100%" />

<!-- Contributing -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=70&section=header&text=Contributing&fontSize=28&fontColor=ffffff&animation=fadeIn" />
</p>

Contributions are welcome! If you'd like to improve the bot, fix bugs, or add new features:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

Please make sure to update tests and documentation as appropriate.

<!-- Neon Divider -->
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=4&section=header&text=&fontSize=0" width="100%" />

<!-- Support Section -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:000000,50:3b1d78,100:ff4fd8&height=70&section=header&text=Support%20the%20Project&fontSize=28&fontColor=ffffff&animation=fadeIn" />
</p>

<p align="center">
  <a href="https://www.buymeacoffee.com/i7rvn">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="50" width="210" alt="Buy Me a Coffee" />
  </a>
</p>

<p align="center">
  If you find this tool useful, consider starring the repo ⭐ or dropping a coffee!<br/>
  <a href="https://github.com/i7rvn" style="color: #FF69B4;">@i7rvn</a> – all feedback and contributions are welcome.
</p>

<!-- Footer Wave -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:000000,50:3b1d78,100:ff4fd8&height=160&section=footer" alt="Footer Wave" />
</p>
