from front_end.helper_windows import HelperWidget, LedgerTools
from functools import partial


class RedstarHelper(LedgerTools):
    def __init__(self, main_app):
        super().__init__(main_app, "Red Star Helper")
        self.next_btn = self.create_button(
            "Next", partial(self.operations.redstar_master.cycle_ledger, "next")
        )
        self.prev_btn = self.create_button(
            "Prev", self.operations.redstar_master.cycle_ledger
        )
        self.create_ledger_tools()
        self.add_back_btn()
