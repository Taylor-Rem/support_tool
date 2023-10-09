from front_end.helper_windows import HelperWidget
from front_end.ledger_window import LedgerTools
from functools import partial


class TicketHelper(HelperWidget):
    def __init__(self, main_app):
        super().__init__(main_app, "Ticket Helper")
        self.open_ticket_dropdown = self.create_configured_dropdown(
            ["Open Ticket", "Ledger", "Unit", "Resident"], self._open_ticket
        )
        self.resolve_dropdown = self.create_configured_dropdown(
            ["Resolve Ticket", "Resolve", "In Progress", "Unresolve"],
            self.operations.ticket_master.change_ticket_status,
        )
        self.add_back_btn()

    def _open_ticket(self, location):
        self.operations.open_ticket(location)
        self.main_app.switch_window(self.main_app.ledger_window)


class LedgerWindow(LedgerTools):
    def __init__(self, main_app):
        super().__init__(main_app, "Ledger Tools")
        self.create_ledger_tools()
        self.add_back_btn()


class RedstarHelper(LedgerTools):
    def __init__(self, main_app):
        super().__init__(main_app, "Red Star Helper")
        self.next_btn = self.create_button(
            "Next", partial(self.operations.redstar_master.cycle_ledger, "next")
        )
        self.prev_btn = self.create_button(
            "Prev", self.operations.redstar_master.cycle_ledger
        )
        self.create_ledger_tools()
        self.add_back_btn()
