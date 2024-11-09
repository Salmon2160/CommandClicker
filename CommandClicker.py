
from genericpath import isfile
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from PIL import Image,ImageTk
import os
import sys
import copy

from multiprocessing import freeze_support

from widget.custom_notebook import CustomNotebook
from widget.edit_window import edit_window

from utils import *
from config.config import ConfigManager

DEFAULT_FONT=("", 12)

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

        self.base_tab = CustomNotebook(
            self.base_frm,
            image_size = (9, 9),
            tab_num = ConfigManager().GetMaxTabNum()
            )
        self.base_tab.grid(column=0, row=0, sticky=(N, S, W, E))
        
        for idx in range(ConfigManager().GetTabNum()):
            tab = tab_frm(self.base_tab, idx)
            tab.grid(column=0, row=0, sticky=(N, S, W, E))
            
            self.base_tab.add(
                tab,
                text=ConfigManager().GetTabName(idx),
                padding=5,
                )
        
class CustomButton(Button):
    def __init__(self, master=None, id=None, **kwargs):
        super().__init__(master, **kwargs)
        self.id = id
        
    def get_id(self):
        return self.id
        
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

    def __init__(self, master, id):
        super().__init__(
            master=master,
            relief="ridge",
            )
        self.id = id
        self.move_btn = None
        self.make_widget()
        
    def make_widget(self):
        width, height = ConfigManager().GetBtnSize()

        self.btn_list = []
        btn_list = ConfigManager().GetBtnList(self.id)
        for y in range(height):
            for x in range(width):
               btn_id = width * y + x
               btn_data = btn_list[btn_id]
               
               btn = CustomButton(
                self,
                id = btn_id,
                text=btn_data["name"],
                font=DEFAULT_FONT,
                borderwidth = 3,
                wraplength=120,
                padx=10,
                width=11,
               )
               
               btn.grid(column=x, row=y, padx=2, pady=2)
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
        ConfigManager().SwapBtnData(self.id, source_idx, target_idx)
        ConfigManager().SaveConfig()
        
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
                menu = Menu(btn, tearoff=0)
                self.btn_edit_key = "編集"
                menu.add_command(
                    label=self.btn_edit_key,
                    command=self.press_menu(btn, self.btn_edit_key),
                    font=DEFAULT_FONT,
                    )
                
                self.btn_copy_key = "コピー"
                menu.add_command(
                    label=self.btn_copy_key,
                    command=self.press_menu(btn, self.btn_copy_key),
                    font=DEFAULT_FONT,
                    )
                
                self.btn_paste_key = "貼り付け"
                menu.add_command(
                    label=self.btn_paste_key,
                    command=self.press_menu(btn, self.btn_paste_key),
                    font=DEFAULT_FONT,
                    )
                if not ClipBoard().IsValidBtnData():
                    menu.entryconfig(self.btn_paste_key, state="disabled")

                menu.add_separator()
                
                menu.add_command(
                    label="閉じる",
                    font=DEFAULT_FONT,
                    )
                x, y = event.x_root, event.y_root
                menu.post(x, y)
        else:
            # ボタンをドラッグ中の場合は交換
            if self.move_btn is not None:
                self.exchange_move_button(event) 
                self.reset_move_button()
            
    def press_menu(self, btn, label):        
        def _press_menu():
            if label == self.btn_edit_key:
                edit_window(self, self.id, btn)
            elif label == self.btn_copy_key:
                ClipBoard().SetBtnData(self.id, btn.id)
            elif label == self.btn_paste_key:
                if not ClipBoard().IsValidBtnData():
                    return
                btn_data = ClipBoard().GetBtnData()
                btn["text"] = btn_data["name"]
                self.update_btn_data(btn.id, btn_data)
                ConfigManager().SaveConfig()
                
        return _press_menu
    
    def update_btn_data(self, btn_id, btn_data):
        self.btn_list[btn_id]["text"]   = btn_data["name"]
        ConfigManager().SetBtnData(self.id, btn_id, btn_data)

    def update_tab_data(self, tab_data):
        for btn_id, btn_data in enumerate(tab_data["btn_list"]):
            self.update_btn_data(btn_id, btn_data)
    
    def exec_btn_cmd(self, btn_id):
        btn_list = ConfigManager().GetBtnList(self.id)
        if btn_id >= len(btn_list):
            return
        
        cmd_list = btn_list[btn_id]["cmd"]
        cmd_list = [cmd for cmd in cmd_list if cmd != ""]
        
        if len(cmd_list) == 0:
            print("コマンドが登録されていません")
            return

        process_exec_cmd(cmd_list, is_parallel=btn_list[btn_id]["exec_type"], is_background = btn_list[btn_id]["exec_type2"])
            
def set_window_size(win, size):
    h,w = size
    win.columnconfigure(0, weight=1)    # 列についての重みを決定
    win.rowconfigure(0, weight=1)       # 行についての重みを設定
    
def main():
    
    # 設定ファイルをロードして、復元
    ConfigManager()
    
    # クリップボードを有効化
    ClipBoard()

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
    # pyinstallerとmultiprocessingを併用する場合は以下の関数を初回に呼び出しておく
    freeze_support()
    main()