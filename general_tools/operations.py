from general_tools.os_ops import ReportsBase
from resmap.ledger import LedgerOps
from resmap.transaction import TransactionOps


class OperationsBase:
    def __init__(self, browser):
        self.browser = browser
        self.ledger_master = LedgerMaster(browser)
        self.transaction_master = TransactionMaster(browser)
        self.redstar_master = RedStarMaster(browser, "redstar_report")


class Operations(OperationsBase):
    def __init__(self, browser):
        super().__init__(browser)

    def init_operation(self, item):
        month_table = ["allocate", "unallocate", "delete"]
        if item["operation"] in month_table:
            self.loop_through_ledger(item)

    def loop_through_ledger(self, item):
        current_url = self.browser.driver.current_url
        idx = 0
        while True:
            rows_length = self.ledger_master.retrieve_rows_length()
            if idx >= rows_length:
                break
            transaction = self.ledger_master.retrieve_elements()[idx]
            if "nsf" in transaction["label"].lower():
                idx += 1
                continue
            if self.ledger_master.click_transaction(transaction, item):
                self.transaction_master.define_type(item, transaction["type"])
                self.browser.driver.get(current_url)
            idx += 1


class LedgerMaster(LedgerOps):
    def __init__(self, browser):
        super().__init__(browser)

    def click_transaction(self, transaction, item):
        if transaction["type"] in item["type"]:
            self.browser.click_element(transaction["link"])
            return True
        return False


class TransactionMaster(TransactionOps):
    def __init__(self, browser):
        super().__init__(browser)

    def define_type(self, item, type):
        if type == "payment":
            type = "credit"
        self.transactions_loop(type, item)

    def transactions_loop(self, type, item):
        idx = 0
        while True:
            rows_length = self.retrieve_rows_length()
            if idx >= rows_length:
                break
            allocations = self.retrieve_elements(type)
            allocation = allocations[idx]
            self.perform_transaction_op(item["operation"], allocation)
            idx += 1


class RedStarMaster(ReportsBase):
    def __init__(self, browser, report):
        super().__init__(report)
        self.browser = browser
        self.redstar_idx = -1

    def cycle_ledger(self, operation="prev"):
        self.redstar_idx = (
            self.redstar_idx + 1 if operation == "next" else self.redstar_idx - 1
        )
        self.open_redstar_ledger()

    def open_redstar_ledger(self):
        urls = self.csv_ops.get_url_columns()
        url = urls[self.redstar_idx]
        self.browser.driver.get(url)
