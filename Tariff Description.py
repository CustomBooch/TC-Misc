import customtkinter as ctk
import tkinter.filedialog as fd
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class CommodityApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Commodity Descriptor Extractor")
        self.geometry("600x400")

        self.label = ctk.CTkLabel(self, text="Select CSV File with HS Codes")
        self.label.pack(pady=10)

        self.select_button = ctk.CTkButton(self, text="Select File", command=self.select_file)
        self.select_button.pack(pady=5)

        self.start_button = ctk.CTkButton(self, text="Start Processing", command=self.start_processing)
        self.start_button.pack(pady=5)

        self.status_text = ctk.CTkTextbox(self, height=200, width=550)
        self.status_text.pack(pady=10)

        self.codes = []
        self.output_path = "commodity_descriptors_output.csv"

    def select_file(self):
        file_path = fd.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = pd.read_csv(file_path)
            self.codes = df.iloc[:, 0].astype(str).tolist()
            self.status_text.insert("end", f"Loaded {len(self.codes)} HS codes.\n")

    def start_processing(self):
        if not self.codes:
            self.status_text.insert("end", "Please load a CSV file first.\n")
            return

        self.status_text.insert("end", "Starting threaded scraping...\n")
        self.update()

        def fetch_descriptors(hs_code):
            if len(hs_code) == 8:
                hs_code += "00"
            try:
                url = f"https://www.trade-tariff.service.gov.uk/commodities/{hs_code}?day=20&month=5&year=2025"
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                descriptors = [d.get_text(strip=True) for d in soup.select(".commodity-ancestors__descriptor")]
                return hs_code, descriptors
            except Exception as e:
                return hs_code, [f"Error: {e}"]

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_descriptors, code): code for code in self.codes}
            for future in as_completed(futures):
                hs_code, descriptors = future.result()
                results.append({"HS Code": hs_code, "Descriptors": "; ".join(descriptors)})
                self.status_text.insert("end", f"Processed {hs_code}\n")
                self.update()

        df_out = pd.DataFrame(results)
        df_out.to_csv(self.output_path, index=False)
        self.status_text.insert("end", f"\nDone. Output saved to {self.output_path}\n")
        self.update()

if __name__ == "__main__":
    app = CommodityApp()
    app.mainloop()
