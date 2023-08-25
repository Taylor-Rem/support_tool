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
        resolve_ticket_btn = self.webdriver.wait_for_presence_of_element(
            By.XPATH,
            "//button[contains(., 'Change Ticket Status')]",
        )
        self.webdriver.click_element(resolve_ticket_btn)

        resolution_btn = self.webdriver.wait_for_element_clickable(
            By.XPATH,
            f"//button[.//i[contains(@class, 'material-icons') and text()='{icon}']]",
        )
        self.webdriver.click_element(resolution_btn)

        if back:
            back_btn = self.webdriver.wait_for_element_clickable(
                By.XPATH,
                f"//a[.//i[contains(@class, 'material-icons') and text()='{back}']]",
            )
            self.webdriver.click_element(back_btn)
