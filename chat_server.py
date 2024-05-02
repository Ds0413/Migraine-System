import socket
import threading
import pickle
import os
import sys
import time
from datetime import datetime


class ChatRoom:
    def __init__(self):
        self.clients = {}
        self.chat_log = []
        self.log_file = "chat_log.txt"
        self.log_lock = threading.Lock()

    def connect(self, username, client, doc_name):
        self.clients[username] = (client, doc_name)
        # Create or open a chat log file based on the patient's username and doctor's name
        folder_path = 'chat_logs'
        chat_log_file = os.path.join(folder_path, f'{username}_{doc_name}_chatlog.txt')

        # Whether the file exists or not, print the header
        header = f"\nChat Log between {username} and {doc_name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        if os.path.isfile(chat_log_file):
            with open(chat_log_file, "a") as log_file:
                log_file.write(header)

        if os.path.isfile(chat_log_file):
            # The file already exists, do nothing
            pass

        # if os.path.isfile(chat_log_file):
        #     with open(chat_log_file, "r") as existing_log:
        #         self.chat_log.extend(existing_log.readlines())


    def disconnect(self, username):
        with self.log_lock:
            self.log_message(f"User Disconnected: {username}")
            # Save the chat log to the respective file upon disconnection
            client, doc_name = self.clients.get(username, (None, None))
            if client and doc_name:
                folder_path = 'chat_logs'
                chat_log_file = os.path.join(folder_path, f'{username}_{doc_name}_chatlog.txt')
                if os.path.isfile(chat_log_file):
                    with open(chat_log_file, "a") as log_file:
                        log_file.writelines(self.chat_log)

    # if username in self.clients:
    #     del self.clients[username]

    def send_message(self, message, sender):
        formatted_message = f"\n{sender}: {message}\n"
        with self.log_lock:
            self.log_message(formatted_message)
        for username, (client, _) in self.clients.items():
            if username != sender:
                client.send(bytes(formatted_message, "utf-8"))

    def log_message(self, message):
        self.chat_log.append(message)
        with open(self.log_file, "a") as log_file:
            log_file.write(message + "\n")


def chat_handler(client, username, chat_room, doc_name):
    chat_room.connect(username, client, doc_name)
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message == "/disconnect":
                chat_room.disconnect(username)
                print("User Disconnected:", username)
                break
            else:
                chat_room.send_message(message, username)
        except ConnectionResetError:
            chat_room.disconnect(username)
            print("User Disconnected:", username, "| |")
            break


def main():
    doc_name = sys.argv[1]
    chat_room = ChatRoom()
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(("localhost", 8000))
    listen_socket.listen(1)
    print("Chat Server running")

    while True:
        client, _ = listen_socket.accept()
        username = client.recv(1024).decode("utf-8")
        chat_room.connect(username, client, doc_name)
        print("User Connected:", username)

        threading.Thread(target=chat_handler, args=(client, username, chat_room, doc_name)).start()


if __name__ == "__main__":
    main()
