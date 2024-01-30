from general_tools.general_info import GeneralInfo
from main_tools.operations import Operations
from selenium.webdriver.common.by import By
from main_tools.operations import RedStarMaster
from manage_portal.tickets import TicketOperations
import time


class TicketBot(Operations):
    def __init__(self, browser, operations_list, thread_helper=None):
        super().__init__(browser, thread_helper)
        self.operations_list = operations_list
        self.ticket_ops = TicketOperations(browser, command=None)
        self.support_desk_link = "https://residentmap.kmcmh.com/#/support_desk"

    def loop_through_tickets(self, command):
        self.command = command
        self.init_classes()
        self.supportdesk_master.go_to_supportdesk()
        tickets_info = self.supportdesk_master.support_desk_loop()
        for ticket in tickets_info:
            if self.thread_helper and self.thread_helper._is_cancelled:
                break
            if (
                self.command["operation"] == "unresolve_all"
                and ticket["status"] == "in_progress"
            ):
                self.unresolve_ticket(ticket)
            if self.command["operation"] == "random":
                self.random_ticket_op(ticket)

    def unresolve_ticket(self, ticket):
        self.browser.wait_for_presence_of_element(By.TAG_NAME, "tbody")
        self.browser.open_program(f"{self.support_desk_link}/{ticket['id']}")
        self.ticket_ops.command = {"selection": "unresolve", "type": "automatic"}
        self.ticket_ops.change_ticket_status()

    def random_ticket_op(self, ticket):
        pass


class RedstarBot(Operations):
    def __init__(self, browser, operations_list, thread_helper=None, nsf_bot=None):
        super().__init__(browser, thread_helper)
        self.operations_list = operations_list
        self.nsf_bot = nsf_bot
        self.general_info = GeneralInfo()
        self.redstar_master = RedStarMaster(browser)

    def loop_through_redstars(self):
        urls = self.redstar_master.csv_ops.get_url_columns()
        for url in urls:
            self.browser.driver.get(url)
            if self.thread_helper and self.thread_helper._is_cancelled:
                break
            if not self.has_redstar():
                continue
            try:
                self.allocate_unallocate()
            except:
                continue

    def allocate_unallocate(self):
        if not self.has_redstar():
            return
        self.run_command("Allocate Payments", "current")
        if not self.has_redstar():
            return
        self.run_command("Unallocate Payments", "current")
        self.run_command("Unallocate Charges", "current")
        self.run_command("Allocate All", "current")

    def has_redstar(self):
        return self.browser.element_exists(
            By.XPATH, '//td//font[@color="red" and text()="*"]'
        )


class NSFBot(Operations):
    def __init__(self, browser, operations_list, thread_helper=None):
        super().__init__(browser, thread_helper)
        self.operations_list = operations_list

    def fix_nsf(self):
        self.run_command("Delete NSF", "current")
        self.run_command("Delete Late Fees", "current")
        self.run_command("Unallocate All", "current")

    def create_bounce_check_command(self):
        command = {"operations": "bounce"}
