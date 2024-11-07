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
session_data = {
    "sorted_fonts": None,
    "top_font_history": [],
    "next_font_index": 3,  # Tracks the next font to use in sorted_fonts after the initial top 3
    "justification": {},
    "bin": {}
}

# Load pre-computed font embeddings from CSV
def load_font_embeddings():
    font_data = []
    with open('data/embeddings_updated.csv', mode='r') as file:
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
        return np.array(embedding)

    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# Calculate cosine similarity between two vectors
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def generate_top_fonts(user_embedding):
    # Load font embeddings and compute cosine similarity
    font_data = load_font_embeddings()
    similarities = [
        (font["name"], font["keywords"], cosine_similarity(user_embedding, font["embedding"]))
        for font in font_data
    ]
    # Sort fonts based on similarity score
    sorted_fonts = sorted(similarities, key=lambda x: x[2], reverse=True)
    session_data["sorted_fonts"] = sorted_fonts  # Save sorted list for reference
    
    # Set initial top 3 fonts and save to history
    top_fonts = sorted_fonts[:3]
    session_data["top_font_history"].append(list(top_fonts))  # Save initial top 3
    print(f"Initial Top Fonts: {top_fonts}")
    return top_fonts
   

# Generate justifications between user's input and the top fonts
def generate_justification(user_input, top_fonts):
    font_names = ", ".join([font[0] for font in top_fonts])
    cache_key = f"{user_input}_{font_names}"
    
    # Check cache for justification
    if cache_key in session_data["justification"]:
        print("Using cached justification.")
        return session_data["justification"][cache_key]
    
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
                        "and font recommendations, provide a justification for why each of these fonts"
                        "were chosen in once sentence for each font."
                        "The justification should align with the user's description, mood, and use case."
                    )
                },
                {
                    "role": "user",
                    "content": f"User input: {user_input}\nRecommended Fonts: {font_names}"
                }
            ]
            
        )
        # Extract, clean, cache and return the justification    
        justification = response.choices[0].message['content'].strip()
        session_data["justification"][cache_key] = justification  # Cache the justification
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

@app.route('/remove_font/<int:index>', methods=['POST'])
def remove_font(index):
    if session_data["sorted_fonts"] and "next_font_index" in session_data:
        # Save the deleted font to bin
        deleted_font = user_data["top_fonts"][index]
        cache_key = f"{deleted_font}"
        session_data["bin"][cache_key] = deleted_font  # Cache the justification

        # Remove the disliked font from top_fonts
        user_data["top_fonts"].pop(index)

        # Find and add the next font in sorted_fonts that’s not already in top_fonts
        while session_data["next_font_index"] < len(session_data["sorted_fonts"]):
            next_font = session_data["sorted_fonts"][session_data["next_font_index"]]
            session_data["next_font_index"] += 1  # Move to next font in sorted_fonts

            if next_font not in user_data["top_fonts"]:
                user_data["top_fonts"].insert(index, next_font)
                user_data["top_fonts"].sort(key=lambda x: x[2], reverse=True)  # Keep list in descending similarity
                break

        # Save the updated top_fonts to history
        session_data["top_font_history"].append(list(user_data["top_fonts"]))

        print(f"Updated Top Fonts: {[font[0] for font in user_data['top_fonts']]}")


    return redirect(url_for('result'))


# Main route to generate results
@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        user_data['option'] = request.form.get('option', '')
        user_data['heading_type'] = request.form.get('heading_type', '')
        user_data['description'] = request.form.get('description', '')
        user_data['mood'] = request.form.get('mood', '')
        action = request.form.get('action', '')

        # Clear the cached embedding only if the regenerate button was clicked
        if action == 'regenerate':
            print("Regenerate action detected. Clearing cached embedding.")
            user_data["embedding"] = None

    user_input = f"{user_data.get('option', '')} {user_data.get('heading_type', '')} {user_data.get('description', '')} {user_data.get('mood', '')}".strip()

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
        user_data["top_fonts"] = generate_top_fonts(user_embedding)
    else:
        user_embedding = user_data["embedding"]
        print("Using cached embedding from memory.")

    # Prepare fonts for display with links
    top_fonts_with_links = [
        (
            font[0].title(),
            font[1],
            font[2],
            f"https://fonts.google.com/specimen/{'+'.join(word.capitalize() for word in font[0].split())}"
        )
        for font in user_data["top_fonts"]
    ]

    # Generate justification for the fonts
    justification = generate_justification(user_input, user_data["top_fonts"])
    cleaned_justification = remove_characters(justification)

    # Get deleted fonts (bin) from session_data
    deleted_fonts = list(session_data.get("bin", {}).values())

    return render_template('result.html', data=user_data, api_result=top_fonts_with_links, cleaned_justification=cleaned_justification, deleted_fonts=deleted_fonts)


# Home route to restart
@app.route('/')
def index():
    user_data["embedding"] = None  # Clear embedding
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
