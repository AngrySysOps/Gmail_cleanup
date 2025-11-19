# Gmail Bulk Deleter (PyQt + IMAP)

`gmail_cleanup.py` is a standalone PyQt5 desktop application that connects to Gmail over IMAP, lets you see how many messages live inside each label, and bulk deletes them in a controlled way. Everything runs locally: the app uses SSL-encrypted IMAP sessions, worker threads for long-running operations, and no Google OAuth or cloud services.

**Author:** Piotr Tarnawski (Angry Admin) | <https://www.angrysysops.com> | <https://playhackmenow.com> | @TheTechWorldPod

## Feature Highlights

- Neon-styled PyQt5 UI with an animated login-to-main transition, log console, and detailed status messages.
- Secure IMAP over SSL (port 993) using Gmail App Passwords instead of stored OAuth tokens.
- Dynamic folder discovery with **Select All / Deselect All** buttons plus an in-app help dialog on both screens.
- Scan mode counts messages in any combination of folders without touching their contents.
- Delete mode supports **Move to Trash** (recoverable) and **Permanent Delete** (irreversible) workflows with progress updates every 100 messages.
- The **STOP** action toggles a shared flag checked inside worker threads so scans or deletions can be cancelled safely, and closing the window logs out of IMAP.

## How It Works

1. The login screen collects your Gmail username (with or without `@gmail.com`) and the 16-character App Password that Gmail issues for IMAP clients.
2. After connecting through `imaplib.IMAP4_SSL`, the UI fades into the main dashboard where every IMAP folder (except `[Gmail]` and `Notes`) appears as a checkbox.
3. Scans iterate through the selected folders in a background thread, call `SELECT` + `SEARCH ALL`, and display counts in the terminal-style log view.
4. Deletes reuse the same folder selection, walk each message UID, and either copy it to `[Gmail]/Trash` or stage it for hard delete by capturing `X-GM-MSGID` values before expunging.
5. The GUI stays responsive because scan and delete actions run in background threads that frequently check the shared `is_running` flag controlled by the **STOP** button.

## Requirements

- Python 3.9+ (imaplib's Gmail extensions and PyQt5 behave best on current interpreters).
- Gmail account with IMAP enabled and 2-Step Verification (App Passwords require it).
- PyQt5 (`pip install PyQt5`). Every other import used by the script comes from the Python standard library.


## Prepare Your Gmail Account

1. Sign in to Gmail on the web and open **Settings -> See all settings -> Forwarding and POP/IMAP**. Enable IMAP and save.
2. Visit <https://myaccount.google.com/security> and turn on **2-Step Verification** if it is not already enabled.
3. Still under Security, open **App passwords**, choose **Mail** as the application and any device label, then generate a 16-character password.
4. Copy that password and plan to paste it into the app instead of your normal Gmail password.

You can revoke the App Password once you finish cleaning up.

## Installation

```bash
git clone https://github.com/AngrySysOps/gmail_cleanup.git
cd gmail_cleanup
python -m venv .venv
.\.venv\Scripts\activate      # Windows PowerShell
pip install --upgrade pip
pip install PyQt5
```

If you prefer not to use a virtual environment, install PyQt5 in the interpreter that will launch the script. The provided `requirements.txt` was kept from an earlier Gmail API prototype; PyQt5 is the dependency that matters for the current UI.

## Running the App

```bash
python gmail_cleanup.py
```

### 1. Connect to Gmail

1. Launch the program and stay on the login view.
2. Enter either `username` or `username@gmail.com` in the **USERNAME** field.
3. Paste your App Password into the **APP PASSWORD** field.
4. Click **CONNECT TO GMAIL**. The status bar and terminal log report the progress. On success the UI fades to the main dashboard and mailbox folders appear automatically.

### 2. Choose Folders

- Each Gmail label returned by IMAP becomes a checkbox (Inbox, Sent, Spam, custom labels, etc.).
- Use **SELECT ALL** or **DESELECT ALL** to bulk toggle the list.
- The log view records how many folders load. This is a quick sanity check that IMAP returned what you expect.

### 3. Pick a Delete Mode

- **Move to Trash (default):** Every message is copied to `[Gmail]/Trash`, flagged as `\Deleted`, and the folder is expunged once the batch completes. Gmail keeps the items for 30 days, so they remain recoverable.
- **Permanent Delete:** The app reads each `X-GM-MSGID`, moves messages into the Trash label, switches to `[Gmail]/Trash`, and runs `EXPUNGE` only on the collected message IDs. This bypasses the 30-day safety net. Use it only when you are sure.

### 4. Scan or Delete

- **SCAN FOLDERS** counts messages in the selected folders without performing any destructive action. Run this first to estimate the cleanup size.
- **DELETE EMAILS** processes the selected folders using the active mode. Progress is logged for each folder and every 100 processed emails.
- **STOP** flips the shared `is_running` flag. Worker threads test that flag between operations so they can finish the current IMAP call and abort the rest safely.

### 5. Monitor and Review

- The terminal panel records every step (connections, folder names, counts, errors, and summaries).
- The status bar mirrors the current operation ("Scanning folders...", "Deletion complete", etc.).
- The **HELP** button (visible on both the login and main screens) opens an in-app reference covering IMAP/App Password setup, safety notes, and troubleshooting advice.

Closing the window or quitting the application triggers `closeEvent`, which logs out of IMAP before the app exits.

## Safety, Limits, and Notes

- Credentials only live in memory for the lifetime of the process. Nothing is written to disk, and IMAP SSL encrypts all traffic.
- Gmail throttles IMAP when labels contain thousands of messages. Expect gradual progress and keep the window open; the log shows how many items ran.
- Folder processing is sequential. If you select multiple folders, the app finishes one before moving to the next.
- Gmail exposes system labels such as `[Gmail]/All Mail`. Selecting them may duplicate work because the same message can appear under multiple labels.
- Permanent deletion removes the messages from Trash immediately. There is no undo.

## Troubleshooting

**Authentication error**  
- Confirm IMAP is enabled.  
- Verify you pasted the App Password, not the main account password.  
- Revoke and reissue the App Password if you suspect a typo, then try again.

**Connection error or timeout**  
- Firewalls or corporate proxies may block TCP 993.  
- Disable VPNs temporarily or whitelist `imap.gmail.com`.  
- Gmail sometimes delays IMAP logins if it suspects unusual activity. Waiting a few minutes usually resolves it.

**No folders listed after connecting**  
- Large Gmail accounts may need a few seconds before IMAP is ready. Wait briefly and re-open the HELP dialog to force a refresh.  
- The app intentionally filters `[Gmail]` and `Notes`. If you expect other labels and they do not appear, check the terminal log for IMAP errors.  
- Make sure the account actually has the folders you are trying to target.

**PyQt5 import error**  
- Run `pip install PyQt5` inside the same environment you use to start the app.  
- Linux desktops sometimes need additional Qt platform plugins (for example `sudo apt install libxcb-xinerama0`).

**Deletion feels stuck**  
- Very large labels trigger Gmail throttling. Watch the log; it prints progress every 100 emails so you can distinguish "slow" from "stalled".  
- Press **STOP** once if you must abort. The app finishes the in-flight IMAP command and then returns to idle.

## FAQ

- **Can I use my normal Gmail password?**  
  No. Gmail now requires App Passwords for IMAP clients when 2-Step Verification is enabled. Regular account passwords will fail with an authentication error.

- **Is scanning safe if I just want counts?**  
  Yes. SCAN only issues `SELECT` and `SEARCH ALL`, so it never flags or deletes messages.

- **What happens if I close the app mid-operation?**  
  The `closeEvent` handler logs out of IMAP. Any deletions already issued remain in Gmail, while the remaining folders stop processing.

- **Does permanent delete really skip the 30-day Trash hold?**  
  Yes. The app removes the Gmail Trash label after expunging specific message IDs, so the items disappear immediately.

- **How do I undo an accidental Move to Trash?**  
  Open Gmail, go to Trash, select the messages, and move them back to the folder you want. Gmail keeps Trash contents for 30 days.

- **Can multiple people run the tool at once on the same account?**  
  Technically yes, but Gmail rate limits IMAP sessions. Running multiple copies at the same time increases the risk of throttling or temporary lockouts.

## Project Structure and Customization

- `gmail_cleanup.py` - the entire application: UI layout, IMAP logic, and threading helpers.
- `requirements.txt` - placeholder list of Google API libraries kept from an earlier prototype. Update it if you want to formally track PyQt5 or future dependencies.

To customize:
- Adjust the folder filter inside `load_folders` if you want to hide additional system labels.
- Edit the stylesheets in `create_login_screen` and `create_main_screen` to match your branding.
- Change the progress logging cadence by modifying the `if i % 100 == 0` block in `delete_emails`.

## Credits and Support

Created by Piotr Tarnawski (Angry Admin). Keep the "Provided by Angry Admin" branding plus the angrysysops.com and playhackmenow.com links if you redistribute the tool unchanged. For updates or contact, follow @TheTechWorldPod.

For extra help:
- File an issue or start a discussion in this repository.
- Review Gmail's IMAP quotas and best practices: <https://support.google.com/mail/answer/7126229>
- Revisit the in-app HELP dialog for condensed setup and security reminders.

## Branding and Licensing Notice

The "Angry Admin Branding License" described below: By cloning, running, or redistributing this project you agree to:

1. Preserve the in-app text **"Provided by Angry Admin"** without alteration.
2. Keep the hyperlinks to **https://www.angrysysops.com**, **https://playhackmenow.com**, **https://buymeacoffee.com/angrysysops**, and the Angry Admin YouTube channel wherever the UI or documentation exposes them.
3. Include this paragraph (or a direct link to it) in any derivative README, documentation bundle, download page, or installer.
4. Reproduce the author credit: **Piotr Tarnawski (Angry Admin) — @TheTechWorldPod**.

If you publish a modified build, you must state that it is based on this project and still comply with the four requirements above. If you cannot accept these conditions, you do not have permission to redistribute the code or assets.
