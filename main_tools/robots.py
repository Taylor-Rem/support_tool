from general_tools.general_info import GeneralInfo
from main_tools.operations import Operations
from selenium.webdriver.common.by import By
from main_tools.operations import RedStarMaster


class TicketBot(Operations):
    def __init__(self, browser, operations_list, thread_helper=None):
        super().__init__(browser, thread_helper)
        self.operations_list = operations_list

    def loop_through_tickets(self, command):
        self.command = command
        self.init_classes()
        self.supportdesk_master.go_to_supportdesk()
        self.tickets_info = self.supportdesk_master.support_desk_loop()
        self.idx = 0
        while True:
            if self.idx >= self.tickets_info[0]["length"] or (
                self.thread_helper and self.thread_helper._is_cancelled
            ):
                break
            self.ticket = self.tickets_info[self.idx]
            if self.check_continue():
                continue
            self.browser.click_element(self.ticket["link"])
            self.ticket_info = self.ticket_master.scrape_ticket()
            if self.command["operation"] == "unresolve_all":
                self.run_command("Unresolve")
                self.command = command
            if self.command["operation"] != "unresolve_all":
                self.supportdesk_master.go_to_supportdesk()
            self.tickets_info = self.supportdesk_master.support_desk_loop()
            self.idx += 1

    def check_continue(self):
        if (
            self.command["operation"] == "unresolve_all"
            and self.ticket["status"] == "unresolved"
        ):
            self.idx += 1
            return True

    def unresolve_all(self):
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
            self.allocate_unallocate()

    def allocate_unallocate(self):
        self.run_command("Allocate All", "current")
        if not self.has_redstar():
            return
        self.run_command("Unallocate All", "current")
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
