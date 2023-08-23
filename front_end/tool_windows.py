from front_end.helper_windows import HelperWidget, LedgerOps

from applications.ticket_master import TicketMaster
from applications.report_master import ReportMaster


class TicketWindow(HelperWidget, TicketMaster):
    def __init__(self, main_app):
        super().__init__(main_app, "Ticket Helper")
        self.icons = {
            "In Progress": "scatter_plot",
            "Resolved": "done_outline",
            "Back": "arrow_back",
        }
        self.open_btn = self.create_button("🤖 Open Ticket", self.open_ticket)
        self.in_progress_btn = self.create_button(
            "🔵 In Progress",
            lambda: (
                self.change_ticket_status(self.icons["In Progress"], self.icons["Back"])
            ),
        )
        self.resolve_btn = self.create_button(
            "✅ Resolve", lambda: (self.change_ticket_status(self.icons["Resolved"]))
        )
        self.add_back_btn()

    def open_ticket(self):
        self.main_app.switch_window(self.main_app.ticket_ops_window)
        self.open_ticket()

    def change_ticket_status(self, icon, back=None):
        self.change_ticket_status(icon, back)


class TicketOpsWindow(LedgerOps):
    def __init__(self, main_app):
        super().__init__(main_app, "Ticket Helper")
        self.create_ledger_buttons()
        self.add_back_btn()


class ReportWindow(HelperWidget):
    def __init__(self, main_app):
        super().__init__(main_app, "Report Helper")
        self.zero_btn = self.create_button(
            "Zero Report", lambda: (self.open_report("zero_report"))
        )
        self.double_btn = self.create_button(
            "Double Report", lambda: (self.open_report("double_report"))
        )
        self.moveout_btn = self.create_button(
            "Moveout Report", lambda: (self.open_report("moveout_report"))
        )
        self.add_back_btn()

    def open_report(self, report):
        self.main_app.switch_window(self.main_app.report_ops_window)
        report_master = ReportMaster(report)
        print(report_master.reports_path)


class ReportOpsWindow(LedgerOps):
    def __init__(self, main_app):
        super().__init__(main_app, "Report Helper")
        self.create_ledger_buttons()
        self.add_back_btn()


class RedstarWindow(HelperWidget):
    def __init__(self, main_app):
        super().__init__(main_app, "Redstar Helper")
        self.add_back_btn()


class RedstarOpsWindow(LedgerOps):
    def __init__(self, main_app):
        super().__init__(main_app, "Redstar Helper")
        self.create_ledger_buttons()
        self.add_back_btn()
