
from genericpath import isfile
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from PIL import Image,ImageTk
import os
import sys
from multiprocessing import Process, Array, freeze_support, Manager

from widget.custom_notebook import CustomNotebook
from widget.edit_window import edit_window

from utils import *

DEFAULT_FONT=("", 12)

CONFIG_PATH = "config.yaml"
DEFOULT_CONFIG = (6, 5, 6)

def init_tab_config(size, tab_name):
    width, height = size
    tab_data = {}
    tab_data["name"] = tab_name
    tab_data["btn_list"] = []
    for y in range(height):
        for x in range(width):
            btn_data = {}
            btn_data["name"] = 'コマンド {}'.format(width * y + x)
            btn_data["cmd"] = []
            btn_data["exec_type"] = False
            tab_data["btn_list"].append(btn_data)
    return tab_data
            
def init_config(tab_num, size):
    config = {}
    config["tab_num"] = tab_num
    config["btn_size"] = list(size)
    config["data"] = []
    width, height = size
       
    for tab_idx in range(tab_num):
        tab_data = init_tab_config(size, 'タブ {}'.format(tab_idx))
        config["data"].append(tab_data)
    return config

def is_valid_config(config):
    tab_num = config["tab_num"]
    w, h = config["btn_size"]
    data = config["data"]
    
    if tab_num != len(data):
        return False
    
    for tab_idx in range(tab_num):
        if len(data[tab_idx]["btn_list"]) != w * h:
            return False
    
    return True

class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.finish_resource = []
        
        def close():  # ウィンドウの右上の✖アイコンから閉じるときの処理（ウィンドウを閉じる処理を書き換える）
            self.finish()
            self.quit()
            self.destroy()
        self.protocol("WM_DELETE_WINDOW", close)  # ウィンドウを閉じる処理を書き換える
        
    def register_finish(self,func):
        self.finish_resource.append(func)
        
    def finish(self):
        for finish_item in self.finish_resource:
            finish_item()
            
class main_frm(Frame):

    def __init__(self, master):
        super().__init__(master=master)
        self.master = master
        self.grid(column=0, row=0, sticky=(N, S, W, E))
        self.make_widget()
        
    def make_widget(self):
        self.base_frm = Frame(
            self,
            background="white",
            relief="ridge",
            borderwidth=2
            )
        self.base_frm.grid(column=0, row=0, sticky=(N, S, W, E))
        
        # タブのフォント設定
        # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        ttk.Style().configure(
            'CustomNotebook.Tab',
            font=DEFAULT_FONT,
            padding=(10, 5), 
            borderwidth = 30,
            )
        
        # 設定ファイルをロードして、復元
        is_exist_config = os.path.isfile(CONFIG_PATH)
        if is_exist_config:
            self.config = LoadYaml(CONFIG_PATH)
            
        if not is_exist_config or not is_valid_config(self.config):
            tab_num, width, height = DEFOULT_CONFIG
            self.config = init_config(tab_num, (width, height))
            SaveYaml(CONFIG_PATH, self.config)

        self.base_tab = CustomNotebook(
            self.base_frm,
            image_size = (9, 9)
            )
        self.base_tab.grid(column=0, row=0, sticky=(N, S, W, E))
        
        self.tab_list = []
        for idx in range(self.config["tab_num"]):
            tab = self.make_tab_frm(idx)
            tab.grid(column=0, row=0, sticky=(N, S, W, E))
            
            self.base_tab.add(
                tab,
                text=self.config["data"][idx]["name"],
                padding=5,
                )

            self.tab_list.append(tab)
            
    def make_tab_frm(self, idx):
        return tab_frm(self.base_tab, idx, self.config["btn_size"], self.config["data"][idx]["btn_list"])

    def save_config(self):
        SaveYaml(CONFIG_PATH, self.config)
        
    def rename_tab_config(self, tab_idx, tab_name):
        self.config["data"][tab_idx]["name"] = tab_name
        self.save_config()
        
    def remove_tab_config(self, tab_idx):
        self.config["tab_num"] -= 1
        self.config["data"].pop(tab_idx)
        self.save_config()
        
    def add_tab_config(self, tab_idx, tab_name, tab_data = None):
        self.config["tab_num"] += 1
        if tab_data is None:
            tab_data = init_tab_config(self.config["btn_size"], tab_name)
        self.config["data"].insert(tab_idx, tab_data)
        self.save_config()
     
    def insert_tab_congig(self, from_idx, to_idx):
        if from_idx == to_idx:
            return

        data = self.config["data"]
        if from_idx < to_idx:
            data.insert(to_idx + 1, data[from_idx])
            data.pop(from_idx)
        else:
            data.insert(to_idx, data[from_idx])
            data.pop(from_idx + 1)
        self.save_config()
        
class CustomButton(Button):
    def __init__(self, master=None, id=None, **kwargs):
        super().__init__(master, **kwargs)
        self.id = id
        
class tab_frm(Frame):

    def __init__(self, master, id, size, data):
        super().__init__(
            master=master,
            relief="ridge",
            )
        self.id = id
        self.size = size
        self.data = data
        self.make_widget()
        
    def make_widget(self):
        width, height = self.size

        for y in range(height):
            for x in range(width):
               btn_id = width * y + x
               btn_data = self.data[btn_id]
               
               btn = CustomButton(
                self,
                id = btn_id,
                text=btn_data["name"],
                font=DEFAULT_FONT,
                borderwidth = 3,
                wraplength=150,
                padx=15,
               )
               
               btn.grid(column=x, row=y)
               btn.bind("<ButtonRelease>",self.release_button)
               
    def release_button(self, event):
        btn = event.widget
        if not is_valid_release(event):
            return
        
        # 左クリックの場合
        if event.num == 1:
            # 設定されているコマンドを実行
            self.exec_btn_cmd(btn.id)
        
        # 右クリックの場合
        if event.num == 3:
            # ポップメニューを表示
            pmenu = Menu(btn, tearoff=0)
            self.btn_edit_key = "ボタンの編集"
            pmenu.add_command(
                label=self.btn_edit_key,
                command=self.press_menu(btn, self.btn_edit_key),
                font=DEFAULT_FONT,
                )
            pmenu.add_command(
                label="閉じる",
                font=DEFAULT_FONT,
                )
            x, y = event.x_root, event.y_root
            pmenu.post(x, y)
            
    def press_menu(self, btn, label):        
        def _press_menu():
            if label == self.btn_edit_key:
                 edit_window(self, btn, self.data[btn.id])
        return _press_menu
    
    def exec_btn_cmd(self, btn_id):
        if btn_id >= len(self.data):
            return
        
        cmd_list = self.data[btn_id]["cmd"]
        cmd_list = [cmd for cmd in cmd_list if cmd != ""]
        
        if len(cmd_list) == 0:
            print("コマンドが登録されていません")
            return

        exec_cmd(cmd_list, is_parallel=self.data[btn_id]["exec_type"])
            
def set_window_size(win, size):
    h,w = size
    win.columnconfigure(0, weight=1)    # 列についての重みを決定
    win.rowconfigure(0, weight=1)       # 行についての重みを設定
    
def main():
    # メインウィンドウの設定
    main_win = MainWindow()
    main_win.title("Command Clicker")

    # フレームの設定
    main_frm(master=main_win)
    
    # # ウィンドウのサイズを固定
    main_win.wm_resizable(False, False)

    # サイズグリップを貼り付ける用のフレームの設定
    sizegrip_frm = ttk.Frame(main_win, style="Sizegrip.TFrame")
    sizegrip_frm.grid(column=0, row=1, sticky=(N, S, W, E))
    sizegrip_frm.columnconfigure(0, weight=1)
    sizegrip_frm.rowconfigure(0, weight=1)
    sizegrip_frm_style = ttk.Style()
    sizegrip_frm_style.configure("Sizegrip.TFrame", background="white") # 背景を白に指定

    # サイズグリップの設定(サブフレームへ配置)
    sizegrip = ttk.Sizegrip(sizegrip_frm)
    sizegrip.grid(row=500, column=100, sticky=(S, E))

    main_win.mainloop()  # メインウィンドウがここで動く

if __name__=="__main__":
    main()