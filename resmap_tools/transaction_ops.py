from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class TransactionScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def scrape_transaction(self):
        full_charge = float(
            self.webdriver.driver.find_element(
                By.XPATH,
                "//input[@type='text' and @name='amount']",
            ).get_attribute("value")
        )
        top_allocation_element = self.allocation_elements(2)
        top_allocation_value = float(top_allocation_element.get_attribute("value"))
        additional_rent_element = self.allocation_elements(3)
        return (
            full_charge,
            top_allocation_element,
            top_allocation_value,
            additional_rent_element,
        )

    def allocation_elements(self, num):
        try:
            return self.webdriver.driver.find_element(
                By.XPATH,
                f"/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[2]/tbody/tr[2]/td/table/tbody/tr[{num}]/td[2]/form/input[4]",
            )
        except NoSuchElementException:
            return False


class TransactionFunctions(TransactionScrape):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def scrape_page(self):
        (
            self.full_charge,
            self.top_allocation_element,
            self.top_allocation_value,
            self.additional_rent_element,
        ) = self.scrape_transaction()

    def auto_allocate(self):
        try:
            self.webdriver.click(By.NAME, "realloc_trid")
            self.webdriver.click(By.NAME, "update")
        except NoSuchElementException:
            self.webdriver.driver.back()

    def allocate_cents(self, amount):
        self.scrape_page()
        try:
            if self.charge_equals_top_value():
                self.subtract_current_allocation(
                    amount,
                )
                self.webdriver.send_keys_element(
                    self.additional_rent_element, amount, True
                )
            if self.top_allocation_value == 0:
                self.webdriver.send_keys_element(
                    self.top_allocation_element, amount, True
                )
        except:
            pass

    def charge_equals_top_value(self):
        if self.full_charge == self.top_allocation_value:
            return True

    def subtract_top_allocation(self, amount):
        new_allocation = round(self.top_allocation_value - amount, 2)
        self.webdriver.send_keys_element(
            self.top_allocation_element, new_allocation, True
        )

    def subtract_compliance_from_rent(self, compliance_amount):
        self.scrape_page()
        if self.charge_equals_top_value():
            self.subtract_current_allocation(compliance_amount)

    def allocate_amount(self, amount):
        self.webdriver.send_keys(
            By.XPATH,
            "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/form/input[4]",
            amount,
            True,
        )

    def delete_charge(self):
        self.webdriver.click(By.NAME, "delete")
        alert = self.webdriver.driver.switch_to.alert
        alert.accept()


class TransactionMaster(TransactionFunctions):
    def __init__(self, webdriver):
        super().__init__(webdriver)
