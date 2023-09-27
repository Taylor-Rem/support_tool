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

        self.allocate = {
            "All": {"operation": "allocate", "type": all_types},
            "Payments": {"operation": "allocate", "type": "payment"},
            "Charges": {"operation": "allocate", "type": "charge"},
        }
        self.unallocate = {
            "All": {"operation": "unallocate", "type": all_types},
            "Payments": {"operation": "unallocate", "type": "payment"},
            "Charges": {"operation": "unallocate", "type": "charge"},
        }

    def create_ledger_tools(self):
        self.allocate_dropdown = self.create_configured_dropdown(
            ["Allocate"] + list(self.allocate.keys()),
            self.operations.init_operation,
        )
        self.unallocate_dropdown = self.create_configured_dropdown(
            ["Unallocate"] + list(self.allocate.keys()),
            self.operations.init_operation,
        )
