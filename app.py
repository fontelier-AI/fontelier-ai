from flask import Flask, request, render_template, redirect, url_for, session
import openai
import numpy as np
import csv

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

app = Flask(__name__)
app.secret_key = 'very-secret-key'

# Store user input and embedding temporarily (in-memory)
user_data = {"embedding": None}

# Load pre-computed font embeddings from CSV
def load_font_embeddings():
    font_data = []
    with open('data/embeddings.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            font_data.append({
                "name": row["Name"],
                "keywords": row["Keywords"],
                "embedding": np.array(eval(row["Embedding"]))
            })
    return font_data

# Remove unwanted characters from markdwown output
def remove_characters(text):
    chars_to_remove = ['"', "'", '-', '*']
    for char in chars_to_remove:
        text = text.replace(char, '')
    return text

# Clean and extract meaning using GPT-3.5
def clean_and_extract_meaning(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at extracting meaning from text. Clean, simplify, and summarize the following user input, focusing on key themes, mood, and use case. Format the final output in 5 key words."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )
        cleaned_input = response.choices[0].message['content'].strip()
        print(f"Cleaned Input: {cleaned_input}")
        return cleaned_input

    except Exception as e:
        print(f"Error in cleaning input: {e}")
        return user_input

# Generate embedding using text-embedding-ada-002
def get_openai_embedding(cleaned_input):
    try:
        response = openai.Embedding.create(
            input=cleaned_input,
            model="text-embedding-ada-002"
        )
        embedding = response['data'][0]['embedding']
        print(f"Generated embedding for input: {cleaned_input}")
        return np.array(embedding)

    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# Calculate cosine similarity between two vectors
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Generate justifications between user's input and the top fonts
def generate_justification(user_input, top_fonts):
    try:
        # Format the top fonts into a readable string
        font_names = ", ".join([font[0] for font in top_fonts])
        # Call GPT-3.5 to generate a justification
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in typography and design. Based on the following user input"
                        "and font recommendations, provide a sentence-long justification of why each of these fonts were chosen. "
                        "The justification should align with the user's description, mood, and use case."
                    )
                },
                {
                    "role": "user",
                    "content": f"User input: {user_input}\nRecommended Fonts: {font_names}"
                }
            ]
            
        )
        # Extract, clean and return the justification
        justification = response.choices[0].message['content'].strip()
        return justification
    except Exception as e:
        print(f"Error generating justification: {e}")
        return "Could not generate a justification at this time."
    
# Route to collect font option input
@app.route('/step1', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        user_data['option'] = request.form.get('option')
        return redirect(url_for('step2'))
    return render_template('step1.html')

# Route to collect heading type input
@app.route('/step2', methods=['GET', 'POST'])
def step2():
    if request.method == 'POST':
        user_data['heading_type'] = request.form.get('heading_type')
        return redirect(url_for('step3'))
    return render_template('step2.html')

# Route to collect description input
@app.route('/step3', methods=['GET', 'POST'])
def step3():
    if request.method == 'POST':
        user_data['description'] = request.form.get('description')
        return redirect(url_for('step4'))
    return render_template('step3.html')

# Route to collect mood input
@app.route('/step4', methods=['GET', 'POST'])
def step4():
    if request.method == 'POST':
        user_data['mood'] = request.form.get('mood')
        return redirect(url_for('result'))
    return render_template('step4.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        # Get updated user input from the form
        user_data['option'] = request.form.get('option', '')
        user_data['heading_type'] = request.form.get('heading_type', '')
        user_data['description'] = request.form.get('description', '')
        user_data['mood'] = request.form.get('mood', '')

    # Combine user input into a single string
    user_input = f"{user_data.get('option', '')} {user_data.get('heading_type', '')} {user_data.get('description', '')} {user_data.get('mood', '')}".strip()

    # Check if embedding is cached, otherwise generate it
    if user_data["embedding"] is None:
        print("Calling OpenAI API to generate embedding.")
        cleaned_input = clean_and_extract_meaning(user_input)
        user_embedding = get_openai_embedding(cleaned_input)

        if user_embedding is None:
            print("Failed to generate embedding.")
            return render_template('result.html', data=user_data, api_result=[
                {"name": "Error", "description": "Failed to generate recommendations.", "similarity": 0.0}
            ])
        user_data["embedding"] = user_embedding
    else:
        user_embedding = user_data["embedding"]
        print("Using cached embedding from memory.")

    # Load font embeddings
    font_data = load_font_embeddings()

    # Calculate cosine similarity for each font
    similarities = [
        (
            font["name"],
            font["keywords"],
            cosine_similarity(user_embedding, font["embedding"])
        )
        for font in font_data
    ]

    # Sort by similarity and select the top 3 fonts
    top_fonts = sorted(similarities, key=lambda x: x[2], reverse=True)[:3]


    # Add a URL to each font in the top 3 recommendations
    top_fonts_with_links = [
          (
            font[0].title(),  # name
            font[1],  # description
            font[2],  # similarity
            f"https://fonts.google.com/specimen/{'+'.join(word.capitalize() for word in font[0].split())}"  # URL with capitalization and space replaced by '+'
        )
        for font in top_fonts
    ]

    # Generate a justification using GPT-3.5
    justification = generate_justification(user_input, top_fonts)
    cleaned_justification = remove_characters(justification)

    # Print top 3 fonts and their URLs to the terminal for debugging
    print("\nTop 3 Recommended Fonts:")
    for font in top_fonts:
        font_name = font[0]
        font_url = f"https://fonts.googleapis.com/css2?family={font_name.replace(' ', '+')}&display=swap"
        print(f"Font: {font_name}, URL: {font_url}")

    # Render the result page with the top 3 fonts
    return render_template('result.html', data=user_data, api_result=top_fonts_with_links, cleaned_justification=cleaned_justification)


# Home route to restart
@app.route('/')
def index():
    user_data["embedding"] = None  # Clear embedding
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
