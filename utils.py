# utils.py

import pandas as pd
from PyQt5.QtWidgets import QMessageBox


class SaveToFile:
    def save_search_to_excel(self, data, file_path):
        try:
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            QMessageBox.information(None, "Success", "Data saved successfully!")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save data: {e}")


def clean_searchresults_from_filesearches(search_results):
    cleaned_results = []
    seen = set()
    for result in search_results:
        if result not in seen:
            cleaned_results.append(result)
            seen.add(result)
    return cleaned_results
