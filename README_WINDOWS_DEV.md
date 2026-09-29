# Le-Francais: Windows Local Development Guide

This guide allows you to run the **le-francais** development environment on Windows with zero manual installation of Python, PostgreSQL, or system services.

---

## Quickstart in 3 Steps

### Step 1: Initial Setup (Run Once)
1. Double-click `setup.bat` in the project root folder.
2. When prompted:
   ```text
   Enter project secrets decryption password:
   ```
   Type the project password provided by the project administrator and press **Enter** (the input will be hidden for security).
3. The script will automatically:
   - Download the isolated Python 3.7 runtime (Micromamba).
   - Download and configure the portable PostgreSQL database engine on port `5433`.
   - Restore the baseline development databases (`courses` and `le_francais`).
   - Configure all security certificates and dependencies.
4. When finished, you will see `Setup complete!`. Press any key to close the window.

> **Note on Windows Firewall Popup:** During setup or when launching for the first time, Windows Defender Firewall may show a notification saying:
> *"Windows Defender Firewall has blocked some features of this app"* (for `postgres.exe` or `python.exe`).
> * Simply click **"Allow access"** (or "Cancel" — both will work).
> * This is standard Windows behavior when a database or web server opens an internal communication port. It only asks the first time.

---

### Step 2: Daily Development
Whenever you want to work on the project:
1. Double-click **`start.bat`**.
2. It will automatically:
   - Check and start the database server.
   - Start the local web server.
   - Automatically open **`http://127.0.0.1:8000`** in your default web browser as soon as the site is ready.
3. Keep the terminal window open while you work. Any changes you make to Python files or templates will automatically reload.

---

### Step 3: Stopping the Server
When you are finished working:
1. Press `Ctrl + C` in the `start.bat` terminal window (or simply close the window).
2. To shut down the background database server, double-click **`stop.bat`**.

---

## Troubleshooting

### Q: What if I accidentally close the window and start.bat won't open?
* `start.bat` is designed to be resilient to unexpected exits. Simply double-click `start.bat` again; it will automatically reconnect to the running database or clean any stale lockfiles.
* If you ever want to do a clean restart, double-click `stop.bat` first, then run `start.bat`.

### Q: Will running `setup.bat` again erase my local changes?
* **No.** `setup.bat` contains an automatic data-loss guard (`.restore_complete`). If the database has already been restored, it will safely skip the import step to preserve your local work.

### Q: Port conflict on port 5433 or 8000?
* The local portable database is pre-configured to use port **5433** to avoid collisions with any other PostgreSQL installed on your computer.
* If port `8000` is already in use by another program, you can edit `start.bat` and change `8000` to `8080` (in both the browser opener line and the `runserver` line).
