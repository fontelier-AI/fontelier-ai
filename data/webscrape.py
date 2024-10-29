import requests
import csv
import time
from bs4 import BeautifulSoup
import os

# List of diverse & popular Google Fonts
FONT_NAMES = [
    "opensans", "roboto", "montserrat", "poppins", "lato",
    "merriweather", "playfairdisplay", "sourcecodepro", "inconsolata",
    "dancingscript", "oswald", "ubuntu", "kanit", "firasans", "nunito",
    "raleway", "abrilfatface", "alegreya", "cabin", "courgette",
    "hind", "ptserif", "manrope", "balsamiqsans", "overpass", 
    "saira", "asap", "crimsonpro", "josefinsans", "teko", 
    "questrial", "jost", "indieflower", "vibes", "anton", 
    "volkhov", "archivo", "satisfy", "lexend", "kalam",
    "signika", "yanonekaffeesatz", "patuaone", "titilliumweb",
    "arvo", "amatic", "hindmadurai", "cormorant", "expletus", 
    "teko", "archivo", "spacegrotesk", "varta", "sora", 
    "ibmplexsans", "ibmplexserif", "adamina",
    "barlow", "bitter", "domine", "grandstander", "heebo", 
    "karla", "literata", "lora", "mate", "neuton", 
    "notoserif", "padauk", "recoleta", "spectral", "vollkorn", 
    "zillaslab", "tinos", "trirong", "prata", "chilanka",
    "athiti", "mukta", "sarabun", "kadwa", "sura", 
    "noto", "baloo", "ibarrarealnova", "faustina", "librefranklin", 
    "bhavnagar", "khand", "thasadith", "yrsa", "fira", 
    "nunito", "rubik", "vazir", "simonetta", "gloock", "inter", 
    "orbitron", "mulish", "limelight", "play", 
    "mada", "ralewaydots", "amiko", "fugazone", "francoisone", 
    "markazitext", "syncopate", "changa", "rufina", "oxanium", 
    "nanumgothic", "tajawal", "majormonodisplay", "exo2", "coda",
    "bagelfatone", "sarina", "chango", "creepster", "notable", 
    "monoton", "zentokyozoo", "ribeye", "danfo", "rye", 
    "ewert", "imperialscript", "rougescript", "tangerine", 
    "leaguescript", "bangers", "hennypennt", "rubikglitch", 
    "delius", "borel", "chewy", "macondo", "caesardressing", 
    "almendra", "schoolbell", "comingsoon", "thegirlnextdoor", 
    "orbitron", "quantico", "michroma", "iceberg", "pinyonscript", 
    "specialelite", "gochihand"
]

# Base URL for the Google Fonts repository
BASE_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl"

CSV_FILE = "data/google_fonts_descriptions.csv"

def load_existing_fonts():
    """Load existing fonts from the CSV file to avoid duplicates."""
    if not os.path.exists(CSV_FILE):
        return set()  # If the file doesn't exist, return an empty set

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        return {row[0].strip().lower() for row in reader}  # Store font names in lowercase for consistency

def fetch_description_file(font_name):
    """Fetch the DESCRIPTION.en_us.html file for a specific font."""
    url = f"{BASE_URL}/{font_name}/DESCRIPTION.en_us.html"
    print(f"Fetching: {url}")
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch description for {font_name}. Status code: {response.status_code}")
        return None

def clean_html(html_content):
    """Remove HTML tags and return plain text."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ").strip()

def save_to_csv(data):
    """Save the extracted font data to a CSV file."""
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Font Name", "Description"])

        for row in data:
            writer.writerow(row)

def main():
    """Main function to fetch and save font descriptions."""
    existing_fonts = load_existing_fonts()  # Load existing fonts from CSV
    font_data = []

    for font_name in FONT_NAMES:
        if font_name.lower() in existing_fonts:
            print(f"Skipping {font_name}, already processed.")
            continue

        html_content = fetch_description_file(font_name)
        if html_content:
            description = clean_html(html_content)
            font_data.append((font_name, description))
            print(f"Font: {font_name}\nDescription: {description[:100]}...\n")

        time.sleep(1)  # Avoid overwhelming the server

    if font_data:
        save_to_csv(font_data)
        print(f"Saved {len(font_data)} new fonts to {CSV_FILE}.")
    else:
        print("No new fonts to add.")

if __name__ == "__main__":
    main()
