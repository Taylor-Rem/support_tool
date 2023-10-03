from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


class TransactionScrape:
    def __init__(self, browser):
        self.browser = browser
        self.table_identifier = {
            "charge": "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[2]/tbody/tr[2]/td/table/tbody",
            "payment": "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/table[2]/tbody/tr[2]/td/table/tbody",
        }

    def retrieve_rows(self, type):
        return self.browser.get_rows(By.XPATH, self.table_identifier[type])

    def retrieve_charge_info(self, cells):
        title = cells[0].text.strip()
        amount_input = cells[1].find_element(By.NAME, "amount")
        amount = float(amount_input.get_attribute("value"))
        return {"name": title, "amount": amount, "input": amount_input}

    def retrieve_payment_info(self, cells):
        name = cells[0].text.strip()
        date = cells[1].text.strip()
        bill_amount = self.browser.get_number_from_inner_html(cells[2].text.strip())
        amount_input = cells[3].find_element(By.TAG_NAME, "input")
        current_allocation = amount_input.get_attribute("value")
        return {
            "name": name,
            "date": date,
            "bill_amount": bill_amount,
            "amount": current_allocation,
            "input": amount_input,
        }

    def auto_allocate(self):
        try:
            self.browser.click(By.NAME, "realloc_trid")
            self.browser.click(By.NAME, "update")
        except NoSuchElementException:
            self.browser.driver.back()

    def scrape_total_amount(self, transaction_type):
        if transaction_type == "payment":
            element = self.browser.find_element(
                By.XPATH,
                "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/table[1]/tbody/tr[2]/td/table/tbody/tr[4]/td[2]",
            )
            value = self.browser.get_number_from_inner_html(element.text)
            if value is not None:
                return value
            else:
                element_input = element.find_element(By.TAG_NAME, "input")
                return float(element_input.get_attribute("value"))
        elif transaction_type == "charge":
            element = self.browser.find_element(
                By.XPATH,
                "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/input",
            )
            return float(element.get_attribute("value"))


class TransactionLoop(TransactionScrape):
    def __init__(self, browser):
        super().__init__(browser)

    def loop_through_table(self, rows, type):
        allocations = []
        for row in rows:
            if self.browser.skip_row(row, "th3"):
                continue
            if self.browser.skip_row(row, "td3"):
                continue
            cells = row.find_elements(By.TAG_NAME, "td")
            if type == "charge":
                allocation_info = self.retrieve_charge_info(cells)
            elif type == "payment":
                allocation_info = self.retrieve_payment_info(cells)
            allocations.append(allocation_info)
        return allocations


class TransactionOps(TransactionLoop):
    def __init__(self, browser):
        super().__init__(browser)

    def retrieve_elements(self, transaction_type):
        rows = self.browser.get_rows(By.XPATH, self.table_identifier[transaction_type])
        return {
            "rows": self.loop_through_table(rows, transaction_type),
            "rows_length": len(rows) - 2,
            "total_amount": self.scrape_total_amount(transaction_type),
        }

    def perform_transaction_op(
        self, command, allocation, transaction_type, total_amount, finished_list
    ):
        if command["operation"] == "allocate":
            if transaction_type == "payment":
                self.auto_allocate()
                return "break"

            if transaction_type == "charge":
                if allocation["amount"] == total_amount:
                    return "break"
                if allocation["amount"] != 0:
                    return
                amount_to_allocate = total_amount - allocation["amount"]
                self.browser.send_keys_to_element(
                    allocation["input"], amount_to_allocate, True
                )

        if command["operation"] == "unallocate":
            if transaction_type == "payment":
                self.clear_element(allocation["input"], finished_list)

            if transaction_type == "charge":
                if allocation["amount"] == 0 or allocation["amount"] == "":
                    return "break"
                self.clear_element(allocation["input"], True)
                return "reload"

        if command["operation"] == "delete":
            try:
                self.browser.click(By.NAME, "delete")
                alert = self.browser.driver.switch_to.alert
                alert.accept()
            except:
                return "break"

    def clear_element(self, input_element, enter):
        self.browser.send_keys_to_element(input_element, Keys.CONTROL + "a", False)
        self.browser.send_keys_to_element(input_element, Keys.BACKSPACE, enter)
