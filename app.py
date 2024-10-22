from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# To store user data
user_data = {}

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# [User input] Single font / pair
@app.route('/step1', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        option = request.form.get('option')

        # Validate input is not missing
        if not option:
            return redirect(url_for('step1'))
        
        user_data['option'] = option
        return redirect(url_for('step2'))
    return render_template('step1.html')

# [User input] Heading type
@app.route('/step2', methods=['GET', 'POST'])
def step2():
    if request.method == 'POST':
        heading_type = request.form.get('heading_type')

        # Validate input is not missing
        if not heading_type:
            return redirect(url_for('step2'))
        
        user_data['heading_type'] = heading_type
        return redirect(url_for('step3'))
    return render_template('step2.html')

# [User input] Description of what they're looking for
@app.route('/step3', methods=['GET', 'POST'])
def step3():
    if request.method == 'POST':
        description = request.form.get('description')

        # Validate input is not missing
        if not description:
            return redirect(url_for('step3'))
        
        user_data['description'] = description
        return redirect(url_for('step4'))
    return render_template('step3.html')

# [User input] Feelings or mood
@app.route('/step4', methods=['GET', 'POST'])
def step4():
    if request.method == 'POST':
        mood = request.form.get('mood')

        # Validate input is not missing
        if not mood:
            return redirect(url_for('step4'))
        
        user_data['mood'] = mood
        return redirect(url_for('result'))
    return render_template('step4.html')

# Result
@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('result.html', data=user_data)

if __name__ == '__main__':
    app.run(debug=True)
