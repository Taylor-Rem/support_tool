from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchWindowException,
    ElementNotInteractableException,
)
from selenium.webdriver.common.action_chains import ActionChains
import re
from config import username, password
from bs4 import BeautifulSoup


class WebDriverBase:
    _instance = None

    def __init__(self):
        if not WebDriverBase._instance:
            WebDriverBase._instance = self.setup_webdriver()

        self.driver = WebDriverBase._instance
        self.wait = WebDriverWait(self.driver, 10)
        self.primary_tab = None

    def setup_webdriver(self):
        service = Service()
        options = Options()
        return webdriver.Chrome(service=service, options=options)

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            WebDriverBase._instance = None


class WebElementOperations(WebDriverBase):
    def find_element(self, by, value):
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            return None

    def find_elements(self, by, value):
        try:
            return self.driver.find_elements(by, value)
        except NoSuchElementException:
            return []

    def send_keys(self, by, value, keys, enter=False):
        element = self.find_element(by, value)
        if element:
            self.send_keys_to_element(element, keys, enter)

    def send_keys_to_element(self, element, keys, enter=False):
        try:
            element.clear()
            element.send_keys(keys)
            if enter:
                element.send_keys(Keys.ENTER)
        except ElementNotInteractableException:
            print("Error: Element is not interactable.")

    def click(self, by, value):
        element = self.find_element(by, value)
        if element:
            self.click_element(element)
        else:
            raise NoSuchElementException

    def click_element(self, element):
        try:
            if self.is_element_clickable(element):
                self.scroll_to_element(element)
                element.click()
        except (ElementNotInteractableException, NoSuchElementException) as e:
            print(f"Error: {e}")

    def is_element_clickable(self, element):
        is_clickable = element.is_displayed() and element.is_enabled()
        return element and is_clickable

    def scroll_to_element(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()

    def return_element_html(self, by, value):
        try:
            element = self.driver.find_element(by, value)
            return element.get_attribute("innerHTML").strip()
        except NoSuchElementException:
            return None

    def return_last_element(self, name):
        elements = self.find_elements(
            By.XPATH, f"//*[self::a or self::button][contains(., '{name}')]"
        )
        return elements[-1] if elements else None

    def element_exists(self, by, value):
        return bool(self.find_element(by, value))

    def get_number_from_inner_html(self, HTML):
        # Check for values in the format: ($ 13.81)
        match = re.search(r"\(\$ ([\d,]+\.?\d*)\)", HTML)

        # If not found, check for values in the format: $ 803.88
        if not match:
            match = re.search(r"\$ ([\d,]+\.?\d*)", HTML)

        if match:
            value_str = match.group(1)
            value_str_cleaned = value_str.replace(",", "")
            return float(value_str_cleaned)
        else:
            print("Value not found")
            return None




class WebUtilityOperations(WebDriverBase):
    def wait_for_presence_of_element(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def wait_for_element_clickable(self, by, value):
        return self.wait.until(EC.element_to_be_clickable((by, value)))

    def extract_float_from_string(self, text):
        match = re.search(r"\$\s*([\d\.]+)", text)
        if match:
            return float(match.group(1))
        return None

    def check_current_url(self, url):
        return self.driver.current_url == url

    def new_tab(self):
        self.driver.execute_script("window.open('about:blank', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def switch_to_primary_tab(self):
        if self.primary_tab is None:
            self.primary_tab = self.driver.window_handles[0]
        else:
            try:
                current_tab = self.driver.current_window_handle
                if current_tab != self.primary_tab:
                    self.driver.close()
            except NoSuchWindowException:
                pass
        self.driver.switch_to.window(self.primary_tab)

    def login(self, username, password):
        try:
            self.send_keys(By.NAME, "username", username)
            self.send_keys(By.NAME, "password", password, True)
        except NoSuchElementException:
            pass

    def navigate_to(self, site, login_required=False, username="", password=""):
        self.driver.get(site)
        if login_required:
            self.login(username, password)

    def navigate_back_if_not(self, desired_url):
        if not self.check_current_url(desired_url):
            self.driver.back()

    def open_program(self, site):
        self.driver.get(site)
        self.login(username, password)


class WebdriverResmapOperations(WebDriverBase):
    def skip_row(self, row, class_name):
        return row.find("td", class_=class_name) is not None

    def define_table(self, by, value):
        table_elements = self.driver.find_elements(by, value)
        table = [element.get_attribute("outerHTML") for element in table_elements]
        return table

    def get_rows(self, table):
        all_rows = []  # Initialize an empty list to collect all rows
        for table_html in table:
            soup = BeautifulSoup(table_html, "html.parser")
            rows = soup.find_all("tr")
            all_rows.extend(rows)  # Add rows to the list
        return all_rows  # Return the list of all rows


class WebdriverOperations(
    WebElementOperations, WebUtilityOperations, WebdriverResmapOperations
):
    def __init__(self):
        super(WebdriverOperations, self).__init__()
        self.res_map_url = "https://kingsley.residentmap.com/index.php"
        self.manage_portal_url = "https://residentmap.kmcmh.com/#/support_desk"
