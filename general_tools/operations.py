from general_tools.os_ops import ReportsBase
from resmap.ledger import LedgerOps
from resmap.transaction import TransactionOps
from resmap.add_credit import AddCreditOps


class OperationsBase:
    def __init__(self, browser):
        self.browser = browser
        self.redstar_master = RedStarMaster(self.browser, "redstar_report")

    def init_operation(self, command):
        self.command = command
        self.initialize_classes(command)
        self.perform_operation()

    def initialize_classes(self, command):
        self.transaction_master = TransactionMaster(self.browser, command)
        self.ledger_master = LedgerMaster(
            self.browser, command, self.transaction_master
        )


class Operations(OperationsBase):
    def __init__(self, browser):
        super().__init__(browser)

    def perform_operation(self):
        month_table = ["allocate", "unallocate", "delete"]
        general_ledger = ["credit"]

        if self.command["operation"] in month_table:
            self.ledger_month_ops("current")

        if self.command["operation"] in general_ledger:
            self.ledger_master.click_ledger()

    def ledger_month_ops(self, month):
        self.ledger_master.ledger_loop(month)


class LedgerMaster(LedgerOps):
    def __init__(self, browser, command, transaction_master):
        super().__init__(browser, command)
        self.transaction_master = transaction_master
        self.current_url = self.browser.driver.current_url

    def ledger_loop(self, table):
        self.table = table
        idx = 0
        self.ledger_info = self.retrieve_elements()
        rows_length = len(self.ledger_info)
        while True:
            if idx >= rows_length or self.break_early():
                break
            self.ledger_row = self.ledger_info[idx]
            if self.check_nsf():
                idx += 1
                continue
            if self.click_transaction():
                self.transaction_master.transaction_loop(self.ledger_row)
                self.return_to_ledger()
                self.ledger_info = self.retrieve_elements()
                rows_length = len(self.ledger_info)
            idx += 1

    def break_early(self):
        if (
            self.command["operation"] == "allocate" and "charge" in self.command["type"]
        ) and self.ledger_info["prepaid_amount"] <= 0:
            return True


class TransactionMaster(TransactionOps):
    def __init__(self, browser, command):
        super().__init__(browser, command)

    def transaction_loop(self, ledger_row):
        self.ledger_row = ledger_row
        self.transaction_info = self.retrieve_elements()
        idx = 0
        while True:
            if idx >= self.transaction_info["rows_length"]:
                break
            self.finished_list = idx >= self.transaction_info["rows_length"] - 1
            self.allocation = self.transaction_info["rows"][idx]
            operation_result = self.perform_transaction_op()
            if operation_result == "break":
                break
            if operation_result == "continue":
                continue
            if operation_result == "reload":
                self.transaction_info = self.retrieve_elements()
                continue
            idx += 1


class AddCreditMaster(AddCreditOps):
    def __init__(self, browser, command):
        super().__init__()


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
