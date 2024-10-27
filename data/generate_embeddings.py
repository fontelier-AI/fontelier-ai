import openai
import csv
import numpy as np

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

# Input and output CSV paths
input_csv = "Font _database_ - Sheet1.csv"
output_csv = "font_embeddings_with_vectors.csv"

# Generate embeddings for each font in the CSV
def generate_and_save_embeddings(input_csv, output_csv):
    with open(input_csv, mode='r') as infile, open(output_csv, mode='w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["Embedding"]  # Add 'Embedding' column
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for row in reader:
            description = row["Description"]

            try:
                # Generate embedding from OpenAI API
                response = openai.Embedding.create(
                    input=description,
                    model="text-embedding-ada-002"
                )
                embedding = response['data'][0]['embedding']
                
                # Add embedding to the row
                row["Embedding"] = embedding
                print(f"Generated embedding for: {row['Name']}")

            except Exception as e:
                print(f"Error generating embedding for {row['Name']}: {e}")
                row["Embedding"] = "Error"

            # Write the updated row with embedding
            writer.writerow(row)

# Run the embedding generation and save to CSV
generate_and_save_embeddings(input_csv, output_csv)

print("Embedding generation completed. Saved to:", output_csv)