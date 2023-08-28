from PyQt5.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QMessageBox,
    QInputDialog,
)
from PyQt5.QtCore import QThread, pyqtSignal

from functools import partial
from resmap_tools.ledger_ops import LedgerMaster


class ThreadHelper(QThread):
    finished_signal = pyqtSignal()
    cancelled_signal = pyqtSignal()

    def __init__(self, func, main_app, return_widget, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False

        # Adjust the function argument to include the is_cancelled method
        self.func = func

        self.main_app = main_app
        self.return_widget = return_widget

        # Connect signals here to unify the behavior
        self.finished_signal.connect(self.on_finished)
        self.cancelled_signal.connect(self.on_cancelled)

    def is_cancelled(self):
        return self._is_cancelled

    def run(self):
        self.func()  # now the function has all the arguments it needs already
        if self._is_cancelled:
            self.cancelled_signal.emit()
        else:
            self.finished_signal.emit()

    def reset(self):
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def start(self):
        self.operation_window = ThreadRunningWindow(self.main_app, self)
        self.main_app.switch_window(self.operation_window, False)
        super().start()

    def finish_operation(self):
        print("Operation Completed")
        self.main_app.switch_window(self.return_widget, False)

    def on_cancelled(self):
        self.finish_operation()

    def on_finished(self):
        self.finish_operation()


class HelperWidget(QWidget):
    def __init__(self, main_app, title):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle(title)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(title, self)
        self.layout.addWidget(self.label)

        self.button_layout = QVBoxLayout()
        self.layout.addLayout(self.button_layout)

    def create_button(self, text, callback):
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        self.layout.addWidget(button)
        return button

    def go_back(self):
        if self.main_app.previous_widgets:
            last_widget = self.main_app.previous_widgets.pop()
            self.main_app.stack.setCurrentWidget(last_widget)
        else:
            # In case the widget history is empty, fall back to the main window
            self.main_app.stack.setCurrentWidget(self.main_app.main_window)

    def add_back_btn(self):
        self.back_btn = self.create_button("⬅️ Back", self.go_back)

    def get_confirmation(self, message="Are You Sure?", title="Confirm Operation"):
        confirm_dialog = QMessageBox()
        confirm_dialog.setWindowTitle(title)
        confirm_dialog.setText(message)
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_dialog.setDefaultButton(QMessageBox.No)

        response = confirm_dialog.exec_()
        return response == QMessageBox.Yes

    def choose_between_values(
        self, title, label, items=[], current_index=0, editable=False
    ):
        item, ok = QInputDialog.getItem(
            self, title, label, items, current_index, editable
        )
        return item if ok else None


class ThreadRunningWindow(HelperWidget):
    def __init__(self, main_app, thread_helper, title="Running Operation"):
        super().__init__(main_app, title)
        self.thread_helper = thread_helper

        self.operation_label = QLabel("Operation is running...", self)
        self.layout.addWidget(self.operation_label)

        self.cancel_btn = self.create_button("Cancel operation", self.cancel_operation)

    def cancel_operation(self):
        self.thread_helper.cancel()
        self.operation_label.setText("Cancelling operation...")
        self.cancel_btn.setEnabled(False)


class LedgerOps(HelperWidget):
    def __init__(self, main_app, title):
        super().__init__(main_app, title)
        self.ledger_master = LedgerMaster(main_app.webdriver)
        self.create_ledger_buttons()

    def create_ledger_buttons(self):
        BUTTONS_MAP = {
            "Allocate All": "allocate_all",
            "Delete All Charges": "delete_all_charges",
            "Delete All Late Fees": "delete_all_late_fees",
        }
        self.credit_all_charges_btn = self.create_button(
            "Credit All Charges",
            partial(
                self.choose_values,
                "Choose Credit Type",
                "Type",
                ["Concession", "Credit"],
                "credit_all_charges",
            ),
        )
        self.change_ledger_btn = self.create_button(
            "Go to Former/Current",
            partial(
                self.choose_values,
                "Choose Resident",
                "Resident",
                ["Former", "Current"],
                "change_ledger",
            ),
        )
        for btn_text, action in BUTTONS_MAP.items():
            self.create_button(btn_text, partial(self.click_button, action))

    def click_button(self, operation, chosen_item=None):
        if chosen_item:
            if operation == "credit_all_charges":
                func = partial(
                    self.ledger_master.loop_through_table, operation, chosen_item
                )
            else:
                func = partial(self.ledger_master.change_ledger, chosen_item)
        elif self.get_confirmation():
            func = partial(self.ledger_master.loop_through_table, operation)
        else:
            print("Operation canceled.")
            return

        # Instantiate the thread helper here, similar to RedstarWindow
        self.thread_helper = ThreadHelper(func, self.main_app, self)
        self.ledger_master.thread_helper = (
            self.thread_helper
        )  # Inject ThreadHelper to LedgerMaster
        self.thread_helper.reset()
        self.thread_helper.start()

    def choose_values(self, title, label, items, operation):
        chosen_item = self.choose_between_values(title, label, items)
        self.click_button(operation, chosen_item)
