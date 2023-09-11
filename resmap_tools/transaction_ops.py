from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


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

    def scrape_total_from_nsf(self):
        try:
            total_amount = self.webdriver.find_element(
                By.XPATH,
                f"{self.base_xpath}form/table[1]/tbody/tr[2]/td/table/tbody/tr[4]/td[2]",
            )
            return self.webdriver.get_number_from_inner_html(total_amount.text)
        except NoSuchElementException:
            return None

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

    def loop(self, operation, URL, prepaid=None, nsf_info=None):
        idx = 0
        nsf_total = self.scrape_total_from_nsf()
        allocation_names = []
        bill_amounts = []
        while True:
            table_identifier = {
                "charges": f"{self.base_xpath}table[2]/tbody/tr[2]/td/table/tbody",
                "allocate_charge": f"{self.base_xpath}table[2]/tbody/tr[2]/td/table/tbody",
                "credits": f"{self.base_xpath}form/table[2]/tbody/tr[2]/td/table/tbody",
                "bounced_nsf_payment": f"{self.base_xpath}form/table[2]/tbody/tr[2]/td/table/tbody",
                "allocate_nsf_charge": f"{self.base_xpath}form/table[2]/tbody",
            }

            rows = self.webdriver.get_rows(table_identifier[operation])
            finished_list = idx >= len(rows) - 2
            if idx >= len(rows):
                break

            row = rows[idx]

            try:
                input_element = row.find_element(By.XPATH, ".//input[@type='text']")
            except:
                idx += 1
                continue

            value = input_element.get_attribute("value")
            value = 0 if "NaN" in value or value == "" else float(value)

            if operation == "charges":
                if value == 0 or value == "":
                    break
                self.clear_element(input_element, True)

            if operation == "credits":
                self.clear_element(input_element, finished_list)
                idx += 1
                if finished_list:
                    break

            if operation == "bounced_nsf_payment":
                cells = row.find_elements(By.TAG_NAME, "td")

                allocation_name = cells[0].text
                bill_amount = self.webdriver.get_number_from_inner_html(cells[2].text)
                if "(nsf)" in allocation_name.lower():
                    self.clear_element(input_element, finished_list)
                    idx += 1
                    continue
                key = bill_amount if nsf_total >= bill_amount else nsf_total

                """clear the input using javascript so it remains in focus"""
                self.webdriver.driver.execute_script(
                    "arguments[0].value = '';", input_element
                )
                self.webdriver.driver.execute_script(
                    "arguments[0].focus();", input_element
                )

                input_element.send_keys(key)
                if finished_list:
                    input_element.send_keys(Keys.ENTER)
                nsf_total = round(nsf_total - bill_amount, 2)
                allocation_names.append(allocation_name)
                bill_amounts.append(bill_amount)

                idx += 1
                if finished_list:
                    return [allocation_names, bill_amounts]

            if operation == "allocate_nsf_charge":
                imported_allocation_names = nsf_info[0]
                imported_bill_amounts = nsf_info[1]
                imported_allocation_name = imported_allocation_names[idx]
                imported_bill_amount = imported_bill_amounts[idx]
                cells = row.find_elements(By.TAG_NAME, "td")
                dropdown = cells[0].find_element(By.TAG_NAME, "select")
                select = Select(dropdown)
                select.select_by_visible_text(imported_allocation_name)

                """clear the input using javascript so it remains in focus"""
                self.webdriver.driver.execute_script(
                    "arguments[0].value = '';", input_element
                )
                self.webdriver.driver.execute_script(
                    "arguments[0].focus();", input_element
                )
                input_element.send_keys(imported_bill_amount)
                idx += 1
                if idx >= len(imported_allocation_names):
                    input_element.send_keys(Keys.ENTER)
                    return

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
