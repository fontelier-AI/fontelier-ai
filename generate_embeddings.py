import requests
from bs4 import BeautifulSoup
import csv
import openai
import time

# Load the API key
def load_api_key():
    try:
        with open('api-key.txt', 'r') as file:
            return file.readline().strip()
    except FileNotFoundError:
        print("API key file not found.")
        return None

api_key = load_api_key()
openai.api_key = api_key

# Base URLs for scraping
GOOGLE_FONTS_URL = "https://fonts.google.com/?sort=popularity"
FONT_URL_TEMPLATE = "https://fonts.google.com/specimen/{}"

# Function to get the top 200 font links from Google Fonts
def get_top_fonts():
    response = requests.get(GOOGLE_FONTS_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the font links (limited to 200)
    font_links = soup.find_all('a', class_='font-name', limit=200)
    return [link.text.strip() for link in font_links]

# Function to get author and description from a specific font's page
def get_font_details(font_name):
    font_name_url = font_name.replace(" ", "+")
    url = FONT_URL_TEMPLATE.format(font_name_url)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract author and description
    try:
        author = soup.find('a', class_='about__designer-link').text.strip()
    except AttributeError:
        author = "Unknown"

    try:
        description = soup.find('div', class_='about__content').text.strip()
    except AttributeError:
        description = "No description available."

    return author, description

# Function to clean and extract key points from the description using OpenAI
def clean_description(description):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Extract 5 key points from the following font description to summarize its tone, feel, and main characteristics."
                },
                {
                    "role": "user",
                    "content": description
                }
            ]
        )
        summary = response.choices[0].message['content'].strip()
        return summary

    except Exception as e:
        print(f"Error cleaning description: {e}")
        return description  # Fallback to original description

# Function to scrape and save font data to CSV
def scrape_and_save_fonts():
    font_data = []

    # Get the top 200 fonts
    fonts = get_top_fonts()
    print(f"Found {len(fonts)} fonts.")

    # Scrape each font's details
    for font_name in fonts:
        print(f"Scraping details for: {font_name}")
        author, description = get_font_details(font_name)

        # Clean the description using OpenAI
        cleaned_description = clean_description(description)

        # Append to data list
        font_data.append({
            "Name": font_name,
            "Author": author,
            "Description": cleaned_description
        })

        # Sleep to avoid overwhelming the server
        time.sleep(1)

    # Save the data to a CSV file
    with open('google_fonts.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Author", "Description"])
        writer.writeheader()
        writer.writerows(font_data)

    print("Data saved to google_fonts.csv")

# Run the scraper
if __name__ == "__main__":
    scrape_and_save_fonts()
