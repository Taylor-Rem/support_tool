from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class LedgerScrape:
    def __init__(self, browser):
        self.browser = browser
        self.base_xpath = "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table"
        self.choose_table = {
            "current": f"{self.base_xpath}[last()-4]/tbody/tr[2]/td/table/tbody",
            "previous": f"{self.base_xpath}[last()-5]/tbody/tr[2]/td/table/tbody",
        }

    def ledger_has_redstar(self):
        return self.browser.element_exists(
            By.XPATH, '//td//font[@color="red" and text()="*"]'
        )

    def get_URL(self):
        return self.browser.driver.current_url

    def get_transaction_and_amount(self, row):
        cells = row.find_elements(By.TAG_NAME, "td")
        transaction = cells[2].text.strip()
        amount = cells[3].text.strip()
        return transaction, amount

    def check_is_metered(self, row):
        try:
            row.find_element(By.XPATH, ".//img[@src='/images/magnify.gif']")
            return True
        except NoSuchElementException:
            return False

    def scrape_prepaid(self):
        prepaid_element = self.browser.find_element(
            By.XPATH,
            f"{self.base_xpath}[3]/tbody/tr[2]/td/table/tbody/tr[3]/td[5]",
        )
        value = prepaid_element.text.strip()
        if "(" not in value:
            return self.browser.get_number_from_inner_html(value)


class LoopFunctions(LedgerScrape):
    def __init__(self, browser):
        super().__init__(browser)

    def determine_transaction_type(self, transaction, amount):
        transaction_is_charge = "(" not in amount
        transaction_is_credit = (
            "credit" in transaction.lower() or "concession" in transaction.lower()
        )
        if (
            "rule compliance" in transaction.lower()
            or "credit card" in transaction.lower()
        ):
            transaction_is_credit = False
        transaction_is_payment = ("(" in amount) and (not transaction_is_credit)

        if transaction_is_charge:
            return "charge"
        elif transaction_is_payment:
            return "payment"
        elif transaction_is_credit:
            return "credit"

    def is_special_transaction(self, row, transaction, amount):
        conditions = {
            "late_fee": "late" in transaction.lower(),
            "metered": self.check_is_metered(row),
            "bounced_check": "(" in amount and "(nsf" in transaction.lower(),
            "system_nsf": "(" not in amount and "(nsf)" in transaction.lower(),
        }

        return [key for key, condition_met in conditions.items() if condition_met]


class LedgerLoop(LoopFunctions):
    def __init__(self, browser):
        super().__init__(browser)

    def loop_through_table(self, rows):
        ledger_info = []

        for row in rows:
            if self.browser.skip_row(row, "th3"):
                continue

            transaction, amount = self.get_transaction_and_amount(row)
            amount_value = self.browser.get_number_from_inner_html(amount)

            transaction_type = self.determine_transaction_type(transaction, amount)
            special_types = self.is_special_transaction(row, transaction, amount)

            trans_idx = 0
            while True:
                try:
                    transaction_element = row.find_element(
                        By.XPATH,
                        f".//a[contains(text(), '{transaction[: trans_idx]}')]",
                    )
                    break
                except:
                    if trans_idx == -len(transaction):
                        continue
                    trans_idx -= 1

            transaction_info = {
                "label": transaction,
                "amount": amount_value,
                "type": transaction_type,
                "special_type": special_types,
                "link": transaction_element,
            }

            ledger_info.append(transaction_info)

        return ledger_info


class LedgerOps(LedgerLoop):
    def __init__(self, browser):
        super().__init__(browser)
        self.table_xpath = self.choose_table["current"]

    def retrieve_elements(self):
        rows = self.browser.get_rows(By.XPATH, self.table_xpath)
        return {
            "rows": self.loop_through_table(rows),
            "rows_length": len(rows) - 2,
            "prepaid_amount": self.scrape_prepaid(),
        }
