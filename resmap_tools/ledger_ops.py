from selenium.webdriver.common.by import By

from resmap_tools.credit_ops import CreditMaster
from resmap_tools.transaction_ops import TransactionMaster
from resmap_tools.nav_to_ledger import NavToLedgerMaster


class LedgerScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver
        self.base_xpath = "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table"
        self.choose_table = {
            "current": f"{self.base_xpath}[last()-4]/tbody/tr[2]/td/table/tbody",
            "previous": f"{self.base_xpath}[last()-5]/tbody/tr[2]/td/table/tbody",
        }

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
            f"{self.base_xpath}[3]/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/a",
        )

    def scrape_dates(self):
        try:
            dates_element = self.webdriver.find_element(
                By.XPATH,
                f"{self.base_xpath}[3]/tbody/tr[2]/td/table/tbody/tr[5]/td[2]",
            )
            return dates_element.text.strip()
        except:
            return ""

    def scrape_prepaid(self):
        prepaid_element = self.webdriver.find_element(
            By.XPATH,
            f"{self.base_xpath}[3]/tbody/tr[2]/td/table/tbody/tr[3]/td[5]",
        )
        value = prepaid_element.text.strip()
        prepaid_is_credit = self.is_payment(value) == False
        return self.webdriver.get_number_from_inner_html(value), prepaid_is_credit


class LedgerFunctions(LedgerScrape):
    def __init__(self, webdriver):
        super().__init__(webdriver)
        self.transaction_ops = TransactionMaster(self.webdriver)
        self.credit_ops = CreditMaster(self.webdriver)
        self.nav_to_ledger = NavToLedgerMaster(self.webdriver)

    def is_payment(self, text):
        return "(" in text or ")" in text

    def is_metered(self, row):
        try:
            row.find_element(By.XPATH, ".//img[@src='/images/magnify.gif']")
            return True
        except:
            return False

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

    def delete_charge(self, transaction_element):
        self.webdriver.click_element(transaction_element)
        if self.cancelled_true():
            return
        self.transaction_ops.delete_charge()

    def credit_all_charges(self, chosen_item):
        self.webdriver.click_element(self.webdriver.return_last_element("Add Credit"))
        if self.cancelled_true():
            return
        self.credit_ops.credit_charge(chosen_item)

    def auto_allocate(self, transaction_element):
        self.webdriver.click_element(transaction_element)
        if self.cancelled_true():
            return
        self.transaction_ops.auto_allocate()

    def allocate_credit(self, transaction_element):
        self.webdriver.click_element(transaction_element)
        if self.cancelled_true():
            return
        self.transaction_ops.loop("allocate_credit", self.URL)

    def allocate_charge(self, transaction_element, prepaid):
        self.webdriver.click_element(transaction_element)
        if self.cancelled_true():
            return
        self.transaction_ops.loop("allocate_charge", self.URL, prepaid)

    def unallocate_all(self, transaction_element, operation):
        self.webdriver.click_element(transaction_element)
        if self.cancelled_true():
            return
        try:
            self.transaction_ops.loop(operation, self.URL)
        except:
            self.webdriver.driver.get(self.URL)

    def nsf_functions(self, transaction_element, operation):
        self.webdriver.click_element(transaction_element)
        if operation == "bounced_nsf_payment":
            self.nsf_info = self.transaction_ops.loop(operation, self.URL)
        if operation == "allocate_nsf_charge":
            self.transaction_ops.loop(operation, self.URL, nsf_info=self.nsf_info)

    def loop_through_table(
        self,
        operation,
        chosen_item=None,
        chosen_month="current",
        is_autostar=False,
        reloop=False,
    ):
        self.URL = self.get_URL()
        table_xpath = self.choose_table[chosen_month]
        has_late_credit = False
        contains_nsf = False
        if not reloop:
            try:
                rows = self.webdriver.get_rows(table_xpath)
            except:
                return
            for row in rows:
                if self.webdriver.skip_row(row, "th3"):
                    continue
                transaction, amount = self.get_transaction_and_amount(row)
                if "late fee credit" in transaction.lower():
                    has_late_credit = True
                if "nsf" in transaction.lower():
                    contains_nsf = True

        if has_late_credit and chosen_item != "late Fees":
            self.loop_through_table(
                "delete_charges", "late Fees", chosen_month=chosen_month, reloop=True
            )
        if contains_nsf and is_autostar:
            return "nsf"

        idx = 0

        while True:
            rows = self.webdriver.get_rows(table_xpath)
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

            if "rule compliance" in transaction.lower():
                transaction = "Rule Compliance"

            while True:
                trans_idx = 0
                try:
                    transaction_element = row.find_element(
                        By.XPATH,
                        f".//a[contains(text(), '{transaction[: trans_idx]}')]",
                    )
                    break
                except:
                    if trans_idx == -len(transaction):
                        idx += 1
                        continue
                    trans_idx -= 1

            transaction_is_payment = self.is_payment(amount)
            transaction_is_credit = (
                "credit" in transaction.lower() or "concession" in transaction.lower()
            )
            transaction_is_metered = self.is_metered(row)
            transaction_is_nsf = "(nsf" in transaction.lower()
            if operation == "fix_nsf":
                if transaction_is_nsf and transaction_is_payment:
                    self.nsf_functions(transaction_element, "bounced_nsf_payment")
                if transaction_is_nsf and not transaction_is_payment:
                    self.nsf_functions(transaction_element, "allocate_nsf_charge")

            if transaction_is_nsf:
                idx += 1
                continue

            if operation == "unallocate_all":
                if (
                    (chosen_item == "charges" and not transaction_is_payment)
                    or (chosen_item == "credits" and transaction_is_payment)
                ) and not transaction_is_credit:
                    self.unallocate_all(transaction_element, chosen_item)

            if operation == "allocate_all":
                if (
                    chosen_item == "credits"
                    and transaction_is_payment
                    and not transaction_is_credit
                ):
                    self.auto_allocate(transaction_element)
                # if chosen_item == "Credits" and transaction_is_credit:
                #     self.allocate_credit(transaction_element)

                prepaid, prepaid_is_credit = self.scrape_prepaid()
                if (
                    (chosen_item == "charges")
                    and (not transaction_is_payment)
                    and (prepaid != 0)
                    and (prepaid_is_credit)
                ):
                    self.allocate_charge(transaction_element, prepaid)

            if operation == "credit_all_charges":
                if not transaction_is_payment:
                    try:
                        self.credit_all_charges(chosen_item)
                    except:
                        self.webdriver.driver.get(self.URL)
                        break

            if operation == "delete_charges":
                if chosen_item == "all" or chosen_item == "except metered":
                    if transaction_is_payment or (
                        chosen_item == "except metered" and transaction_is_metered
                    ):
                        idx += 1
                        continue
                    self.delete_charge(transaction_element)
                    continue
                if chosen_item == "late fees" and "late" in transaction.lower():
                    self.delete_charge(transaction_element)
                    continue

            idx += 1

    def cancelled_true(self):
        if self.is_cancelled():
            self.webdriver.driver.get(self.URL)
            return True

    def is_cancelled(self):
        if self.thread_helper:
            return self.thread_helper.is_cancelled()
