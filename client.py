#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import messagebox
import socket
import random
from threading import Thread

root = Tk()
root.geometry("650x650")
#root.geometry('{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight()))
root.wm_title("Python P2P Client Side")

class Client(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.app_name = "P2P Chat"
        self.version = "1.0.0"
        self.author =  "isma91"
        self.nickname = "user" + str(random.randint(0, 123456789))
        self.your_port = random.randint(1000, 9998)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('google.com', 80))
        self.your_ip = self.s.getsockname()[0]
        self.s.close()
        
        self.host = ''
        self.your_channel = "default"
        self.list_friend_channel = {}
        self.server_port = 9999

        self.chat_friend_ip = ""
        self.chat_friend_port = 0000
        self.chat_friend_name = ""
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.server_port))
        msg = 'command=i|{0},{1}:{2}=>{3}'.format(self.nickname, self.your_ip, self.your_port, self.your_channel)
        msg_byte = bytes(msg.encode('utf-8'))
        self.s.send(msg_byte)
        self.s.close()

        msg = 'command=f|{0},{1}:{2}=>{3}'.format(self.nickname, self.your_ip, self.your_port, self.your_channel)
        msg_byte = bytes(msg.encode('utf-8'))
        tmp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmp_s.connect((self.host, self.server_port))
        tmp_s.send(msg_byte)
        
        self.start()
        self.menu()
        self.client_side()

    def run(self):
        self.tmp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tmp_s.bind((self.host, self.your_port))
        self.tmp_s.listen(5)
        while True:
            conn, addr = self.tmp_s.accept()
            response = conn.recv(255)
            data = response.decode()
            command = data[8:9]
            print(data)
            if command == "f":
                if data[10:] != "":
                    channel_ip_port_name = data[10:].split('~')
                    friend_ip_port = channel_ip_port_name[1].split('|*SEPARATOR*|')
                    if channel_ip_port_name[1] == "empty":
                        self.your_channel = channel_ip_port_name[0]
                        self.display_info('No user found in {0}'.format(self.your_channel))
                    elif channel_ip_port_name[1] == "no":
                        self.display_error("Channel {0} not found !!".format(channel_ip_port_name[0]))
                    else:
                        self.your_channel = channel_ip_port_name[0]
                        self.list_friend_channel = {}
                        list_friend = channel_ip_port_name[1].split("|*SEPARATOR*|")
                        for user_list in list_friend:
                            if user_list == "":
                                list_friend.remove("")
                        for user_list in list_friend:
                            name_ip = user_list.split("=>")
                            self.list_friend_channel[name_ip[0]] = name_ip[1]
                    """friend_name_connection = channel_ip_port_name[1]
                    self.friend_channel
                    ip_port = channel_ip_port_name[0].split(":")
                    ip_friend = ip_port[0]
                    port_friend = ip_port[1]
                    self.chat_friend_name = friend_name_connection
                    self.chat_friend_ip = ip_friend
                    self.chat_friend_port = int(port_friend)
                    self.chat_label["text"] = "Chat with {0} here !!".format(self.chat_friend_name)
                    self.chat_label.pack()
                    self.display_info("Successfully connected with {0} !!\n ip : {1} port : {2}".format(friend_name_connection, ip_friend, port_friend))"""
                else:
                    self.display_error("Friend {0} not found !! Check the list in the server side !!".format(data[10:]))
            elif command == "t":
                if data[10:] != "":
                    name_text = data[10:].split("=>")
                    recv_name = name_text[0]
                    recv_text = name_text[1]
                    self.chat_text.insert(END, "{0} : {1}\n".format(recv_name, recv_text))
            elif command == "c":
                if data[10:17] == "success":
                    self.nickname = data[19:]
                    self.nickname_label["text"] = "Welcome {0} !!".format(self.nickname)
                    for friend_name, friend_ip_port in self.list_friend_channel.items():
                        if friend_ip_port == "{0}:{1}".format(self.your_ip, self.your_port):
                            del self.list_friend_channel[friend_name]
                            break
                    self.list_friend_channel[self.nickname] = "{0}:{1}".format(self.your_ip, self.your_port)
                    self.display_info("Nickname changed sucessfully !!")
                else:
                    self.display_error("Nickname already used by someone else !!")

    def quit(self):
        self.s.close()
        print("quitting client")
        root.destroy()

    def user_list_current_channel(self):
        text = ""
        for friend_name, friend_ip_port in self.list_friend_channel.items():
            text = text + friend_name + "\n"
        self.display_info("Here his the user list of {0} :\n{1}".format(self.your_channel, text))

    def send_msg(self, msg):
        msg = msg.strip()
        if msg != "":
            text = "command=t|{0}=>{1}".format(self.nickname, msg)
            self.s.close()
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.host, self.chat_friend_port))
            msg_byte = bytes(text.encode('utf-8'))
            self.s.sendto(msg_byte, (self.chat_friend_ip, self.chat_friend_port))
            self.s.close()
            self.chat_text.insert(END, "{0} : {1}\n".format(self.nickname, msg))

    def display_error(self, error_message):
        messagebox.showerror("Some trouble here !!", error_message)
    def display_info(self, info_message):
        messagebox.showinfo("Some info here !!", info_message)

    """ Method for menu """
    def about(self):
        self.display_info("{0} version {1}\n made by {2}".format(self.app_name, self.version, self.author))

    def get_ip(self):
        self.display_info("Your local ip is\n{0}".format(self.your_ip))
    """ End Method for menu """

    def create_channel(self, channel_name):
        channel_name = channel_name.strip()
        if channel_name != "":
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.host, self.server_port))
            msg = 'command=n|{0}=>{1}'.format(self.nickname, channel_name)
            msg_byte = bytes(msg.encode('utf-8'))
            self.s.send(msg_byte)
            self.s.close()

    def menu(self):
        menubar = Menu(root)

        menu_file = Menu(menubar, tearoff = 0)
        menu_file.add_command(label = "Get your ip", command = self.get_ip)
        menu_file.add_command(label = "Get current channel user list", command = self.user_list_current_channel)
        menu_file.add_separator()
        menu_file.add_command(label = "Quit", command = lambda : self.quit())
        menubar.add_cascade(label = "File", menu = menu_file)

        menu_about = Menu(menubar, tearoff = 0)
        menu_about.add_command(label = "About", command = self.about)
        menubar.add_cascade(label = "Help", menu = menu_about)

        root.config(menu = menubar)

    def change_nickname(self, nickname):
        nickname = nickname.strip()
        if nickname != "":
            msg = 'command=c|{0},{1}:{2}=>{3}'.format(nickname, self.your_ip, self.your_port, self.your_channel)
            msg_byte = bytes(msg.encode('utf-8'))
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.host, self.server_port))
            self.s.send(msg_byte)
            self.s.close()

    def connection_with_channel(self, channel_name):
        channel = channel_name.strip()
        if channel != "":
            msg = 'command=f|{0},{1}:{2}=>{3}'.format(self.nickname, self.your_ip, self.your_port, channel)
            msg_byte = bytes(msg.encode('utf-8'))
            tmp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tmp_s.connect((self.host, self.server_port))
            tmp_s.send(msg_byte)

    def client_side(self):
        client_labelframe = LabelFrame(root, text = "Client side")
        client_labelframe.pack(fill = "both", expand = "yes")

        create_channel_value = StringVar()
        create_channel_input = Entry(client_labelframe, textvariable = create_channel_value).pack()
        create_channel_button = Button(client_labelframe, text = "Create another channel", command = lambda : self.create_channel(create_channel_value.get())).pack()

        change_nickname_value = StringVar()
        change_nickname_input = Entry(client_labelframe, textvariable = change_nickname_value).pack()
        change_nickname_button = Button(client_labelframe, text = "Change your nickname", command = lambda : self.change_nickname(change_nickname_value.get())).pack()
        
        self.nickname_label = Label(client_labelframe, text = "Welcome {0} !!".format(self.nickname))
        self.nickname_label.pack()

        channel_to_chat_label = Label(client_labelframe, text = "Write your channel to communicate with them").pack()
        channel_to_chat_value = StringVar()
        channel_to_chat_input = Entry(client_labelframe, textvariable = channel_to_chat_value).pack()
        channel_to_chat_button = Button(client_labelframe, text = "Connection", command = lambda : self.connection_with_channel(channel_to_chat_value.get())).pack()
        
        self.chat_text = Text(client_labelframe)
        self.chat_text.pack(fill = "both", expand = "yes")
        self.chat_label = Label(client_labelframe, text = "")
        self.chat_label.pack()
        chat_value = StringVar()
        chat_input = Entry(client_labelframe, textvariable = chat_value).pack()
        chat_button = Button(client_labelframe, text = "Send", command = lambda : self.send_msg(chat_value.get())).pack()

client = Client()
root.mainloop()