from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


class TransactionScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def scrape_total(self):
        total_amount = self.webdriver.find_element(
            By.XPATH,
            '//tr[td[@class="td2" and text()="Amount"]]/td[@class="td2"]/input[@name="amount"]',
        )
        return float(total_amount.get_attribute("value"))

    def charge_scrape_allocations(self):
        return self.webdriver.find_elements(
            By.XPATH, "//form[@name='EditAllocs']//input[@type='text']"
        )

    def charge_scrape_top_allocation(self):
        return self.charge_scrape_allocations()[0]


class TransactionFunctions(TransactionScrape):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def auto_allocate(self):
        try:
            self.webdriver.click(By.NAME, "realloc_trid")
            self.webdriver.click(By.NAME, "update")
        except NoSuchElementException:
            self.webdriver.driver.back()

    def allocate_from_prepaid(self, prepaid):
        total_amount = self.scrape_total()
        key = total_amount if total_amount < prepaid else prepaid
        input_element = self.charge_scrape_top_allocation()
        self.webdriver.send_keys_to_element(input_element, key, True)

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

    def unallocate_all_charges(self, URL=None):
        while True:
            input_element = self.charge_scrape_top_allocation()
            value = input_element.get_attribute("value")
            if value == "0":
                break
            self.webdriver.send_keys_to_element(input_element, "0", True)
        self.webdriver.driver.get(URL) if URL else self.webdriver.driver.back()

    def unallocate_all_credits(self, URL=None):
        current_index = 0
        while True:
            input_elements = self.webdriver.find_elements(
                By.XPATH, "//input[contains(@name, 'alloc') and @type='text']"
            )
            input_element = input_elements[current_index]
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
        self.webdriver.get(URL) if URL else self.webdriver.driver.back()

    def allocate_transactions(self, chosen_item, prepaid, URL=None):
        if chosen_item == "Auto":
            self.auto_allocate()
        else:
            self.allocate_from_prepaid(prepaid)
        self.webdriver.driver.get(URL) if URL else self.webdriver.driver.back()
