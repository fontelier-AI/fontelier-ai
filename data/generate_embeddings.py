import openai
import csv
import os

# Load the API key from a file
def load_api_key():
    try:
        with open('api-key.txt', 'r') as file:
            return file.readline().strip()
    except FileNotFoundError:
        print("API key file not found.")
        return None

# Set the OpenAI API key
api_key = load_api_key()
openai.api_key = api_key

# Input and output CSV paths
input_csv = "data/font_keywords.csv"
output_csv = "data/embeddings.csv"

# Load existing embeddings from the output CSV (if it exists)
def load_existing_embeddings(output_csv):
    """Returns a set of font names already processed."""
    if os.path.exists(output_csv):
        with open(output_csv, mode='r') as file:
            reader = csv.DictReader(file)
            return {row["Font Name"] for row in reader}
    return set()

# Function to generate and save embeddings
def generate_and_save_embeddings(input_csv, output_csv):
    """Generate embeddings and append to the CSV."""
    # Load existing fonts to avoid duplicate processing
    existing_fonts = load_existing_embeddings(output_csv)

    # Open input CSV for reading, output CSV for appending
    with open(input_csv, mode='r') as infile, open(output_csv, mode='a', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ["Name", "Keywords", "Embedding"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        # Write the header only if the output CSV is empty or doesn't exist
        if not os.path.exists(output_csv) or os.stat(output_csv).st_size == 0:
            writer.writeheader()

        # Iterate over the input CSV rows
        for row in reader:
            font_name = row["Font Name"]
            keywords = row["Keywords"]

            if font_name in existing_fonts:
                print(f"Skipping {font_name}, already exists in {output_csv}.")
                continue  # Skip existing fonts

            try:
                # Generate embedding using OpenAI API
                response = openai.Embedding.create(
                    input=keywords,
                    model="text-embedding-ada-002"
                )
                embedding = response['data'][0]['embedding']

                # Write the row with embedding to the output CSV
                writer.writerow({
                    "Name": font_name,
                    "Keywords": keywords,
                    "Embedding": embedding
                })
                print(f"Generated embedding for: {font_name}")

            except Exception as e:
                print(f"Error generating embedding for {font_name}: {e}")
                # Skip writing to the CSV on error

    print("Embedding generation completed. Saved to:", output_csv)

# Run the function to generate and save embeddings
generate_and_save_embeddings(input_csv, output_csv)
