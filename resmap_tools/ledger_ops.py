from selenium.webdriver.common.by import By

from resmap_tools.credit_ops import CreditMaster
from resmap_tools.transaction_ops import TransactionMaster
from resmap_tools.nav_to_ledger import NavToLedgerMaster


class LedgerScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def get_URL(self):
        return self.webdriver.driver.current_url

    def get_transaction_and_amount(self, row):
        cells = row.find_elements(By.TAG_NAME, "td")
        transaction = cells[2].text.strip()
        amount = cells[3].text.strip()
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
        prepaid_is_credit = self.is_credit(value) == False
        return self.webdriver.get_number_from_inner_html(value), prepaid_is_credit

    def choose_table(self, num):
        return f"/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[last(){num}]/tbody/tr[2]/td/table/tbody"


class LedgerFunctions(LedgerScrape):
    def __init__(self, webdriver):
        super().__init__(webdriver)
        self.transaction_ops = TransactionMaster(self.webdriver)
        self.credit_ops = CreditMaster(self.webdriver)
        self.nav_to_ledger = NavToLedgerMaster(self.webdriver)

    def is_credit(self, text):
        return "(" in text or ")" in text

    def is_metered(self, row):
        try:
            row.find_element(By.XPATH, ".//img[@src='/images/magnify.gif']")
            return True
        except:
            return False

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

    def loop_through_table(
        self, operation, chosen_item=None, chosen_month=-4, is_autostar=False
    ):
        URL = self.get_URL()
        idx = 0

        while True:
            rows = self.retrieve_rows(chosen_month)
            redstar_in_ledger = self.webdriver.element_exists(
                By.XPATH, '//td//font[@color="red"]'
            )
            if (
                idx >= len(rows)
                or self.is_cancelled()
                or (is_autostar and not redstar_in_ledger)
            ):
                break

            row = rows[idx]

            if self.webdriver.skip_row(row, "th3"):
                idx += 1
                continue

            transaction, amount = self.get_transaction_and_amount(row)

            transaction_element = row.find_element(
                By.XPATH, f".//a[text() = '{transaction}']"
            )

            transaction_is_credit = self.is_credit(amount)
            transaction_is_nsf = "NSF" in transaction
            transaction_is_metered = self.is_metered(row)

            if transaction_is_nsf:
                break

            if operation == "unallocate_all":
                if chosen_item == "Charges" and not transaction_is_credit:
                    self.webdriver.click_element(transaction_element)
                    self.transaction_ops.loop("unallocate_charge", URL)
                elif chosen_item == "Credits" and transaction_is_credit:
                    self.webdriver.click_element(transaction_element)
                    self.transaction_ops.loop("unallocate_credit", URL)

            if operation == "allocate_all":
                prepaid, prepaid_is_credit = self.scrape_prepaid()
                if (
                    (chosen_item == "Manual")
                    and (not transaction_is_credit)
                    and (prepaid != 0)
                    and (prepaid_is_credit)
                ):
                    self.webdriver.click_element(transaction_element)
                    self.transaction_ops.loop("allocate_charge", URL, prepaid)

                if chosen_item == "Auto" and transaction_is_credit:
                    self.webdriver.click_element(transaction_element)
                    self.transaction_ops.auto_allocate()

            if operation == "credit_all_charges":
                if transaction_is_credit:
                    idx += 1
                    continue
                self.webdriver.click_element(
                    self.webdriver.return_last_element("Add Credit")
                )
                self.credit_ops.credit_charge(chosen_item)

            if operation == "delete_charges":
                if chosen_item == "All" or "Except Metered":
                    if transaction_is_credit or (
                        chosen_item == "Except Metered" and transaction_is_metered
                    ):
                        idx += 1
                        continue
                    self.webdriver.click_element(transaction_element)
                    self.transaction_ops.delete_charge()
                    idx -= 1
                    continue
                if chosen_item == "Late Fees" and (
                    "Late" in transaction or transaction in "Late"
                ):
                    self.webdriver.click_element(transaction_element)
                    self.transaction_ops.delete_charge()
                    idx -= 1
                    continue

            idx += 1

    def is_cancelled(self):
        if self.thread_helper:
            return self.thread_helper.is_cancelled()
