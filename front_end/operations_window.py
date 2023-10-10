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
                    "tool": "ledger",
                },
                "Allocate Payments": {
                    "operation": "allocate",
                    "type": ["payment"],
                    "tool": "ledger",
                },
                "Allocate Charges": {
                    "operation": "allocate",
                    "type": ["charge"],
                    "tool": "ledger",
                },
            },
            "unallocate": {
                "Unallocate All": {
                    "operation": "unallocate",
                    "type": ["all"],
                    "tool": "ledger",
                },
                "Unallocate Payments": {
                    "operation": "unallocate",
                    "type": ["payment"],
                    "tool": "ledger",
                },
                "Unallocate Charges": {
                    "operation": "unallocate",
                    "type": ["charge"],
                    "tool": "ledger",
                },
            },
            "delete": {
                "Delete All": {
                    "operation": "delete",
                    "type": ["credit", "charge"],
                    "tool": "ledger",
                },
                "Delete Charges": {
                    "operation": "delete",
                    "type": ["charge"],
                    "tool": "ledger",
                },
                "Delete Credits": {
                    "operation": "delete",
                    "type": ["credit"],
                    "tool": "ledger",
                },
                "Delete Late Fees": {
                    "operation": "delete",
                    "type": ["late_fee"],
                    "tool": "ledger",
                },
                "Delete Except Metered": {
                    "operation": "delete",
                    "type": ["credit", "charge"],
                    "exclude": "metered",
                    "tool": "ledger",
                },
            },
            "credit": {
                "Credit": {
                    "operation": "credit",
                    "widgets": ["text_input"],
                    "tool": "ledger",
                },
                "Concession": {
                    "operation": "concession",
                    "widgets": ["text_input"],
                    "tool": "ledger",
                },
            },
            "open_ticket": {
                "Ledger": {
                    "operation": "open_ticket",
                    "selection": "ledger",
                    "tool": "ticket",
                },
                "Unit": {
                    "operation": "open_ticket",
                    "selection": "unit",
                    "tool": "ticket",
                },
                "Resident": {
                    "operation": "open_ticket",
                    "selection": "resident",
                    "tool": "ticket",
                },
            },
            "resolve_ticket": {
                "Resolve": {
                    "operation": "resolve_ticket",
                    "selection": "resolve",
                    "tool": "ticket",
                },
                "In Progress": {
                    "operation": "resolve_ticket",
                    "selection": "in_progress",
                    "tool": "ticket",
                },
                "Unresolve": {
                    "operation": "resolve_ticket",
                    "selection": "unresolve",
                    "tool": "ticket",
                },
            },
        }
