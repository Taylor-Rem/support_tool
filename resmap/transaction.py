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
        current_allocation = float(amount_input.get_attribute("value"))
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
            self.browser.accept_alert()
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
                return float(value)
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

    def loop_through_table(self, rows):
        allocations = []
        for row in rows:
            if self.browser.skip_row(row, "th3"):
                continue
            if self.browser.skip_row(row, "td3"):
                continue
            cells = row.find_elements(By.TAG_NAME, "td")
            if self.ledger_row["type"] == "charge":
                allocation_info = self.retrieve_charge_info(cells)
            elif self.ledger_row["type"] == "payment":
                allocation_info = self.retrieve_payment_info(cells)
            allocations.append(allocation_info)
        return allocations


class TransactionOps(TransactionLoop):
    def __init__(self, browser, command, thread_helper):
        super().__init__(browser)
        self.command = command
        self.thread_helper = thread_helper

    def retrieve_elements(self):
        table = self.browser.find_element(
            By.XPATH, self.table_identifier[self.ledger_row["type"]]
        )
        if table is None:
            return None
        rows = table.find_elements(By.XPATH, ".//tr")
        transaction_info = {
            "rows": self.loop_through_table(rows),
            "rows_length": len(rows) - 2,
            "total_amount": self.scrape_total_amount(self.ledger_row["type"]),
        }
        return transaction_info

    def perform_transaction_op(self):
        if self.command["operation"] == "allocate":
            if self.ledger_row["type"] == "payment":
                self.auto_allocate()
                return "break"

            if self.ledger_row["type"] == "charge":
                combined_amounts = sum(
                    row["amount"] for row in self.transaction_info["rows"]
                )
                if (
                    self.allocation["amount"] == self.transaction_info["total_amount"]
                    or combined_amounts >= self.transaction_info["total_amount"]
                ):
                    return "break"
                self.potential_allocation = round(
                    (self.potential_allocation - self.allocation["amount"]),
                    2,
                )
                if self.allocation["amount"] != 0:
                    return
                amount_to_allocate = (
                    self.potential_allocation
                    if self.potential_allocation <= self.ledger_row["prepaid_amount"]
                    else self.ledger_row["prepaid_amount"]
                )
                self.browser.send_keys_to_element(
                    self.allocation["input"], amount_to_allocate, True
                )

        if self.command["operation"] == "unallocate":
            if self.ledger_row["type"] == "payment":
                self.clear_element(self.allocation["input"], self.finished_list)

            if self.ledger_row["type"] == "charge":
                if self.allocation["amount"] == 0 or self.allocation["amount"] == "":
                    return "break"
                self.clear_element(self.allocation["input"], True)
                return "reload"

    def delete(self):
        if self.thread_helper and not self.thread_helper._is_cancelled:
            try:
                self.browser.click(By.NAME, "delete")
                self.browser.accept_alert()
            except:
                return

    def clear_element(self, input_element, enter):
        self.browser.send_keys_to_element(input_element, Keys.CONTROL + "a", False)
        self.browser.send_keys_to_element(input_element, Keys.BACKSPACE, enter)
