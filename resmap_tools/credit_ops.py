from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class CreditScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def get_name_and_bill_amount(self):
        rows = self.webdriver.find_elements(By.XPATH, "//tr[contains(@class, 'td')]")
        row = rows[-1]
        columns = row.find_elements(By.TAG_NAME, "td")
        bill_amount_str = columns[2].text.strip()
        bill_amount_replace = (
            bill_amount_str.replace("$", "").replace(" ", "").replace(",", "")
        )

        self.name = columns[0].text.strip()
        self.bill_amount = float(bill_amount_replace)

    def define_select(self):
        select_element = self.webdriver.find_element(By.XPATH, "//select[@name='ttid']")
        self.select = Select(select_element)


class CreditFunctions(CreditScrape):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def fill_select(self, is_concession):
        if (self.name == "Rent" or self.name == "Home Rental") and is_concession:
            self.select.select_by_visible_text(f"{self.name} Concession")
        else:
            self.select.select_by_visible_text(self.name)

    def send_credit_keys(self):
        credit_input = self.webdriver.find_element(
            By.XPATH, "//input[@type='text' and @name='amount']"
        )
        credit_input.send_keys(self.bill_amount)
        comments = self.webdriver.find_element(By.XPATH, "//textarea[@name='comments']")
        comments.send_keys("charge concession")
        self.webdriver.find_element(
            By.XPATH, "//input[@type='submit' and @name='submit1']"
        ).click()


class CreditMaster(CreditFunctions):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def credit_charge(self, is_concession):
        self.get_name_and_bill_amount()
        self.define_select()
        self.fill_select(is_concession)
        self.send_credit_keys()
