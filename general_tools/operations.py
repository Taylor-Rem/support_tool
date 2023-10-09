from general_tools.os_ops import ReportsBase
from resmap.ledger import LedgerOps
from resmap.transaction import TransactionOps
from resmap.add_credit import AddCreditOps
from resmap.navigation import ResmapNav
from manage_portal.tickets import TicketOperations


class OperationsBase:
    def __init__(self, browser, thread_helper=None):
        self.browser = browser
        self.thread_helper = thread_helper
        self.redstar_master = RedStarMaster(self.browser, "redstar_report")
        self.cancelled = False
        self.ticket_master = TicketMaster(self.browser)
        self.resmap_nav = ResmapNavMaster(self.browser, None)

    def init_operation(self, command):
        self.command = command
        self.initialize_classes(command)
        self.perform_operation()

    def initialize_classes(self, command):
        self.transaction_master = TransactionMaster(
            self.browser, command, self.thread_helper
        )
        self.ledger_master = LedgerMaster(
            self.browser, command, self.thread_helper, self.transaction_master
        )


class Operations(OperationsBase):
    def perform_operation(self):
        if self.command["type"] == "all":
            self.specific_operations()
        else:
            self.ledger_master.ledger_loop()

    def specific_operations(self):
        if self.command["operation"] in ["allocate", "unallocate"]:
            types = ["payment", "charge"]
            for transaction_type in types:
                self.command["type"] = transaction_type
                self.ledger_master.ledger_loop()

    def open_ticket(self, location):
        self.browser.switch_to_primary_tab()
        self.resmap_nav.info = self.ticket_master.scrape_ticket()
        self.resmap_nav.resmap_nav(location.lower())


class TicketMaster(TicketOperations):
    def __init__(self, browser):
        super().__init__(browser)


class ResmapNavMaster(ResmapNav):
    def __init__(self, browser, info):
        super().__init__(browser, info)

    def resmap_nav(self, location):
        self.nav_to_unit()
        if location == "ledger":
            self.open_ledger()
        if location == "resident":
            pass


class LedgerMaster(LedgerOps):
    def __init__(self, browser, command, thread_helper, transaction_master):
        super().__init__(browser, command)
        self.transaction_master = transaction_master
        self.thread_helper = thread_helper
        self.current_url = self.browser.driver.current_url

    def ledger_loop(self):
        idx = 0
        self.ledger_info = self.retrieve_elements()
        rows_length = len(self.ledger_info)
        while True:
            if (
                (idx >= rows_length)
                or (self.break_early())
                or (self.thread_helper and self.thread_helper._is_cancelled)
            ):
                break
            self.ledger_row = self.ledger_info[idx]
            if self.check_nsf():
                idx += 1
                continue
            if self.click_ledger_element():
                self.transaction_master.transaction_loop(self.ledger_row)
                self.return_to_ledger()
                self.ledger_info = self.retrieve_elements()
                rows_length = len(self.ledger_info)
            idx += 1

    def break_early(self):
        if (
            self.command["operation"] == "allocate" and "charge" in self.command["type"]
        ) and self.ledger_info[0]["prepaid_amount"] <= 0:
            return True


class TransactionMaster(TransactionOps):
    def __init__(self, browser, command, thread_helper):
        super().__init__(browser, command)
        self.thread_helper = thread_helper

    def transaction_loop(self, ledger_row):
        self.ledger_row = ledger_row
        self.transaction_info = self.retrieve_elements()
        idx = 0
        while True:
            if idx >= self.transaction_info["rows_length"] or (
                self.thread_helper and self.thread_helper._is_cancelled
            ):
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
