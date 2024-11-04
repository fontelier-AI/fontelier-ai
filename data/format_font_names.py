import pandas as pd
import re
import requests

# Load the CSV file
input_path = 'data/embeddings.csv'
output_path = 'data/embeddings_updated.csv'
df = pd.read_csv(input_path)

# List to store fonts that couldn't be validated
unsuccessful_fonts = []

# Common words in font names for better splitting guesses
common_words = ["bold", "light", "script", "serif", "sans", "display", "mono", "condensed", "fat", "thin", "italic", "hand", "one"]

# Function to split and capitalize font names
def split_and_capitalize(name):
    # Split using common words and regex patterns, then capitalize each word
    for word in common_words:
        name = re.sub(f'({word})', r' \1', name)
    return ' '.join(word.capitalize() for word in name.split())

# Function to check if the Google Fonts link works
def check_google_fonts_link(name):
    formatted_font = name.replace(" ", "+")
    url = f"https://fonts.googleapis.com/css?family={formatted_font}&display=swap"
    response = requests.head(url)
    return response.status_code == 200

# Apply the split and capitalize function, then check link validity
def format_and_validate_font_name(name):
    formatted_name = split_and_capitalize(name)
    
    # Check if the link works; if not, log as unsuccessful
    if check_google_fonts_link(formatted_name):
        return formatted_name
    else:
        unsuccessful_fonts.append(name)
        return name  # Return original name if the link check fails

# Update the "Name" column with validated font names
df['Name'] = df['Name'].apply(format_and_validate_font_name)

# Save the updated DataFrame
df.to_csv(output_path, index=False)
print(f"Updated CSV saved to {output_path}")

# Output list of unsuccessful fonts for review
if unsuccessful_fonts:
    print("The following fonts were unsuccessful and may need manual review:")
    print(unsuccessful_fonts)
