from general_tools.os_ops import ReportsBase
from resmap.ledger import LedgerOps
from resmap.transaction import TransactionOps
from resmap.credit import CreditOps
from resmap.navigation import ResmapNav
from manage_portal.support_desk import SupportDeskOperations
from manage_portal.tickets import TicketOperations

import re


class OperationsBase:
    def __init__(self, browser, thread_helper=None):
        self.browser = browser
        self.thread_helper = thread_helper
        self.cancelled = False
        self.redstar_master = None

    def init_operation(self, command):
        self.command = command
        self.init_classes()
        self.perform_operation()

    def run_command(self, selection, table=None):
        ledger_operations = ["allocate", "unallocate", "delete", "credit"]
        ticket_operations = (
            ("open_ticket", ("Ledger", "Unit", "Resident")),
            ("resolve_ticket", ("Resolve", "In Progress", "Unresolve")),
        )

        operation = None

        for specific_operation in ledger_operations:
            # Using regex word boundary (\b) to ensure we match whole words
            if re.search(
                r"\b" + re.escape(specific_operation) + r"\b", selection.lower()
            ):
                operation = specific_operation
                break

        if operation is None:
            for specific_operation, selections in ticket_operations:
                if selection in selections:
                    operation = specific_operation
                    break

        if operation in ledger_operations:
            command = self.operations_list.ledger_ops_dict[operation][selection]
            command["table"] = table
        else:
            command = self.operations_list.ticket_ops_dict[operation][selection]
        command["comment"] = "ledger doesn't match bill"
        self.init_operation(command)

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
            if "nav" in self.command["tools"]:
                click_location = ResmapNavMaster(self.browser, self.command, None)
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
            self.ledger_master.define_operation()


class LedgerMaster(LedgerOps):
    def __init__(self, browser, command, thread_helper, click_location):
        super().__init__(browser, command)
        self.click_location = click_location
        self.thread_helper = thread_helper
        self.current_url = self.browser.driver.current_url

    def define_operation(self):
        if "all" in self.command.get("type", []):
            self.multiple_loops()
        if any(tool in self.command["tools"] for tool in ["table", "credit"]):
            self.ledger_loop()
        if "nav" in self.command["tools"]:
            unit_element = self.scrape_unit()
            self.click_location.change_resident(unit_element)

    def multiple_loops(self):
        types = [["payment"], ["charge"]]
        for transaction_type in types:
            self.command["type"] = transaction_type
            self.ledger_loop()

    def ledger_loop(self):
        self.idx = 0
        self.refresh_ledger_info()
        self.last_row = None
        while True:
            if self.break_early():
                break
            self.ledger_row = self.ledger_info[self.idx]
            if self.continue_loop():
                continue
            self.last_row = self.ledger_row
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
        if (
            self.ledger_row.get("link") is None
            and self.command["operation"] != "credit"
        ) or (self.last_row == self.ledger_row):
            self.idx += 1
            return True

    def break_early(self):
        if (
            (self.thread_helper and self.thread_helper._is_cancelled)
            or self.rows_length is None
            or (self.idx >= self.rows_length)
            or (
                self.command["operation"] == "allocate"
                and "charge" in self.command["type"]
                and self.ledger_info[0]["prepaid_amount"] <= 0
            )
            or self.rows_length == 0
            # or self.check_nsf()
        ):
            return True


class TransactionMaster(TransactionOps):
    def __init__(self, browser, command, thread_helper):
        super().__init__(browser, command, thread_helper)

    def operation(self, row):
        self.ledger_row = row
        self.idx = 0
        if not self.refresh_transaction_info():
            return
        self.potential_allocation = self.transaction_info["total_amount"]
        while True:
            if self.check_break():
                break

            self.finished_list = self.idx >= self.transaction_info["rows_length"] - 1
            self.allocation = self.transaction_info["rows"][self.idx]
            operation_result = self.perform_transaction_op()
            if operation_result == "break":
                break
            if operation_result == "continue":
                continue
            if operation_result == "reload":
                self.transaction_info = self.retrieve_elements()
                continue
            self.idx += 1

    def check_break(self):
        if self.idx >= self.transaction_info["rows_length"] or (
            self.thread_helper and self.thread_helper._is_cancelled
        ):
            return True

    def refresh_transaction_info(self):
        self.transaction_info = self.retrieve_elements()
        if self.transaction_info is None:
            if self.command["operation"] == "allocate":
                self.auto_allocate()
            return False
        return True


class CreditMaster(CreditOps):
    def __init__(self, browser, command):
        super().__init__(browser, command)

    def operation(self, row):
        self.credit_row = row
        self.add_credit()


class RedStarMaster(ReportsBase):
    def __init__(self, browser):
        super().__init__("redstar_report")
        self.browser = browser
        self.redstar_idx = 0

    def cycle_ledger(self, next_ledger):
        urls_length = len(self.csv_ops.get_url_columns())

        if next_ledger:
            if self.redstar_idx == urls_length - 1:  # if at the last index
                self.redstar_idx = 0  # reset to the beginning
            else:
                self.redstar_idx += 1
        else:
            if self.redstar_idx == 0:  # if at the beginning
                self.redstar_idx = urls_length - 1  # set to the last index
            else:
                self.redstar_idx -= 1

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
        self.nav_to_selection()

    def change_resident(self, unit_element):
        self.browser.click_element(unit_element)
        if self.command["selection"] == "current":
            self.open_ledger()
        elif self.command["selection"] == "former":
            self.open_former_ledger()
