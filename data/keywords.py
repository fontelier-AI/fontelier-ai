import pandas as pd
import openai
import os

# Load OpenAI API key
def load_api_key():
    try:
        with open('api-key.txt', 'r') as file:
            return file.readline().strip()
    except FileNotFoundError:
        print("API key file not found.")
        return None

openai.api_key = load_api_key()

def extract_typographic_keywords(summary):
    """
    Use GPT-3.5 to extract meaningful keywords optimized for embedding and recommendation.
    Ensure keywords reflect both technical typographic elements and emotional tones.
    """

    if not summary.strip():
        return "No description provided"

    try:
        prompt = (
            f"Extract exactly 5 concise and meaningful keywords or short phrases from the following font description. "
            f"Focus on style, visual elements, design influence, intended use, and emotional tone. "
            f"Use words that align with design contexts such as posters, UI interfaces, and themed projects. "
            f"Avoid mentioning designers, licenses, or updates:\n\n"
            f"{summary}"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "You are a typography expert. Extract 5 meaningful keywords or phrases that capture the font's "
                    "style, design influence, intended use, and emotional tone. Avoid mentioning designers or licenses.")},
                {"role": "user", "content": prompt},
            ],
            max_tokens=60,  # Keep it concise
            temperature=0.5,
        )

        keywords = response.choices[0].message['content'].strip()
        return keywords

    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return "Error in extracting keywords"

def load_existing_keywords(output_file_path):
    """Load existing keywords from the output file to prevent reprocessing."""
    if os.path.exists(output_file_path):
        return pd.read_csv(output_file_path)
    return pd.DataFrame(columns=["Font Name", "Keywords"])

def process_fonts(input_file_path, output_file_path):
    """Process fonts and save keywords to a new CSV file."""
    # Load existing data to avoid duplication
    existing_data = load_existing_keywords(output_file_path)
    existing_fonts = set(existing_data["Font Name"])

    # Load the summarized descriptions
    df = pd.read_csv(input_file_path)
    processed_fonts = []

    for _, row in df.iterrows():
        font_name = row['Font Name']
        if font_name in existing_fonts:
            print(f"Skipping {font_name}, already processed.")
            continue

        summary = row['Summarized Description']
        keywords = extract_typographic_keywords(summary)
        print(f"Processed: {font_name} -> {keywords}")

        processed_fonts.append((font_name, keywords))

    # Append new data to the existing data and save it
    new_data = pd.DataFrame(processed_fonts, columns=["Font Name", "Keywords"])
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    combined_data.to_csv(output_file_path, index=False)

    print(f"Saved keywords to {output_file_path}.")

if __name__ == "__main__":
    input_file_path = "data/summarized_google_fonts_descriptions.csv"
    output_file_path = "data/font_keywords.csv"

    process_fonts(input_file_path, output_file_path)
