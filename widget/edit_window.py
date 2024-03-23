from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from utils import *

DEFAULT_FONT=("", 12)

class edit_window(Toplevel):
    def __init__(self, master, edit_btn, edit_data):
        self.master = master
        super().__init__(master=master)
        self.edit_btn = edit_btn
        self.edit_data = edit_data
        
        self.make_widget()
        
        # サイズ固定
        self.wm_resizable(False, False)
        
        # 親の位置を元に表示
        x = int(self.master.winfo_x() + self.master.winfo_width() / 2.0)
        y = int(self.master.winfo_y() + self.master.winfo_height() / 2.0)
        self.geometry("+{}+{}".format(x, y))
        
        # フォーカス
        self.focus_force()

    def make_widget(self):
        def _on_closing():  # ウィンドウの右上の✖アイコンから閉じるときの処理（ウィンドウを閉じる処理を書き換える）
            if self.is_change_entry():
                # 保存するかどうかの確認ダイアログを表示
                response = messagebox.askyesnocancel("Confirmation", "変更内容を保存しますか？")
                if response is True:
                    self.save_entry()
                elif response is False:
                    pass
                else:
                    return
            
            self.destroy()
        self.protocol("WM_DELETE_WINDOW", _on_closing)  # ウィンドウを閉じる処理を書き換える
        
        setting_frm = Frame(
            self,
            relief="ridge",
            borderwidth=2,
        )
        setting_frm.grid(column=0, row=0, sticky=(N, S, W, E))
        
        # text setting
        text_sticky = (N, S, W)
        text_label = ttk.Label(
            setting_frm,
            text="コマンド名",
            font=DEFAULT_FONT,
        )
        text_label.grid(column=0, row=0, sticky=text_sticky)
        
        text_label = ttk.Label(
            setting_frm,
            text="実行コマンド",
            font=DEFAULT_FONT,
        )
        text_label.grid(column=0, row=1, sticky=text_sticky)

        # input setting
        # ボタン名の入力
        input_sticky = (N, S, W)
        self.btn_name_entry = Entry(
            setting_frm,
            font=DEFAULT_FONT,
            width=18,
        )
        self.btn_name_entry.insert(0, self.edit_data["name"])
        self.btn_name_entry.grid(column=1, row=0, sticky=input_sticky)
        
        # 実行コマンドの入力形式のチェックボックス
        self.checkbox_var = BooleanVar()
        self.cmd_type_checkbox = Checkbutton(
            setting_frm,
            text="並列実行",
            variable=self.checkbox_var,
            font = DEFAULT_FONT
        )
        self.cmd_type_checkbox.grid(column=1, row=1, sticky=(W, E))
        self.checkbox_var.set(self.edit_data["exec_type"])

        # 実行コマンドの入力
        self.btn_cmd_entry = ScrolledText(
            setting_frm,
            font=DEFAULT_FONT,
            height=10,
            width=40,
        )
        self.btn_cmd_entry.delete("1.0", "end")
        cmd_list = self.edit_data["cmd"]
        
        # コマンド内容をロード（最後の挿入のみ、改行コードを省略）
        for idx, cmd in enumerate(cmd_list):
            self.btn_cmd_entry.insert(END, cmd + "\n" if idx != len(cmd_list) - 1 else cmd)
        self.btn_cmd_entry.grid(column=0, row=2, columnspan = 2, sticky=(W, E))

        btn_frm = Frame(
            self,
            relief="ridge",
        )
        btn_frm.grid(column=0, row=1)
        self.save_button = Button(
            btn_frm,
            text='保存',
            command=lambda: self.exec_save(),
            font=DEFAULT_FONT,
            padx=15,
        )
        self.save_button.grid(column=1, row=1, sticky=(E))
        
        self.cmd_button = Button(
            btn_frm,
            text='実行',
            command=lambda: self.exec_cmd(),
            font=DEFAULT_FONT,
            padx=15,
        )
        self.cmd_button.grid(column=0, row=1, sticky=(E))
        
        self.bind("<Control-s>", self.exec_save_bind)
        self.bind("<Control-e>", self.exec_cmd_bind)

        """ フォーカス """
        self.transient(self.master)
        self.grab_set()
        
    def exec_save_bind(self, event):
        return self.exec_save()

    # 保存ボタンの処理
    def exec_save(self):
        # 保存
        if self.is_change_entry():
            self.save_entry()
            
        self.destroy() # ウィンドウの削除
        
    def save_entry(self):
        name = self.btn_name_entry.get()
        self.edit_btn["text"] = name
        self.edit_data["name"] = name
        self.edit_data["cmd"] = self.get_cmd_entry()
        self.edit_data["exec_type"] = self.checkbox_var.get()
        
        self.master.master.master.master.save_config()
        
    def is_change_entry(self):
        if self.btn_name_entry.get() != self.edit_data["name"]:
            return True
            
        if not lists_match(self.get_cmd_entry(), self.edit_data["cmd"]):
            return True
            
        if self.checkbox_var.get() != self.edit_data["exec_type"]:
            return True
        
        return False

    def get_cmd_entry(self):
        cmd_list = self.btn_cmd_entry.get("1.0", "end").split("\n")
        
        # 末尾が改行コードの場合は無視
        if cmd_list[-1] == "":
            cmd_list.pop()
        return cmd_list
        
    def exec_cmd_bind(self,event):
        return self.exec_cmd()
    
    def exec_cmd(self):
        cmd_list = self.btn_cmd_entry.get("1.0", "end").split("\n")
        cmd_list = [cmd for cmd in cmd_list if cmd != ""]
        if len(cmd_list) == 0:
            print("コマンドが登録されていません")
            return
        process_exec_cmd(cmd_list, is_parallel = self.checkbox_var.get())