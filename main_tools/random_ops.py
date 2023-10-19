from main_tools.operations import Operations, ResmapNavMaster
from selenium.webdriver.common.by import By
import pandas as pd


class RandomOps(Operations):
    def __init__(self, browser, operations_list, thread_helper=None):
        super().__init__(browser, thread_helper)
        self.operations_list = operations_list
        self.idx = -1

    def random_operation(self, next):
        path = (
            "/Users/taylorremund/Desktop/Data/Haven Cove Home Rent Audit. - Sheet1.csv"
        )
        df = pd.read_csv(path)
        self.space_ids = (
            df[df["spaceid"].notna()]
            .filter(like="spaceid")
            .astype(int)
            .values.flatten()
            .tolist()
        )
        self.change_ledger(next)

    def change_ledger(self, next):
        if next:
            self.idx += 1
        else:
            self.idx -= 1
        url = f"https://kingsley.residentmap.com/forward.php?propid=66&script=space.php&cmd=viewspace&spaceid={self.space_ids[self.idx]}"
        self.browser.open_program(url)
        self.browser.click(By.XPATH, "(//a[text()='Ledger'])[last()]")
