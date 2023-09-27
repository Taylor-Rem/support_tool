from datetime import datetime
import calendar


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
