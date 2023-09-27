from selenium.webdriver.common.by import By


class SupportDeskLoop:
    def __init__(self, browser):
        self.browser = browser

    def support_desk_retrieve_rows_length(self):
        return len(self.browser.get_rows(By.TAG_NAME, "tbody"))

    def support_desk_retrieve_url(self, idx):
        rows = self.browser.get_rows(By.TAG_NAME, "tbody")
        row = rows[idx]
        cells = row.find_elements(By.TAG_NAME, "td")
        link = cells[3].find_element(By.TAG_NAME, "a")
        return link


class SupportDeskOperations(SupportDeskLoop):
    def __init__(self, browser):
        super().__init__(browser)
