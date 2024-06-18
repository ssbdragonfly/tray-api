from flask import Flask, render_template, request, redirect, url_for, flash
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import os
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

MODEL_PATH = 'website/food11_model.h5'
model = load_model(MODEL_PATH)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class_labels = ['Bread', 'Dairy Product', 'Dessert', 'Egg', 'Fried food', 'Meat', 'Noodles-Pasta', 'Rice', 'Seafood', 'Soup', 'Vegetable-Fruit']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/<model_name>', methods=['GET', 'POST'])
def upload_image(model_name):
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
            
            # Load and preprocess image for prediction
            image = load_img(filepath, target_size=(224, 224))
            image = img_to_array(image) / 255.0
            image = np.expand_dims(image, axis=0)
            
            # Make prediction
            prediction = model.predict(image)
            predicted_class = np.argmax(prediction, axis=1)
            predicted_label = class_labels[predicted_class[0]]
            print(f"Prediction: {predicted_label}")
            
            # Save prediction to history
            save_history(file.filename, predicted_label, model_name)

            # Redirect to result page
            return redirect(url_for('prediction_result', model_name=model_name, prediction=predicted_label))

    return render_template('api.html', prediction=None, model_name=model_name)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

def save_history(filename, prediction, model_name):
    history_file = 'uploads/history.json'
    if not os.path.exists(history_file):
        history = []
    else:
        with open(history_file, 'r') as f:
            history = json.load(f)
    
    history.append({'filename': filename, 'prediction': prediction, 'model_name': model_name})
    
    with open(history_file, 'w') as f:
        json.dump(history, f)
    
    print(f"Saved to history.json: {filename}, {prediction}, {model_name}")

@app.route('/history')
def history():
    history_file = 'uploads/history.json'
    if not os.path.exists(history_file):
        history = []
    else:
        with open(history_file, 'r') as f:
            history = json.load(f)
    return render_template('history.html', history=history)

@app.route('/result/<model_name>/<prediction>')
def prediction_result(model_name, prediction):
    return render_template('result.html', model_name=model_name, prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)
