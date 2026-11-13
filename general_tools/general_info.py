from datetime import datetime
from general_tools.os_ops import ReportsBase
import calendar
import pandas as pd
from config import prop_ids


class GeneralInfo:
    def __init__(self):
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.day = now.day

        self.months = {
            "January": "1",
            "February": "2",
            "March": "3",
            "April": "4",
            "May": "5",
            "June": "6",
            "July": "7",
            "August": "8",
            "September": "9",
            "October": "10",
            "November": "11",
            "December": "12",
        }
        self.months_array = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        # Property name -> portal property id; the list lives in config.py (gitignored).
        self.prop_ids = dict(prop_ids)