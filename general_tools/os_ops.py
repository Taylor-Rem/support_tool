import pandas as pd
from datetime import datetime
import os
import json
import re
import fitz


class OSBase:
    def __init__(self):
        now = datetime.now()
        year = now.year
        month = now.month
        self.day = now.day
        username = "taylorremund"
        self.root_path = f"/Users/{username}/Desktop/Reports/{year}/{month}/"


class OSInteract(OSBase):
    def create_folders(self):
        reports = [
            "zero_report",
            "double_report",
            "redstar_report",
            "moveout_report",
        ]
        for report in reports:
            report_path = f"{self.root_path}/{self.day}/{report}"
            if not os.path.exists(report_path):
                os.makedirs(report_path)


class ReportsBase(OSBase):
    def __init__(self, report):
        super().__init__()
        self.reports_path = f"{self.root_path}/{self.day}/{report}"
        self.full_json_path = f"{self.root_path}/json_reports/{report}"
        self.full_report_path = self.retrieve_file()

        self.csv_ops = CsvOperations(self.full_report_path)
        self.pdf_ops = PdfOperations(self.full_report_path)
        self.json_ops = JsonOperations(self.full_json_path)

    def retrieve_file(self):
        try:
            file_name = os.listdir(self.reports_path)[-1]
            return f"{self.reports_path}/{file_name}"
        except:
            return None

    def retrieve_report_info(self):
        if self.full_report_path.endswith(".csv"):
            return self.csv_ops.retrieve_csv_info()
        elif self.full_report_path.endswith(".pdf"):
            return self.pdf_ops.retrieve_pdf_info()
        else:
            print("Report not found")
            return None, None, None


class CsvOperations:
    def __init__(self, file_path):
        self.file_path = file_path

    def retrieve_csv_info(self):
        df = pd.read_csv(self.file_path)
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
        df = pd.read_csv(self.file_path)
        return df.filter(like="URL").values.flatten().tolist()


class PdfOperations:
    def __init__(self, file_path):
        self.file_path = file_path

    def retrieve_pdf_info(self):
        pdf_text = []
        numbers = []
        with fitz.open(self.file_path) as pdf:
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


class JsonOperations:
    def __init__(self, file_path):
        self.file_path = file_path

    def write_json(self, data):
        try:
            with open(self.file_path, "w") as file:
                json.dump(data, file)
        except Exception as e:
            print(e)

    def retrieve_json(self):
        try:
            with open(self.file_path, "r") as file:
                json_string = file.read()
            data = json.loads(json_string)
            return data
        except:
            return []

    def delete_json(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
