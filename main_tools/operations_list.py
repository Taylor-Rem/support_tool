class OperationsList:
    def __init__(self):
        self.month_selector = {"Current Month": "current", "Previous Month": "previous"}
        self.ticket_ops_dict = {
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
                "Resolve ✅": {
                    "operation": "resolve_ticket",
                    "selection": "resolve",
                    "tools": "ticket",
                },
                "In Progress 🔵": {
                    "operation": "resolve_ticket",
                    "selection": "in_progress",
                    "tools": "ticket",
                },
                "Unresolve ⛔️": {
                    "operation": "resolve_ticket",
                    "selection": "unresolve",
                    "tools": "ticket",
                },
            },
            "ticket_bot": {
                "Unresolve All": {
                    "operation": "unresolve_all",
                    "tools": "ticket",
                },
                "Automation": {
                    "operation": "automation",
                    "tools": "ticket",
                },
            },
        }
        self.ledger_ops_dict = {
            "change_resident": {
                "Current": {
                    "operation": "change_resident",
                    "selection": "current",
                    "tools": ["ledger", "nav"],
                },
                "Former": {
                    "operation": "change_resident",
                    "selection": "former",
                    "tools": ["ledger", "nav"],
                },
            },
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
                "Delete NSF": {
                    "operation": "delete",
                    "type": ["sytem_nsf", "nsf"],
                    "tools": ["ledger", "table"],
                    "exclude": ["payment"],
                },
                "Delete All Except": {
                    "operation": "delete",
                    "type": ["credit", "charge"],
                    "widgets": [
                        (
                            "dropdown",
                            ["None", "Metered", "Rent"],
                            "exclude",
                        ),
                        ("text_input", ("", "Exclude:"), "exclude"),
                    ],
                    "tools": ["ledger", "table"],
                },
            },
            "credit": {
                "Credit": {
                    "operation": "credit",
                    "selection": "credit",
                    "widgets": [("text_input", ("", "Enter Comment"), "comment")],
                    "tools": ["ledger", "credit"],
                },
                "Concession": {
                    "operation": "credit",
                    "selection": "concession",
                    "widgets": [("text_input", ("", "Enter Comment"), "comment")],
                    "tools": ["ledger", "credit"],
                },
            },
        }
