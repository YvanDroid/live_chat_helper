# Builtin
import time, datetime, sys, os
import traceback

# Requires install
import dearpygui.dearpygui as dpg
from chat_downloader import ChatDownloader # Use Indigo128/chat-downloader fork for working YouTube
import pandas as pd

downloader = ChatDownloader()
chat_columns = ["Timestamp", "Author", "Message"]
df = pd.DataFrame(columns=chat_columns) # For storing live chats

unique_chats = 0

dpg.create_context()
dpg.create_viewport(title='YouTube Chat Monitor', width=600, height=300)

today = datetime.datetime.today()
formatted_date = today.strftime('%Y-%m-%d-%H-%M-%S')
filename = os.path.join(os.getcwd(),f"{formatted_date}.csv")

def save_chats(sender, app_data, user_data):
    df.to_csv(app_data['file_path_name'], index=False)


def scroll_to_bottom(sender, app_data, user_data):
    with dpg.mutex():
        y_scroll = dpg.get_y_scroll(user_data[1])
        max_scroll = dpg.get_y_scroll_max(user_data[1])

def chat_filter(message, chat_count):
    # Entry
    entry_timestamp = message['timestamp']/1_000_000
    entry_author = message['author']['name']
    entry_message = message['message']

    new_row = pd.DataFrame([{"Timestamp":entry_timestamp, "Author":entry_author, "Message":entry_message}])
    global df
    author_rows = df[df['Author'] == entry_author]
    unique_rows = author_rows.drop_duplicates(subset=['Message'],keep='first')
    df = pd.concat([df, new_row], ignore_index=True)

    with dpg.table_row(parent="chat_table"):
        dpg.add_text(f"{datetime.datetime.fromtimestamp(entry_timestamp).strftime("%H:%M:%S")}")
        dpg.add_text(entry_author)
        dpg.add_text(entry_message)
    dpg.set_y_scroll("chat_table", dpg.get_y_scroll_max("chat_table"))

    # Check author's previous posts
    num_rows = unique_rows.shape[0]
    unique_rows = pd.concat([unique_rows, new_row], ignore_index=True)
    unique_rows = unique_rows.drop_duplicates(subset=['Message'], keep='first')
    num_unique_rows = unique_rows.shape[0]
    # print(num_rows, num_unique_rows)

    if num_rows == num_unique_rows: # Not unique
        pass
    else:
        with dpg.table_row(parent="unique_table"):
            dpg.add_text(f"{datetime.datetime.fromtimestamp(entry_timestamp).strftime("%H:%M:%S")}")
            dpg.add_text(entry_author)
            dpg.add_text(entry_message)
        dpg.set_y_scroll("unique_table", dpg.get_y_scroll_max("unique_table"))
        global unique_chats
        unique_chats += 1
        dpg.set_value("unique_amount", f'Unique Chats ({unique_chats})')

def start_livechat(sender, app_data, user_data):
    print(app_data)
    print(user_data)
    url = dpg.get_value(user_data)
    print(url)
    if url is None:
        url = app_data

    chat_count = 0
    dpg.add_text("Live Chats", parent="Primary Window", tag="chat_amount")
    with dpg.group(parent="Primary Window", horizontal=True):
        dpg.add_button(label="Save Live Chat", callback=lambda: dpg.show_item("file_dialog_tag"))
    dpg.add_table(tag="chat_table",
                  clipper=True,
                  parent="Primary Window",
                  policy=dpg.mvTable_SizingFixedFit,
                  header_row=True,
                  row_background=True,
                  resizable=True,
                  context_menu_in_body=True,
                  no_host_extendX=True,
                  borders_innerV=True,
                  borders_outerV=True,
                  borders_innerH=True,
                  borders_outerH=True,
                  scrollY=True,
                  scrollX=True,
                  height=300,
                  freeze_rows=1,
                  freeze_columns=1
                  )
    dpg.add_table_column(label="Timestamp", tag="column_timestamp", parent="chat_table", width_fixed=True, width=20)
    dpg.add_table_column(label="Author", tag="column_author", parent="chat_table", width_fixed=True, width=100)
    dpg.add_table_column(label="Message", tag="column_message", parent="chat_table",width_stretch=True)

    dpg.add_text("Unique Chats", parent="Primary Window", tag="unique_amount")
    dpg.add_table(tag="unique_table",
                  clipper=True,
                  parent="Primary Window",
                  policy=dpg.mvTable_SizingFixedFit,
                  header_row=True,
                  row_background=True,
                  resizable=True,
                  context_menu_in_body=True,
                  no_host_extendX=True,
                  borders_innerV=True,
                  borders_outerV=True,
                  borders_innerH=True,
                  borders_outerH=True,
                  scrollY=True,
                  scrollX=True,
                  height=300,
                  freeze_rows=1,
                  freeze_columns=1
                  )
    dpg.add_table_column(label="Timestamp", tag="column_timestamp_u", parent="unique_table", width_fixed=True, width=20)
    dpg.add_table_column(label="Author", tag="column_author_u", parent="unique_table", width_fixed=True, width=100)
    dpg.add_table_column(label="Message", tag="column_message_u", parent="unique_table",width_stretch=True)
    # with open(filename, "w+", encoding='utf-8') as file:
        # file.write("Timestamp, Author, Message\n")
    try:
        for message in downloader.get_chat(url):
            #entry = f"{datetime.datetime.fromtimestamp(message['timestamp']/1_000_000)},{message['author']['name']},{message['message']}"
            # print(entry)
            # file.write(entry+"\n")
            chat_filter(message, chat_count)
            chat_count += 1
            dpg.set_value("chat_amount", f'Live Chats ({chat_count})')

    except Exception:
        # print(f"Something went wrong with the following error: {e}")
        print(traceback.format_exc())
        # exit(2)

# Main Window
with dpg.window(label="Example Window", tag="Primary Window"):
    dpg.add_text("Please enter your YouTube live link")
    input_url = dpg.add_input_text(label="Live YouTube Link", default_value="", on_enter=True, callback=start_livechat)
    dpg.add_button(label="Enter", callback=start_livechat, user_data=input_url)
    with dpg.file_dialog(directory_selector=False,
                         show=False,
                         callback=save_chats,
                         tag='file_dialog_tag',
                         width=700, height=400,
                         default_filename=f"{formatted_date}"):
        dpg.add_file_extension(".csv", color=(255,0,255,255))




dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()

