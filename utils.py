import os
import yaml
import datetime
import shlex
import copy
import subprocess
from multiprocessing import Process, Array

def lists_match(l1, l2):
    if len(l1) != len(l2):
        return False
    return all(x == y and type(x) == type(y) for x, y in zip(l1, l2))

def LoadYaml(path):
    if os.path.exists(path):
        # 日本語も含む場合は'rb'モード
        with open(path, 'rb') as file:
            config = yaml.safe_load(file)
        return config
    return None

def SaveYaml(path, dic):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except:
        pass
    
    # 日本語も含む場合は'rb'モード
    with open(path, 'wb') as file:
            yaml.dump(
                dic,
                file,
                encoding='utf-8',
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
                )
   
# - encoding = 'utf-8', 'shiftjis'
def exec_cmd(cmd_list, encoding = 'shiftjis', is_parallel = True, is_background = False):
    start = "start "
    if is_background:
        start += "/b "       
    prefix = "cmd /c "
    # prefix = "cmd /k " # for debug
    suffix = " && "
    
    exec_list = []
    if not is_parallel:
        # 各命令を「start cmd /c "cmd1 && cmd2 &&..."」の形式に連結
        cmd = start + prefix
        args=""
        arg_num = len(cmd_list)
        for idx, arg in enumerate(cmd_list):
            args += arg + suffix if idx != arg_num - 1 else arg
        cmd += "\"{}\"".format(args)
        exec_list.append(cmd)
    else:
        # 各命令を「start cmd /c {cmd}」の形式に整形
        exec_list = [start + prefix + "\"{}\"".format(cmd) for cmd in cmd_list]
        
    process_list = []
    for cmd in exec_list:
        process = subprocess.Popen(
            cmd,
            shell=True,
            encoding=encoding,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            )
        process_list.append(process)
        print("> " + cmd)
            
def process_exec_cmd(cmd_list, encoding = 'shiftjis', is_parallel = True, is_background = False):
    # 子プロセスを途中で終了させたい場合, Arrayによる管理が必要
    process = Process(target=exec_cmd, args=(cmd_list, encoding, is_parallel, is_background))
    process.start()
    return process
            
def is_release_in_same_widget(event):
    widget = event.widget
    
    # アクティブではないなら何もしない（誤作動対策）
    if not widget.focus_displayof():
        return
    
    # ディスプレイ座標系で比較
    x1 = widget.winfo_rootx()
    y1 = widget.winfo_rooty()
    x2 = x1 + widget.winfo_width()
    y2 = y1 + widget.winfo_height()

    x, y = event.x_root, event.y_root
    return (x1 < x < x2) and (y1 < y < y2)

def get_current_datetime_string():
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%Y_%m_%d_%S")
    return formatted_datetime

class Singleton(type):
    instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]
    
    def IsValid(cls):
        return cls in cls.instances.keys()
    
class ClipBoard(metaclass=Singleton):

    tab_data = None
    btn_data = None

    def __init__(self):
        if not Singleton.IsValid(self.__class__):
            pass
    
    def SetTabData(self, tab_idx):        
        from config.config import ConfigManager
        self.tab_data = ConfigManager().GetTabData(tab_idx)
        
    def GetTabData(self):
        return self.tab_data

    def IsValidTabData(self):
        return self.tab_data is not None
    
    def SetBtnData(self, tab_idx, btn_idx):
        from config.config import ConfigManager
        self.btn_data = ConfigManager().GetBtnData(tab_idx, btn_idx)
        
    def GetBtnData(self):
        return self.btn_data
    
    def IsValidBtnData(self):
        return self.btn_data is not None
