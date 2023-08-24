from general_tools.os_ops import ReportsBase
from resmap_tools.nav_to_ledger import NavToLedgerMaster


class FilterLedgers(ReportsBase):
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
        set2 = set(self.json_ops.retrieve_json())
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
    def __init__(self, webdriver, report):
        super().__init__(report)
        properties, units, residents = self.filter_properties()
        self.webdriver = webdriver
        self.nav_to_ledger = NavToLedgerMaster(webdriver)
        self.current_index = 0
        self.property = properties[self.current_index]
        self.unit = units[self.current_index]
        self.resident = residents[self.current_index]
        self.nav_to_ledger.open_ledger(self.property, str(self.unit), self.resident)
