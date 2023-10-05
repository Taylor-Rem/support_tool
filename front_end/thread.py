from PyQt5.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from PyQt5.QtCore import QThread, pyqtSignal


class ThreadHelper(QThread):
    finished_signal = pyqtSignal()
    cancelled_signal = pyqtSignal()

    def __init__(self, func, main_app, return_widget, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False
        self.func = func
        self.main_app = main_app
        self.return_widget = return_widget

        # Connect signals here to unify the behavior
        self.finished_signal.connect(self.on_finished)
        self.cancelled_signal.connect(self.on_cancelled)

    def is_cancelled(self):
        return self._is_cancelled

    def run(self):
        self.func(*self.args, **self.kwargs)
        if self._is_cancelled:
            self.cancelled_signal.emit()
        else:
            self.finished_signal.emit()

    def reset(self):
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def start(self):
        self.operation_window = ThreadRunningWindow(self.main_app, self)
        self.main_app.switch_window(self.operation_window, False)
        super().start()

    def finish_operation(self):
        self.main_app.switch_window(self.return_widget, False)

    def on_cancelled(self):
        self.finish_operation()

    def on_finished(self):
        self.finish_operation()


class ThreadRunningWindow(QWidget):
    def __init__(self, main_app, thread_helper, title="Running Operation"):
        super().__init__()
        self.main_app = main_app
        self.thread_helper = thread_helper

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.operation_label = QLabel("Operation is running...", self)
        self.layout.addWidget(self.operation_label)

        self.cancel_btn = QPushButton("Cancel operation", self)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        self.layout.addWidget(self.cancel_btn)

    def cancel_operation(self):
        self.thread_helper.cancel()
        self.operation_label.setText("Cancelling operation...")
        self.cancel_btn.setEnabled(False)
