from general_tools.general_info import GeneralInfo
from main_tools.operations import Operations
from selenium.webdriver.common.by import By


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
            if (
                self.command["operation"] == "unresolve_all"
                and self.ticket["status"] == "unresolved"
            ):
                self.idx += 1
                continue
            self.browser.click_element(self.ticket["link"])
            self.ticket_info = self.ticket_master.scrape_ticket()
            if self.command["operation"] == "unresolve_all":
                temp_command = self.operations_list.ticket_ops_dict["resolve_ticket"][
                    "Unresolve"
                ]
                self.init_operation(temp_command)
                self.command = command
            if self.command["operation"] != "unresolve_all":
                self.supportdesk_master.go_to_supportdesk()
            self.tickets_info = self.supportdesk_master.support_desk_loop()
            self.idx += 1

    def unresolve_all(self):
        pass


class RedstarBot(Operations):
    def __init__(self, browser, operations_list, thread_helper=None, nsf_bot=None):
        super().__init__(browser, thread_helper)
        self.operations_list = operations_list
        self.nsf_bot = nsf_bot
        self.general_info = GeneralInfo()

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
        tables = ["current"]
        if self.general_info.day <= 15:
            tables.append("previous")
        for table in tables:
            self.run_command("Allocate Payments", table)
            if not self.has_redstar():
                return
            self.run_command("Unallocate All", table)
            self.run_command("Allocate All", table)
            if not self.has_redstar():
                return

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


