from front_end.helper_windows import HelperWidget


class OperationsHelper(HelperWidget):
    def __init__(self, main_app, title):
        super().__init__(main_app, title)
        self.month_selector = {"Current Month": "current", "Previous Month": "previous"}
        self.operations_dict = {
            "allocate": {
                "Allocate All": {
                    "operation": "allocate",
                    "type": ["all"],
                    "tools": ["ledger", "table"],
                },
                "Allocate Payments": {
                    "operation": "allocate",
                    "type": ["payment"],
                    "tools": ["ledger", "table"],
                },
                "Allocate Charges": {
                    "operation": "allocate",
                    "type": ["charge"],
                    "tools": ["ledger", "table"],
                },
            },
            "unallocate": {
                "Unallocate All": {
                    "operation": "unallocate",
                    "type": ["all"],
                    "tools": ["ledger", "table"],
                },
                "Unallocate Payments": {
                    "operation": "unallocate",
                    "type": ["payment"],
                    "tools": ["ledger", "table"],
                },
                "Unallocate Charges": {
                    "operation": "unallocate",
                    "type": ["charge"],
                    "tools": ["ledger", "table"],
                },
            },
            "delete": {
                "Delete All": {
                    "operation": "delete",
                    "type": ["credit", "charge"],
                    "tools": ["ledger", "table"],
                },
                "Delete Charges": {
                    "operation": "delete",
                    "type": ["charge"],
                    "tools": ["ledger", "table"],
                },
                "Delete Credits": {
                    "operation": "delete",
                    "type": ["credit"],
                    "tools": ["ledger", "table"],
                },
                "Delete Late Fees": {
                    "operation": "delete",
                    "type": ["late_fee"],
                    "tools": ["ledger", "table"],
                },
                "Delete All Except": {
                    "operation": "delete",
                    "type": ["credit", "charge"],
                    "widgets": ["dropdown", "text_input"],
                    "tools": ["ledger", "table"],
                },
            },
            "credit": {
                "Credit": {
                    "operation": "credit",
                    "widgets": ["text_input"],
                    "tools": ["ledger", "credit"],
                },
                "Concession": {
                    "operation": "concession",
                    "widgets": ["text_input"],
                    "tools": ["ledger", "credit"],
                },
            },
            "open_ticket": {
                "Ledger": {
                    "operation": "open_ticket",
                    "selection": "ledger",
                    "tools": "ticket",
                },
                "Unit": {
                    "operation": "open_ticket",
                    "selection": "unit",
                    "tools": "ticket",
                },
                "Resident": {
                    "operation": "open_ticket",
                    "selection": "resident",
                    "tools": "ticket",
                },
            },
            "resolve_ticket": {
                "Resolve": {
                    "operation": "resolve_ticket",
                    "selection": "resolve",
                    "tools": "ticket",
                },
                "In Progress": {
                    "operation": "resolve_ticket",
                    "selection": "in_progress",
                    "tools": "ticket",
                },
                "Unresolve": {
                    "operation": "resolve_ticket",
                    "selection": "unresolve",
                    "tools": "ticket",
                },
            },
        }
