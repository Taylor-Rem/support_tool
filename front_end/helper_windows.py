from PyQt5.QtWidgets import QVBoxLayout, QLabel
from front_end.base_widget import BaseWidget
from general_tools.operations import Operations
from functools import partial


class HelperWidget(BaseWidget):
    def __init__(self, main_app, title):
        super().__init__()
        self.operations = Operations(main_app.browser)
        self.main_app = main_app
        self.setWindowTitle(title)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(title, self)
        self.layout.addWidget(self.label)

        self.button_layout = QVBoxLayout()
        self.layout.addLayout(self.button_layout)

    def create_button(self, text, callback):
        return super()._create_button(text, callback, self.layout)

    def go_back(self):
        if self.main_app.previous_widgets:
            last_widget = self.main_app.previous_widgets.pop()
            self.main_app.stack.setCurrentWidget(last_widget)
        else:
            self.main_app.stack.setCurrentWidget(self.main_app.main_window)

    def add_back_btn(self):
        self.back_btn = self.create_button("⬅️ Back", self.go_back)


class LedgerTools(HelperWidget):
    def __init__(self, main_app, title):
        super().__init__(main_app, title)
        all_types = ["payment", "charge", "credit"]

        self.operations_dict = {
            "allocate": {
                "Allocate All": {"operation": "allocate", "type": all_types},
                "Allocate Payments": {"operation": "allocate", "type": "payment"},
                "Allocate Charges": {"operation": "allocate", "type": "charge"},
            },
            "unallocate": {
                "Unallocate All": {"operation": "unallocate", "type": all_types},
                "Unallocate Payments": {"operation": "unallocate", "type": "payment"},
                "Unallocate Charges": {"operation": "unallocate", "type": "charge"},
            },
            "delete": {
                "Delete All": {"operation": "delete", "type": all_types},
                "Delete Charges": {"operation": "delete", "type": "charge"},
                "Delete Credits": {"operation": "delete", "type": "credit"},
                "Delete Late Fees": {
                    "operation": "delete",
                    "type": None,
                    "special_type": "late_fee",
                },
                "Delete Except Metered": {
                    "operation": "delete",
                    "type": all_types,
                    "special_type": "metered",
                },
            },
        }

    def create_ledger_tools(self):
        self.allocate_dropdown = self.create_configured_dropdown(
            ["Allocate"] + list(self.operations_dict["allocate"].keys()),
            self.operations.init_operation,
        )
        self.unallocate_dropdown = self.create_configured_dropdown(
            ["Unallocate"] + list(self.operations_dict["unallocate"].keys()),
            self.operations.init_operation,
        )
        self.delete_dropdown = self.create_configured_dropdown(
            ["Delete"] + list(self.operations_dict["delete"].keys()),
            self.operations.init_operation,
        )
