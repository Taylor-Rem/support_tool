from PyQt5.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
)
from general_tools.webdriver import WebdriverOperations

from front_end.tool_windows import (
    LedgerTools,
    TicketWindow,
    ReportWindow,
    ReportOpsWindow,
    RedstarWindow,
    RedstarOpsWindow,
)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()
        self.previous_widgets = []

        self.webdriver = WebdriverOperations()

        self.init_windows()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Support Master")
        self.add_widgets()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stack)

    def init_windows(self):
        self.init_main_window()
        self.ledger_tools = LedgerTools(self)
        self.ticket_window = TicketWindow(self)
        self.report_window = ReportWindow(self)
        self.report_ops_window = ReportOpsWindow(self)
        self.redstar_window = RedstarWindow(self)
        self.redstar_ops_window = RedstarOpsWindow(self)

    def add_widgets(self):
        windows = [
            self.main_window,
            self.ledger_tools,
            self.ticket_window,
            self.report_window,
            self.report_ops_window,
            self.redstar_window,
            self.redstar_ops_window,
        ]
        for window in windows:
            self.stack.addWidget(window)

    def init_main_window(self):
        self.main_window = QWidget()
        main_layout = QVBoxLayout()
        self.main_window.setLayout(main_layout)

        button_configs = [
            {
                "name": "Ledger Tools",
                "method": lambda: self.switch_window(self.ledger_tools),
            },
            {
                "name": "Ticket Helper",
                "method": lambda: self.switch_window(
                    self.ticket_window, True, self.webdriver.manage_portal_url
                ),
            },
            {
                "name": "Report Helper",
                "method": lambda: self.switch_window(
                    self.report_window, True, self.webdriver.res_map_url
                ),
            },
            {
                "name": "Redstar Helper",
                "method": lambda: self.switch_window(
                    self.redstar_window, True, self.webdriver.res_map_url
                ),
            },
        ]

        for config in button_configs:
            self.create_button(config["name"], config["method"], main_layout)

    def create_button(self, text, callback, layout):
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        layout.addWidget(button)

    def switch_window(self, window, previous_widget=True, open_program=None):
        if window not in [self.stack.widget(i) for i in range(self.stack.count())]:
            self.stack.addWidget(window)
        if previous_widget:
            self.previous_widgets.append(self.stack.currentWidget())
        self.stack.setCurrentWidget(window)
        if open_program:
            self.webdriver.switch_to_primary_tab()
            self.webdriver.open_program(open_program)

    def quit_app(self):
        self.close()
