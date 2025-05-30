# Task Reminder Application

A simple desktop reminder application to help you manage and get notified about your tasks.

## Requirements

- Python 3.10 or higher
- Windows OS (recommended)
- Recommended: Use the provided virtual environment (`reminder_venv`) or create a new one

### Python Packages
- bottle
- pystray
- pillow
- plyer
- schedule
- tinydb
- pywebview

All required packages are listed in `requirements.txt`.

## Setup & Installation

1. **Clone or Download the Project**
   - Download or clone this repository to your local machine.

2. **(Optional) Create and Activate Virtual Environment**
   - Open PowerShell and navigate to the project directory.
   - To use the provided venv:
     ```powershell
     .\reminder_venv\Scripts\Activate
     ```
   - Or create a new one:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate
     ```

3. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

## Running the Program

1. Make sure your virtual environment is activated (if using one).
2. Run the main script:
   ```powershell
   python task_reminder.py
   ```
3. The application will start and run in the background/system tray.

## Importing/Exporting Tasks

- Tasks are stored in `tasks.csv`.
- You can edit this file directly using Excel or a text editor.
- Ensure the file format is preserved (CSV, comma-separated).

## Precautions

- Do not delete or rename `tasks.csv` while the program is running.
- Ensure all dependencies are installed in your environment.
- If you encounter permission issues, try running PowerShell as Administrator.
- For best results, keep the application running to receive timely reminders.

## Contact Me

For questions, suggestions, or bug reports, please contact:

- **Sudip KC**
- Email: sudipkc289@gmail.com
- GitHub: [your-github-username](https://github.com/sudipkc3)

---
Feel free to customize this project as needed !
Don't forget to give credit.🐈🐱
