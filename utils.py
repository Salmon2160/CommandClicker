import os
import yaml
from shlex import quote
import copy
import subprocess
import webbrowser

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
def exec_cmd(cmd_list, encoding = 'shiftjis', is_parallel = True):
    
    if not is_parallel:
        cmd_list = ["&&".join(cmd_list)]
        
    for cmd in cmd_list:
        result = subprocess.Popen(
            cmd,
            shell=True,
            encoding=encoding,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            )
        print("> " + cmd.replace("&&","\n> "))
        
        out, err = result.communicate()

        if out is not None and "" != out:
            print(result.communicate()[0])
        
        if err is not None and "" != err:
            print(result.communicate()[1])
            
def is_valid_release(event):
    # ディスプレイ座標系で比較

    widget = event.widget
    x1 = widget.winfo_rootx()
    y1 = widget.winfo_rooty()
    x2 = x1 + widget.winfo_width()
    y2 = y1 + widget.winfo_height()

    x, y = event.x_root, event.y_root
    return (x1 <= x <= x2) and (y1 <= y <= y2)