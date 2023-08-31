from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


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
        try:
            self.webdriver.click(By.NAME, "delete")
            alert = self.webdriver.driver.switch_to.alert
            alert.accept()
        except:
            self.webdriver.driver.back()


class TransactionMaster(TransactionFunctions):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def unallocate_all(self, transaction_type, URL):
        current_index = 0
        while True:
            if transaction_type == "Charges":
                input_elements = self.webdriver.find_elements(
                    By.XPATH, "//form[@name='EditAllocs']//input[@type='text']"
                )
                input_element = input_elements[0]
                value = input_element.get_attribute("value")
                if value == "0":
                    break
                self.webdriver.send_keys_to_element(input_element, "0", True)
            else:
                input_elements = self.webdriver.find_elements(
                    By.XPATH, "//input[contains(@name, 'alloc') and @type='text']"
                )
                input_element = input_elements[current_index]
                value = input_element.get_attribute("value")
                press_enter = current_index == len(input_elements) - 2
                self.webdriver.send_keys_to_element(
                    input_element, Keys.CONTROL + "a", press_enter
                )
                self.webdriver.send_keys_to_element(
                    input_element, Keys.BACKSPACE, press_enter
                )
                current_index += 1
                if press_enter:
                    break

        self.webdriver.driver.get(URL)
