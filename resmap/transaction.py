from selenium.webdriver.common.by import By


class TransactionScrape:
    def __init__(self, browser):
        self.browser = browser
        self.table_identifier = {
            "charge": "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[2]/tbody/tr[2]/td/table/tbody",
            "credit": "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/table[2]/tbody/tr[2]/td/table/tbody",
        }

    def retrieve_rows(self, type):
        return self.browser.get_rows(By.XPATH, self.table_identifier[type])

    def retrieve_charge_info(self, cells):
        title = cells[0].text.strip()
        amount_input = cells[1].find_element(By.NAME, "amount")
        amount = amount_input.get_attribute("value")
        return {"name": title, "amount": amount, "input": amount_input}

    def retrieve_credit_info(self, cells):
        name = cells[0].text.strip()
        date = cells[1].text.strip()
        bill_amount = self.browser.get_number_from_inner_html(cells[2].text.strip())
        amount_input = cells[3].find_element(By.TAG_NAME, "input")
        current_allocation = amount_input.get_attribute("value")
        return {
            "name": name,
            "date": date,
            "bill_amount": bill_amount,
            "current_allocation": current_allocation,
            "input": amount_input,
        }


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
            for cell in cells:
                print(cell.text)
            if type == "charge":
                allocation_info = self.retrieve_charge_info(cells)
            elif type == "credit":
                allocation_info = self.retrieve_credit_info(cells)
            allocations.append(allocation_info)
        return allocations


class TransactionOps(TransactionLoop):
    def __init__(self, browser):
        super().__init__(browser)

    def retrieve_rows_length(self, type):
        return len(self.browser.get_rows(By.XPATH, self.table_identifier[type])) - 2

    def retrieve_elements(self, type):
        rows = self.browser.get_rows(By.XPATH, self.table_identifier[type])
        return self.loop_through_table(rows, type)

    def perform_transaction_op(self, operation, allocation):
        if operation == "allocate_credit":
            pass
        if operation == "unallocate_credit":
            pass
        if operation == "allocate_charge":
            pass
        if operation == "unallocate_charge":
            pass
