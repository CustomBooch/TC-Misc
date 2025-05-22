# Tariff Description Extractor

This tool scrapes commodity (HS code) descriptions from the UK Trade Tariff site and saves them to a CSV.

## 🔧 How It Works

- You select a CSV file with HS codes (first column).
- It scrapes the UK government tariff site for each HS code.
- Saves the descriptors into `commodity_descriptors_output.csv`.

## 🖥️ Requirements

Install dependencies:

```bash
pip install -r requirements.txt
