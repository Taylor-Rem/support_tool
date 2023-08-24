from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class ManageportalScrape:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def scrape_ticket(self):
        try:
            property = self.webdriver.return_element_html(
                By.XPATH,
                "//tr/td[@class='text-xs-right' and contains(text(), 'Property')]/following-sibling::td[@class='text-xs-left']/strong/a",
            )
        except NoSuchElementException:
            property = None

        try:
            unit = self.webdriver.return_element_html(
                By.XPATH,
                "//tr/td[@class='text-xs-right' and contains(text(), 'Space')]/following-sibling::td[@class='text-xs-left']/a/strong",
            )
        except NoSuchElementException:
            unit = None
        try:
            resident = self.webdriver.return_element_html(
                By.XPATH,
                "//tr/td[@class='text-xs-right' and contains(text(), 'Resident')]/following-sibling::td[@class='text-xs-left']/a/strong",
            )
        except NoSuchElementException:
            resident = None
        return property, unit, resident


class ManageportalMaster(ManageportalScrape):
    def __init__(self, webdriver):
        super().__init__(webdriver)

    def resolve_ticket(self, icon, back):
        self.webdriver.click(By.XPATH, "//button[contains(., 'Change Ticket Status')]")

        self.click_button("button", icon)

        if back:
            self.click_button("a", back)

    def click_button(self, element_type, icon):
        xpath = f"//{element_type}[.//i[contains(@class, 'material-icons') and text()='{icon}']]"
        self.webdriver.wait_for_element_clickable(By.XPATH, xpath)
        self.webdriver.click(By.XPATH, xpath)
