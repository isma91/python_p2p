#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import messagebox
from threading import Thread
import socket

root = Tk()
root.geometry('{}x{}'.format(int(root.winfo_screenwidth() / 2), int(root.winfo_screenheight() / 2)))
root.wm_title("Python P2P Server Side")

class Server(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.app_name = "P2P Chat Server"
        self.version = "1.0.0"
        self.author =  "isma91"
        self.list_channel = {"default" : [], "first_year" : [], "second_year" : []}
        self.your_host = ''
        self.your_port = 9998
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.menu()
        self.start()

    def quit(self):
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        print("quitting server")
        root.destroy()

    def list(self):
        text = ""
        for channel_name, list_user in self.list_channel.items():
            if len(list_user) == 0:
                text = text + "Channel {0} is empty\n".format(channel_name)
            else:
                text = text + "Channel {0} : {1} user(s)\n".format(channel_name, len(list_user))
                for user_name_ip_port in list_user:
                    user_name_ip_port = user_name_ip_port.split("=>")
                    user_name = user_name_ip_port[0]
                    user_ip_port = user_name_ip_port[1].split(":")
                    user_ip = user_ip_port[0]
                    user_port = user_ip_port[1]
                    text = text + "name = {0} ip = {1} port {2}\n".format(user_name, user_ip, user_port)
        messagebox.showinfo("Some info here !!", text)

    def menu(self):
        menubar = Menu(root)

        menu_file = Menu(menubar, tearoff = 0)
        menu_file.add_command(label = "list all channel", command = lambda : self.list())
        menu_file.add_command(label = "Quit", command = lambda : self.quit())
        menubar.add_cascade(label = "File", menu = menu_file)
        root.config(menu = menubar)

    def run(self):
        server_labelframe = LabelFrame(root, text = "Server side")
        server_labelframe.pack(fill = "both", expand = "yes")

        list_label_all_chat = Label(server_labelframe, text = "Here is the list of chatting").pack()
        self.list_label = Label(server_labelframe, text = "")
        self.s.bind((self.your_host, self.your_port))
        self.s.listen(5)
        while True:
            conn, addr = self.s.accept()
            response = conn.recv(255)
            if response != "":
                    print(response.decode())
                    command = response.decode()[8:9]
                    if command == "i":
                        self.add_list(response.decode()[10:])
                    if command == "c":
                        self.change_list(response.decode()[10:])
                    if command == "f":
                        self.find_and_send_channel(response.decode()[10:])
                    if command == "l":
                        self.send_list_channel(response.decode()[10:])
                    if command == "n":
                        self.create_channel(response.decode()[10:])

    def add_list(self, name_and_ip_channel):
        name_and_ip_channel = name_and_ip_channel.split("=>")
        channel = name_and_ip_channel[1]
        name_and_ip = name_and_ip_channel[0].split(',')
        name = name_and_ip[0]
        ip_port = name_and_ip[1]
        self.list_channel[channel].append("{0}=>{1}".format(name, ip_port))
        for user_list in self.list_channel[channel]:
            user_list = user_list.split("=>")
            if name != user_list[0]:
                self.send_user_list_channel(user_list[1], channel)
        self.update_list()

    def change_list(self, name_and_ip_channel):
        name_and_ip_channel = name_and_ip_channel.split("=>")
        channel = name_and_ip_channel[1]
        name_and_ip = name_and_ip_channel[0].split(',')
        name = name_and_ip[0]
        ip_port = name_and_ip[1]
        ip_and_port = ip_port.split(":")
        duplicate_name = False
        for channel_name, user_list in self.list_channel.items():
            if len(user_list) != 0:
                for user_name_ip in user_list:
                    name_ip = user_name_ip.split("=>")
                    user = name_ip[0]
                    ip = name_ip[1]
                    if user == name:
                        duplicate_name = True
                        msg = "command=c|fail"
                        break
        if duplicate_name == False:
            for channel_name, user_list in self.list_channel.items():
                if len(user_list) != 0:
                    for user_name_ip in user_list:
                        name_ip = user_name_ip.split("=>")
                        user = name_ip[0]
                        ip = name_ip[1]
                        if ip_port == ip:
                            msg = "command=c|success=>{0}".format(name)
                            self.list_channel[channel_name].remove(user_name_ip)
                            self.list_channel[channel_name].append("{0}=>{1}".format(name, ip_port))
                            break
        self.send_msg(ip_and_port[0], int(ip_and_port[1]), msg)
        self.update_list()
        for user_list in self.list_channel[channel]:
            user_list = user_list.split("=>")
            self.send_user_list_channel(user_list[1], channel)

    def update_list(self):
        self.list_label["text"] = ""
        text = ""
        for channel_name ,user_list in self.list_channel.items():
            if len(user_list) != 0:
                for user_ip in user_list:
                    text = text + "channel {0} = {1}\n".format(channel_name, user_ip)
            else:
                text = text + "channel {0} = {1}\n".format(channel_name, "no user found")
        self.list_label["text"] = text
        self.list_label.pack(fill = "both", expand = True)

    def find_and_send_channel(self, channel):
        channel = channel.split("=>")
        channel_name = channel[1]
        name_and_ip = channel[0].split(",")
        name = name_and_ip[0]
        ip_port = name_and_ip[1]
        msg = "command=f|{0}~no".format(channel_name)
        channel_exist = False
        for channel_name_list_list, user_list_list in self.list_channel.items():
            if channel_name_list_list == channel_name:
                channel_exist = True
                break
        if channel_exist == True:
            for channel_name_list_list, user_list_list in self.list_channel.items():
                if len(user_list_list) != 0:
                    for user_name_ip_list in user_list_list:
                        name_ip_list = user_name_ip_list.split("=>")
                        if name_ip_list[0] == name:
                            self.list_channel[channel_name_list_list].remove(user_name_ip_list)
                            text_list = ""
                            for user_list_list_list in self.list_channel[channel_name_list_list]:
                                text_list = text_list + user_list_list_list + "|*SEPARATOR*|"
                            msg_list = "command=f|{0}~{1}".format(channel_name_list_list, text_list)
                            for user_list_list_list in self.list_channel[channel_name_list_list]:
                                user_list_list_list_list = user_list_list_list.split("=>")
                                user_name_ip_list_list = user_list_list_list_list[1].split(":")
                                self.send_msg(user_name_ip_list_list[0], int(user_name_ip_list_list[1]), msg_list)
                            self.list_channel[channel_name].append("{0}=>{1}".format(name, ip_port))
                            break
            for channel_name_list, user_list in self.list_channel.items():
                if channel_name_list == channel_name:
                    if len(user_list) == 0:
                        msg = "command=f|{0}~empty".format(channel_name)
                    else:
                        text = ""
                        for user_name_ip in user_list:
                            text = text + user_name_ip + "|*SEPARATOR*|"
                        msg = "command=f|{0}~{1}".format(channel_name, text)
            for user_list in self.list_channel[channel_name]:
                user_list_list = user_list.split("=>")
                user_list_list_name = user_list_list[0]
                user_list_list_ip_port = user_list_list[1].split(":")
                self.send_msg(user_list_list_ip_port[0], int(user_list_list_ip_port[1]), msg)
        ip_port = ip_port.split(":")
        ip = ip_port[0]
        port = int(ip_port[1])
        self.update_list()
        self.send_msg(ip, port, msg)

    def send_user_list_channel(self, ip_port, channel_name):
        msg = "command=f|{0}~no".format(channel_name)
        for channel_name_list, user_list in self.list_channel.items():
            if channel_name_list == channel_name:
                if len(user_list) == 0:
                    msg = "command=f|{0}~empty".format(channel_name)
                else:
                    text = ""
                    for user_name_ip in user_list:
                        text = text + user_name_ip + "|*SEPARATOR*|"
                    msg = "command=f|{0}~{1}".format(channel_name, text)
        ip_port = ip_port.split(":")
        ip = ip_port[0]
        port = int(ip_port[1])
        self.send_msg(ip, port, msg)

    def send_list_channel(self, ip_and_port):
        ip_and_port = ip_and_port.split(":")
        ip = ip_and_port[0]
        port = int(ip_and_port[1])
        text = "command=l|"
        for channel_name, user_list in self.list_channel.items():
            text = text + channel_name + "|*SEPARATOR*|"
        self.send_msg(ip, port, text)

    def create_channel(self, name_ip_port_channel):
        name_ip_port_channel = name_ip_port_channel.split("=>")
        new_channel = name_ip_port_channel[1]
        name_ip_port = name_ip_port_channel[0].split(",")
        name = name_ip_port[0]
        ip_port = name_ip_port[1].split(":")
        ip = ip_port[0]
        port = int(ip_port[1])
        duplicate_channel = False
        for channel_name, user_list in self.list_channel.items():
            if channel_name == new_channel:
                msg = "command=n|{0}=>{1}".format("fail", new_channel)
                duplicate_channel = True
                break
        if duplicate_channel == False:
            for channel_name, user_list in self.list_channel.items():
                if len(user_list) != 0:
                    for list_user in user_list:
                        user_name_ip_port = list_user.split("=>")
                        user_name = user_name_ip_port[0]
                        user_ip_port = user_name_ip_port[1].split(":")
                        user_ip = user_ip_port[0]
                        user_port = user_ip_port[1]
                        if user_name == name:
                            self.old_channel = channel_name
                            self.list_channel[channel_name].remove(list_user)
            self.list_channel[new_channel] = ["{0}=>{1}:{2}".format(name, ip, port)]
            self.update_list()
            for channel_name_list, user_list_list_list in self.list_channel.items():
                print(channel_name_list)
                if len(user_list_list_list) != 0:
                    for list_list_user in user_list_list_list:
                        print(list_list_user)
                        user_name_ip_port = list_list_user.split("=>")
                        user_name = user_name_ip_port[0]
                        user_ip_port = user_name_ip_port[1].split(":")
                        user_ip = user_ip_port[0]
                        user_port = user_ip_port[1];
                        self.send_list_channel("{0}:{1}".format(user_ip, user_port))
                if channel_name_list == self.old_channel:
                    user_list_list = list_list_user.split("=>")
                    print("old_channel = " + user_list_list[1])
                    self.send_user_list_channel(user_list_list[1], self.old_channel)
            msg = "command=n|{0}=>{1}".format("success", new_channel)
            self.send_msg(ip, port, msg)

    def send_msg(self, ip, port, msg):
        msg_byte = bytes(msg.encode('utf-8'))
        tmp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmp_s.connect((ip, port))
        tmp_s.send(msg_byte)
        tmp_s.shutdown(socket.SHUT_RDWR)
        tmp_s.close()

server = Server()
root.mainloop()