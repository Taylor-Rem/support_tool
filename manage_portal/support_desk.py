from selenium.webdriver.common.by import By


class SupportDeskFunctions:
    def __init__(self, browser):
        self.browser = browser
        self.status_icons = {
            "done_outline": "resolved",
            "scatter_plot": "in_progress",
            "error": "unresolved",
        }

    def return_status(self, cells):
        result = cells[0].text
        return self.status_icons[result]


class SupportDeskLoop(SupportDeskFunctions):
    def __init__(self, browser):
        super().__init__(browser)

    def support_desk_loop(self):
        support_desk_info = []
        rows = self.browser.get_rows(By.TAG_NAME, "tbody")
        rows_length = int(len(rows))
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            link = cells[3].find_element(By.TAG_NAME, "a")
            status = self.return_status(cells)
            support_desk_info.append(
                {"length": rows_length, "link": link, "status": status}
            )
        return support_desk_info


class SupportDeskOperations(SupportDeskLoop):
    def __init__(self, browser):
        super().__init__(browser)

    def go_to_supportdesk(self):
        if self.browser.driver.current_url != self.browser.supportdesk_url:
            self.browser.driver.get(self.browser.supportdesk_url)
