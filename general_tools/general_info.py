from datetime import datetime
from general_tools.os_ops import ReportsBase
import calendar
import pandas as pd


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
        self.prop_ids = {
            "Arbordale Acres": 6,
            "Brentwood Southern": 8,
            "Carefree": 10,
            "Casa de Francisco": 15,
            "Casa Estates": 19,
            "Childs Lake Estates": 58,
            "Cielo Grande": 38,
            "Coach Royal": 31,
            "Colonial Manor": 52,
            "Country Meadows": 33,
            "Country Club": 32,
            "Douglass Village": 64,
            "East Gardens": 12,
            "Forest Hills Village": 60,
            "Forest View": 61,
            "Fountain East": 5,
            "Four Seasons": 56,
            "Front Range": 29,
            "FV Aurora": 20,
            "Friendly Village of Orangewood": 27,
            "FV Rockies": 26,
            "Gateway": 65,
            "Green Acres": 7,
            "Greenview Estates": 57,
            "Haven Cove": 66,
            "Highland Meadows": 1,
            "Hunter's Creek": 53,
            "Independence Woods": 47,
            "Kimberly Hills": 28,
            "Kings River": 49,
            "Knoll Terrace": 70,
            "La Montana del Sur": 16,
            "Lake Haven Estates": 22,
            "Lake Villa": 59,
            "Lakewood Estates TX": 54,
            "Lakewood": 45,
            "Lamplighter Village": 21,
            "Majestic Meadows": 23,
            "Majestic Oaks": 13,
            "Maplewood Estates": 62,
            "Mountain View": 14,
            "Oakland Estates": 48,
            "Palm Bay": 51,
            "Pecan Lake": 4,
            "Pleasant Valley": 36,
            "Quail Run": 17,
            "Riverhaven": 44,
            "Riverwoods": 46,
            "Sea-Vu South": 74,
            "Sea-Vu West": 75,
            "Shadow Ridge": 37,
            "Shadowstone Village ": 68,
            "Sherwood Forest ": 3,
            "Southwind": 41,
            "Stoneridge": 25,
            "Sugarberry Place": 9,
            "Summer Hill": 73,
            "Sunny Crest": 34,
            "Sunrise Estates": 67,
            "Sunshine Lake Estates": 55,
            "The Cliffs": 39,
            "The Meadows": 50,
            "Villa Cajon": 40,
            "Westcrest": 18,
            "Westwood Estates": 24,
            "Wintergreen": 30,
        }
