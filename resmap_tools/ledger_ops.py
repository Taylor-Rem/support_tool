from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import re

from resmap_tools.credit_ops import CreditMaster
from resmap_tools.transaction_ops import TransactionMaster
from resmap_tools.nav_to_ledger import NavToLedgerMaster


class LedgerScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def retrieve_transaction_and_amount(self, row):
        cells = row.find_all("td")
        transaction = cells[2].get_text(strip=True)
        amount = cells[3].get_text(strip=True)
        return transaction, amount

    def scrape_prepaid(self):
        HTML = self.webdriver.find_element(
            By.XPATH,
            "//tr[td[@class='td2' and contains(text(), 'Prepaid Rent')]]/td[@class='td2' and contains(text(), '$')]",
        ).get_attribute("innerHTML")
        has_parenthesis = bool(re.match(r"^\(\$ [\d,]+\.?\d*\)", HTML))
        prepaid_value = self.webdriver.get_number_from_inner_html(HTML)
        print(has_parenthesis, prepaid_value)
        return prepaid_value, has_parenthesis

    def scrape_unit(self):
        return self.webdriver.find_element(
            By.XPATH,
            "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/a",
        )

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
        self.nav_to_ledger = NavToLedgerMaster(self.webdriver)

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

    def change_ledger(self, chosen_item):
        unit = self.scrape_unit()
        if chosen_item == "Current":
            self.webdriver.click_element(unit)
            self.nav_to_ledger.click_ledger()
        else:
            self.nav_to_ledger.open_former_ledger(unit, None)

    def prepaid_is_amount(self, transaction):
        self.webdriver.click_element(self.webdriver.return_last_element(transaction))
        self.transaction_ops.delete_allocation()


class LedgerMaster(LedgerFunctions):
    def __init__(self, webdriver, thread_helper=None):
        super().__init__(webdriver)
        self.thread_helper = thread_helper

    def loop_through_table(self, operation, chosen_item=None):
        rows = self.retrieve_rows()
        for row in rows:
            if self.is_cancelled():
                print("Loop operation cancelled")
                break
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
                    self.credit_all_charges(chosen_item)
                except:
                    pass

            if operation == "delete_all_charges":
                self.delete_charges(transaction)

            if operation == "delete_all_late_fees":
                if "Late" in transaction or transaction in "Late":
                    self.delete_charges("Late")

            if operation == "transaction_is_prepaid":
                prepaid, has_parenthesis = self.scrape_prepaid()
                amount_num = self.webdriver.get_number_from_inner_html(amount)
                if (prepaid == amount_num) and has_parenthesis:
                    self.prepaid_is_amount(transaction)

    def is_cancelled(self):
        if self.thread_helper:
            return self.thread_helper.is_cancelled()
