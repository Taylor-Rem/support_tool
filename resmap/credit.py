from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class CreditScrape:
    def __init__(self, browser):
        self.browser = browser

    def define_select(self):
        select_element = self.browser.find_element(By.XPATH, "//select[@name='ttid']")
        self.select = Select(select_element)


class CreditOps(CreditScrape):
    def __init__(self, browser, command):
        super().__init__(browser)
        self.command = command

    def add_credit(self):
        self.define_select()
        self.fill_select()
        self.send_credit_keys()

    def fill_select(self):
        selection = (
            f"{self.credit_row['label']} Concession"
            if self.command["operation"] == "concession"
            and (
                self.credit_row["label"] == "Rent"
                or self.credit_row["label"] == "Home Rental"
            )
            else self.credit_row["label"]
        )
        for index, option in enumerate(self.select.options):
            if option.text.lower() == selection:
                self.select.select_by_index(index)
                break

    def send_credit_keys(self):
        credit_input = self.browser.find_element(
            By.XPATH, "//input[@type='text' and @name='amount']"
        )
        credit_input.send_keys(self.credit_row["amount_value"])
        comments = self.browser.find_element(By.XPATH, "//textarea[@name='comments']")
        comments.send_keys(self.command["comment"])
        self.browser.find_element(
            By.XPATH, "//input[@type='submit' and @name='submit1']"
        ).click()
