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


class LedgerLoop(LedgerScrape):
    def __init__(self, browser):
        super().__init__(browser)

    def loop_through_table(self, rows):
        transactions = []

        for row in rows:
            if self.browser.skip_row(row, "th3"):
                continue

            transaction, amount = self.get_transaction_and_amount(row)
            amount_value = self.browser.get_number_from_inner_html(amount)

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
                transaction_type = "charge"
            elif transaction_is_payment:
                transaction_type = "payment"
            elif transaction_is_credit:
                transaction_type = "credit"

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
                        continue
                    trans_idx -= 1

            transaction_info = {
                "label": transaction,
                "amount": amount_value,
                "type": transaction_type,
                "link": transaction_element,
            }
            transactions.append(transaction_info)

        return transactions


class LedgerOps(LedgerLoop):
    def __init__(self, browser):
        super().__init__(browser)
        self.table_xpath = self.choose_table["current"]

    def retrieve_rows_length(self):
        return len(self.browser.get_rows(By.XPATH, self.table_xpath)) - 2

    def retrieve_elements(self):
        rows = self.browser.get_rows(By.XPATH, self.table_xpath)
        return self.loop_through_table(rows)
