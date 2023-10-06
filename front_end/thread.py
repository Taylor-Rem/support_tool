from PyQt5.QtCore import QThread, pyqtSignal


class ThreadHelper(QThread):
    thread_signal = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False

    def run(self):
        if not self._is_cancelled:
            result = self.func(*self.args, **self.kwargs)
            self.thread_signal.emit(result)

    def cancel(self):
        self._is_cancelled = True
