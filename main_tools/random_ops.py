from main_tools.operations import Operations, ResmapNavMaster
from selenium.webdriver.common.by import By
import pandas as pd


class RandomOps(Operations):
    def __init__(self, browser, operations_list, thread_helper=None):
        super().__init__(browser, thread_helper)
        self.operations_list = operations_list
        self.idx = -1

    """
    MONTLY CONCESSIONS
    """

    def random_operation(self):
        command = {"operation": "credit", "tools": ["ledger", "credit"]}
        command["comment"] = "Monthly Charge Concessions"
        command["table"] = "bottom"
        df = pd.read_csv(
            "/Users/taylorremund/Desktop/Data/Monthly Credits_Concessions - Sheet1.csv"
        )
        urls = df.filter(like="URL").values.flatten().tolist()
        selection = df.filter(like="Credit or Concession").values.flatten().tolist()
        units = df.filter(like="Unit").values.flatten().tolist()
        idx = 0
        while True:
            if idx >= len(urls):
                break
            print(urls[idx], units[idx])
            self.browser.open_program(urls[idx])
            command["selection"] = selection
            self.init_operation(command)
            idx += 1

    # """
    # PROPERTY FEES REMOVAL
    # """
    # def random_operation(self):
    #     while True:
    #         try:
    #             self.browser.click(
    #                 By.XPATH, "//i[@class='material-icons' and text()='check_box']"
    #             )
    #         except:
    #             pass
    #         self.browser.click(
    #             By.XPATH,
    #             "//button[@type='submit' and normalize-space(text())='save and next']",
    #         )

    # """
    # DOUBLE CHARGE REMOVAL
    # """
    # def random_operation(self):
    #     for i in range(925, 1238):
    #         if self.thread_helper and self.thread_helper._is_cancelled:
    #             break
    #         url = f"https://kingsley.residentmap.com/forward.php?propid=5&script=space.php&cmd=viewspace&spaceid={i}"
    #         self.browser.open_program(url)
    #         try:
    #             self.browser.click(
    #                 By.XPATH, ".//a[contains(text(), 'Monthly Charges/Credits')]"
    #             )
    #         except:
    #             continue
    #         rows = self.browser.get_rows(
    #             By.XPATH,
    #             "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[6]/tbody/tr[2]/td/table/tbody",
    #         )
    #         for row in rows:
    #             if self.browser.skip_row(row, "th3"):
    #                 continue
    #             cells = row.find_elements(By.TAG_NAME, "td")
    #             end_date = cells[4].text.strip()
    #             if "/" not in end_date:
    #                 delete_element = row.find_element(
    #                     By.XPATH, ".//a[contains(text(), 'Delete')]"
    #                 )
    #                 self.browser.click_element(delete_element)
    #                 alert = self.browser.driver.switch_to.alert
    #                 alert.accept()
