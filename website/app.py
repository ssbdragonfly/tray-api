from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import json
import requests
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')
UPLOAD_FOLDER = os.path.join('website', 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class_labels = ['Bread', 'Dairy Product', 'Dessert', 'Egg', 'Fried food', 'Meat', 'Noodles-Pasta', 'Rice', 'Seafood', 'Soup', 'Vegetable-Fruit']
BLOG_POSTS_FILE = 'website/uploads/blog_posts.json'
API_KEY = 'AIzaSyChnUdm2fzlucXpeoRSAGcYZILuJ_gqLek'
API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}'

TRAY_API_DESCRIPTION = """
You are a helpful and witty assistant for Tray API, an accurate and powerful API for food image classification. 
Your role is to provide information about Tray API, answer questions related to food classification, 
and assist users with any queries they might have about the service. Please be friendly, informative, 
and concise in your responses. Feel free to sprinkle in food-related jokes and puns to keep the conversation light and enjoyable.

Key points about Tray API:
- It uses various machine learning techniques for food image classification.
- It is open-source and available at github.com/ssbdragonfly/tray-api.
- For more information, users can contact the developers at bishtshaurya314@gmail.com.

Tray API website features:
- Documentation: Comprehensive guides on how to use the API.
- Blog: Regular updates, tips, and insights about food classification and machine learning.
- Performance metrics: Detailed information about the API's accuracy and speed.
- History: Users can view their past image classifications.
- FAQ: Answers to common questions about the service.
- Team page: Information about the developers behind Tray API.
- Legal information: Privacy policy and terms of service.
- Partnerships: Information for potential business partners.

All these features and more can be found on our website. Users can easily navigate through different sections to find the information they need or to use our services.

Remember to keep your responses concise and avoid mentioning any truncation or limitations in your replies.

Example Responses:

General Information:
"Welcome to Tray API! We're your go-to source for food image classification. Got a food pic you need identified? Just ask away!"
Documentation:

Documentation:
"Looking to dive into our API? Check out our comprehensive documentation here for all the juicy details."
Performance Metrics:

Performance Metrics:
"Want to see how we measure up? Our performance metrics show off our accuracy and speed. Spoiler: We're pretty fast and accurate!"
Contact:

Contact:
"Got a question that needs a human touch? Reach out to our developers at bishtshaurya314@gmail.com."
Fun and Friendly:

Friendly:
"Why did the tomato turn red? Because it saw the salad dressing! Speaking of, our API can recognize that salad in no time!"
Partnerships:

Partnerships
"Interested in a partnership? Let's make some delicious collaborations happen. Check out our partnerships page for more info."
Keep responses concise and engaging, making sure users feel supported and entertained.
"""

MAX_CONTEXT_LENGTH = 5
MAX_CHAT_HISTORY = 5

@app.before_request
def before_request():
    if 'chat_history' not in session:
        session['chat_history'] = []

def update_chat_history(user_message, bot_reply):
    chat_history = session.get('chat_history', [])
    chat_history.append({
        'timestamp': datetime.now().isoformat(),
        'user_message': user_message,
        'bot_reply': bot_reply
    })
    session['chat_history'] = chat_history[-MAX_CHAT_HISTORY:]

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
                predicted_label = 'Bread'  # Replace with actual prediction logic
                save_history(file.filename, predicted_label, model_name)
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

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/team')
def team():
    return render_template('team.html')

def load_blog_posts():
    if os.path.exists(BLOG_POSTS_FILE):
        with open(BLOG_POSTS_FILE, 'r') as f:
            return json.load(f)
    return []

def get_categories():
    posts = load_blog_posts()
    categories = set()
    for post in posts:
        if 'category' in post:
            categories.add(post['category'])
    return list(categories)

def get_tags():
    posts = load_blog_posts()
    tags = set()
    for post in posts:
        if 'tags' in post:
            tags.update(post['tags'])
    return list(tags)

@app.route('/blog')
def blog():
    posts = load_blog_posts()
    categories = get_categories()
    tags = get_tags()
    return render_template('blog.html', posts=posts, categories=categories, tags=tags)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        posts = load_blog_posts()
        search_results = [post for post in posts if search_term.lower() in post['title'].lower() or search_term.lower() in post['content'].lower()]
        return render_template('search_results.html', search_results=search_results, search_term=search_term)
    return render_template('search.html')

@app.route('/category/<category_name>')
def category(category_name):
    posts = load_blog_posts()
    category_posts = [post for post in posts if post.get('category') == category_name]
    return render_template('category.html', posts=category_posts, category_name=category_name)

@app.route('/tag/<tag_name>')
def tag(tag_name):
    posts = load_blog_posts()
    tag_posts = [post for post in posts if tag_name in post.get('tags', [])]
    return render_template('tag.html', posts=tag_posts, tag_name=tag_name)

@app.route('/post/<post_title>')
def post(post_title):
    posts = load_blog_posts()
    post = next((post for post in posts if post['title'] == post_title), None)
    if post:
        return render_template('post.html', post=post)
    else:
        flash('Post not found.')
        return redirect(url_for('blog'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/performance')
def performance():
    return render_template('performance.html')

@app.route('/legal/privacy-policy')
def privacy_policy():
    return render_template('legal/privacy-policy.html')

@app.route('/legal/terms-of-service')
def terms_of_service():
    return render_template('legal/terms-of-service.html')

@app.route('/partnerships')
def partnerships():
    return render_template('partnerships.html')

def process_response(reply_text):
    reply_text = re.sub('<[^<]+?>', '', reply_text)
    return reply_text.strip()

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        'contents': [{
            'parts': [{
                'text': TRAY_API_DESCRIPTION + user_message
            }]
        }]
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    response_data = response.json()
    
    if response.status_code == 200:
        replies = response_data.get('candidates', [])
        if replies:
            reply_text = replies[0].get('content', {}).get('parts', [{}])[0].get('text', 'Sorry, I can\'t understand that.')
        else:
            reply_text = 'Sorry, I can\'t understand that.'
    else:
        reply_text = 'Sorry, I can\'t understand that.'
    
    update_chat_history(user_message, reply_text)
    
    return jsonify({
        'reply': reply_text, 
        'api_status': response.status_code, 
        'api_response': response_data,
        'chat_history': session['chat_history']
    })

@app.route('/get_chat_history')
def get_chat_history():
    return jsonify(session.get('chat_history', []))

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)