from docx import Document

def search_word(doc, search_term):
    print("search_word function started.")
    extracted_data = []
    search_terms_not_found = {}
    
    if not isinstance(search_term, list):
        search_term = [search_term]
    print(f"search_word: Searching for search terms: {search_term}")
    
    for page_num, para in enumerate(doc.paragraphs):
        missing_terms = []
        found_text = ""
        
        for term in search_term:
            term = str(term).lower()
            if term in para.text.lower():
                found_text = para.text
            else:
                missing_terms.append(term)
        
        if found_text:
            extracted_data.append({
                "page_num": page_num + 1,
                "combined_text": found_text
            })
            print(f"search_word: Found match in paragraph {page_num + 1}")
        
        if missing_terms:
            search_terms_not_found[page_num + 1] = missing_terms
    
    print("search_word: Starting table search")
    for table_num, table in enumerate(doc.tables):
        missing_terms = []
        found_text = ""
        
        for row in table.rows:
            for cell in row.cells:
                for term in search_term:
                    term = str(term).lower()
                    if term in cell.text.lower():
                        found_text += cell.text + "\n"
                    else:
                        missing_terms.append(term)
        
        if found_text:
            extracted_data.append({
                "page_num": f"table_{table_num + 1}",
                "combined_text": found_text.strip()
            })
            print(f"search_word: Found match in table {table_num + 1}")
        
        if missing_terms:
            search_terms_not_found[f"table_{table_num + 1}"] = list(set(missing_terms))

    print("search_word function ended.")
    return {
        "extracted_data": extracted_data,
        "keywords_not_found": search_terms_not_found
    }