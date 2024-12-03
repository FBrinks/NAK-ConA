import os
import sqlite3
import openai
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Hämta API-nyckel och databaskonfigurationer från miljövariabler
api_key = os.getenv("OPENAI_API_KEY")
db_name = os.getenv("DB_NAME", "products")

openai.api_key = api_key

class ProductDescriptionGenerator: # OpenAIHandler for generating product descriptions
    def __init__(self):
        pass

    def generate_product_texts(self, brand, product_name, weight, material, sustainability, dimensions, color, other_info):
        prompt = f"""
        Skriv en produktbeskrivning för följande produkt:

        - Märke: {brand}
        - Produktnamn: {product_name}
        - Vikt: {weight}
        - Material: {material}
        - Hållbarhet: {sustainability}
        - Dimensioner: {dimensions}
        - Färg: {color}
        - Övrig information: {other_info}

        Följ dessa instruktioner:
        1. **Struktur**:
        - Första stycket (Kort text) ska sammanfatta produktens huvudegenskaper. Max 300 tecken.
        - Andra stycket (Long text) ska ge en utförligare beskrivning och inspirera läsaren med exempel på användning. Ge förslag på användningsområde. Undvik subjektiva värdeord såsom Bästa, Snyggaste. Max 600 tecken.
        - Tredje stycket (I korthet) ska lista all tillgänglig fakta för produkten, varje punkt ska vara minst 40 och maximalt 100 tecken. Använd inte kommatecken här.

        2. **Språk och Format**:
        - Återge all information minst en gång.
        - Skriv produktbeskrivningarna på svenska, även om ursprunglig information ges på annat språk.
        - Använd inte apostrofer.
        - Materialnamn, produktnamn samt varumärkesnamn ska alltid inledas med versal och avslutas med gemener. 
        - Lyft fram produkten ur ett hållbarhetsperspektiv, om det uttryckligen finns sån information.

        #### Exempel på Produktbeskrivningar
        Varje Ex. visar hur du kan anpassa en beskrivning för olika typer av produkter:

        Ex. 1. **Friluftsbyxor**: Betona egenskaper som slitstyrka, väderresistens och var fickorna är placerade.
        Ex. 2. **Keps**: Beskriv justerbar passform och material som förbättrar synlighet och komfort samt om den kan regleras i storlek.
        Ex. 3. **Klättersele**: Fokusera på komfort, justerbara funktioner, hållbarhet och säkerhetsaspekter.
        Ex. 4. **Vandringsbyxor för dam**: Framhäv materialets kvaliteter, praktiska design och passform samt fickornas placering.
        Ex. 5. **Teknisk vardagsjacka**: Presentera väderskydd, packbarhet och ventilationsmöjligheter och eventuella fickor samt huvan.
        Ex. 6. **Multifuel kök för friluftsliv**: Understryk pålitlighet, mångsidighet och tillbehör som medföljer samt vilka bränslen som den kan användas med.
        Ex. 7. **Tunneltält**: Detaljera tältets kapacitet, konstruktion och specifika fördelar för olika miljöer.
        Ex. 8. **Vandringskängor **: Beskriv tekniska specifikationer som vattentäthet, material, sulans egenskapar, mellansulans egenskaper, ventilation, användningsområde.
        Ex. 9. **Funktionell jacka för året-runt bruk**: Betona funktioner, på vilka sätt den kan användas, vilka fickor som finns.
        Ex. 10. **Teknisk skaljacka**: Fokusera på dess lättvikt, väderskydd, packbarhet och funktioner samt huvan och om den har fickor.

        ####Slut på instruktioner
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "Du är en AI-assistent specialiserad på att skriva produktbeskrivningar enligt dina instruktioner på svenska."},
                    {"role": "user", "content": prompt}
                ]
            )
            logging.info("Successfully generated product description via OpenAI.")
            product_texts = response.choices[0].message["content"].strip().split("\n\n")
            headline = product_texts[0]
            short_text = product_texts[1]
            long_text = product_texts[2]
            bullet_list = product_texts[3]
            return headline, short_text, long_text, bullet_list
        except Exception as e:
            logging.error(f"Error generating product description: {e}")
            return "", "", "", ""

    def parse_and_generate_texts(self, extracted_text):
        prompt = f"""
        Analysera och generera produktbeskrivningar från följande text:

        {extracted_text}

        Följ dessa instruktioner:
        1. **Struktur**:
        - Första stycket (Kort text) ska sammanfatta produktens huvudegenskaper. Max 300 tecken.
        - Andra stycket (Long text) ska ge en utförligare beskrivning och inspirera läsaren med exempel på användning. Ge förslag på användningsområde. Undvik subjektiva värdeord såsom Bästa, Snyggaste. Max 600 tecken.
        - Tredje stycket (I korthet) ska lista all tillgänglig fakta för produkten, varje punkt ska vara minst 40 och maximalt 100 tecken. Använd inte kommatecken här.

        2. **Språk och Format**:
        - Återge all information minst en gång.
        - Skriv produktbeskrivningarna på svenska, även om ursprunglig information ges på annat språk.
        - Använd inte apostrofer.
        - Materialnamn, produktnamn samt varumärkesnamn ska alltid inledas med versal och avslutas med gemener. 
        - Lyft fram produkten ur ett hållbarhetsperspektiv, om det uttryckligen finns sån information.

        ####Slut på instruktioner
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "Du är en AI-assistent specialiserad på att analysera och generera produktbeskrivningar enligt dina instruktioner på svenska."},
                    {"role": "user", "content": prompt}
                ]
            )
            logging.info("Successfully generated product description via OpenAI.")
            product_texts = response.choices[0].message["content"].strip().split("\n\n")
            headline = product_texts[0]
            short_text = product_texts[1]
            long_text = product_texts[2]
            bullet_list = product_texts[3]
            return headline, short_text, long_text, bullet_list
        except Exception as e:
            logging.error(f"Error generating product description: {e}")
            return "", "", "", ""


class DatabaseQueryHandler: # OpenAIHandler for connecting to the database and fetching product information to generate descriptions
    def __init__(self):
        try:
            self.connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', f'{db_name}.db'))
            logging.info("Database connection established successfully.")
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")
            self.connection = None

    def fetch_product_info(self, keyword):
        """Hämta produktinformation från databasen baserat på ett sökord."""
        if not self.connection:
            logging.error("No database connection available.")
            return None

        query = """
        SELECT *
        FROM products
        WHERE search_term LIKE ?
        LIMIT 1;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (f'%{keyword}%',))
            result = cursor.fetchone()
            if result:
                colnames = [desc[0] for desc in cursor.description] # Get the columnnames
                logging.info(f"Product information fetched for keyword: {keyword}")
                return dict(zip(colnames, result)) # Create a dictionary with columnnames and its info
            else:
                logging.warning(f"No product found for keyword: {keyword}")
                return None
        except Exception as e:
            logging.error(f"Error fetching product information: {e}")
            return None

    def close(self):
        """Stäng databasanslutningen."""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")


class ProductDescriptionFromDatabase: # Main class for coordinating database queries and OpenAI description generation
    def __init__(self):
        self.db_handler = DatabaseQueryHandler()
        self.ai_handler = ProductDescriptionGenerator()

    def generate_product_description_for_keyword(self, keyword):
        product_info = self.db_handler.fetch_product_info(keyword)
        
        if product_info:
            logging.info(f"Product info fetched for keyword '{keyword}': {product_info}")
            # Generate product description via OpenAI
            generated_description = self.ai_handler.generate_product_texts(
                product_info.get("brand", ""),
                product_info.get("product_name", ""),
                product_info.get("weight", ""),
                product_info.get("material", ""),
                product_info.get("sustainability", ""),
                product_info.get("dimensions", ""),
                product_info.get("color", ""),
                product_info.get("other_info", "")
            )
            if generated_description:
                logging.info(f"Product description generated successfully for keyword: {keyword}")
            else:
                logging.error("Failed to generate product description.")
            return generated_description
        else:
            logging.warning(f"No product information found for keyword: {keyword}")
            return None

    def close(self):
        """Stäng alla anslutningar."""
        self.db_handler.close()
        logging.info("ProductDescriptionGenerator closed.")
