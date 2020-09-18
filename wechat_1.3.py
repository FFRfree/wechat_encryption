import itchat
import itchat
from threading import Thread
import tkinter as tk
from tkinter import scrolledtext,StringVar
from encryptor import encodeDataInImage,decodeImage,s_dectry,s_enctry
from PIL import Image
import time
import os
                        
space = '　'
itchat.auto_login(True)

class Conversation():
    def __init__(self,category,name):
        #itchat部分
        self.name = name
        self.category = category
        if category == '1':#群聊
            self.users = itchat.search_chatrooms(name=name)
            self.userName = self.users[0]['UserName']
        elif category == '2': #联系人
            self.users = itchat.search_friends(name=name)
            self.userName = self.users[0]['UserName']

        self.chat_hty = []
        self.raw_pic_path = os.path.abspath('./pic')+'/'
        #"C:\\MyPythonScripts\\wechat\\pic\\"
        #C:\MyPythonScripts\wechat\pic\

    def main_loop(self):
        #gui部分
        #创建基本框架布局
        self.root = tk.Tk()  #创建窗口
        self.frame = tk.Frame(self.root) #创建控件，指定这个控件的master 也就是root
        self.frame.grid() #将frame部件放入主窗口
        #创建基本按钮
        self.dialogue = tk.Label(self.frame,text=f'与{self.name}的聊天')
        self.dialogue.grid(row=0,column=0)
        self.send_button = tk.Button(self.frame,text = 'send', command=self.send_msg)
        self.send_button.grid(row=2,column=1,sticky='w e')
        self.text_entry1 = tk.Entry(self.frame,cursor='plus',width=60)
        self.text_entry1.grid(row=2,column=0,sticky='w')
        self.text_entry1.bind("<Return>", func=self.send_msg) #回车发送 从哪冒出的第二个参数？
        self.filename_entry = tk.Entry(self.frame,cursor='plus',width=20)
        self.filename_entry.grid(row=3,sticky='w')
        self.filename_entry.insert(0,'1.png')
        self.key_entry = tk.Entry(self.frame,cursor='plus',width=20)
        self.key_entry.grid(row=3,sticky='e')
        self.key_entry.insert(0,'key')
        scrolW = 60 # 设置文本框的长度
        scrolH = 10 # 设置文本框的高度
        self.scr = scrolledtext.ScrolledText(self.frame,width=scrolW, height=scrolH, wrap=tk.WORD)
        self.scr.grid(row=1)
               
        self.start_receiving()

        self.root.mainloop()


    def send_msg(self,*args):
        raw_msg = self.text_entry1.get() #获取信息
        key = self.key_entry.get() #获取密钥
        msg = '我： ' + raw_msg
        self.text_entry1.delete(0,'end') #清空输入栏
        self.scr.insert('end',f'{msg}\n') #显示在gui中
        self.chat_hty.append(msg) #加入聊天记录

        # 隐写
        filename = self.filename_entry.get() #获取原始图片文件名
        encoded_pic_path = f'{self.raw_pic_path}{time.time()}.png' #加密完的图片路径
        encodeDataInImage(Image.open(f'{self.raw_pic_path}{filename}'), raw_msg).save(encoded_pic_path)


        #发送
        itchat.send_image(encoded_pic_path,toUserName=self.userName)
        os.remove(encoded_pic_path)
        print(f'已发送：{raw_msg}')


    def start_receiving(self):
        key = self.key_entry.get()
        if self.category == '2':
            @itchat.msg_register('Picture')
            def download_pic(recv_pic,isFriendChat=True):
                if recv_pic['FromUserName'] == self.userName:
                    filename = recv_pic['FileName']
                    path = f'{self.raw_pic_path}{filename}'
                    recv_pic['Text'](path) #注册器中text中的一个保存图片到本地的函数
                    msg = decodeImage(Image.open(path)) #encryptor的解码函数
                    # msg = s_dectry(msg,key)
                    self.scr.insert('end',f'{self.name}: {msg}\n') #显示在gui中
                    self.chat_hty.append(msg) #加入历史消息
                    os.remove(path)
                    print('received')
        elif self.category == '1':
            @itchat.msg_register('Picture',isGroupChat=True)
            def download_pic(recv_pic):
                if recv_pic['FromUserName'] == self.userName:
                    nickname = recv_pic['ActualNickName']
                    filename = recv_pic['FileName']
                    path = f'{self.raw_pic_path}{filename}'
                    recv_pic['Text'](path) #注册器中text中的一个保存图片到本地的函数
                    msg = decodeImage(Image.open(path)) #encryptor的解码函数
                    # msg = s_dectry(msg,key)
                    self.scr.insert('end',f'{nickname}: {msg}\n') #显示在gui中
                    self.chat_hty.append(f'nickname: {msg}') #加入历史消息
                    print('received')


        self.t1 = Thread(target= itchat.run) #使用一个线程监听消息
        self.t1.setDaemon(True) #设置为守护线程，不然退出去时候卡死
        self.t1.start()


conv1 = Conversation(input('群聊(1)/联系人(2)？： '),input('备注：'))
conv1.main_loop()
