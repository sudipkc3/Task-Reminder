import webview
import threading
import time
import os
import sys
import platform
import csv
from plyer import notification
import schedule
import uuid
import pystray
from PIL import Image
try:
    import win32com.client
except ImportError:
    win32com = None

# Add winsound import for notification sound on Windows
import winsound

# Global variables
running = True
tray_icon = None
window = None
TASKS_CSV = 'tasks.csv'

def show_window():
    global tray_icon
    if tray_icon:
        tray_icon.stop()
        tray_icon = None
    if window:
        window.show()

# --- System Tray Integration for Windows ---
def on_tray_icon_clicked(icon, item):
    # Left click: show window
    show_window()

def on_tray_icon_right_click(icon, item):
    # Right click: show context menu (handled by pystray)
    pass  # No-op, menu is handled by pystray

def create_system_tray():
    global tray_icon
    try:
        image = Image.open("reminder.ico")
    except FileNotFoundError:
        print("Warning: Could not load 'reminder.ico'. Using default icon.")
        image = Image.new("RGB", (64, 64), color="blue")

    menu = pystray.Menu(
        pystray.MenuItem("Show", lambda: show_window()),
        pystray.MenuItem(
            "Add Task",
            lambda: window.evaluate_js('showAddTaskModal()') if window else print("Warning: Main window not available.")
        ),
        pystray.MenuItem("Exit", exit_app)
    )
    tray_icon = pystray.Icon("Task Reminder", image, "Task Reminder", menu)
    tray_icon.visible = False  # Hide from taskbar, show only in hidden icons
    tray_icon.run_detached()
    # pystray handles right-click menu by default

class Api:
    def add_task(self, task, interval):
        try:
            interval = float(interval)
            if task.strip() and interval > 0:
                task_id = str(uuid.uuid4())
                # Append to CSV
                with open(TASKS_CSV, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([task_id, task, interval])
                # Schedule using the correct interval in minutes (as int)
                schedule.every(int(interval)).minutes.do(self.show_notification, task_id=task_id, task=task).tag(task_id)
                return {"status": "success", "message": f"Task '{task}' added"}
            else:
                return {"status": "error", "message": "Invalid task or interval"}
        except ValueError:
            return {"status": "error", "message": "Invalid interval"}

    def delete_task(self, task_id):
        tasks = self.get_tasks()
        found = False
        # Remove from CSV
        with open(TASKS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for t in tasks:
                if t['id'] != task_id:
                    writer.writerow([t['id'], t['task'], t['interval']])
                else:
                    found = True
        schedule.clear(task_id)
        if found:
            return {"status": "success", "message": "Task deleted"}
        return {"status": "error", "message": "Task not found"}

    def get_tasks(self):
        tasks = []
        if os.path.exists(TASKS_CSV):
            with open(TASKS_CSV, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    # Defensive: skip empty or malformed rows
                    if len(row) == 3 and row[0] and row[1] and row[2]:
                        try:
                            interval = float(row[2])
                        except ValueError:
                            continue
                        tasks.append({'id': row[0], 'task': row[1], 'interval': interval})
        return tasks

    def minimize_to_tray(self):
        if window:
            window.hide()
            create_system_tray()
        return {"status": "success", "message": "Minimized to tray"}

    def toggle_theme(self):
        return {"status": "success", "message": "Theme toggled"}

    def show_notification(self, task_id, task):
        try:
            # Play a notification sound (Windows default sound)
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            if hasattr(notification, 'notify'):
                notify_func = notification.notify  # type: ignore
                if notify_func:
                    notify_func(
                        title="Task Reminder",
                        message=task,
                        app_icon="reminder.ico" if os.path.exists("reminder.ico") else None,
                        timeout=10
                    )
                else:
                    print("Error: notification.notify is None.")
                    return schedule.CancelJob
            else:
                print("Error: plyer.notification is not available.")
                return schedule.CancelJob
            # Do not return schedule.CancelJob on success, so the job repeats
        except Exception as e:
            print(f"Error displaying notification: {e}")
            return schedule.CancelJob

def reminder_thread():
    while running:
        schedule.run_pending()
        time.sleep(0.1)  # Faster polling for second-based scheduling

# --- Window Event Handling ---
def on_window_closing():
    # Minimize to tray instead of closing
    if window:
        window.hide()
        create_system_tray()
    return False  # Prevent window from closing

def exit_app():
    global running, tray_icon
    running = False
    schedule.clear()
    # Prevent double stop or NoneType error
    if tray_icon is not None:
        try:
            tray_icon.stop()
        except Exception as e:
            print(f"Tray icon stop error: {e}")
        tray_icon = None
    if window:
        window.destroy()
    # Use os._exit(0) to force exit without raising SystemExit in pystray handler
    os._exit(0)

def setup_autostart():
    if platform.system() == "Windows" and win32com:
        appdata = os.getenv("APPDATA")
        if not appdata:
            print("Warning: APPDATA not found. Auto-start skipped.")
            return
        startup_folder = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        script_path = os.path.abspath(__file__)
        shortcut_name = "TaskReminder.lnk"
        shortcut_path = os.path.join(startup_folder, shortcut_name)

        if not os.path.exists(shortcut_path):
            try:
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.TargetPath = sys.executable
                shortcut.Arguments = f'"{script_path}"'
                shortcut.WorkingDirectory = os.path.dirname(script_path)
                shortcut.IconLocation = script_path
                shortcut.save()
                print("Auto-start shortcut created.")
            except Exception as e:
                print(f"Warning: Could not create auto-start shortcut: {e}")
    else:
        print("Warning: Auto-start only supported on Windows with pywin32.")

def load_tasks():
    # Only load tasks if tasks.csv exists and is not empty
    if os.path.exists(TASKS_CSV) and os.path.getsize(TASKS_CSV) > 0:
        with open(TASKS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 3:
                    task_id, task, interval = row
                    schedule.every(int(float(interval))).minutes.do(Api().show_notification, task_id=task_id, task=task).tag(task_id)
    else:
        print("No tasks to load from tasks.csv.")

if __name__ == "__main__":
    setup_autostart()
    load_tasks()
    threading.Thread(target=reminder_thread, daemon=True).start()
    window = webview.create_window("Task Reminder", "index.html", js_api=Api(), width=550, height=450, resizable=False)
    # Attach close event to minimize to tray
    window.events.closing += on_window_closing
    try:
        webview.start()
    except KeyboardInterrupt:
        exit_app()
