from selenium.webdriver.common.by import By

import re

from resmap_tools.credit_ops import CreditMaster
from resmap_tools.transaction_ops import TransactionMaster
from resmap_tools.nav_to_ledger import NavToLedgerMaster


class LedgerScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def get_URL(self):
        return self.webdriver.driver.current_url

    def retrieve_transaction_and_amount(self, row):
        cells = row.find_all("td")
        transaction = cells[2].get_text(strip=True)
        amount = cells[3].get_text(strip=True)
        return transaction, amount

    def scrape_unit(self):
        return self.webdriver.find_element(
            By.XPATH,
            "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/a",
        )

    def scrape_prepaid(self):
        prepaid_element = self.webdriver.find_element(
            By.XPATH,
            "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td[5]",
        )
        value = prepaid_element.text.strip()
        prepaid_is_credit = ("(" or ")") not in value
        return self.webdriver.get_number_from_inner_html(value), prepaid_is_credit

    def choose_table(self, num):
        return f"/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[last(){num}]/tbody/tr[2]/td/table/tbody"

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

    def retrieve_rows(self, table_num):
        table = self.webdriver.define_table(By.XPATH, self.choose_table(table_num))
        return self.webdriver.get_rows(table)

    def change_ledger(self, chosen_item):
        URL = self.get_URL()
        unit = self.scrape_unit()
        if chosen_item == "Current":
            self.webdriver.click_element(unit)
            try:
                self.nav_to_ledger.click_ledger()
            except:
                self.webdriver.driver.get(URL)
        else:
            self.nav_to_ledger.open_former_ledger(unit, None, URL)


class LedgerMaster(LedgerFunctions):
    def __init__(self, webdriver, thread_helper=None):
        super().__init__(webdriver)
        self.thread_helper = thread_helper

    def loop_through_table(self, operation, chosen_item=None, chosen_month=-4):
        URL = self.get_URL()
        rows = self.retrieve_rows(chosen_month)

        for row in rows:
            if self.is_cancelled():
                print("Loop operation cancelled")
                break
            if self.webdriver.skip_row(row, "th3"):
                continue
            (
                transaction,
                amount,
            ) = self.retrieve_transaction_and_amount(row)

            transaction_element = self.webdriver.return_last_element(transaction)
            transaction_is_credit = ("(" or ")") in amount
            transaction_is_nsf = "NSF" in transaction

            if transaction_is_nsf:
                break

            if operation == "unallocate_all":
                try:
                    if (chosen_item == "Charges" and not transaction_is_credit) or (
                        (chosen_item == "Credits" and transaction_is_credit)
                        and ("Street Lamp" not in transaction)
                    ):
                        self.webdriver.click_element(transaction_element)
                        self.transaction_ops.unallocate_all(chosen_item, URL)

                except:
                    pass

            if operation == "allocate_all":
                try:
                    prepaid, prepaid_is_credit = self.scrape_prepaid()
                    if (chosen_item == "Auto" and transaction_is_credit) or (
                        (chosen_item == "Manual")
                        and (not transaction_is_credit)
                        and (prepaid != 0)
                        and (prepaid_is_credit)
                    ):
                        self.webdriver.click_element(transaction_element)
                        self.transaction_ops.allocate_transactions(
                            chosen_item, prepaid, URL
                        )
                except:
                    pass

            if operation == "credit_all_charges":
                if transaction_is_credit:
                    continue
                try:
                    self.webdriver.click_element(
                        self.webdriver.return_last_element("Add Credit")
                    )
                    self.credit_ops.credit_charge(chosen_item)
                except:
                    self.webdriver.driver.get(URL)
                    break

            if operation == "delete_charges":
                if (chosen_item == "All") or (
                    chosen_item == "Late Fees"
                    and ("Late" in transaction or transaction in "Late")
                ):
                    self.webdriver.click_element(transaction_element)
                    self.transaction_ops.delete_charge()

    def is_cancelled(self):
        if self.thread_helper:
            return self.thread_helper.is_cancelled()
