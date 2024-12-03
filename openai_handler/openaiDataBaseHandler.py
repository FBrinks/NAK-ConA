import os
import sqlite3
import openai
from dotenv import load_dotenv
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Imports from other files in my project
from utils import clean_searchresults_from_filesearches

load_dotenv('.env')

# Fetch the OpenAI API Key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI client setup
openai.api_key = api_key

# Database path
db_path = "products.db"

class ProductAnalysis:
    def __init__(self):
        self.brand = ""
        self.product_name = ""
        self.product_no = ""
        self.weight = ""
        self.material = ""
        self.dimensions = ""
        self.color = ""
        self.sustainability = ""
        self.other_info = ""
        self.headline = ""
        self.short_text = ""
        self.long_text = ""
        self.bullet_points = []

class OpenAIAnalyzer:
    def __init__(self):
        self.preprocess_search_term_result = None
        self.truncated_search_term_result = None

    def analyze_text(self, search_term_result, model="gpt-4o-2024-08-06"):
        print(f"OpenAIAnalyzer.analyze_text: Analyzing {search_term_result}")
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Analyze the product text and extract information in this format:\n"
                            "BRAND: [extract brand]\n"
                            "PRODUCT NAME: [extract name]\n"
                            "PRODUCT NUMBER: [extract number]\n"
                            "WEIGHT: [extract weight]\n"
                            "MATERIALS: [extract materials]\n"
                            "DIMENSIONS: [extract dimensions]\n"
                            "COLOR: [extract color]\n"
                            "SUSTAINABILITY: [extract sustainability info]\n"
                            "OTHER INFO: [extract other relevant details]\n"
                            "---MARKETING CONTENT---\n"
                            "HEADLINE: [create SEO title in Swedish, max 75 chars]\n"
                            "SHORT TEXT: [create short description in Swedish, max 300 chars]\n"
                            "LONG TEXT: [create detailed description in Swedish, max 900 chars]\n"
                            "BULLET POINTS [in Swedish]:\n"
                            "- [key feature 1]\n"
                            "- [key feature 2]\n"
                            "..."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this product:\n\n{search_term_result}"
                    }
                ],
                max_tokens=2000
            )

            analysis = ProductAnalysis()
            content = response.choices[0].message["content"].strip()
            
            # Parse the response into structured data
            current_section = ""
            bullet_points = []
            
            for line in content.split('\n'):
                line = line.strip()
                if line.endswith(':'):
                    current_section = line[:-1].upper()
                elif line.startswith('- '):
                    bullet_points.append(line[2:])
                elif ': ' in line:
                    key, value = line.split(': ', 1)
                    key = key.upper()
                    if key == 'BRAND': analysis.brand = value
                    elif key == 'PRODUCT NAME': analysis.product_name = value
                    elif key == 'PRODUCT NUMBER': analysis.product_no = value
                    elif key == 'WEIGHT': analysis.weight = value
                    elif key == 'MATERIALS': analysis.material = value
                    elif key == 'DIMENSIONS': analysis.dimensions = value
                    elif key == 'COLOR': analysis.color = value
                    elif key == 'SUSTAINABILITY': analysis.sustainability = value
                    elif key == 'OTHER INFO': analysis.other_info = value
                    elif key == 'HEADLINE': analysis.headline = value
                    elif key == 'SHORT TEXT': analysis.short_text = value
                    elif key == 'LONG TEXT': analysis.long_text = value

            analysis.bullet_points = bullet_points
            return analysis

        except Exception as e:
            logging.error(f"OpenAIAnalyzer.analyze_text: Error analyzing text: {e}")
            return ProductAnalysis()

class DatabaseHandler:
    def __init__(self, db_path='products.db'):
        self.db_path = db_path

    def update_database(self, search_term, analysis):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if the search_term already exists
            cursor.execute("SELECT COUNT(*) FROM products WHERE search_term = ?", (search_term,))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Update existing record
                cursor.execute("""
                    UPDATE products SET brand = ?, product_name = ?, product_no = ?, weight = ?, 
                    material = ?, dimensions = ?, color = ?, sustainability = ?, other_info = ?, 
                    headline = ?, short_text = ?, long_text = ?, bullet_points = ?
                    WHERE search_term = ?
                """, (analysis.brand, analysis.product_name, analysis.product_no, analysis.weight, 
                      analysis.material, analysis.dimensions, analysis.color, analysis.sustainability, 
                      analysis.other_info, analysis.headline, analysis.short_text, analysis.long_text, 
                      '\n'.join(analysis.bullet_points), search_term))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO products (search_term, brand, product_name, product_no, weight, 
                    material, dimensions, color, sustainability, other_info, headline, 
                    short_text, long_text, bullet_points)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (search_term, analysis.brand, analysis.product_name, analysis.product_no, 
                      analysis.weight, analysis.material, analysis.dimensions, analysis.color, 
                      analysis.sustainability, analysis.other_info, analysis.headline, 
                      analysis.short_text, analysis.long_text, '\n'.join(analysis.bullet_points)))
            
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database update failed: {e}")
        finally:
            conn.close()

class DatabaseSearch:
    def __init__(self, db_path='products.db'):
        self.db_path = db_path

    def search_database(self, search_term):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM products WHERE search_term = ?
            """, (search_term,))
            rows = cursor.fetchall()
            if rows:
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
                return results
            else:
                return []
        except sqlite3.Error as e:
            logging.error(f"Database search failed: {e}")
            return []
        finally:
            conn.close()

    def fetch_data(self, search_terms):
        data_from_databaseSearch = []
        for search_term in search_terms:
            search_results = self.search_database(search_term.strip())
            if search_results:
                print(f"Database search-results found for {search_term.strip()}")
                data_from_databaseSearch.extend(search_results)
        return data_from_databaseSearch




