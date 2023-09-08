from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


class TransactionScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver
        self.base_xpath = "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/"

    def scrape_total(self):
        total_amount = self.webdriver.find_element(
            By.XPATH,
            '//tr[td[@class="td2" and text()="Amount"]]/td[@class="td2"]/input[@name="amount"]',
        )
        return float(total_amount.get_attribute("value"))

    def scrape_credit_amount(self):
        credit_amount = self.webdriver.find_element(
            By.XPATH,
            f"{self.base_xpath}form/table[1]/tbody/tr[2]/td/table/tbody/tr[5]/td[2]/input",
        )
        return float(credit_amount.get_attribute("value"))


class TransactionFunctions(TransactionScrape):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def auto_allocate(self):
        try:
            self.webdriver.click(By.NAME, "realloc_trid")
            self.webdriver.click(By.NAME, "update")
        except NoSuchElementException:
            self.webdriver.driver.back()

    def delete_charge(self):
        try:
            self.webdriver.click(By.NAME, "delete")
            alert = self.webdriver.driver.switch_to.alert
            alert.accept()
        except:
            self.webdriver.driver.back()

    def clear_element(self, input_element, enter):
        self.webdriver.send_keys_to_element(input_element, Keys.CONTROL + "a", False)
        self.webdriver.send_keys_to_element(input_element, Keys.BACKSPACE, enter)


class TransactionMaster(TransactionFunctions):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def loop(self, operation, URL, prepaid=None):
        idx = 0
        while True:
            table_identifier = (
                f"{self.base_xpath}table[2]/tbody/tr[2]/td/table/tbody"
                if "charge" in operation.lower()
                else f"{self.base_xpath}form/table[2]/tbody/tr[2]/td/table/tbody"
            )
            rows = self.webdriver.get_rows(table_identifier)

            if idx >= len(rows):
                break

            row = rows[idx]

            try:
                input_element = row.find_element(By.XPATH, ".//input[@type='text']")
                value = float(input_element.get_attribute("value"))
            except:
                idx += 1
                continue

            if operation == "Charges":
                if value == 0 or value == "":
                    break
                self.clear_element(input_element, True)

            if operation == "Credits":
                press_enter = idx >= len(rows) - 2
                self.clear_element(input_element, press_enter)
                idx += 1
                if press_enter:
                    break

            # if operation == "allocate_credit":
            #     credit_amount = self.scrape_credit_amount()
            #     cells = row.find_elements(By.TAG_NAME, "td")
            #     bill_amount = self.webdriver.get_number_from_inner_html(cells[2].text)
            #     if bill_amount == credit_amount:
            #         self.webdriver.get_keys(input_element, bill_amount, True)

            if operation == "allocate_charge":
                if value != 0:
                    idx += 1
                    continue
                total_amount = self.scrape_total()
                amount_to_allocate = round(total_amount - value, 2)
                key = amount_to_allocate if amount_to_allocate < prepaid else prepaid
                self.webdriver.send_keys_to_element(input_element, key, True)
                break
        if self.webdriver.driver.current_url != URL:
            self.webdriver.driver.get(URL)
