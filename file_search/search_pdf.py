import pdfplumber
import pytesseract
from PIL import Image
import fitz
import logging

# Set the logging level for every library and everything else to WARNING
logging.getLogger("pdfplumber").setLevel(logging.WARNING)
logging.getLogger("fitz").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("pytesseract").setLevel(logging.WARNING)
logging.getLogger("pdf2image").setLevel(logging.WARNING)
logging.getLogger("pdf2image").propagate = False


# Function to clean text and remove duplicates
def function_clean_text(text):
    seen = set()
    filtered_lines = []
    for line in text.splitlines():
        clean_line = line.strip()
        if clean_line and clean_line not in seen:
            filtered_lines.append(clean_line)
            seen.add(clean_line)
    return "\n".join(filtered_lines)


def search_pdf_advanced(pdf, doc, search_term):
    print("search_pdf_advanced function started.")
    if not isinstance(search_term, list):
        search_term = [search_term]
    print(f"search_pdf_advanced: Searching for search terms: {search_term}")

    extracted_data = []
    search_terms_not_found = {}
    search_interrupted = False

    try:
        print(f"search_pdf_advanced: Processing PDF with {len(pdf.pages)} pages")

        for page_num, page in enumerate(pdf.pages):
            print(f"search_pdf_advanced: Processing page {page_num + 1}")
            found_text = ""
            missing_terms = []

            for term in search_term:
                term = str(term).strip().lower()
                term_found = False

                # Extract text using different methods
                text_sources = {
                    "pdfplumber": lambda: page.extract_text(),
                    "pytesseract": lambda: pytesseract.image_to_string(
                        page.to_image().original
                    ),
                    "pymupdf": lambda: doc.load_page(page_num).get_text("text"),
                }

                for source_name, extract_func in text_sources.items():
                    try:
                        text = extract_func()
                        if text and term in text.lower():
                            found_text += f"{source_name}:\n{text}\n\n"
                            term_found = True
                    except Exception as e:
                        print(f"{source_name} error on page {page_num + 1}: {e}")

                if not term_found:
                    missing_terms.append(term)

            if found_text:
                print(
                    f"search_pdf_advanced: Found match for '{term}' on page {page_num + 1}"
                )
                extracted_data.append(
                    {
                        "page_num": page_num + 1,
                        "combined_text": function_clean_text(found_text),
                    }
                )

            if missing_terms:
                search_terms_not_found[page_num + 1] = missing_terms
                search_interrupted = True

        print("search_pdf_advanced: PDF processing complete")
        return {
            "extracted_data": extracted_data,
            "keywords_not_found": search_terms_not_found,
            "search_interrupted": search_interrupted,
        }

    except Exception as e:
        print(f"search_pdf_advanced: Error processing PDF - {str(e)}")
        return {
            "extracted_data": [],
            "keywords_not_found": {1: search_term},
            "search_interrupted": True,
        }


def process_combined_results(extracted_data):
    print("process_combined_results function started.")
    """Process the extracted data and combine it into a structured format."""
    full_extracted_search_results = ""

    # Loop through the extracted data and make sure each item is a dictionary
    for result in extracted_data:
        if (
            isinstance(result, dict)
            and "page_num" in result
            and "combined_text" in result
        ):
            # Safely access the dictionary elements
            full_extracted_search_results += f"--- Page {result['page_num']} ---\n"
            full_extracted_search_results += result["combined_text"] + "\n"
        else:
            # If the result is not in the expected format, log an error and continue
            print(f"Unexpected result format: {result}")

    print("process_combined_results function ended.")
    return full_extracted_search_results
