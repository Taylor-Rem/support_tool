from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


class NavToLedgerScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def scrape_resident(self):
        try:
            RM_resident = self.webdriver.return_element_html(
                By.XPATH,
                '//tbody/tr[2]/td[2]/a[contains(@href, "resident.php?cmd=viewresident")]',
            )
            return RM_resident
        except:
            return None


class NavToLedgerOps(NavToLedgerScrape):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def open_property(self, property):
        self.webdriver.click(By.XPATH, "//a[contains(., 'CHANGE PROPERTY')]")
        self.webdriver.click(By.XPATH, f"//a[contains(., '{property}')]")

    def open_unit(self, unit):
        self.webdriver.send_keys(By.NAME, "search_input", unit + Keys.ENTER)

    def click_ledger(self, unit=None, resident=None):
        try:
            self.webdriver.click(By.XPATH, ".//a[text()='Ledger']")
        except NoSuchElementException:
            self.open_former_ledger(unit, resident)

    def search_resident(self, resident, num):
        self.webdriver.click(
            By.ID,
            f"former{num}",
        )
        self.webdriver.send_keys(By.NAME, "ressearch", resident + Keys.ENTER)

    def open_unit_and_ledger(self, unit, resident):
        self.open_unit(unit)
        if self.compare_resident(resident) or resident is None:
            self.click_ledger(unit, resident)
        else:
            self.open_former_ledger(unit, resident)

    def search_resident_and_open_ledger(self, resident):
        try:
            self.search_resident(resident, 1)
            self.click_ledger()
        except NoSuchElementException:
            self.search_resident(resident, 2)
            self.click_ledger()
        except:
            print(f"there was a problem with ledger {resident}")
            pass

    def open_former_ledger(self, unit, resident):
        try:
            self.webdriver.click(By.XPATH, f".//a[text()='{unit}']")
            self.webdriver.click(
                By.XPATH,
                "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody/tr[2]/td[5]/a",
            )
            self.click_last_ledger()
        except NoSuchElementException:
            self.search_resident_and_open_ledger(resident)

    def click_last_ledger(self):
        table = self.webdriver.find_element(
            By.XPATH,
            "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[2]/tbody/tr[2]/td/table/tbody",
        )
        ledger_links = table.find_elements(By.XPATH, ".//a[text()='Ledger']")
        if ledger_links:
            self.webdriver.click_element(ledger_links[-1])
        else:
            self.click_ledger()


class NavToLedgerMaster(NavToLedgerOps):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def open_ledger(self, property, unit, resident):
        self.open_property(property)
        if unit is not None:
            self.open_unit_and_ledger(unit, resident)

    def compare_resident(self, resident):
        RM_resident = self.scrape_resident()
        if RM_resident and resident:
            if resident in RM_resident or RM_resident in resident:
                return True
            else:
                return False
        return False
