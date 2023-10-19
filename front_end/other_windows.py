from front_end.helper_windows import HelperWidget

from functools import partial
from PyQt5.QtWidgets import QHBoxLayout
from front_end.helper_windows import AdditionalInfoWindow
from general_tools.general_info import GeneralInfo


class LedgerTools(HelperWidget):
    def __init__(self, main_app, title=None):
        if not title:
            title = "Ledger Tools"
        super().__init__(main_app, title)
        self.additional_info_window = AdditionalInfoWindow(main_app)
        self.general_info = GeneralInfo()
        self.previous_closed = self.general_info.day >= 17

    def create_ledger_tools(self):
        self.change_resident_dropdown = self.configured_operations_dropdown(
            ["Change Resident"]
            + list(self.operations_list.ledger_ops_dict["change_resident"].keys()),
            self.submit,
        )
        if not self.previous_closed:
            self.choose_month_dropdown = self.create_dropdown(
                list(self.operations_list.month_selector.keys())
            )
        self.allocate_dropdown = self.configured_operations_dropdown(
            ["Allocate"]
            + list(self.operations_list.ledger_ops_dict["allocate"].keys()),
            self.submit,
        )
        self.unallocate_dropdown = self.configured_operations_dropdown(
            ["Unallocate"]
            + list(self.operations_list.ledger_ops_dict["unallocate"].keys()),
            self.submit,
        )
        self.delete_dropdown = self.configured_operations_dropdown(
            ["Delete"] + list(self.operations_list.ledger_ops_dict["delete"].keys()),
            self.submit,
        )
        self.credit_dropdown = self.configured_operations_dropdown(
            ["Credit Charges"]
            + list(self.operations_list.ledger_ops_dict["credit"].keys()),
            self.submit,
        )
        self.fix_nsf_btn = self.create_button(
            "Fix NSF", lambda: self.run_in_thread(self.nsf_bot.fix_nsf)
        )

    def create_AIW_with_widgets(self, command):
        self.additional_info_window = AdditionalInfoWindow(self.main_app, command)
        self.main_app.switch_window(self.additional_info_window, add_to_previous=False)

    def submit(self, command):
        command["window"] = self.main_app.current_window()
        command["table"] = (
            self.operations_list.month_selector[
                self.choose_month_dropdown.currentText()
            ]
            if not self.previous_closed
            else "current"
        )
        if command.get("widgets", None):
            if command["operation"] == "credit":
                command["table"] = "bottom"
            self.create_AIW_with_widgets(command)
            return
        self.run_in_thread(self.operations.init_operation, command)


class TicketHelper(HelperWidget):
    def __init__(self, main_app):
        super().__init__(main_app, "Ticket Helper")
        self.open_ticket_dropdown = self.configured_operations_dropdown(
            ["Open Ticket"]
            + list(self.operations_list.ticket_ops_dict["open_ticket"].keys()),
            self.submit,
        )
        self.resolve_dropdown = self.configured_operations_dropdown(
            ["Resolve Ticket"]
            + list(self.operations_list.ticket_ops_dict["resolve_ticket"].keys()),
            self.submit,
        )
        self.run_bot = self.configured_operations_dropdown(
            ["Run Ticket Bot"]
            + list(self.operations_list.ticket_ops_dict["ticket_bot"].keys()),
            self.run_bot,
        )
        self.add_back_btn()

    def submit(self, command):
        self.operations.init_operation(command)
        if command["operation"] == "open_ticket":
            self.main_app.switch_window(self.main_app.ledger_window)

    def run_bot(self, command):
        command["window"] = self.main_app.current_window()
        self.run_in_thread(self.ticket_bot.loop_through_tickets, command)


class LedgerWindow(LedgerTools):
    def __init__(self, main_app):
        super().__init__(main_app)
        self.create_ledger_tools()
        self.add_back_btn()


class RedstarHelper(LedgerTools):
    def __init__(self, main_app):
        super().__init__(main_app, "Red Star Helper")
        # Create a QHBoxLayout for the buttons
        buttons_layout = QHBoxLayout()

        # Add "Prev" button to the horizontal layout
        self.prev_btn = self.create_button(
            "< Prev", partial(self.operations.open_redstars, False)
        )
        buttons_layout.addWidget(self.prev_btn)

        # Add "Next" button to the horizontal layout
        self.next_btn = self.create_button(
            "Next >", partial(self.operations.open_redstars, True)
        )
        buttons_layout.addWidget(self.next_btn)

        # Add the QHBoxLayout to the main layout
        self.layout.addLayout(buttons_layout)

        self.create_ledger_tools()
        self.run_bot = self.create_button("Run Bot", self.run_bot)
        self.add_back_btn()

    def run_bot(self):
        self.run_in_thread(self.redstar_bot.loop_through_redstars)


class RandomWindow(HelperWidget):
    def __init__(self, main_app):
        super().__init__(main_app, "Random Task")
        # Create a QHBoxLayout for the buttons
        buttons_layout = QHBoxLayout()
        # Add "Prev" button to the horizontal layout
        self.prev_btn = self.create_button(
            "< Prev", partial(self.random_ops.random_operation, False)
        )
        buttons_layout.addWidget(self.prev_btn)

        # Add "Next" button to the horizontal layout
        self.next_btn = self.create_button(
            "Next >", partial(self.random_ops.random_operation, True)
        )
        buttons_layout.addWidget(self.next_btn)
        self.layout.addLayout(buttons_layout)
        self.add_back_btn()
