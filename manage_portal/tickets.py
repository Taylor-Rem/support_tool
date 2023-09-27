from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from general_tools.interpretation import Interpretation


class TicketScrape:
    def __init__(self, browser):
        self.browser = browser
        self.interpretation = Interpretation()

    def scrape_ticket(self):
        title = (
            self.browser.wait_for_presence_of_element(
                By.XPATH,
                '//*[contains(@class, "pull-left") and contains(@class, "text-xs-left") and contains(@class, "blue--text")]',
            )
            .get_attribute("innerHTML")
            .strip()
        )

        description = (
            self.browser.wait_for_presence_of_element(
                By.XPATH,
                "//tr/td[@class='text-xs-right' and contains(text(), 'Description')]/following-sibling::td[@class='text-xs-left']",
            )
            .get_attribute("innerHTML")
            .strip()
        )

        property = (
            self.browser.wait_for_presence_of_element(
                By.XPATH,
                "//tr/td[@class='text-xs-right' and contains(text(), 'Property')]/following-sibling::td[@class='text-xs-left']/strong/a",
            )
            .get_attribute("innerHTML")
            .strip()
        )

        unit = self.browser.find_element(
            By.XPATH,
            "//tr/td[@class='text-xs-right' and contains(text(), 'Space')]/following-sibling::td[@class='text-xs-left']/a/strong",
        )
        if unit is not None:
            unit = unit.get_attribute("innerHTML").strip()
        else:
            unit = self.interpretation.extract_unit_number(title + description)

        resident = self.browser.find_element(
            By.XPATH,
            "//tr/td[@class='text-xs-right' and contains(text(), 'Resident')]/following-sibling::td[@class='text-xs-left']/a/strong",
        )
        if resident is not None:
            resident = resident.get_attribute("innerHTML").strip()
        else:
            resident = self.interpretation.extract_resident_name(title + description)

        return [title, description, property, unit, resident]


class TicketOperations(TicketScrape):
    def __init__(self, browser):
        super().__init__(browser)
        self.icons = {
            "Resolve": "done_outline",
            "In Progress": "scatter_plot",
            "Unresolve": "error",
            "Back": "arrow_back",
        }

    def change_ticket_status(self, selection):
        resolve_ticket_btn = self.browser.wait_for_presence_of_element(
            By.XPATH, "//button[contains(., 'Change Ticket Status')]"
        )
        self.browser.click_element(resolve_ticket_btn)

        resolution_btn = self.browser.wait_for_element_clickable(
            By.XPATH,
            f"//button[.//i[contains(@class, 'material-icons') and text()='{self.icons[selection]}']]",
        )
        self.browser.click_element(resolution_btn)

        back = selection == "In Progress" or selection == "Unresolve"

        if back:
            back_btn = self.browser.wait_for_element_clickable(
                By.XPATH,
                f"//a[.//i[contains(@class, 'material-icons') and text()='arrow_back']]",
            )
            self.browser.click_element(back_btn)
