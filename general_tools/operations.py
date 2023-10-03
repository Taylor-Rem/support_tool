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

    def init_operation(self, command):
        month_table = ["allocate", "unallocate", "delete"]
        general_ledger = ["delete"]
        if command["operation"] in month_table:
            self.loop_through_ledger(command)
        if command["operation"] in general_ledger:
            print(command)

    def loop_through_ledger(self, command):
        current_url = self.browser.driver.current_url
        idx = 0
        ledger_info = self.ledger_master.retrieve_elements()
        while True:
            if idx >= ledger_info["rows_length"] or self.break_early(
                command, ledger_info
            ):
                break
            ledger_row = ledger_info["rows"][idx]
            ledger_row["prepaid_amount_info"] = ledger_info["prepaid_amount_info"]
            if ledger_row.get("special_type"):
                if (
                    "bounced_check" in ledger_row["special_type"]
                    or "system_nsf" in ledger_row["special_type"]
                ):
                    idx += 1
                    continue
            if self.ledger_master.click_transaction(ledger_row, command):
                self.transaction_master.transactions_loop(command, ledger_row)
                if self.browser.driver.current_url != current_url:
                    self.browser.driver.get(current_url)
                ledger_info = self.ledger_master.retrieve_elements()
            idx += 1

    def break_early(self, command, ledger_info):
        if command["operation"] == "allocate" and "charge" in command["type"]:
            if (
                ledger_info["prepaid_amount_info"]["prepaid_amount"] == 0
                or not ledger_info["prepaid_amount_info"]["is_credit"]
            ):
                return True


class LedgerMaster(LedgerOps):
    def __init__(self, browser):
        super().__init__(browser)

    def click_transaction(self, ledger_row, command):
        exclude = command.get("exclude", [])
        if command["operation"] in ("allocate", "unallocate", "delete"):
            if (
                (ledger_row["type"] in command["type"])
                or (ledger_row["special_type"] in command["type"])
            ) and (
                (ledger_row["type"] not in exclude)
                or ledger_row["special_type"] not in exclude
            ):
                self.browser.click_element(ledger_row["link"])
                return True

    def click_ledger(self, command):
        if command["operation"] == "credit":
            pass


class TransactionMaster(TransactionOps):
    def __init__(self, browser):
        super().__init__(browser)

    def transactions_loop(self, command, transaction):
        idx = 0
        transaction_info = self.retrieve_elements(transaction["type"])
        while True:
            if idx >= transaction_info["rows_length"]:
                break
            finished_list = idx >= transaction_info["rows_length"] - 1
            allocation = transaction_info["rows"][idx]
            operation_result = self.perform_transaction_op(
                command,
                allocation,
                transaction["type"],
                transaction_info["total_amount"],
                finished_list,
            )
            if operation_result == "break":
                break
            if operation_result == "continue":
                continue
            if operation_result == "reload":
                transaction_info = self.retrieve_elements(transaction["type"])
                continue
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
