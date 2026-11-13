import os
from config import support_desk_url, data_dir
from main_tools.operations import Operations, ResmapNavMaster
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re, time
import pandas as pd
from datetime import datetime, date
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import urllib.parse


class RandomOps(Operations):
    def __init__(self, browser, operations_list, thread_helper=None):
        super().__init__(browser, thread_helper)
        self.operations_list = operations_list
        self.support_desk_link = support_desk_url
        self.idx = 0


        


                


    """
    MONTLY CONCESSIONS
    """

    def random_operation(self):
        command = {"operation": "credit", "tools": ["ledger", "credit"]}
        command["comment"] = "Monthly Charge Concessions"
        command["table"] = "bottom"
        df = pd.read_csv(
            os.path.join(data_dir, "Monthly Credits_Concessions - Sheet1.csv")
        )
        urls = df.filter(like="URL").values.flatten().tolist()
        selection = df.filter(like="Credit or Concession").values.flatten().tolist()
        units = df.filter(like="Unit").values.flatten().tolist()
        idx = 0
        while True:
            if idx >= len(urls):
                break
            self.browser.open_program(urls[idx])
            command["selection"] = selection[idx]
            self.init_operation(command)
            idx += 1


