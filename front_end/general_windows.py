from front_end.helper_windows import HelperWidget
from functools import partial


class LedgerOperations(HelperWidget):
    def __init__(self, main_app, title):
        super().__init__(main_app, title)
        self.additional_info_window = AdditionalInfoWindow(main_app)
        all_types = ["payment", "charge", "credit"]
        self.operations_dict = {
            "allocate": {
                "Allocate All": {"operation": "allocate", "type": all_types},
                "Allocate Payments": {"operation": "allocate", "type": ["payment"]},
                "Allocate Charges": {"operation": "allocate", "type": ["charge"]},
            },
            "unallocate": {
                "Unallocate All": {"operation": "unallocate", "type": all_types},
                "Unallocate Payments": {"operation": "unallocate", "type": ["payment"]},
                "Unallocate Charges": {"operation": "unallocate", "type": ["charge"]},
            },
            "delete": {
                "Delete All": {"operation": "delete", "type": all_types},
                "Delete Charges": {"operation": "delete", "type": ["charge"]},
                "Delete Credits": {"operation": "delete", "type": ["credit"]},
                "Delete Late Fees": {"operation": "delete", "type": ["late_fee"]},
                "Delete Except Metered": {
                    "operation": "delete",
                    "type": all_types,
                    "exclude": "metered",
                },
            },
            "credit": {
                "Credit": {"operation": "credit", "widgets": ["text_input"]},
                "Concession": {"operation": "concession", "widgets": ["text_input"]},
            },
        }


class LedgerTools(LedgerOperations):
    def __init__(self, main_app, title):
        super().__init__(main_app, title)

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
        self.credit_dropdown = self.create_configured_dropdown(
            ["Credit Charges"] + list(self.operations_dict["credit"].keys()),
            self.create_AIW_with_widgets,
        )

    def create_AIW_with_widgets(self, command):
        self.additional_info_window.create_additional_info_widgets(command)
        self.main_app.switch_window(self.additional_info_window)


class AdditionalInfoWindow(HelperWidget):
    def __init__(self, main_app, command=None):
        super().__init__(main_app, "Additional Info")
        if command:
            self.create_additional_info_widgets(command)

    def create_additional_info_widgets(self, command):
        for widget in command["widgets"]:
            if widget == "text_input":
                comment = self.create_text_input("Enter Comment")
        self.create_button("Submit", partial(self.submit, command, comment))

    def submit(self, command, input):
        command["comment"] = input.text()
        self.operations.init_operation(command)
