from PyQt5.QtWidgets import QVBoxLayout, QLabel
from front_end.base_widget import BaseWidget
from general_tools.operations import Operations
from functools import partial
from front_end.thread import ThreadHelper


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

    def run_in_thread(self, func, *args, **kwargs):
        self.thread_helper = ThreadHelper(func, self.main_app, self, *args, **kwargs)
        self.thread_helper.finished_signal.connect(self.handle_thread_finished)
        self.thread_helper.cancelled_signal.connect(self.handle_thread_cancelled)
        self.thread_helper.start()

    def handle_thread_finished(self):
        # Implement any behavior you want when the thread finishes
        print("Thread finished!")

    def handle_thread_cancelled(self):
        # Implement any behavior you want when the thread is cancelled
        print("Thread cancelled!")

    def go_back(self):
        if self.main_app.previous_widgets:
            last_widget = self.main_app.previous_widgets.pop()
            self.main_app.stack.setCurrentWidget(last_widget)
        else:
            self.main_app.stack.setCurrentWidget(self.main_app.main_window)

    def add_back_btn(self):
        self.back_btn = self.create_button("⬅️ Back", self.go_back)

    def closeEvent(self, event):
        if hasattr(self, "thread_helper") and self.thread_helper.isRunning():
            self.thread_helper.cancel()
        event.accept()
