from main_tools.operations import Operations, ResmapNavMaster
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd
from datetime import datetime, date
from selenium.webdriver.support.ui import Select


class RandomOps(Operations):
    def __init__(self, browser, operations_list, thread_helper=None):
        super().__init__(browser, thread_helper)
        self.operations_list = operations_list
        self.support_desk_link = "https://residentmap.kmcmh.com/#/support_desk"

    # def random_operation(self):
    #     lot_numbers = [
    #         1,
    #         7,
    #         17,
    #         28,
    #         30,
    #         36,
    #         44,
    #         52,
    #         58,
    #         60,
    #         69,
    #         70,
    #         82,
    #         87,
    #         96,
    #         99,
    #         100,
    #         101,
    #         104,
    #         123,
    #         125,
    #         128,
    #         136,
    #         141,
    #         150,
    #         166,
    #         184,
    #         207,
    #         208,
    #         218,
    #         242,
    #         255,
    #         268,
    #         270,
    #         279,
    #         285,
    #         310,
    #         315,
    #         324,
    #         333,
    #         338,
    #         349,
    #         368,
    #         371,
    #         375,
    #         384,
    #         386,
    #         387,
    #         388,
    #         390,
    #     ]
    #     decimal_values = [
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.03,
    #         0.01,
    #         0.01,
    #         0.04,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.04,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.06,
    #         0.04,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.03,
    #         0.01,
    #         0.01,
    #         0.06,
    #         0.01,
    #         0.04,
    #         0.04,
    #         0.01,
    #         0.01,
    #         0.01,
    #         0.04,
    #         0.01,
    #         0.03,
    #         0.01,
    #     ]

    #     for unit, decimal in zip(lot_numbers, decimal_values):
    #         if self.thread_helper and self.thread_helper._is_cancelled:
    #             break
    #     self.browser.send_keys(By.NAME, "search_input", unit, True)
    #     self.browser.click(By.XPATH, "(//a[text()='Ledger'])[last()]")

    def random_operation(self):
        pets_on_lease_dict = {0: 0, 5: 1, 10: 2, 15: 3, 20: 4}
        df = pd.read_csv(
            "/Users/taylorremund/Desktop/Misc/FV Aurora Potential Pet Fee Credits - Sheet1.csv"
        )
        units = df.filter(like="Unit").values.flatten().tolist()
        lease_amounts = df.filter(like="Amount on Lease").values.flatten().tolist()
        units_to_refund = []

        for unit, lease_amount in zip(units, lease_amounts):
            try:
                if int(lease_amount) == 0:
                    units_to_refund.append(unit)
            except:
                units_to_refund.append(unit)
        print(units_to_refund)

    #     for url, lease_amount in zip(urls, lease_amounts):
    #         if self.thread_helper and self.thread_helper._is_cancelled:
    #             break

    #         self.browser.open_program(url)

    #         try:
    #             pets_on_lease = pets_on_lease_dict[int(lease_amount)]
    #         except:
    #             pets_on_lease = 0
    #         have_pet_fee = False if pets_on_lease == 0 else True

    #         move_in_date_element = self.browser.find_element(
    #             By.XPATH,
    #             "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody/tr[5]/td[2]",
    #         ).text.strip()
    #         date_pattern = r"\d{2}/\d{2}/\d{4}"
    #         move_in_date = re.search(date_pattern, move_in_date_element).group()
    #         start_date = datetime.strptime(move_in_date, "%m/%d/%Y").date()
    #         reference_date = date(2022, 7, 1)
    #         is_new_lease = start_date > reference_date

    #         pet_fee = 35 if is_new_lease else 5
    #         ledger_pet_fee = pet_fee * pets_on_lease

    #         rows = self.browser.get_rows(
    #             By.XPATH,
    #             "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[last()-4]/tbody/tr[2]/td/table/tbody",
    #         )
    #         idx = 0
    #         while True:
    #             if idx >= len(rows):
    #                 break
    #             row = rows[idx]
    #             if self.browser.skip_row(row, "th3"):
    #                 idx += 1
    #                 continue
    #             cells = row.find_elements(By.TAG_NAME, "td")
    #             # transaction_date = cells[0].text.strip().lower()
    #             transaction = cells[2]
    #             # amount_value = self.browser.get_number_from_inner_html(
    #             #     cells[3].text.strip()
    #             # )
    #             label = transaction.text.strip().lower()
    #             transaction_link = transaction.find_element(By.CSS_SELECTOR, "a.a5")

    #             if "pet fee" in label:
    #                 transaction_link.click()
    #                 if not have_pet_fee:
    #                     self.delete_pet_fee()
    #                     break
    #                 else:
    #                     self.change_fee_amount(ledger_pet_fee)
    #                     self.run_command("Allocate Payments", "current")
    #                     break
    #             idx += 1
    #         if (is_new_lease) or (not have_pet_fee):
    #             continue
    #         self.browser.click(
    #             By.XPATH,
    #             "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[1]/tbody/tr/td[4]/a",
    #         )
    #         self.browser.click(
    #             By.XPATH,
    #             "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[6]/tbody/tr[1]/td/table/tbody/tr/td[3]/a",
    #         )
    #         select_element = self.browser.find_element(
    #             By.XPATH, "//select[@name='ttid']"
    #         )
    #         select = Select(select_element)
    #         select.select_by_visible_text("Pet Fee")

    #         self.browser.send_keys(
    #             By.XPATH,
    #             "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/table/tbody/tr[2]/td/table/tbody/tr[5]/td[2]/input",
    #             ledger_pet_fee,
    #             True,
    #         )

    # def change_fee_amount(self, fee):
    #     amount_input = self.browser.find_element(
    #         By.XPATH,
    #         "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/input",
    #     )
    #     self.browser.driver.execute_script("arguments[0].focus();", amount_input)
    #     self.browser.driver.execute_script(f"arguments[0].value = {fee};", amount_input)

    #     comment_box = self.browser.find_element(
    #         By.XPATH,
    #         "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/table/tbody/tr[2]/td/table/tbody/tr[5]/td[2]/textarea",
    #     )
    #     self.browser.send_keys_to_element(comment_box, "corrected amount")
    #     self.browser.click(
    #         By.XPATH,
    #         "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/input[4]",
    #     )

    # def delete_pet_fee(self):
    #     delete_btn = self.browser.find_element(
    #         By.XPATH,
    #         "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/input[5]",
    #     )
    #     self.browser.click_element(delete_btn)
    #     self.browser.accept_alert()


# def random_operation(self)
#     self.browser.open_program(
#         "https://kingsley.residentmap.com/forward.php?propid=62&script=residentadmin.php"
#     )
#     for number in numbers:
#         if self.thread_helper and self.thread_helper._is_cancelled:
#             break
#         self.browser.send_keys(By.NAME, "search_input", number, True)
#         self.browser.click(By.XPATH, "(//a[text()='Ledger'])[last()]")
#         command = self.operations_list.ledger_ops_dict["delete"]["Delete Late Fees"]
#         command["table"] = "current"
#         self.init_operation(command)

# def get_ledger_info(self):
#     rows = self.browser.get_rows(
#         By.XPATH,
#         "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[last()-4]/tbody/tr[2]/td/table/tbody",
#     )
#     idx = 0
#     while True:
#         if idx >= len(rows):
#             break
#         row = rows[idx]
#         if self.browser.skip_row(row, "th3"):
#             idx += 1
#             continue
#         cells = row.find_elements(By.TAG_NAME, "td")
#         transaction = cells[2]
#         amount_value = self.browser.get_number_from_inner_html(
#             cells[3].text.strip()
#         )
#         label = transaction.text.strip()
#         transaction_link = transaction.find_element(By.CSS_SELECTOR, "a.a5")

# """
# MONTLY CONCESSIONS
# """

# def random_operation(self):
#     command = {"operation": "credit", "tools": ["ledger", "credit"]}
#     command["comment"] = "Monthly Charge Concessions"
#     command["table"] = "bottom"
#     df = pd.read_csv(
#         "/Users/taylorremund/Desktop/Data/Monthly Credits_Concessions - Sheet1.csv"
#     )
#     urls = df.filter(like="URL").values.flatten().tolist()
#     selection = df.filter(like="Credit or Concession").values.flatten().tolist()
#     units = df.filter(like="Unit").values.flatten().tolist()
#     idx = 0
#     while True:
#         if idx >= len(urls):
#             break
#         self.browser.open_program(urls[idx])
#         command["selection"] = selection[idx]
#         self.init_operation(command)
#         idx += 1

# """
# PROPERTY FEES REMOVAL
# """
# def random_operation(self):
#     while True:
#         try:
#             self.browser.click(
#                 By.XPATH, "//i[@class='material-icons' and text()='check_box']"
#             )
#         except:
#             pass
#         self.browser.click(
#             By.XPATH,
#             "//button[@type='submit' and normalize-space(text())='save and next']",
#         )

# """
# DOUBLE CHARGE REMOVAL
# """

# def random_operation(self):
#     for i in range(24432, 24762):
#         if self.thread_helper and self.thread_helper._is_cancelled:
#             break
#         url = f"https://kingsley.residentmap.com/forward.php?propid=61&script=space.php&cmd=viewspace&spaceid={i}"
#         self.browser.open_program(url)
#         try:
#             self.browser.click(
#                 By.XPATH,
#                 "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[2]/tbody/tr/td[3]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/a[3]",
#             )
#         except:
#             continue
#         self.run_command("Allocate Payments", "current")
# table = self.browser.find_element(
#     By.XPATH,
#     "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[last()-4]/tbody/tr[2]/td/table/tbody",
# )
# rows = table.find_elements(By.XPATH, ".//tr")
# idx = 0
# while True:
#     if idx >= len(rows):
#         break
#     row = rows[idx]
#     if self.browser.skip_row(row, "th3"):
#         idx += 1
#         continue
#     cells = row.find_elements(By.TAG_NAME, "td")
#     transaction = cells[2]
#     amount_value = self.browser.get_number_from_inner_html(
#         cells[3].text.strip()
#     )
#     label = transaction.text.strip()
#     transaction_link = transaction.find_element(By.CSS_SELECTOR, "a.a5")
#     if "water" in label.lower() or "sewer" in label.lower():
#         self.browser.click_element(transaction_link)
#         water_amount = 16.01
#         sewer_amount = 28.63
#         amount_input = self.browser.find_element(
#             By.XPATH,
#             "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/input",
#         )
#         if "water" in label.lower():
#             self.browser.driver.execute_script(
#                 "arguments[0].focus();", amount_input
#             )
#             self.browser.driver.execute_script(
#                 f"arguments[0].value = {water_amount};", amount_input
#             )
#         if "sewer" in label.lower():
#             self.browser.driver.execute_script(
#                 "arguments[0].focus();", amount_input
#             )
#             self.browser.driver.execute_script(
#                 f"arguments[0].value = {sewer_amount};", amount_input
#             )
#         comment_value = self.browser.find_element(
#             By.XPATH,
#             "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/table/tbody/tr[2]/td/table/tbody/tr[5]/td[2]/textarea",
#         )
#         self.browser.send_keys_to_element(
#             comment_value, "Correcting amount"
#         )
#         self.browser.click(
#             By.XPATH,
#             "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/form/input[4]",
#         )
#         table = self.browser.find_element(
#             By.XPATH,
#             "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[last()-4]/tbody/tr[2]/td/table/tbody",
#         )
#         rows = table.find_elements(By.XPATH, ".//tr")
#     idx += 1

# for row in rows:
#     if self.browser.skip_row(row, "th3"):
#         continue
#     cells = row.find_elements(By.TAG_NAME, "td")
#     end_date = cells[4].text.strip()
#     if "/" not in end_date:
#         delete_element = row.find_element(
#             By.XPATH, ".//a[contains(text(), 'Delete')]"
#         )
#         self.browser.click_element(delete_element)
#         alert = self.browser.driver.switch_to.alert
#         alert.accept()
