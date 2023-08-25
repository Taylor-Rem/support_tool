from front_end.helper_windows import HelperWidget, LedgerOps

from applications.ticket_master import TicketMaster
from applications.report_master import ReportMaster
from applications.redstar_master import RedstarMaster


class LedgerTools(LedgerOps):
    def __init__(self, main_app):
        super().__init__(main_app, "Redstar Helper")
        self.create_ledger_buttons()
        self.add_back_btn()


class TicketWindow(HelperWidget):
    def __init__(self, main_app):
        super().__init__(main_app, "Ticket Helper")
        self.ticket_master = TicketMaster(main_app.webdriver)
        self.icons = {
            "In Progress": "scatter_plot",
            "Resolved": "done_outline",
            "Back": "arrow_back",
        }
        self.open_btn = self.create_button("🤖 Open Ticket", self.open_tickets)
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

    def open_tickets(self):
        self.main_app.switch_window(self.main_app.ticket_ops_window)
        self.ticket_master.open_ticket()

    def change_ticket_status(self, icon, back=None):
        self.ticket_master.change_ticket_status(icon, back)


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
        report_ops_window = ReportOpsWindow(self.main_app, report)
        self.main_app.stack.addWidget(report_ops_window)
        self.main_app.switch_window(report_ops_window)


class ReportOpsWindow(LedgerOps):
    def __init__(self, main_app, report=None):
        super().__init__(main_app, "Report Helper")
        if report is not None:
            self.report_master = ReportMaster(main_app.webdriver, report)
            self.complete_btn = self.create_button(
                "✅ Add", lambda: self.report_master.ledger_cycle(True)
            )
            self.skip_btn = self.create_button(
                "⛔️ Skip", self.report_master.ledger_cycle
            )
            self.create_ledger_buttons()
            self.add_back_btn()


class RedstarWindow(HelperWidget):
    def __init__(self, main_app):
        super().__init__(main_app, "Redstar Helper")
        self.redstar_master = RedstarMaster(main_app.webdriver)
        self.open_report_btn = self.create_button(
            "Redstar Helper", self.open_redstar_window
        )
        self.run_autostar_btn = self.create_button("Run AutoStar", self.run_autostar)
        self.stop_autostar_btn = self.create_button("Stop AutoStar", self.stop_autostar)

        self.add_back_btn()

    def open_redstar_window(self):
        self.main_app.switch_window(self.main_app.redstar_ops_window)
        self.redstar_master.open_redstar_ledger()

    def run_autostar(self):
        self.redstar_master.running = True
        self.redstar_master.run_autostar()

    def stop_autostar(self):
        self.redstar_master.running = False


class RedstarOpsWindow(LedgerOps):
    def __init__(self, main_app):
        super().__init__(main_app, "Redstar Helper")
        self.create_ledger_buttons()
        self.add_back_btn()
