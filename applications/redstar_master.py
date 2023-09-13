from selenium.webdriver.common.by import By

from general_tools.os_ops import ReportsBase
from resmap_tools.ledger_ops import LedgerMaster


class RedstarBase(ReportsBase):
    def __init__(self):
        super().__init__("redstar_report")
        try:
            self.URLs = self.csv_ops.get_url_columns()
        except:
            self.URLs = None


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
        if self.current_index >= len(self.URLs):
            return
        self.open_redstar_ledger()

    def open_redstar_ledger(self):
        if self.URLs:
            URL = self.URLs[self.current_index]
            self.webdriver.driver.get(URL)
        else:
            pass


class RedstarMaster(RedstarFunctions):
    def __init__(self, webdriver, thread_helper=None):
        super().__init__(webdriver, thread_helper)

    def auto_star_operations(self, month):
        self.loop_through_table(
            "allocate_all", "credits", is_autostar=True, chosen_month=month
        )
        if not self.ledger_has_redstar():
            return
        self.loop_through_table(
            "unallocate_all", "charges", is_autostar=True, chosen_month=month
        )
        self.loop_through_table(
            "unallocate_all", "credits", is_autostar=True, chosen_month=month
        )
        self.loop_through_table(
            "allocate_all", "charges", is_autostar=True, chosen_month=month
        )
        self.loop_through_table(
            "allocate_all", "credits", is_autostar=True, chosen_month=month
        )

    def run_autostar(self):
        choose_month = ["current", "previous"]
        for URL in self.URLs:
            if self.is_cancelled():
                print("operation_cancelled")
                break
            self.webdriver.driver.get(URL)
            for month in choose_month:
                if not self.ledger_has_redstar():
                    break
                if self.fix_nsf(month):
                    break
                if not self.ledger_has_redstar():
                    break
                self.auto_star_operations(month)

    def is_cancelled(self):
        if self.thread_helper:
            return self.thread_helper.is_cancelled()
