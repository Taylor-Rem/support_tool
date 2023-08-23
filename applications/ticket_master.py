from manageportal_tools.ticket_ops import ManageportalMaster
from resmap_tools.nav_to_ledger import NavToLedgerMaster


class TicketMaster(ManageportalMaster, NavToLedgerMaster):
    def __init__(self):
        super().__init__()

    def change_ticket_status(self, icon, back):
        self.switch_to_primary_tab()
        self.resolve_ticket(icon, back)

    def open_ticket(self):
        self.switch_to_primary_tab()
        property, unit, resident = self.scrape_ticket()
        print(property, unit, resident)
        self.new_tab()
        self.open_program(self.res_map_url)
        self.open_ledger(property, unit, resident)
