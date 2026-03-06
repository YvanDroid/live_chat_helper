# Builtin
import time, datetime, sys, os
import traceback, threading

# Requires install
import dearpygui.dearpygui as dpg
from chat_downloader import ChatDownloader # Use Indigo128/chat-downloader fork for working YouTube
import pandas as pd
import pyperclip


downloader = ChatDownloader()
chat_columns = ["Timestamp", "Author", "Message"]
df = pd.DataFrame(columns=chat_columns) # For storing live chats
unique_df = pd.DataFrame(columns=chat_columns) # For storing unique instances of chats
current_highlight = ""
unique_chats = 0
chat_count = 0

# For toggling between chats
chat_autoscroll = 1
unique_autoscroll = 1
scroll_status = {0: "Autoscrolling Off",
                 1: "Autoscrolling On"}



url = ""

dpg.create_context()
dpg.create_viewport(title='YouTube Chat Monitor', width=600, height=300)

today = datetime.datetime.today()
formatted_date = today.strftime('%Y-%m-%d-%H-%M-%S')
filename = os.path.join(os.getcwd(),f"{formatted_date}.csv")
#
# def on_mouse_wheel():
#     if dpg.is_item_hovered("unique_table"):
#         global unique_autoscroll
#         unique_autoscroll = 0
#     if dpg.is_item_hovered("chat_table"):
#         global chat_autoscroll
#         chat_autoscroll = 0

def toggle_autoscroll(sender, app_data, user_data):
    if user_data == "unique":
        global unique_autoscroll
        unique_autoscroll ^= 1
        print(unique_autoscroll)
        dpg.configure_item("unique_scroll_button", label=scroll_status[unique_autoscroll])
    if user_data == "chat":
        global chat_autoscroll
        chat_autoscroll ^= 1
        print(chat_autoscroll)
        dpg.configure_item("chat_scroll_button", label=scroll_status[chat_autoscroll])

def bottom_of_table(sender, app_data, user_data):
    dpg.set_y_scroll(user_data, dpg.get_y_scroll_max(user_data))

def copy_to_clipboard(sender, app_data, user_data):
    print(f'App: {app_data} \nUser: {user_data}')
    global current_highlight
    pyperclip.copy(current_highlight)
    print(f"Copied to clipboard: {current_highlight}")

def new_unique(sender, app_data, user_data):
    # Random row from the unique_df
    global unique_df
    random_row = df.sample(n=1, random_state=42).iloc[0]
    print(random_row)
    display_text = ', '.join(map(str, random_row.tolist()[1:]))
    dpg.set_value("highlight_text", display_text)
    global current_highlight
    current_highlight = display_text


def row_to_display(sender, app_data, user_data):
    # Add this to a bottom row section that lets you do the following:
    # Save the chat to clipboard, select a random unique chat
    # user_data should be a tuple detailing the dataframe and the row index
    print(user_data)
    print(app_data)
    if user_data[1] == "chats":
        global df # Shallow copy the dataframe to stop the thread from being interrupted
        copy = df.copy(deep=False)
        data = copy
        print(data)
    if user_data[1] == "unique":
        global unique_df
        data = unique_df
        print(data)
    display_text = ', '.join(map(str, data.iloc[user_data[0]].tolist()[1:]))
    dpg.set_value("highlight_text", display_text)
    global current_highlight
    current_highlight = display_text

def save_chats(sender, app_data, user_data):
    df.to_csv(app_data['file_path_name'], index=False)

def grab_chats():
    global url, chat_count
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
        dpg.add_selectable(label=entry_message, span_columns=True, callback=row_to_display, user_data=(chat_count, "chats"))
        # NOTE: Assess memory increases due to this change
    # TODO: Make toggleable
    if chat_autoscroll:
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
        global unique_chats
        with dpg.table_row(parent="unique_table"):
            dpg.add_text(f"{datetime.datetime.fromtimestamp(entry_timestamp).strftime("%H:%M:%S")}")
            dpg.add_text(entry_author)
            # dpg.add_text(entry_message)
            dpg.add_selectable(label=entry_message, span_columns=True, callback=row_to_display, user_data=(unique_chats, "unique"))
        # TODO: Make toggleable
        if unique_autoscroll:
            dpg.set_y_scroll("unique_table", dpg.get_y_scroll_max("unique_table"))
        global unique_df
        unique_df = pd.concat([unique_df, new_row], ignore_index=True)
        unique_chats += 1
        dpg.set_value("unique_amount", f'Unique Chats ({unique_chats})')

def start_livechat(sender, app_data, user_data):
    global url
    print(app_data)
    print(user_data)
    url = dpg.get_value(user_data)
    print(url)
    if url is None:
        url = app_data
    global chat_count
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
    with dpg.group(parent="Primary Window", horizontal=True):
        dpg.add_button(label="Autoscrolling On", tag="chat_scroll_button", callback=toggle_autoscroll, user_data="chat")
        dpg.add_button(label="Scroll to bottom", callback=bottom_of_table, user_data="chat_table")
    
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
    with dpg.group(parent="Primary Window", horizontal=True):
        dpg.add_button(label="Autoscrolling On",tag="unique_scroll_button" ,callback=toggle_autoscroll, user_data="unique")
        dpg.add_button(label="Scroll to bottom", callback=bottom_of_table, user_data="unique_table")
    # with open(filename, "w+", encoding='utf-8') as file:
        # file.write("Timestamp, Author, Message\n")

    dpg.add_text(label="Highlighted Message:", parent="Primary Window")
    highlight_text = dpg.add_text(label="", tag="highlight_text", parent="Primary Window")
    with dpg.group(parent="Primary Window", horizontal=True):
        dpg.add_button(label="Copy to Clipboard", callback=copy_to_clipboard, user_data=highlight_text)
        dpg.add_button(label="New Unique Chat", callback=new_unique)

    thread = threading.Thread(target=grab_chats)
    thread.start()
    print("Obtaining chats")

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
#
# with dpg.handler_registry():
#     dpg.add_mouse_wheel_handler(callback=on_mouse_wheel)



dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()

