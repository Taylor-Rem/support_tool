from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class LedgerScrape:
    def __init__(self, browser):
        self.browser = browser
        self.base_xpath = "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table"
        self.choose_table = {
            "current": f"{self.base_xpath}[last()-4]/tbody/tr[2]/td/table/tbody",
            "previous": f"{self.base_xpath}[last()-5]/tbody/tr[2]/td/table/tbody",
            "bottom": f"{self.base_xpath}[last()-1]/tbody/tr[2]/td/table/tbody",
        }
        self.transaction_amount_cells = {"current": [1, 3], "bottom": [1, 2]}

    def ledger_has_redstar(self):
        return self.browser.element_exists(
            By.XPATH, '//td//font[@color="red" and text()="*"]'
        )

    def get_URL(self):
        return self.browser.driver.current_url

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
        prepaid_amount = self.browser.get_number_from_inner_html(value)
        return prepaid_amount if "(" not in value else -prepaid_amount


class LoopFunctions(LedgerScrape):
    def __init__(self, browser):
        super().__init__(browser)

    def get_row_details(self, row):
        cells = row.find_elements(By.TAG_NAME, "td")

        if self.command["table"] in ["current", "previous"]:
            transaction = cells[2]
            amount = cells[3].text.strip()
        elif self.command["table"] == "bottom":
            transaction = cells[0]
            amount = cells[1].text.strip()

        label = transaction.text.strip().lower()
        amount_value = self.browser.get_number_from_inner_html(amount)

        self.row_details = {
            "transaction_label": label,
            "amount_value": amount_value,
            "prepaid_amount": self.prepaid,
        }

        if self.command["table"] in ["current", "previous"]:
            transaction_link = transaction.find_element(By.TAG_NAME, "a")
            self.row_details.update({"link": transaction_link, "amount": amount})
            self.determine_transaction_type(row, label)

    def determine_transaction_type(self, row, label):
        is_charge = "(" not in self.row_details["amount"]
        is_credit = "credit" in label or "concession" in label
        is_payment = not is_charge and not is_credit

        if "rule compliance" in label or "credit card" in label:
            is_credit = False
            is_payment = True

        type_update = {}
        special_type_update = {}

        if is_charge:
            type_update["type"] = "charge"
        elif is_payment:
            type_update["type"] = "payment"
        elif is_credit:
            type_update["type"] = "credit"

        special_types = ["late_fee", "metered", "bounced_check", "system_nsf"]
        checks = [
            "late" in label,
            self.check_is_metered(row),
            is_payment and "(nsf" in label,
            is_charge and "(nsf" in label,
        ]

        for s_type, check in zip(special_types, checks):
            if check:
                special_type_update["special_type"] = s_type
                break

        self.row_details.update(**type_update, **special_type_update)


class LedgerLoop(LoopFunctions):
    def __init__(self, browser):
        super().__init__(browser)

    def loop_through_table(self, rows):
        ledger_info = []
        self.prepaid = self.scrape_prepaid()

        for row in rows:
            if self.browser.skip_row(row, "th3"):
                continue
            self.get_row_details(row)
            ledger_info.append(self.row_details)
        return ledger_info


class LedgerOps(LedgerLoop):
    def __init__(self, browser, command):
        super().__init__(browser)
        self.command = command

    def retrieve_elements(self):
        table_xpath = self.choose_table[self.command["table"]]
        rows = self.browser.get_rows(By.XPATH, table_xpath)
        table_rows = self.loop_through_table(rows)
        return table_rows

    def click_ledger_element(self):
        if self.command["operation"] in ["allocate", "unallocate", "delete"]:
            special_type = self.ledger_row.get("special_type", [])
            exclude = self.command.get("exclude", [])
            for command_type in self.command["type"]:
                if (
                    command_type == self.ledger_row["type"]
                    or command_type in special_type
                ) and (
                    self.ledger_row["type"] not in exclude
                    or special_type not in exclude
                ):
                    self.browser.click_element(self.ledger_row["link"])
                    return True

        elif self.command["operation"] in ["credit"]:
            self.browser.click(By.XPATH, "(.//a[text()='Add Credit'])[last()]")
            return True

    def return_to_ledger(self):
        if self.browser.driver.current_url != self.current_url:
            self.browser.driver.get(self.current_url)

    def check_nsf(self):
        if self.ledger_row.get("special_type"):
            if (
                "bounced_check" in self.ledger_row["special_type"]
                or "system_nsf" in self.ledger_row["special_type"]
            ):
                return True
