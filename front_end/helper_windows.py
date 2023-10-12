from PyQt5.QtWidgets import QVBoxLayout, QLabel
from front_end.base_widget import BaseWidget
from main_tools.operations import Operations
from main_tools.operations_list import OperationsList
from functools import partial
from front_end.thread import ThreadHelper
from main_tools.robots import TicketBot, RedstarBot


class HelperWidget(BaseWidget):
    def __init__(self, main_app, title):
        super().__init__()
        self.operations_list = OperationsList()
        self.operations = Operations(main_app.browser)
        self.ticket_bot = TicketBot(main_app.browser, self.operations_list)
        self.redstar_bot = RedstarBot(main_app.browser, self.operations_list)
        self.main_app = main_app
        self.setWindowTitle(title)
        self.previous_window = None
        self.thread_helper = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(title, self)
        self.layout.addWidget(self.label)

        self.button_layout = QVBoxLayout()
        self.layout.addLayout(self.button_layout)

    def create_button(self, text, callback, target_layout=None):
        if not target_layout:
            target_layout = self.layout
        return super()._create_button(text, callback, target_layout)

    def run_in_thread(self, callback, *args, **kwargs):
        self.command = kwargs.pop("command", None)
        self.previous_window = self.main_app.current_window()
        self.thread_helper = ThreadHelper(callback, *args, **kwargs)
        self.give_thread()
        self.thread_helper.thread_signal.connect(self.on_thread_finished)
        self.cancel_dialog = ThreadRunningWindow(self.main_app, self.thread_helper)
        self.main_app.switch_window(self.cancel_dialog, add_to_previous=False)
        self.thread_helper.start()

    def give_thread(self):
        self.operations.thread_helper = self.thread_helper
        self.ticket_bot.thread_helper = self.thread_helper
        self.redstar_bot.thread_helper = self.thread_helper

    def on_thread_finished(self, result):
        self.cancel_dialog.close()
        if self.command:
            self.main_app.stack.setCurrentWidget(self.command["window"])
        else:
            self.main_app.stack.setCurrentWidget(self.previous_window)

    def go_back(self):
        if self.main_app.previous_widgets:
            last_widget = self.main_app.previous_widgets.pop()
            self.main_app.stack.setCurrentWidget(last_widget)
        else:
            self.main_app.stack.setCurrentWidget(self.main_app.main_window)

    def add_back_btn(self):
        self.back_btn = self.create_button("⬅️ Back", self.go_back)


class ThreadRunningWindow(HelperWidget):
    def __init__(self, main_app, thread_helper, title="Running Operation"):
        super().__init__(main_app, title)
        self.thread_helper = thread_helper

        self.operation_label = QLabel("Operation is running...", self)
        self.layout.addWidget(self.operation_label)
        self.cancel_btn = self.create_button("Cancel operation", self.cancel_operation)

    def cancel_operation(self):
        self.thread_helper.cancel()
        self.operation_label.setText("Cancelling operation...")
        self.cancel_btn.setEnabled(False)


class AdditionalInfoWindow(HelperWidget):
    def __init__(self, main_app, command=None):
        super().__init__(main_app, "Additional Info")
        if command:
            self.create_additional_info_widgets(command)
            self.add_back_btn()

    def create_additional_info_widgets(self, command):
        for widget in command["widgets"]:
            if widget == "dropdown":
                dropdown = self.create_dropdown(["hi", "hello", "how do you do"])
            if widget == "text_input":
                comment = self.create_text_input("")
        self.create_button("Submit", partial(self.submit, command, comment))

    def submit(self, command, input):
        command["comment"] = input.text()
        self.run_in_thread(self.operations.init_operation, command)
