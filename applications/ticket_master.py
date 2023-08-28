from manageportal_tools.ticket_ops import ManageportalMaster
from resmap_tools.nav_to_ledger import NavToLedgerMaster


class TicketMaster:
    def __init__(self, webdriver):
        self.webdriver = webdriver
        self.manageportal_master = ManageportalMaster(webdriver)
        self.nav_to_ledger = NavToLedgerMaster(webdriver)

    def change_ticket_status(self, icon, back):
        self.webdriver.switch_to_primary_tab()
        self.manageportal_master.resolve_ticket(icon, back)

    def open_ticket(self):
        self.webdriver.switch_to_primary_tab()
        property, unit, resident = self.manageportal_master.scrape_ticket()
        print(property, unit, resident)
        self.webdriver.new_tab()
        self.webdriver.open_program(self.webdriver.res_map_url)
        self.nav_to_ledger.open_ledger(property, unit, resident)
