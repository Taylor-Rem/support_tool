import pandas as pd
from datetime import datetime
import os
import json
import re
import fitz


class OSBase:
    def __init__(self, report):
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.day = now.day
        self.username = "taylorremund"
        self.root_path = (
            f"/Users/{self.username}/Desktop/Reports/{self.year}/{self.month}"
        )
        self.report = report
        self.reports_path = f"{self.root_path}/{self.day}/{report}"
        self.json_path = f"{self.root_path}/json_reports/{report}"

        self.reports = [
            "zero_report",
            "double_report",
            "redstar_report",
            "moveout_report",
        ]


class CsvOperations(OSBase):
    def retrieve_csv_info(self):
        df = pd.read_csv(self.reports_path)
        properties = df.filter(like="Property Name").values.flatten().tolist()
        units = df.filter(like="Space Number").values.flatten().tolist()
        residents = (
            df.filter(like="Resident Name")
            .applymap(lambda x: x.split(",")[0] if isinstance(x, str) else x)
            .values.flatten()
            .tolist()
        )

        return properties, units, residents

    def get_url_columns(self):
        df = pd.read_csv(self.reports_path)
        return df.filter(like="URL").values.flatten().tolist()


class PdfOperations(OSBase):
    def retrieve_pdf_info(self):
        pdf_text = []
        numbers = []
        with fitz.open(self.reports_path) as pdf:
            for page_number in range(pdf.page_count):
                page = pdf.load_page(page_number)
                page_text, _ = self.extract_text_and_links(page)

                # Extract property name and unit number using regular expressions
                matches = re.findall(r"([\w\s]+)\s+(\d+\.\d+)", page_text)
                if matches:
                    pdf_text.extend(match[0].split("\n")[-1] for match in matches)
                    numbers.extend(match[1] for match in matches)

        properties = pdf_text[0::2]
        units = numbers[0::2]
        residents = pdf_text[1::2]
        return properties, units, residents

    def extract_text_and_links(self, page):
        text = page.get_text()
        links = []

        for link in page.get_links():
            if link["kind"] == 1:  # 1 represents URI links
                link_url = link["uri"]
                links.append(link_url)

        return text, links


class JsonOperations(OSBase):
    def write_json(self, data):
        try:
            with open(self.json_path, "w") as file:
                json.dump(data, file)
        except Exception as e:
            print(e)

    def retrieve_json(self):
        try:
            with open(self.json_path, "r") as file:
                json_string = file.read()
            data = json.loads(json_string)
            return data
        except:
            return []

    def delete_json(self):
        if os.path.exists(self.json_path):
            os.remove(self.json_path)


class OSInteract(CsvOperations, PdfOperations, JsonOperations):
    def create_folders(self):
        for report in self.reports:
            report_path = os.path.join(f"{self.root_path}/{self.day}", report)
            if not os.path.exists(report_path):
                os.makedirs(report_path)
        if not os.path.exists(self.json_path):
            os.makedirs(self.json_path)

    def retrieve_file(self):
        file_name = os.listdir(self.reports_path)[-1]
        self.file_path = os.path.join(self.reports_path, file_name)

    def retrieve_report_info(self):
        if self.reports_path.endswith(".csv"):
            return self.retrieve_csv_info()
        elif self.reports_path.endswith(".pdf"):
            return self.retrieve_pdf_info()


class OSMaster(OSInteract):
    def __init__(self, report=None):
        if report is not None:
            super().__init__(report)
