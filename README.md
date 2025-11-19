# Gmail Bulk Deleter (PyQt + IMAP)

`gmail_cleanup.py` is a standalone PyQt5 desktop application that connects to Gmail over IMAP, shows how many messages live inside each label, and lets you bulk-delete them safely.  
Everything runs locally: IMAP over SSL, worker threads for long-running actions, and **no Google OAuth or cloud dependencies**.

**Author:** Piotr Tarnawski (Angry Admin)  
**Website:** https://www.angrysysops.com  
**Game:** https://playhackmenow.com  
**Social:** @TheTechWorldPod

---

## ✨ Features

- Neon-styled PyQt5 UI with animated login → dashboard transition  
- Secure IMAP over SSL (port 993) using Gmail **App Passwords**  
- Automatic folder discovery with **Select All / Deselect All**  
- **Scan Mode** – counts messages without touching them  
- **Delete Modes:**  
  - Move to Trash (recoverable)  
  - Permanent Delete (irreversible, bypasses 30-day Trash retention)  
- Background worker threads keep UI responsive  
- STOP button safely cancels operations  
- Built-in HELP dialog covering Gmail setup and troubleshooting  

---

## ⚙️ How It Works

1. Enter Gmail username + 16-character App Password.  
2. App connects using `imaplib.IMAP4_SSL`.  
3. Dashboard lists all IMAP folders (except `[Gmail]` and `Notes`).  
4. **Scan Mode** uses `SELECT` + `SEARCH ALL` to count messages.  
5. **Delete Mode** copies or permanently deletes messages, logging progress every 100 items.  
6. Worker threads regularly check a shared `is_running` flag for safe cancelling.

---

## 📦 Requirements

- Python **3.9+**  
- Gmail App Password (requires **2-Step Verification**)  
- PyQt5  

Install dependency:

    pip install PyQt5

All other imports come from the Python standard library.

---

## 🔐 Prepare Your Gmail for IMAP

1. Gmail → **Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP**  
2. Turn on **2-Step Verification** at https://myaccount.google.com/security  
3. Generate an **App Password** and choose “Mail” as the app.  
4. Use the App Password in the app (not your normal Gmail password).  
5. You may revoke the App Password after cleanup.

---

## 🛠 Installation

    git clone https://github.com/AngrySysOps/gmail_cleanup.git
    cd gmail_cleanup

    python -m venv .venv
    # Windows PowerShell
    .\.venv\Scripts\Activate

    pip install --upgrade pip
    pip install PyQt5

If you prefer not to use a virtual environment, install PyQt5 into the interpreter that will run the script.

---

## 🚀 Running the App

    python gmail_cleanup.py

### 1. Connect to Gmail

- Enter username (with or without `@gmail.com`).  
- Paste the App Password.  
- Click **CONNECT TO GMAIL**.  
- On success, the UI fades to the main dashboard and folders load.

### 2. Choose Folders

- All IMAP labels appear as checkboxes (Inbox, Sent, Spam, custom labels, etc.).  
- Use **SELECT ALL** or **DESELECT ALL** to bulk-toggle.  
- The log view records how many folders were loaded.

### 3. Choose Delete Mode

- **Move to Trash** – Gmail keeps emails in Trash for 30 days (recoverable).  
- **Permanent Delete** – messages are expunged and disappear immediately. Use with care.

### 4. Scan or Delete

- **SCAN FOLDERS** – counts messages in the selected folders without deleting anything.  
- **DELETE EMAILS** – processes selected folders using the active delete mode.  
- Progress is logged per folder and every 100 processed emails.  
- **STOP** flips the shared `is_running` flag so worker threads finish the current IMAP call and then abort safely.

### 5. Monitor Logs

The terminal-style panel records:

- Connection status  
- Folder names and counts  
- Per-batch progress  
- Errors (if any)  
- Final summaries  

The status bar mirrors the current action (`Scanning folders…`, `Deletion complete`, etc.).

---

## 🛡 Safety, Limits & Notes

- Credentials live only in memory; nothing is written to disk.  
- All IMAP traffic is encrypted via SSL.  
- Gmail may throttle IMAP operations on very large folders; progress may appear slow.  
- Folder processing is sequential (one folder fully processed before the next).  
- Selecting system labels like `[Gmail]/All Mail` may cause duplicates.  
- **Permanent Delete** has no undo – deleted emails are gone immediately.

---

## 🧩 Troubleshooting

### Authentication error

- Confirm IMAP is enabled in Gmail settings.  
- Make sure you pasted the **App Password**, not the main account password.  
- Regenerate the App Password if you suspect a typo.

### Connection error / timeout

- Firewalls, VPNs, or proxies may block port 993.  
- Temporarily disable VPN or adjust firewall rules.  
- Gmail can delay or rate-limit logins if it detects unusual activity.

### No folders listed

- Large Gmail accounts may need a few seconds after login.  
- `[Gmail]` and `Notes` are intentionally filtered out.  
- Check the log view for IMAP errors and verify that the account actually has folders.

### PyQt5 import error

- Install PyQt5 in the same environment:

      pip install PyQt5

- On some Linux setups you may need additional Qt platform plugins.

### Deletion feels stuck

- Gmail throttling can slow processing for large labels.  
- The log prints progress every 100 emails to distinguish slow vs stalled.  
- Press **STOP** once if you need to abort; the app will finish the in-flight IMAP command and then return to idle.

---

## ❓ FAQ

**Can I use my normal Gmail password?**  
No. Gmail requires App Passwords for IMAP when 2-Step Verification is enabled.

**Is SCAN safe if I only want counts?**  
Yes. SCAN only issues `SELECT` and `SEARCH ALL`. It does not flag or delete messages.

**What happens if I close the app mid-operation?**  
The `closeEvent` handler logs out of IMAP. Already-issued deletions remain; remaining folders stop processing.

**Does permanent delete really skip the 30-day Trash hold?**  
Yes. The app expunges selected message IDs so they disappear immediately.

**Can multiple people run the tool on the same account?**  
Technically yes, but IMAP rate limits will kick in faster. It is not recommended.

---

## 📁 Project Structure

- `gmail_cleanup.py` – full application: UI, IMAP logic, and threading helpers.  

### Customization Tips

- Adjust folder filtering inside `load_folders()` if you want to hide additional system labels.  
- Modify stylesheets in the UI creation functions to match your own branding.  
- Change the logging cadence in the delete loop if you want more or fewer progress updates.

---

## 🙌 Credits & Support

Created by **Piotr Tarnawski (Angry Admin)**.

If you redistribute this tool unchanged, please keep:

- The in-app text: **"Provided by Angry Admin"**  
- Links to:  
  - https://www.angrysysops.com  
  - https://playhackmenow.com  
  - https://buymeacoffee.com/angrysysops  
- Author credit:  
  **Piotr Tarnawski (Angry Admin) — @TheTechWorldPod**

### Need help?

- Open an Issue in this repository.  
- Review Gmail’s official IMAP guidelines.  
- Use the in-app HELP dialog for condensed setup and security reminders.

---

## 📜 License

This project uses the **Angry Admin Branding License (AABL)**.  
See the full text in the [`LICENSE`](LICENSE) file.
