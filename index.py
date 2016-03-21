#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import messagebox
import socket
import random

root = Tk()
root.geometry("550x550")

class Server():
    def __init__(self):
        self.app_name = "P2P Chat"
        self.version = "1.0.0"
        self.author =  "isma91"
        self.nickname = "user" + str(random.randint(0, 123456789))
        self.host = ''
        self.list_ip = {}
        self.recv_buffer = 4096
        self.port = 9009

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('google.com', 80))

        self.your_ip = s.getsockname()[0]

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)
        self.menu()
        self.server_side()
        self.client_side()

        #a,b = server_socket.accept()

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

    def menu(self):
        menubar = Menu(root)

        menu_file = Menu(menubar, tearoff = 0)
        menu_file.add_command(label = "Get your ip", command = self.get_ip)
        menu_file.add_separator()
        menu_file.add_command(label = "Quit", command = root.quit)
        menubar.add_cascade(label = "File", menu = menu_file)

        menu_about = Menu(menubar, tearoff = 0)
        menu_about.add_command(label = "About", command = self.about)
        menubar.add_cascade(label = "Help", menu = menu_about)

        root.config(menu = menubar)

    def add_ip(self, label, ip_and_name):
        ip_and_name = ip_and_name.split(",")
        error = 0
        if len(ip_and_name) == 2:
            ip = ip_and_name[0]
            name = ip_and_name[1]
            for list_ip_name, list_ip_ip in self.list_ip.items():
                if list_ip_name == name:
                    self.display_error("This name is already taken !!")
                    error = error + 1
                if ip == self.your_ip:
                    self.display_error("You can't add your own ip !!")
                if list_ip_ip == ip:
                    self.display_error("This ip is already taken !!")
                    error = error + 1
            if error == 0:
                self.list_ip[name] = ip
                list_ip_str = ""
                for list_ip_name, list_ip_ip in self.list_ip.items():
                    list_ip_str = list_ip_str + "name : " + list_ip_name + " ip : " + list_ip_ip + "\n"
                label["text"] = list_ip_str
                label.pack()
                self.display_info("Name and ip added sucessfully !!")
        else:
            self.display_error("You must write the ip and the name separated by a comma !!")

    def change_nickname(self, label, nickname):
        label["text"] = nickname
        self.display_info("Nickname changed sucessfully !!")

    def client_side(self):
        client_labelframe = LabelFrame(root, text = "Client side")
        client_labelframe.pack(fill = "both", expand = "yes")

        change_nickname_value = StringVar()
        change_nickname_input = Entry(client_labelframe, text = change_nickname_value).pack()
        change_nickname_button = Button(client_labelframe, text = "Change your nickname", command = lambda : self.change_nickname(nickname_label, change_nickname_value.get())).pack()
        
        nickname_label = Label(client_labelframe, text = "Welcome {0} !!".format(self.nickname))
        nickname_label.pack()

    def server_side(self):
        server_labelframe = LabelFrame(root, text = "Server side")
        server_labelframe.pack(fill = "both", expand = "yes")

        ip_label = Label(server_labelframe, text = "Add your friend ip and his name separated by a comma (e.g 1.2.3.4,foobar)").pack()
        ip_value = StringVar()
        ip_input = Entry(server_labelframe, textvariable = ip_value).pack()
        ip_button = Button(server_labelframe, text = "Add", command = lambda : self.add_ip(list_label, ip_value.get())).pack()
        list_label = Label(server_labelframe, text = "")

server = Server()
root.mainloop()