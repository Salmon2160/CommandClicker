import copy

from utils import *

CONFIG_FILENAME = "config.yaml"
DEFAULT_CONFIG = (6, 4, 4)
BACKUP_FOLDER = "backup"

class ConfigManager(metaclass=Singleton):

    config = None

    def __init__(self):
        if not Singleton.IsValid(self.__class__):
            self.Setup();
            
    def Setup(self):

        # バックアップ内容は起動時の内容に拘る
        is_exist_config = os.path.isfile(CONFIG_FILENAME)
        if is_exist_config:
            self.config = LoadYaml(CONFIG_FILENAME)
            self.UpgradeConfig(self.config)
            time_str = get_current_datetime_string()
            backup_path = os.path.join(BACKUP_FOLDER, time_str+ "_" + CONFIG_FILENAME)
            SaveYaml(backup_path, self.config)
        
        # 設定ファイルがない又は、設定ファイルのサイズ設定が不正の場合は新規作成
        if not is_exist_config or not self.IsValidSize(self.config):
            tab_num, width, height = DEFAULT_CONFIG
            self.config = self.InitConfig(tab_num, (width, height))
            SaveYaml(CONFIG_FILENAME, self.config)
            
        if not self.IsValidConfig(self.config):
            self.config = self.ReshapeConfig(self.config)
            SaveYaml(CONFIG_FILENAME, self.config)

    @staticmethod
    def InitTabConfig(size, tab_name):    
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
                btn_data["exec_type2"] = False
                tab_data["btn_list"].append(btn_data)
        return tab_data
    
    @staticmethod
    def InitConfig(tab_num, size):
        config = {}
        config["tab_num"] = tab_num
        config["btn_size"] = list(size)
        config["data"] = []
        width, height = size
       
        for tab_idx in range(tab_num):
            tab_data = ConfigManager.InitTabConfig(size, 'タブ {}'.format(tab_idx))
            config["data"].append(tab_data)
        return config

    @staticmethod
    def IsValidSize(config):
        tab_num = config["tab_num"]
        w, h = config["btn_size"]
        data = config["data"]
    
        if tab_num <= 0:
            return False
    
        if w * h <= 0:
            return False
    
        if type(data) != list:
            return False
    
        if len(data) == 0:
            return False
    
        for tab_idx in range(len(data)):
            if len(data[tab_idx]["btn_list"]) == 0:
                return False
    
        return True

    @staticmethod
    def IsValidConfig(config):
        tab_num = config["tab_num"]
        w, h = config["btn_size"]
        data = config["data"]
    
        if len(data) > tab_num:
            return False

        for tab_idx in range(len(data)):
            if len(data[tab_idx]["btn_list"]) != w * h:
                return False
    
        return True

    @staticmethod
    def ReshapeConfig(config):
        tab_num = config["tab_num"]
        w, h = config["btn_size"]
        btn_num = w * h
    
        cur_tab_num = len(config["data"])
    
        reshape_config = ConfigManager.InitConfig(tab_num, (w, h))
        for tab_idx in range(min(tab_num, cur_tab_num)):
            reshape_config["data"][tab_idx]["name"] = config["data"][tab_idx]["name"]
        
            cur_btn_num = len(config["data"][tab_idx]["btn_list"])
            for btn_idx in range(min(btn_num, cur_btn_num)):
                reshape_config["data"][tab_idx]["btn_list"][btn_idx] = config["data"][tab_idx]["btn_list"][btn_idx]
        return reshape_config

    @staticmethod
    def UpgradeConfig(config):
        # アップデートで追加された設定変数を古いセーブデータに追加
    
        # exec_type2 の互換性
        for tab_idx in range(len((config["data"]))):
            for btn_idx in range(len(config["data"][tab_idx]["btn_list"])):
                if "exec_type2" not in config["data"][tab_idx]["btn_list"][btn_idx].keys():
                    config["data"][tab_idx]["btn_list"][btn_idx]["exec_type2"] = False
    
        return config
   
    def GetBtnSize(self):
        return copy.deepcopy(self.config["btn_size"])
    
    def GetBtnData(self, tab_idx, btn_idx):
        return copy.deepcopy(self.config["data"][tab_idx]["btn_list"][btn_idx])
    
    def GetBtnList(self, tab_idx):
        return copy.deepcopy(self.config["data"][tab_idx]["btn_list"])
    
    def GetTabData(self, tab_idx):
        return copy.deepcopy(self.config["data"][tab_idx])
    
    def GetMaxTabNum(self):
        return copy.deepcopy(self.config["tab_num"])
    
    def GetTabNum(self):
        return copy.deepcopy(len(self.config["data"]))
    
    def GetTabName(self, tab_idx):
        return copy.deepcopy(self.config["data"][tab_idx]["name"])
    
    def SetBtnData(self, tab_idx, btn_idx, btn_data):
        self.config["data"][tab_idx]["btn_list"][btn_idx] = btn_data
    
    def SwapBtnData(self, tab_idx, from_idx, to_idx):
        btn_list = self.config["data"][tab_idx]["btn_list"]
        btn_list[from_idx], btn_list[to_idx] = btn_list[to_idx], btn_list[from_idx]
    
    def SetTabData(self, tab_idx, tab_name = None, btn_list = None):
        if tab_name is not None:
            self.config["data"][tab_idx]["name"] = tab_name
        if btn_list is not None:
            self.config["data"][tab_idx]["btn_list"] = btn_list
            
    def AddTabData(self, tab_idx, tab_name, tab_data = None):
        if tab_data is None:
            tab_data = self.InitTabConfig(self.GetBtnSize(), tab_name)
        self.config["data"].insert(tab_idx, tab_data)
        # self.config["tab_num"] += 1

    def RemoveTabData(self, tab_idx):
        self.config["data"].pop(tab_idx)
        
    def SwapTabData(self, from_idx, to_idx):
        if from_idx == to_idx:
            return

        data = self.config["data"]
        if from_idx < to_idx:
            data.insert(to_idx + 1, data[from_idx])
            data.pop(from_idx)
        else:
            data.insert(to_idx, data[from_idx])
            data.pop(from_idx + 1)
    
    def SaveConfig(self):
        SaveYaml(CONFIG_FILENAME, self.config)