import base64
from io import BytesIO
from PIL import Image

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
TAB_MAX_NUM = 6
    
class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, prompt=None):
        self.prompt = prompt
        self.value = None
        super().__init__(parent, title=title)

    def body(self, parent):
        self.label = tk.Label(parent, text=self.prompt, font=DEFAULT_FONT)
        self.label.pack()
        self.entry = tk.Entry(parent, font=DEFAULT_FONT)
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

        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)
        self.bind("<Motion>", self.on_close_motion)
        
        self.bind("<ButtonRelease-3>", self.on_tab_release)
        
    # タブ上で右クリック
    def on_tab_release(self, event):
        try:
            index = self.index("@%d,%d" % (event.x, event.y))
        except:
            return
        
        self.make_menu(event, index)
        
    def make_menu(self, event, tab_index):
        # タブメニューを表示
        pmenu = tk.Menu(self, tearoff=0)
        
        self.tab_rename_key = "タブ名の変更"
        pmenu.add_command(
            label=self.tab_rename_key,
            command=self.press_menu(tab_index, self.tab_rename_key),
            font=DEFAULT_FONT,
            )
        
        self.tab_add_key = "タブを追加"
        pmenu.add_command(
            label=self.tab_add_key,
            command=self.press_menu(tab_index, self.tab_add_key),
            font=DEFAULT_FONT,
            )
        
        self.tab_remove_key = "タブを削除"
        pmenu.add_command(
            label=self.tab_remove_key,
            command=self.press_menu(tab_index, self.tab_remove_key),
            font=DEFAULT_FONT,
            )
        
        pmenu.add_command(
            label="閉じる",
            font=DEFAULT_FONT,
            )
        x, y = event.x_root, event.y_root
        pmenu.post(x, y)
        
    def rename_tab(self, tab_index):
        new_name = CustomDialog(
            self,
            title=self.tab_rename_key,
            prompt="新しいタブ名を入力してください\n「{}」 -> ".format(self.tab(tab_index, "text"))
            ).value
        if new_name:
            self.tab(tab_index, text=new_name)
            self.master.master.rename_tab_config(tab_index, new_name)
                    
    def remove_tab(self, tab_index):
        self.forget(tab_index)
        self.event_generate("<<NotebookTabClosed>>")
        self.master.master.remove_tab_config(tab_index)

    def add_tab(self, tab_index):
        tab_count = self.index("end")
        if tab_count >= TAB_MAX_NUM:
            return
        
        tab_name = "タブ {}".format(tab_index)
        self.master.master.add_tab_config(tab_index, tab_name)
        tab_frm = self.master.master.make_tab_frm(tab_index)
        self.insert(tab_index, tab_frm, text=tab_name)
    
    def press_menu(self, tab_index, label):        
        def _press_menu():
            if label == self.tab_rename_key:
                self.rename_tab(tab_index)
            elif label == self.tab_remove_key:
                result = messagebox.askyesnocancel("Confirmation", "タグを削除しますが、よろしいでしょうか？")
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

    def on_close_release(self, event):
        """Called when the button is released"""
        
        if not self.instate(['pressed']) and not self.instate(['hover']):
            return
        
        if self.index("end") <= 1:
            return

        result = messagebox.askyesnocancel("Confirmation", "タグを削除しますが、よろしいでしょうか？")
        if not result:
            return

        element =  self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            self.state(['!pressed'])
            self.state(['!hover'])
            return

        index = self.index("@%d,%d" % (event.x, event.y))

        if self._active == index:
            self.remove_tab(index)

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