import base64
from io import BytesIO
from PIL import Image

from utils import *
from config.config import ConfigManager

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    # from tkinter import *
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import simpledialog
    from tkinter.simpledialog import askstring

DEFAULT_FONT=("", 12)

class CustomTabToplevel(tk.Toplevel):
    def __init__(self, master,tab_index, tab_name, pos):
        self.master = master
        super().__init__(master=master)
        self.overrideredirect(True)         # ウィンドウ枠を削除
        self.wm_attributes("-alpha", 0.75)  # ウィンドウを半透明
        self.attributes("-topmost", True)   # ウィンドウを最前面
        self.tab_index = tab_index
        self.tab_name = tab_name
        
        # タブ
        label = ttk.Label(
            self,
            text=tab_name,
            font=DEFAULT_FONT,
            padding =(15, 6),
            borderwidth = 20,
            relief="solid",
        )
        label.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        # 親の位置を元に表示
        x, y = pos
        self.offset = (10, 10)
        x0, y0 = self.offset
        self.geometry("+{}+{}".format(x - x0, y - y0))
        
        # マウスの移動をトラッキング
        self.move_bind = self.master.bind("<Motion>", self.move_with_mouse, '+')
        
    def move_with_mouse(self, event):
        # マウスの位置を取得し、ウィンドウをその位置に移動
        self.geometry("+{}+{}".format(event.x_root - self.offset[0], event.y_root - self.offset[1]))
        
    def unbind_event(self):
        self.master.unbind("<Motion>", self.move_bind)
    
class CustomDialog(simpledialog.Dialog):
    def __init__(self, master, title=None, prompt=None):
        self.prompt = prompt
        self.value = None
        super().__init__(master, title=title)

    def body(self, master):
        self.label = tk.Label(master, text=self.prompt, font=DEFAULT_FONT)
        self.label.pack()
        self.entry = tk.Entry(master, font=DEFAULT_FONT)
        self.entry.pack()

    def apply(self):
        self.value = self.entry.get()
        
class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        self.image_size = (7, 7)
        if "image_size" in kwargs.keys():
            self.image_size = kwargs.pop('image_size')
            
        if "tab_num" in kwargs.keys():
            self.tab_num = kwargs.pop('tab_num')

        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None
        self.drag_tab = None
        
        self.menu = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)
        self.bind("<Motion>", self.on_close_motion, True)
        
        self.bind("<ButtonRelease-3>", self.on_tab_release)
        
    # タブ上で右クリック
    def on_tab_release(self, event):
        try:
            index = self.index("@%d,%d" % (event.x, event.y))
        except:
            return
        
        self.make_menu(event, index)
        
    def make_menu(self, event, tab_index):
        # ドラッグ中の場合、ドラッグを無効
        self.reset_drag()

        # タブメニューを表示
        menu = tk.Menu(self, tearoff=0)
        
        self.tab_rename_key = "タブ名の変更"
        menu.add_command(
            label=self.tab_rename_key,
            command=self.press_menu(tab_index, self.tab_rename_key),
            font=DEFAULT_FONT,
            )
        
        self.tab_copy_key = "タブをコピー"
        menu.add_command(
            label=self.tab_copy_key,
            command=self.press_menu(tab_index, self.tab_copy_key),
            font=DEFAULT_FONT,
            )
        
        self.tab_paste_key = "タブを貼り付け"
        menu.add_command(
            label=self.tab_paste_key,
            command=self.press_menu(tab_index, self.tab_paste_key),
            font=DEFAULT_FONT,
            )
        if not ClipBoard().IsValidTabData():
            menu.entryconfig(self.tab_paste_key, state="disabled")
        
        menu.add_separator()
        
        self.tab_add_key = "タブを追加"
        menu.add_command(
            label=self.tab_add_key,
            command=self.press_menu(tab_index, self.tab_add_key),
            font=DEFAULT_FONT,
            )
        
        self.tab_remove_key = "タブを削除"
        menu.add_command(
            label=self.tab_remove_key,
            command=self.press_menu(tab_index, self.tab_remove_key),
            font=DEFAULT_FONT,
            )
        
        menu.add_separator()
        menu.add_command(
            label="閉じる",
            font=DEFAULT_FONT,
            )
        x, y = event.x_root, event.y_root
        menu.post(x, y)
        
        self.menu = menu
        
    def rename_tab(self, tab_index):
        new_name = CustomDialog(
            self,
            title=self.tab_rename_key,
            prompt="新しいタブ名を入力してください\n「{}」 -> ".format(self.tab(tab_index, "text"))
            ).value
        if new_name:
            self.tab(tab_index, text=new_name)
            ConfigManager().SetTabData(tab_index, tab_name = new_name)
            ConfigManager().SaveConfig()
                    
    def remove_tab(self, tab_index):
        self.forget(tab_index)
        self.event_generate("<<NotebookTabClosed>>")
        ConfigManager().RemoveTabData(tab_index)
        ConfigManager().SaveConfig()

    def add_tab(self, tab_index):
        # 循環参照するので、局所インポート
        from CommandClicker import tab_frm
        
        tab_count = self.index("end")
        if tab_count >= self.tab_num:
            return
        
        tab_name = "タブ {}".format(tab_index)
        ConfigManager().AddTabData(tab_index, tab_name)
        ConfigManager().SaveConfig()
        tab = tab_frm(self, tab_index)
        if tab_count == tab_index:
            self.add(tab, text=tab_name, padding=5)
        else:
            self.insert(tab_index, tab, text=tab_name, padding=5)
    
    def press_menu(self, tab_index, label):        
        def _press_menu():
            if label == self.tab_rename_key:
                self.rename_tab(tab_index)
            elif label == self.tab_copy_key:
                ClipBoard().SetTabData(tab_index)
            elif label == self.tab_paste_key:
                if not ClipBoard().IsValidTabData():
                    return
                tab_data = ClipBoard().GetTabData()
                tab_frm = self.nametowidget(self.tabs()[tab_index])
                tab_frm.update_tab_data(tab_data)
                self.tab(tab_index, text=tab_data["name"])
                ConfigManager().SetTabData(tab_index, tab_name = tab_data["name"])
                ConfigManager().SaveConfig()
                
            elif label == self.tab_remove_key:
                result = messagebox.askyesnocancel("Confirmation", "タグを削除しますが、よろしいでしょうか？", default = 'no')
                if not result:
                    return
                self.remove_tab(tab_index)
            elif label == self.tab_add_key:
                self.add_tab(tab_index + 1)
                
        return _press_menu
        
    # バツボタンの実装
    def on_close_motion(self, event):
        element = self.identify(event.x, event.y)
        if "close" in element:
            self.state(['!pressed'])
            self.state(['hover'])
        else:
            self.state(['!pressed'])
            self.state(['!hover'])

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self.state(['hover'])
            self._active = index
            return "break"
        else:
            # タブ移動（ドラッグ）
            try:
                index = self.index("@%d,%d" % (event.x, event.y))
            except:
                return
            tab_name = self.tab(index)["text"]
            
            x = int(self.master.winfo_rootx() + event.x)
            y = int(self.master.winfo_rooty() + event.y)
            self.drag_tab = CustomTabToplevel(self, index, tab_name, (x, y))
            
    def reset_drag(self):
        if self.drag_tab is None:
            return
        self.drag_tab.unbind_event()
        self.drag_tab.destroy()
        self.drag_tab = None
        
        # 巻き込まれてunbindされるので再登録
        self.bind("<Motion>", self.on_close_motion, True)

    def on_close_release(self, event):
        """Called when the button is released"""
        if self.drag_tab is not None:
            # タブ移動（ドロップ）
            source_index = self.drag_tab.tab_index
            source_name = self.drag_tab.tab_name
            
            # ドラッグ機能をオフ
            self.reset_drag()
            
            try:
                target_index = self.index("@%d,%d" % (event.x, event.y))
            except:
                return
            
            if target_index == source_index:
                return

            source_tab = self.nametowidget(self.tabs()[source_index])
            self.insert(target_index, source_tab,  text=source_name, padding=5)
            ConfigManager().SwapTabData(source_index, target_index)
            ConfigManager().SaveConfig()
            return
    
        if not self.instate(['pressed']) and not self.instate(['hover']):
            return
        
        if self.index("end") <= 1:
            return

        element =  self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            self.state(['!pressed'])
            self.state(['!hover'])
            return
        
        target_index = self.index("@%d,%d" % (event.x, event.y))
        if self._active == target_index:
            result = messagebox.askyesnocancel("Confirmation", "タグを削除しますが、よろしいでしょうか？", default = 'no')
            if not result:
                return
            self.remove_tab(target_index)

        self.state(["!pressed"])
        self.state(['!hover'])
        self._active = None

    def __initialize_custom_style(self):
        style = ttk.Style()

        def resize_base64(image_data, to_size):
            image_data = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_data))
            resized_image = image.resize(to_size)
            
            buffer = BytesIO()
            resized_image.save(buffer, format="PNG")
            resized_base64_image = base64.b64encode(buffer.getvalue()).decode()
            return resized_base64_image
        
        # image data that is encoded by Base64
        cross_black = '''
                      R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                      d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                      5kEJADs=
                      '''
        cross_black = resize_base64(cross_black, self.image_size)
                      
        cross_yellow = '''
                       R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                       AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                       '''
        cross_yellow = resize_base64(cross_yellow, self.image_size)
        
        cross_red = '''
                    R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                    d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                    5kEJADs=
                    '''
        cross_red = resize_base64(cross_red, self.image_size)

        self.images = (
            tk.PhotoImage("img_close", data=cross_black),
            tk.PhotoImage("img_closehover", data=cross_yellow),
            tk.PhotoImage("img_closepressed", data=cross_red),
            tk.PhotoImage("img_closeintact", data=cross_black)
        )

        style.element_create(
            "close", "image", "img_close",
            ("!active", "!selected", "img_closeintact"),
            ("active", "!pressed", "hover", "!disabled", "img_closehover"), 
            ("active", "pressed", "hover", "!disabled", "img_closepressed"),
            ("active", "!pressed", "!hover", "!disabled", "img_close"), 
            border=8, sticky=''
        )
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                    ]
                            })
                        ]
                    })
                ]
            })
        ])

if __name__ == "__main__":
    root = tk.Tk()

    notebook = CustomNotebook(width=200, height=200)
    notebook.pack(side="top", fill="both", expand=True)

    for color in ("red", "orange", "green", "blue", "violet"):
        frame = tk.Frame(notebook, background=color)
        notebook.add(frame, text=color)

    root.mainloop()