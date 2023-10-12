from general_tools.os_ops import ReportsBase
from resmap.ledger import LedgerOps
from resmap.transaction import TransactionOps
from resmap.credit import CreditOps
from resmap.navigation import ResmapNav
from manage_portal.support_desk import SupportDeskOperations
from manage_portal.tickets import TicketOperations


class OperationsBase:
    def __init__(self, browser, thread_helper=None):
        self.browser = browser
        self.thread_helper = thread_helper
        self.cancelled = False
        self.redstar_master = RedStarMaster(self.browser, "redstar_report")

    def init_operation(self, command):
        self.command = command
        self.init_classes()
        self.perform_operation()

    def init_classes(self):
        if "ticket" in self.command["tools"]:
            self.resmap_nav_master = ResmapNavMaster(self.browser, self.command, None)
            self.ticket_master = TicketMaster(
                self.browser, self.command, self.resmap_nav_master
            )
            self.supportdesk_master = SupportDeskMaster(
                self.browser, self.command, self.ticket_master
            )
        if "ledger" in self.command["tools"]:
            if "table" in self.command["tools"]:
                click_location = TransactionMaster(
                    self.browser, self.command, self.thread_helper
                )
            if "credit" in self.command["tools"]:
                click_location = CreditMaster(self.browser, self.command)

            self.ledger_master = LedgerMaster(
                self.browser, self.command, self.thread_helper, click_location
            )


class Operations(OperationsBase):
    def perform_operation(self):
        if "ticket" in self.command["tools"]:
            self.ticket_master.perform_operation()
        elif "ledger" in self.command["tools"]:
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

    def open_redstars(self, next_ledger):
        self.redstar_master.cycle_ledger(next_ledger)


class LedgerMaster(LedgerOps):
    def __init__(self, browser, command, thread_helper, click_location):
        super().__init__(browser, command)
        self.click_location = click_location
        self.thread_helper = thread_helper
        self.current_url = self.browser.driver.current_url

    def ledger_loop(self):
        self.idx = 0
        self.refresh_ledger_info()
        while True:
            if self.break_early():
                break
            self.ledger_row = self.ledger_info[self.idx]
            if self.continue_loop():
                continue
            if self.perform_operation():
                self.return_to_ledger()
                if not self.refresh_ledger_info():
                    return
            self.idx += 1

    def perform_operation(self):
        result = (
            self.click_ledger_credit()
            if self.command["operation"] == "credit"
            else self.click_ledger_table()
        )
        if result:
            if self.command["operation"] == "delete":
                self.click_location.delete()
            if self.command["operation"] in ["credit", "delete"]:
                self.idx -= 1
            if self.command["operation"] in ["allocate", "unallocate", "credit"]:
                self.click_location.operation(self.ledger_row)
            return True

    def continue_loop(self):
        if self.check_nsf() or (
            self.ledger_row.get("link") is None
            and self.command["operation"] != "credit"
        ):
            self.idx += 1
            return True

    def break_early(self):
        if (
            (self.thread_helper and self.thread_helper._is_cancelled)
            or (self.idx >= self.rows_length)
            or (
                self.command["operation"] == "allocate"
                and "charge" in self.command["type"]
                and self.ledger_info[0]["prepaid_amount"] <= 0
            )
            or self.rows_length == 0
        ):
            return True


class TransactionMaster(TransactionOps):
    def __init__(self, browser, command, thread_helper):
        super().__init__(browser, command)
        self.thread_helper = thread_helper

    def operation(self, row):
        self.ledger_row = row
        self.idx = 0
        self.refresh_transaction_info()
        while True:
            if self.idx >= self.transaction_info["rows_length"] or (
                self.thread_helper and self.thread_helper._is_cancelled
            ):
                break
            self.finished_list = self.idx >= self.transaction_info["rows_length"] - 1
            self.allocation = self.transaction_info["rows"][self.idx]
            operation_result = self.perform_transaction_op()
            if operation_result == "break":
                break
            if operation_result == "continue":
                continue
            if operation_result == "reload":
                self.refresh_transaction_info()
                continue
            self.idx += 1

    def refresh_transaction_info(self):
        self.transaction_info = self.retrieve_elements()


class CreditMaster(CreditOps):
    def __init__(self, browser, command):
        super().__init__(browser, command)

    def operation(self, row):
        self.credit_row = row
        self.add_credit()


class RedStarMaster(ReportsBase):
    def __init__(self, browser, report):
        super().__init__(report)
        self.browser = browser
        self.redstar_idx = 0

    def cycle_ledger(self, next_ledger):
        self.redstar_idx = self.redstar_idx + 1 if next_ledger else self.redstar_idx - 1
        self.open_redstar_ledger()

    def open_redstar_ledger(self):
        urls = self.csv_ops.get_url_columns()
        url = urls[self.redstar_idx]
        self.browser.driver.get(url)


class SupportDeskMaster(SupportDeskOperations):
    def __init__(self, browser, command, ticket_master):
        super().__init__(browser)


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
            self.open_resident()
