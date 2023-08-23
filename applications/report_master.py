from general_tools.os_ops import OSMaster


class FilterLedgers(OSMaster):
    def __init__(self, report):
        super().__init__(report)

    def current_report_items(self):
        properties, units, residents = self.retrieve_report_info()
        current_report_items = []
        for i in range(len(properties)):
            property = properties[i]
            unit = float(units[i])
            resident = residents[i]
            json_entry = f"{property}_{unit}_{resident}"
            current_report_items.append(json_entry)
        return current_report_items

    def filter_properties(self):
        set1 = set(self.current_report_items())
        set2 = set(self.retrieve_json())
        unique_elements = (set1 - set2) | (set2 - set1)
        properties = []
        units = []
        residents = []
        for item in unique_elements:
            prop, unit, res = item.split("_")
            properties.append(prop)
            units.append(float(unit))
            residents.append(res)
        return properties, units, residents


class ReportMaster(FilterLedgers):
    def __init__(self, report):
        super().__init__(report)
        self.temp_storage = self.retrieve_json()
        self.current_index = 0
        self.properties, self.units, self.residents = self.filter_properties()
        self.open_ledger()

    def open_ledger(self):
        self.property = self.properties[self.current_index]
        self.unit = int(self.units[self.current_index])
        self.resident = self.residents[self.current_index]
        print(self.property, self.unit, self.resident)
        self.resmap_ops.open_ledger(self.property, str(self.unit), self.resident)

    def next_ledger(self):
        self.current_index += 1
        self.open_ledger()

    def add_button(self):
        self.add_to_json()
        self.next_ledger()

    def go_to_former(self):
        self.resmap_ops.open_former_ledger(self.unit, self.resident)

    def skip_button(self):
        self.next_ledger()

    def add_to_json(self):
        json_entry = f"{self.property}_{self.unit}_{self.resident}"
        self.temp_storage.append(json_entry)
        self.write_json(self.temp_storage)
