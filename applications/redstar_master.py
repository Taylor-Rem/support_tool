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

    def nsf_in_month(self, chosen_month):
        return (
            self.loop_through_table(None, is_autostar=True, chosen_month=chosen_month)
            == "nsf"
        )

    def ledger_has_redstar(self):
        return self.webdriver.element_exists(By.XPATH, '//td//font[@color="red"]')

    def auto_star_operations(self, month):
        self.loop_through_table(
            "allocate_all", "Credits", is_autostar=True, chosen_month=month
        )
        if not self.ledger_has_redstar():
            return
        self.loop_through_table(
            "unallocate_all", "Charges", is_autostar=True, chosen_month=month
        )
        self.loop_through_table(
            "unallocate_all", "Credits", is_autostar=True, chosen_month=month
        )
        self.loop_through_table(
            "allocate_all", "Charges", is_autostar=True, chosen_month=month
        )
        self.loop_through_table(
            "allocate_all", "Auto", is_autostar=True, chosen_month=month
        )

    def run_autostar(self):
        for URL in self.URLs:
            if self.is_cancelled():
                print("operation_cancelled")
                break
            self.webdriver.driver.get(URL)
            if not self.ledger_has_redstar():
                continue
            if self.nsf_in_month("current"):
                self.loop_through_table("fix_nsf")
                self.auto_star_operations("current")
            if self.ledger_has_redstar():
                continue
            self.auto_star_operations("previous")
            self.auto_star_operations("current")

    def is_cancelled(self):
        if self.thread_helper:
            return self.thread_helper.is_cancelled()
