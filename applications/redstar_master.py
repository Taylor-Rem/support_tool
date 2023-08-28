from selenium.webdriver.common.by import By

from general_tools.os_ops import ReportsBase
from resmap_tools.ledger_ops import LedgerMaster


class RedstarBase(ReportsBase):
    def __init__(self):
        super().__init__("redstar_report")
        self.URLs = self.csv_ops.get_url_columns()


class RedstarFunctions(RedstarBase, LedgerMaster):
    def __init__(self, webdriver, thread_helper):
        RedstarBase.__init__(self)
        LedgerMaster.__init__(self, webdriver, thread_helper)
        self.current_index = 0
        self.open_redstar_ledger()

    def cycle_ledger(self, operation):
        self.current_index = (
            self.current_index + 1 if operation == "next" else self.current_index - 1
        )
        self.open_redstar_ledger()

    def open_redstar_ledger(self):
        URL = self.URLs[self.current_index]
        self.webdriver.driver.get(URL)


class RedstarMaster(RedstarFunctions):
    def __init__(self, webdriver, thread_helper=None):
        super().__init__(webdriver, thread_helper)

    def run_autostar(self):
        for URL in self.URLs:
            if self.is_cancelled():
                print("operation_cancelled")
                break
            self.webdriver.driver.get(URL)
            if not self.webdriver.element_exists(By.XPATH, '//td//font[@color="red"]'):
                continue

            self.loop_through_table("transaction_is_prepaid")

            self.loop_through_table("allocate_all")

    def is_cancelled(self):
        if self.thread_helper:
            return self.thread_helper.is_cancelled()
