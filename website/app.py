from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import os
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

MODEL_PATH = os.getenv('MODEL_PATH', 'website/food11_model.h5')
model = load_model(MODEL_PATH)

UPLOAD_FOLDER = os.path.join('website', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class_labels = ['Bread', 'Dairy Product', 'Dessert', 'Egg', 'Fried food', 'Meat', 'Noodles-Pasta', 'Rice', 'Seafood', 'Soup', 'Vegetable-Fruit']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/<model_name>', methods=['GET', 'POST'])
def upload_image(model_name):
    try:
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file:
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)
                print(f"Saved file: {filepath}")

<<<<<<< HEAD
                predicted_label = 'Bread' 

                save_history(file.filename, predicted_label, model_name)

                return redirect(url_for('prediction_result', model_name=model_name, prediction=predicted_label, filename=file.filename))

        return render_template('upload.html', prediction=None, model_name=model_name)
    except Exception as e:
        print(f"Error during image upload and prediction: {e}")
        flash('An error occurred during processing. Please try again.')
        return redirect(request.url)
=======
                # hardcoded the thing because the ml is too large to put into github
                predicted_label = 'Bread'  

                save_history(file.filename, predicted_label, model_name)
>>>>>>> c2164cb (fixed the github issues, this is the commit for updating history and results, as well as removing babel because it broke everything)

                return redirect(url_for('prediction_result', model_name=model_name, prediction=predicted_label, filename=file.filename))

        return render_template('upload.html', prediction=None, model_name=model_name)
    except Exception as e:
        print(f"Error during image upload and prediction: {e}")
        flash('An error occurred during processing. Please try again.')
        return redirect(request.url)

        
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

def save_history(filename, prediction, model_name):
    try:
        history_file = os.path.join(UPLOAD_FOLDER, 'history.json')
        if not os.path.exists(history_file):
            history = []
        else:
            with open(history_file, 'r') as f:
                history = json.load(f)

        history.append({'filename': filename, 'prediction': prediction, 'model_name': model_name})

        with open(history_file, 'w') as f:
            json.dump(history, f)

        print(f"Saved to history.json: {filename}, {prediction}, {model_name}")
    except Exception as e:
        print(f"Error saving history: {e}")

@app.route('/history')
def history():
    try:
        history_file = os.path.join(UPLOAD_FOLDER, 'history.json')
        if not os.path.exists(history_file):
            history = []
        else:
            with open(history_file, 'r') as f:
                history = json.load(f)
        return render_template('history.html', history=history)
    except Exception as e:
        print(f"Error loading history: {e}")
        flash('An error occurred while loading history.')
        return render_template('history.html', history=[])

@app.route('/result/<model_name>/<prediction>/<filename>')
def prediction_result(model_name, prediction, filename):
    return render_template('result.html', model_name=model_name, prediction=prediction, filename=filename)

@app.route('/routes')
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = f"[{arg}]"
        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {url}")
        output.append(line)
    return '<br>'.join(sorted(output))

if __name__ == '__main__':
    app.run(debug=True)
