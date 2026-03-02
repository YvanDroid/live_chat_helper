import time, datetime, sys, os
from chat_downloader import ChatDownloader

# try:
#     print("Locating cookies.txt. Please ensure you have a working cookies.txt in the same folder")
#     cookie_path = os.path.join(os.getcwd(),f"cookies.txt")
#     downloader = ChatDownloader(cookies=cookie_path)
# except:
#     print("Having trouble locating cookies, will try to use without a session token")
#     downloader = ChatDownloader()

downloader = ChatDownloader()

url = input("Please enter the url of the youtube live video by copying your url and right clicking inside this window:\n")
# filename = f"{os.getcwd()}/{datetime.datetime.now()}.csv"
today = datetime.datetime.today()
formatted_date = today.strftime('%Y-%m-%d-%H-%M-%S')
filename = os.path.join(os.getcwd(),f"{formatted_date}.csv")

chat_count = 0

with open(filename, "w+", encoding='utf-8') as file:
    file.write("Timestamp, Author, Message\n")
    try:
        for message in downloader.get_chat(url):
            # Below usually works for livestreams that are already finished
            entry = f"{datetime.datetime.fromtimestamp(message['timestamp']/1_000_000)},{message['author']['name']},{message['message']}"
            print(entry)
            file.write(entry+"\n")
            chat_count += 1

    except Exception as e:
        error_message = input(f"Something went wrong with the following error: {e}  Press enter to quit program")
        exit(2)

finished_message = input(f"Finished downloading {chat_count} chats from YouTube! Should be located at {filename}.\n Press enter to close the program")
