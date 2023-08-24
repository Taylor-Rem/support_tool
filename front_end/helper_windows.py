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
        confirmation_message = (
            f"Are you sure you want to perform the operation: {operation}?"
        )

        confirm_dialog = QMessageBox()
        confirm_dialog.setWindowTitle("Confirm Operation")
        confirm_dialog.setText(confirmation_message)
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_dialog.setDefaultButton(QMessageBox.No)

        response = confirm_dialog.exec_()

        if response == QMessageBox.Yes:
            if operation == "credit_all_charges":
                items = ["Concession", "Credit"]
                item, ok = QInputDialog.getItem(
                    self, "Choose credit type", "Type:", items, 0, False
                )
                if ok and item:
                    is_concession = item == "Concession"
                    self.ledger_master.loop_through_table(operation, is_concession)
                else:
                    QMessageBox.information(
                        self, "Operation canceled", "Credit operation was canceled."
                    )
            else:
                self.ledger_master.loop_through_table(operation)
        else:
            print("Operation canceled.")
