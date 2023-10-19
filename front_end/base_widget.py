from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QLabel,
)
from functools import partial


class BaseWidget(QWidget):
    def _create_button(self, text, callback, layout=None):
        if layout is None:
            layout = self.layout
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    def create_text_input(self, default_text="", label=None, callback=None):
        if label:
            label = QLabel(label)
            self.layout.addWidget(label)
        text_input = QLineEdit(self)
        text_input.setText(default_text)
        self.layout.addWidget(text_input)
        if callback:

            def on_return_pressed():
                callback(
                    text_input.text()
                )  # Get the current value of the text_input and pass it to the callback

            text_input.returnPressed.connect(on_return_pressed)
            self._create_button("Submit", on_return_pressed)
        return text_input

    def create_dropdown(self, items, current_index=0):
        dropdown = QComboBox(self)
        dropdown.addItems(items)
        dropdown.setCurrentIndex(current_index)
        self.layout.addWidget(dropdown)
        return dropdown

    def create_configured_dropdown(self, items, callback=None):
        dropdown = QComboBox(self)
        dropdown.addItems(items)

        if callback:

            def index_changed_handler(index):
                if index != 0:
                    # Pass dropdown directly here
                    callback(dropdown)
                    dropdown.setCurrentIndex(0)

            dropdown.currentIndexChanged.connect(index_changed_handler)

        self.layout.addWidget(dropdown)
        return dropdown

    def configured_operations_dropdown(self, items, callback=None):
        def ledger_callback(dropdown):
            operation_data = self.get_selected_dropdown_item(dropdown)
            if callback:
                callback(operation_data)

        return self.create_configured_dropdown(items, ledger_callback)

    def get_selected_dropdown_item(self, dropdown: QComboBox):
        selected_item = dropdown.currentText()
        operation = self.get_operation_from_key(selected_item)
        value = self.get_operation_value_from_dropdown(selected_item)
        return {
            "operation": operation,
            **value,
        }

    def get_operation_from_key(self, key):
        for operation, sub_dict in self.operations_list.ticket_ops_dict.items():
            if key in sub_dict:
                return operation
        for operation, sub_dict in self.operations_list.ledger_ops_dict.items():
            if key in sub_dict:
                return operation
        return None

    def get_operation_value_from_dropdown(self, key):
        for sub_dict in self.operations_list.ticket_ops_dict.values():
            if key in sub_dict:
                return sub_dict.get(key)
        for sub_dict in self.operations_list.ledger_ops_dict.values():
            if key in sub_dict:
                return sub_dict.get(key)
        return None

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
