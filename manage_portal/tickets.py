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

        unit_element = self.browser.find_element(
            By.XPATH,
            "//tr/td[@class='text-xs-right' and contains(text(), 'Space')]/following-sibling::td[@class='text-xs-left']/a",
        )

        if unit_element is not None:
            unit_text = unit_element.find_element(By.XPATH, "./strong")
            unit_number = unit_text.get_attribute("innerHTML").strip()
            href_value = unit_element.get_attribute("href")
            space_id = href_value.split("/spaces/")[-1].split("/")[0]
        else:
            unit_number = self.interpretation.extract_unit_number(title + description)
            space_id = None

        resident_element = self.browser.find_element(
            By.XPATH,
            "//tr/td[@class='text-xs-right' and contains(text(), 'Resident')]/following-sibling::td[@class='text-xs-left']/a",
        )
        if resident_element is not None:
            resident_text_rough = resident_element.find_element(By.XPATH, "./strong")
            resident_text = resident_text_rough.get_attribute("textContent").strip()
            href_value = resident_element.get_attribute("href")
            print(href_value)
            rsid = href_value.split("/resident_spaces/")[-1].split("/")[0]
            print(rsid)
        else:
            resident_text = self.interpretation.extract_resident_name(title + description)
            rsid = None

        return {
            "title": title,
            "description": description,
            "property": property,
            "unit": unit_number,
            "space_id": space_id,
            "resident": resident_text,
            "rsid": rsid
        }


class TicketOperations(TicketScrape):
    def __init__(self, browser, command):
        super().__init__(browser)
        self.command = command
        self.icons = {
            "resolve": "done_outline",
            "in_progress": "scatter_plot",
            "unresolve": "error",
            "Back": "arrow_back",
        }

    def change_ticket_status(self):
        resolve_ticket_btn = self.browser.wait_for_presence_of_element(
            By.XPATH, "//button[contains(., 'Change Ticket Status')]"
        )
        self.browser.click_element(resolve_ticket_btn)

        resolution_btn = self.browser.wait_for_element_clickable(
            By.XPATH,
            f"//button[.//i[contains(@class, 'material-icons') and text()='{self.icons[self.command['selection']]}']]",
        )
        self.browser.click_element(resolution_btn)

        back = self.command["selection"] == "in_progress" or (
            self.command["selection"] == "unresolve"
            and self.command["type"] == "manual"
        )

        if back:
            back_btn = self.browser.wait_for_element_clickable(
                By.XPATH,
                f"//a[.//i[contains(@class, 'material-icons') and text()='arrow_back']]",
            )
            self.browser.click_element(back_btn)
