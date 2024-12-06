import pandas as pd
import re
from utils import clean_searchresults_from_filesearches


def normalize_text(text):
    """Normalize text by converting to lowercase and removing special characters."""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"\s+", " ", text)  # Replace multiple spaces with a single space
    text = re.sub(r"[^\w\s]", "", text)  # Remove special characters
    return text.strip()


def search_excel(df, search_term):
    try:
        print(
            f"search_excel: Processing DataFrame. Rows: {df.shape[0]}, Columns: {df.shape[1]}"
        )

        # Convert all columns to string
        df_str = df.astype(str)

        # Fix: Apply normalize_text to all cells in the DataFrame
        df_str = df_str.apply(lambda x: x.map(normalize_text))

        search_term_result = []
        search_terms_not_found = []

        # Normalize search term
        normalized_search_term = normalize_text(search_term)

        for index, row in df_str.iterrows():
            # Filter out empty values and join row values into a single string
            row_values = filter(None, row.values)
            # Join all row values into a single string for the search
            row_str = " ".join(row_values)  # Filter out empty or None values here
            if re.search(r"\b" + re.escape(normalized_search_term) + r"\b", row_str):
                # Append non-empty row values as a list
                non_empty_values = [value for value in row.values if value.strip()]
                # Clean the search results from file searches
                cleaned_values = clean_searchresults_from_filesearches(non_empty_values)
                search_term_result.append(cleaned_values)

        if not search_term_result:
            search_terms_not_found.append(search_term)
            return {
                "search_term_result": [],
                "keywords_not_found": search_terms_not_found,
                "search_interrupted": True,  # New flag to signal interruption
            }

        return {
            "search_term_result": search_term_result,
            "keywords_not_found": search_terms_not_found,
            "search_interrupted": False,
        }

    except Exception as e:
        print(f"search_excel: Error processing DataFrame: {e}")
        return {
            "search_term_result": [],
            "keywords_not_found": [search_term],
            "search_interrupted": True,
        }
