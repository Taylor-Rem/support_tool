from PyQt5.QtWidgets import QVBoxLayout, QWidget, QStackedWidget
from functools import partial
from general_tools.browser import Browser
from front_end.base_widget import BaseWidget
from front_end.visible_windows import RedstarHelper


class App(BaseWidget):
    def __init__(self):
        super().__init__()
        self.browser = Browser()
        self.stack = QStackedWidget()
        self.previous_widgets = []
        self.init_windows()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Support Master")
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)
        self.add_widgets()

    def init_windows(self):
        self.redstar_helper = RedstarHelper(self)
        self.init_main_window()

    def add_widgets(self):
        windows = [self.main_window, self.redstar_helper]
        for window in windows:
            self.stack.addWidget(window)

    def init_main_window(self):
        self.main_window = QWidget()
        main_layout = QVBoxLayout()
        self.main_window.setLayout(main_layout)

        button_configs = [
            {
                "name": "Red Star Helper",
                "method": partial(
                    self.switch_window,
                    self.redstar_helper,
                    self.browser.resmap_url,
                ),
            }
        ]
        [
            self._create_button(config["name"], config["method"], main_layout)
            for config in button_configs
        ]

    def switch_window(self, window, open_program=None):
        self.add_window_to_stack(window)
        self.append_to_previous()
        self.stack.setCurrentWidget(window)
        if open_program:
            self.browser.open_program(open_program)

    def add_window_to_stack(self, window):
        if window not in [self.stack.widget(i) for i in range(self.stack.count())]:
            self.stack.addWidget(window)

    def append_to_previous(self, previous_widget=True):
        if previous_widget:
            self.previous_widgets.append(self.stack.currentWidget())

    def quit_app(self):
        self.close()
