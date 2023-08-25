from PyQt5.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QMessageBox,
    QInputDialog,
)


from functools import partial
from resmap_tools.ledger_ops import LedgerMaster


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


class LedgerOps(HelperWidget):
    def __init__(self, main_app, title):
        super().__init__(main_app, title)
        self.ledger_master = LedgerMaster(main_app.webdriver)

    def create_ledger_buttons(self):
        self.allocate_all_btn = self.create_button(
            "Allocate All", partial(self.click_button, "allocate_all")
        )
        self.credit_all_charges_btn = self.create_button(
            "Credit All Charges", partial(self.click_button, "credit_all_charges")
        )
        self.delete_all_charges_btn = self.create_button(
            "Delete All Charges", partial(self.click_button, "delete_all_charges")
        )
        self.delete_all_late_fees_btn = self.create_button(
            "Delete All Late Fees", partial(self.click_button, "delete_all_late_fees")
        )

    def click_button(self, operation):
        if operation == "credit_all_charges":
            chosen_item = self.choose_between_values(
                "Choose Credit Type", "Type", ["Concession", "Credit"]
            )
            if chosen_item:
                is_concession = chosen_item == "Concession"
                self.ledger_master.loop_through_table(operation, is_concession)
            else:
                QMessageBox.information(
                    self, "Operation canceled", "Credit operation was canceled."
                )
        elif self.get_confirmation():
            self.ledger_master.loop_through_table(operation)
        else:
            print("Operation canceled.")
