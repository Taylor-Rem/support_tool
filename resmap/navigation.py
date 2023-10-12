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
        self.property_link = "https://kingsley.residentmap.com/forward.php?propid="
        self.rest_of_link = "&script=residentadmin.php&cmd=statusbar&rsid="

    def retrieve_ledger_element(self):
        return self.browser.find_element(By.XPATH, "(//a[text()='Ledger'])[last()]")

    def retrieve_resident_element(self):
        return self.browser.find_element(
            By.XPATH, f".//a[contains(text(), '{self.info['resident']}')]"
        )

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

    def open_property(self):
        property_url = f"{self.property_link}{self.general_info.prop_ids[self.info['property']]}{self.rest_of_link}"
        self.browser.launch_operation(property_url)

    def nav_to_unit(self):
        self.open_property()
        if self.info["unit"] is None:
            return
        self.browser.send_keys(By.NAME, "search_input", self.info["unit"] + Keys.ENTER)
        try:
            self.browser.click_element(self.retrieve_unit_element())
        except NoSuchElementException:
            self.search_former_unit()
            self.browser.click_element(self.retrieve_unit_element())

    def open_ledger(self):
        if self.retrieve_resident_element():
            self.browser.click_element(self.retrieve_ledger_element())
        else:
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
