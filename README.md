# Live Chat Helper
This program is designed to take a YouTube Live link and keep track of all the chats sent. It will also keep track of any unique chats from users. You can save chats for after the stream.

## Roadmap
Features I would like to work on:
- [x] Randomized selection of unique chats
- [] Saving unique chats
- [x] Method for copying unique chats to clipboard
- [] Better unique chat filtering (based on ignore patterns)
- [] Build methods for packaging the application

## Installation
To use this application, you will need the following libraries:
- Pandas
- chat_downloader (use Indigo128/chat_downloader fork for fixed YouTube)
- DearPyGUI (for the user interface)
- pyperclip (for copying text to the clipboard)

## Running
You can either:
- Run the python script inside a virtual environment after cloning and installing dependencies.
On linux
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python yt_chat_downloader_gui.py
```
On windows
```powershell
python -m venv .venv
source .venv/bin/activate.ps1
pip install -r requirements.txt
python yt_chat_downloader_gui.py
```
- Run the script from the release builds for different platforms.

## Building
Building this application requires you to install the following extra dependencies:
- PyInstaller (for building a package that can be sent to others without the need for a python environment)

Then after it is installed, you can run:
```bash
pyinstaller yt_chat_downloader_gui.py --onefile
```
And it will build for your platform, allowing you to send this program to other people without the need for python to be installed.
