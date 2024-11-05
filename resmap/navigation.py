from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from general_tools.general_info import GeneralInfo


class ResmapNavScrape:
    def __init__(self, browser, info):
        self.browser = browser
        self.general_info = GeneralInfo()
        if info:
            self.info = info
        else:
            self.info = {}
            self.info["resident"] = None
        self.property_link = "https://kingsley.residentmap.com/forward.php?propid="
        self.space_link = "&script=space.php&cmd=viewspace&spaceid="
        self.ledger_link = "&script=residentadmin.php&cmd=statusbar&rsid="

    def retrieve_ledger_element(self):
        return self.browser.find_element(By.XPATH, "(//a[text()='Ledger'])[last()]")

    def retrieve_resident_element(self):
        if self.info["resident"] == None:
            return True
        try:
            resident_element = self.browser.find_element(
                By.XPATH, f".//a[contains(text(), '{self.info['resident']}')]"
            )
            return resident_element
        except:
            return None

    def retrieve_unit_element(self):
        return self.browser.find_element(
            By.XPATH, f".//a[contains(text(), '{self.info['unit']}')]"
        )

    def retrieve_former_element(self):
        return self.browser.find_element(
            By.XPATH, "//td[text()='List Former Residents']/following-sibling::td/a"
        )


class ResmapNav(ResmapNavScrape):
    def __init__(self, browser, info):
        super().__init__(browser, info)

    def nav_to_selection(self):
        if self.command["selection"] == "unit":
            if self.info["space_id"] is not None:
                self.browser.launch_operation(f"{self.property_link}{self.general_info.prop_ids[self.info['property']]}{self.space_link}{self.info['space_id']}")
                return
        if self.command["selection"] == "ledger":
            if self.info["rsid"] is not None:
                ledger_url = f"{self.property_link}{self.general_info.prop_ids[self.info['property']]}{self.ledger_link}{self.info['rsid']}"
                print(ledger_url)
                self.browser.launch_operation(ledger_url)
                return
            else:
                self.nav_to_unit()
                self.open_ledger()
        if self.command["selection"] == "resident":
            self.nav_to_unit()
            self.open_resident()
            return

    def nav_to_unit(self):
        if self.info["space_id"] is not None:
            self.browser.launch_operation(f"{self.property_link}{self.general_info.prop_ids[self.info['property']]}{self.space_link}{self.info['space_id']}")
        else:
            try:
                self.browser.launch_operation(f"{self.property_link}{self.general_info.prop_ids[self.info['property']]}&script=space.php")
                self.browser.send_keys(By.NAME, "search_input", self.info["unit"] + Keys.ENTER)
            except:
                return
            try:
                self.browser.click_element(self.retrieve_unit_element())
            except NoSuchElementException:
                self.search_former_unit()
                self.browser.click_element(self.retrieve_unit_element())

    def open_ledger(self):
        if self.retrieve_resident_element():
            self.browser.click_element(self.retrieve_ledger_element())
        else:
            self.open_former_ledger()

    def open_former_ledger(self):
        self.browser.click_element(self.retrieve_former_element())
        self.browser.click_element(self.retrieve_ledger_element())

    def open_resident(self):
        try:
            self.browser.click_element(self.retrieve_resident_element())
        except:
            self.browser.click_element(self.retrieve_former_element())
            self.browser.click_element(self.retrieve_resident_element())

    def nav_to_monthly_charges(self):
        self.browser.click(By.XPATH, ".//a[text()='Monthly Charges/Credits']")

    def nav_to_resident_fees(self):
        self.nav_to_monthly_charges()
        self.browser.click(By.XPATH, ".//a[text()='Add Resident Fee']")

    def nav_to_unit_fees(self):
        self.nav_to_monthly_charges()
        self.browser.click(By.XPATH, ".//a[text()='Modify Unit Fees']")

    def search_former_unit(self):
        self.browser.click(By.ID, "former2")
        self.browser.send_keys(By.NAME, "spacenum", self.info["unit"], True)
