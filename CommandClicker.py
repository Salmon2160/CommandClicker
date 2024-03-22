
from genericpath import isfile
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from PIL import Image,ImageTk
import os
import sys
import copy
from multiprocessing import Process, Array, freeze_support, Manager

from widget.custom_notebook import CustomNotebook
from widget.edit_window import edit_window

from utils import *

DEFAULT_FONT=("", 12)

BACKUP_FOLDER = "backup"
CONFIG_FILENAME = "config.yaml"
DEFOULT_CONFIG = (6, 5, 6)
DEFOULT_CONFIG = (6, 4, 4)

def init_tab_config(size, tab_name):
    width, height = size
    tab_data = {}
    tab_data["name"] = tab_name
    tab_data["btn_list"] = []
    for y in range(height):
        for x in range(width):
            btn_data = {}
            btn_data["name"] = 'コマンド {}'.format(width * y + x)
            btn_data["cmd"] = [""]
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
        
        self.config = None
        self.clipboard_btn_data = None
        self.clipboard_tab_data = None

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
        is_exist_config = os.path.isfile(CONFIG_FILENAME)
        if is_exist_config:
            self.config = LoadYaml(CONFIG_FILENAME)
            time_str = get_current_datetime_string()
            backup_path = os.path.join(BACKUP_FOLDER, time_str+ "_" + CONFIG_FILENAME)
            SaveYaml(backup_path, self.config)
            
        if not is_exist_config or not is_valid_config(self.config):
            tab_num, width, height = DEFOULT_CONFIG
            self.config = init_config(tab_num, (width, height))
            SaveYaml(CONFIG_FILENAME, self.config)

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
        SaveYaml(CONFIG_FILENAME, self.config)
        
    def set_tab_data(self, tab_idx, tab_name = None, btn_list = None):
        if tab_name is not None:
            self.config["data"][tab_idx]["name"] = tab_name
        if btn_list is not None:
            self.config["data"][tab_idx]["btn_list"] = btn_list
        
    def remove_tab(self, tab_idx):
        self.config["tab_num"] -= 1
        self.config["data"].pop(tab_idx)
        self.tab_list.pop(tab_idx)
        
    def add_tab(self, tab_idx, tab_name, tab_data = None):
        self.config["tab_num"] += 1
        if tab_data is None:
            tab_data = init_tab_config(self.config["btn_size"], tab_name)
        self.config["data"].insert(tab_idx, tab_data)
        self.tab_list.insert(tab_idx, self.make_tab_frm(tab_idx))
     
    def insert_tab(self, from_idx, to_idx):
        if from_idx == to_idx:
            return

        data = self.config["data"]
        if from_idx < to_idx:
            data.insert(to_idx + 1, data[from_idx])
            data.pop(from_idx)
            
            self.tab_list.insert(to_idx + 1, self.tab_list[from_idx])
            self.tab_list.pop(from_idx)
        else:
            data.insert(to_idx, data[from_idx])
            data.pop(from_idx + 1)
            
            self.tab_list.insert(to_idx, self.tab_list[from_idx])
            self.tab_list.pop(from_idx + 1)
        
    def is_valid_clipboard_btn_data(self):
        return self.clipboard_btn_data is not None
    
    def get_clipboard_btn_data(self):
        return self.clipboard_btn_data
    
    def set_clipboard_btn_data(self, tab_id, btn_id):
        self.clipboard_btn_data = copy.deepcopy(self.config["data"][tab_id]["btn_list"][btn_id])
        
    def is_valid_clipboard_tab_data(self):
        return self.clipboard_tab_data is not None
    
    def get_clipboard_tab_data(self):
        return self.clipboard_tab_data
    
    def set_clipboard_tab_data(self, tab_id):
        self.clipboard_tab_data = copy.deepcopy(self.config["data"][tab_id])
        
    def get_tab(self, tab_id):
        return self.tab_list[tab_id]
        
class CustomButton(Button):
    def __init__(self, master=None, id=None, **kwargs):
        super().__init__(master, **kwargs)
        self.id = id
        
class CustomButtonToplevel(Toplevel):
    def __init__(self, master, btn_name, pos):
        self.master = master
        super().__init__(master=master)
        self.overrideredirect(True)         # ウィンドウ枠を削除
        self.wm_attributes("-alpha", 0.75)  # ウィンドウを半透明
        self.attributes("-topmost", True)   # ウィンドウを最前面
        self.focus_force()
        
        # タブ
        label = ttk.Label(
            self,
            text=btn_name,
            font=DEFAULT_FONT,
            padding =(15, 6),
            borderwidth = 20,
            relief="solid",
        )
        label.grid(column=0, row=0, sticky=(N, S, W, E))
        
        # 親の位置を元に表示
        x, y = pos
        self.offset = (20, 12)
        x0, y0 = self.offset
        self.geometry("+{}+{}".format(x - x0, y - y0))
        
        # マウスの移動をトラッキング
        self.move_bind = self.master.bind("<Motion>", self.move_with_mouse)
        
    def move_with_mouse(self, event):
        # マウスの位置を取得し、ウィンドウをその位置に移動
        self.geometry("+{}+{}".format(event.x_root - self.offset[0], event.y_root - self.offset[1]))
        
    def unbind_event(self):
        self.master.unbind("<Motion>", self.move_bind)
        
class tab_frm(Frame):

    def __init__(self, master, id, size, data):
        super().__init__(
            master=master,
            relief="ridge",
            )
        self.id = id
        self.size = size
        self.data = data
        
        self.move_btn = None
        
        self.make_widget()
        
    def make_widget(self):
        width, height = self.size

        self.btn_list = []
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
               btn.bind("<Control - Button - 3>",self.start_move_button)
               self.btn_list.append(btn)
               
    def start_move_button(self, event):
        if self.move_btn is not None:
            return

        btn = event.widget
        
        x = int(btn.winfo_rootx() + event.x)
        y = int(btn.winfo_rooty() + event.y)
        self.move_btn = CustomButtonToplevel(btn, btn["text"], (x, y) )
        
    def exchange_move_button(self, event):
        source_btn = event.widget
        x = event.x + source_btn.winfo_rootx()
        y = event.y + source_btn.winfo_rooty()
        
        target_idx = None
        for target_btn in self.btn_list:
            x1 = target_btn.winfo_rootx()
            y1 = target_btn.winfo_rooty()
            x2 = x1 + target_btn.winfo_width()
            y2 = y1 + target_btn.winfo_height()

            if (x1 <= x <= x2) and (y1 <= y <= y2):
                target_idx = target_btn.id
                
        if target_idx is None:
            return
        source_idx = source_btn.id
        target_btn = self.btn_list[target_idx]
        
        # 入れ替え
        source_btn["text"], target_btn["text"] = target_btn["text"], source_btn["text"]
        self.data[source_idx], self.data[target_idx] = self.data[target_idx], self.data[source_idx]
        self.master.master.master.save_config()
        
    def reset_move_button(self):
        if self.move_btn is not None:
            self.move_btn.unbind_event()
            self.move_btn.destroy()
            self.move_btn = None
               
    def release_button(self, event):
        btn = event.widget
        
        if is_valid_release(event):
            # 左クリックの場合
            if event.num == 1:
                # 設定されているコマンドを実行
                self.exec_btn_cmd(btn.id)
        
            # 右クリックの場合
            if event.num == 3:
                # ボタンをドラッグ中の場合は何もしない
                if self.move_btn is not None:
                    self.reset_move_button()
                    return

                # ポップメニューを表示
                pmenu = Menu(btn, tearoff=0)
                self.btn_edit_key = "編集"
                pmenu.add_command(
                    label=self.btn_edit_key,
                    command=self.press_menu(btn, self.btn_edit_key),
                    font=DEFAULT_FONT,
                    )
                
                self.btn_copy_key = "コピー"
                pmenu.add_command(
                    label=self.btn_copy_key,
                    command=self.press_menu(btn, self.btn_copy_key),
                    font=DEFAULT_FONT,
                    )
                
                self.btn_paste_key = "貼り付け"
                pmenu.add_command(
                    label=self.btn_paste_key,
                    command=self.press_menu(btn, self.btn_paste_key),
                    font=DEFAULT_FONT,
                    )
                if not self.master.master.master.is_valid_clipboard_btn_data():
                    pmenu.entryconfig(self.btn_paste_key, state="disabled")

                pmenu.add_separator()
                
                pmenu.add_command(
                    label="閉じる",
                    font=DEFAULT_FONT,
                    )
                x, y = event.x_root, event.y_root
                pmenu.post(x, y)
        else:
            # ボタンをドラッグ中の場合は交換
            if self.move_btn is not None:
                self.exchange_move_button(event) 
                self.reset_move_button()
            
    def press_menu(self, btn, label):        
        def _press_menu():
            if label == self.btn_edit_key:
                edit_window(self, btn, self.data[btn.id])
            elif label == self.btn_copy_key:
                self.master.master.master.set_clipboard_btn_data(self.id, btn.id)
            elif label == self.btn_paste_key:
                if not self.master.master.master.is_valid_clipboard_btn_data():
                    return
                btn_data = self.master.master.master.get_clipboard_btn_data()
                btn["text"] = btn_data["name"]
                self.update_btn_data(btn.id, btn_data)
                self.master.master.master.save_config()
                
        return _press_menu
    
    def update_btn_data(self, btn_id, btn_data):
        self.btn_list[btn_id]["text"]   = btn_data["name"]
        self.data[btn_id]["name"]       = btn_data["name"]
        self.data[btn_id]["cmd"]        = btn_data["cmd"]
        self.data[btn_id]["exec_type"]  = btn_data["exec_type"]

    def update_tab_data(self, tab_data):
        for btn_id, btn_data in enumerate(tab_data["btn_list"]):
            self.update_btn_data(btn_id, btn_data)
    
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