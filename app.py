from flask import Flask, request, render_template, redirect, url_for
import openai
import json
import os
import numpy as np
import csv
from dotenv import load_dotenv

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

# Store user input data
user_data = {}

# Load pre-computed font embeddings from CSV
def load_font_embeddings():
    font_data = []
    with open('font_embeddings_with_vectors.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            font_data.append({
                "name": row["Name"],
                "description": row["Description"],
                "embedding": np.array(eval(row["Embedding"]))
            })
    return font_data

# Get embedding from OpenAI's API for user input
def get_openai_embedding(user_input):
    try:
        response = openai.Embedding.create(
            input=user_input,
            model="text-embedding-ada-002"
        )
        embedding = response['data'][0]['embedding']
        return np.array(embedding)  # Convert to numpy array for cosine similarity
    except Exception as e:
        print(f"Failed to generate embedding: {e}")
        return None

# Calculate cosine similarity between two vectors
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

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

# Route to generate and display recommendations
# @app.route('/result', methods=['GET', 'POST'])
# def result():
#     if request.method == 'POST':
#         return redirect(url_for('index'))

#     # Combine user input into a single string
#     user_input = f"{user_data['option']} {user_data['heading_type']} {user_data['description']} {user_data['mood']}"

#     # Generate embedding from OpenAI
#     user_embedding = get_openai_embedding(user_input)

#     if user_embedding is None:
#         return render_template('result.html', data=user_data, api_result=[{
#             "name": "Error", 
#             "description": "Failed to generate recommendations."
#         }])

#     # Load font embeddings
#     font_data = load_font_embeddings()

#     # Calculate cosine similarity for each font
#     similarities = [
#         (font["name"], font["description"], cosine_similarity(user_embedding, font["embedding"]))
#         for font in font_data
#     ]

#     # Sort by similarity and select the top 3 fonts
#     top_fonts = sorted(similarities, key=lambda x: x[2], reverse=True)[:3]

#     # Render the result page with the top 3 fonts
#     return render_template('result.html', data=user_data, api_result=top_fonts)

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        return redirect(url_for('index'))

    # Combine user input into a single string
    user_input = f"{user_data['option']} {user_data['heading_type']} {user_data['description']} {user_data['mood']}"

    # Generate embedding from OpenAI
    user_embedding = get_openai_embedding(user_input)

    if user_embedding is None:
        return render_template('result.html', data=user_data, api_result=[
            {"name": "Error", "description": "Failed to generate recommendations.", "similarity": 0.0}
        ])

    # Load font embeddings
    font_data = load_font_embeddings()

    # Calculate cosine similarity for each font
    similarities = [
        (
            font["name"],
            font["description"],
            cosine_similarity(user_embedding, font["embedding"])
        )
        for font in font_data
    ]

    # Sort by similarity and select the top 3 fonts
    top_fonts = sorted(similarities, key=lambda x: x[2], reverse=True)[:3]

    # Render the result page with the top 3 fonts
    return render_template('result.html', data=user_data, api_result=top_fonts)


# Home route to restart
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
