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
        self.cancelled = False

    def init_operation(self, command):
        self.command = command
        self.init_classes()
        self.perform_operation()

    def init_classes(self):
        if self.command["tool"] == "ticket":
            self.resmap_nav_master = ResmapNavMaster(self.browser, self.command, None)
            self.ticket_master = TicketMaster(
                self.browser, self.command, self.resmap_nav_master
            )
        if self.command["tool"] == "ledger":
            self.transaction_master = TransactionMaster(
                self.browser, self.command, self.thread_helper
            )
            self.ledger_master = LedgerMaster(
                self.browser, self.command, self.thread_helper, self.transaction_master
            )


class Operations(OperationsBase):
    def perform_operation(self):
        if self.command["tool"] == "ticket":
            self.ticket_master.perform_operation()
        elif self.command["tool"] == "ledger":
            if (
                self.command["operation"] in ["allocate", "unallocate"]
                and "all" in self.command["type"]
            ):
                self.specific_operations()
            else:
                self.ledger_master.ledger_loop()

    def specific_operations(self):
        types = [["payment"], ["charge"]]
        for transaction_type in types:
            self.command["type"] = transaction_type
            self.ledger_master.ledger_loop()

    def open_redstars(self, next):
        self.redstar_master = RedStarMaster(self.browser, "redstar_report")
        self.redstar_master.cycle_ledger(next)


class TicketMaster(TicketOperations):
    def __init__(self, browser, command, resmap_nav_master):
        super().__init__(browser, command)
        self.resmap_nav_master = resmap_nav_master

    def perform_operation(self):
        self.browser.switch_to_primary_tab()
        if self.command["operation"] == "open_ticket":
            self.open_ticket()
        elif self.command["operation"] == "resolve_ticket":
            self.change_ticket_status()

    def open_ticket(self):
        self.resmap_nav_master.info = self.scrape_ticket()
        self.resmap_nav_master.resmap_nav()


class ResmapNavMaster(ResmapNav):
    def __init__(self, browser, command, info):
        super().__init__(browser, info)
        self.command = command

    def resmap_nav(self):
        self.nav_to_unit()
        if self.command["selection"] == "ledger":
            self.open_ledger()
        if self.command["selection"] == "resident":
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
            if (idx >= rows_length) or (self.break_early()):
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
            (
                self.command["operation"] == "allocate"
                and "charge" in self.command["type"]
            )
            and self.ledger_info[0]["prepaid_amount"] <= 0
        ) or (self.thread_helper and self.thread_helper._is_cancelled):
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

    def cycle_ledger(self, next):
        self.redstar_idx = self.redstar_idx + 1 if next else self.redstar_idx - 1
        self.open_redstar_ledger()

    def open_redstar_ledger(self):
        urls = self.csv_ops.get_url_columns()
        url = urls[self.redstar_idx]
        self.browser.driver.get(url)
