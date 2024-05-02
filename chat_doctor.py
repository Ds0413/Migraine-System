import socket
import threading
import sys

def chat_input(client):
    while True:
        message = input()
        client.send(bytes(message, "utf-8"))
        if message == "/disconnect":
            break

def chat_listener(client):
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            print(message)
        except ConnectionResetError:
            print("Server disconnected.")
            break

def main():
    if len(sys.argv) < 1:
        print("USAGE: python client.py <IP> <Port>")
        print("EXAMPLE: python client.py localhost 8000")
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(("localhost", 8000))

    username = "Doctor"

    server_socket.send(bytes(username, "utf-8"))
    print("You may begin chatting with your patient.")

    input_thread = threading.Thread(target=chat_input, args=(server_socket,))
    listener_thread = threading.Thread(target=chat_listener, args=(server_socket,))

    input_thread.start()
    listener_thread.start()

    input_thread.join()
    listener_thread.join()

    server_socket.shutdown(socket.SHUT_RDWR)
    server_socket.close()
    print("Disconnected from the chat.")

if __name__ == "__main__":
    main()
