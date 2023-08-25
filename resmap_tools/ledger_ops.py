from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

from resmap_tools.credit_ops import CreditMaster
from resmap_tools.transaction_ops import TransactionMaster


class LedgerScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def retrieve_transaction_and_amount(self, row):
        cells = row.find_all("td")
        transaction = cells[2].get_text(strip=True)
        amount = cells[3].get_text(strip=True)
        return transaction, amount

    def scrape_page(self):
        prepaid_rent_amount = self.get_number_from_string(
            self.return_element(
                By.XPATH,
                "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td[5]",
            )
        )
        current_url = self.webdriver.driver.current_url
        return prepaid_rent_amount, current_url

    def choose_table(self, num):
        return f"/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[last(){num}]/tbody/tr[2]/td/table/tbody"

    def define_table(self, by, value):
        table_elements = self.webdriver.driver.find_elements(by, value)
        table = [element.get_attribute("outerHTML") for element in table_elements]
        return table

    def get_rows(self, table):
        all_rows = []  # Initialize an empty list to collect all rows
        for table_html in table:
            soup = BeautifulSoup(table_html, "html.parser")
            rows = soup.find_all(
                "tr", class_=lambda value: value and value.startswith("td")
            )
            all_rows.extend(rows)  # Add rows to the list
        return all_rows  # Return the list of all rows

    def is_header_row(self, row, class_name):
        return row.find("td", class_=class_name) is not None

    def retrieve_amount_from_bottom(self, row):
        try:
            cells = row.find_all("td")
            amount = cells[1].get_text(strip=True)
            return self.get_number_from_string(amount)
        except:
            return None


class LedgerFunctions(LedgerScrape):
    def __init__(self, webdriver):
        super().__init__(webdriver)
        self.transaction_ops = TransactionMaster(self.webdriver)
        self.credit_ops = CreditMaster(self.webdriver)

    def delete_charges(self, transaction):
        self.webdriver.click_element(self.webdriver.return_last_element(transaction))
        self.transaction_ops.delete_charge()

    def allocate_all_credits(self, amount, element):
        if amount.startswith("(") and amount.endswith(")"):
            try:
                self.webdriver.click_element(element)
                self.transaction_ops.auto_allocate()
            except:
                pass

    def credit_all_charges(self, is_concession):
        self.webdriver.click_element(self.webdriver.return_last_element("Add Credit"))
        self.credit_ops.credit_charge(is_concession)

    def retrieve_rows(self, table_num=-4):
        table = self.define_table(By.XPATH, self.choose_table(table_num))
        return self.get_rows(table)


class LedgerMaster(LedgerFunctions):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def loop_through_table(self, operation, is_concession=False):
        rows = self.retrieve_rows()
        for row in rows:
            if self.is_header_row(row, "th3"):
                continue
            (
                transaction,
                amount,
            ) = self.retrieve_transaction_and_amount(row)
            if operation == "allocate_all":
                self.allocate_all_credits(
                    amount, self.webdriver.return_last_element(transaction)
                )

            if operation == "credit_all_charges":
                try:
                    self.credit_all_charges(is_concession)
                except:
                    pass

            if operation == "delete_all_charges":
                self.delete_charges(transaction)

            if operation == "delete_all_late_fees":
                if "Late" in transaction or transaction in "Late":
                    self.delete_charges("Late")
