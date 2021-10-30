import subprocess
import json
import socket
from threading import Thread
from time import sleep

ip_address = ""
my_name = ""
port = "12345"
ip_dictionary = {}


def get_ip():
    global ip_address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    finally:
        s.close()


def create_message(message_type, body=""):
    global my_name
    global ip_address
    message = {}
    if my_name == "":
        print("Enter your name: ")
        my_name = input()
    if message_type == "1":
        message = {"name": my_name, "IP": ip_address, "type": message_type}
    elif message_type == "2":
        message = {"name": my_name, "IP": ip_address, "type": message_type}
    elif message_type == "3":
        message = {"name": my_name, "type": message_type, "body": body}
    return json.dumps(message)


def discover_online_devices(discover_message):
    global ip_dictionary
    while True:
        ip_dictionary = {}
        for x in range(1, 255):
            echo = subprocess.Popen(["echo", discover_message], stdout=subprocess.PIPE)
            subprocess.Popen(["nc", "-c", "192.168.1." + str(x), port], stdin=echo.stdout, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        sleep(5)


def show_online_devices():
    global ip_dictionary
    if len(ip_dictionary) == 0:
        print("There is no active user")
    else:
        print("Active Users:")
        for key in ip_dictionary.keys():
            print(key)


def listen_message():
    global ip_dictionary

    while True:
        process = subprocess.run(["nc", "-l", port], text=True, capture_output=True)
        output = process.stdout
        if output == "" or output is None:
            print("There is a problem about your socket you should restart your cmd or computer")
            break

        response = json.loads(output)
        if response["type"] == "1":
            if response["IP"] != ip_address:
                ip_dictionary[response["name"]] = response["IP"]
            respond_message = create_message("2")
            echo = subprocess.Popen(["echo", respond_message], stdout=subprocess.PIPE)
            subprocess.Popen(["nc", "-c", response["IP"], port], stdin=echo.stdout, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        elif response["type"] == "2":
            if response["IP"] != ip_address:
                ip_dictionary[response["name"]] = response["IP"]
        elif response["type"] == "3":
            print(response["name"] + ":   " + response["body"])


def application_user_interface():
    global ip_dictionary
    while True:

        user_input = input()
        if user_input == "list":
            show_online_devices()
        elif user_input.split()[0] == "send":
            receiver = user_input.split()[1]
            if receiver in ip_dictionary.keys():
                receiver_ip = ip_dictionary.get(receiver)
                chat_message = " ".join(user_input.split()[2:])
                json_message = create_message("3", body=chat_message)
                echo = subprocess.Popen(["echo", json_message], stdout=subprocess.PIPE)
                process = subprocess.Popen(["nc", "-c", receiver_ip, port], stdin=echo.stdout,
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                exit_code = process.wait()
                if exit_code != 0:
                    print("User has left!")
                    ip_dictionary.pop(receiver)

            else:
                print("No Such Active User!")
        else:
            print("No Valid Command")

        sleep(0.3)


if __name__ == '__main__':
    get_ip()
    print(ip_address)
    application_ui_thread = Thread(target=application_user_interface)
    listen_thread = Thread(target=listen_message)
    discover_thread = Thread(target=discover_online_devices, args=(create_message("1"),))
    application_ui_thread.start()

    listen_thread.start()
    discover_thread.start()
