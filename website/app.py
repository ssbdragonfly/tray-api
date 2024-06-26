from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
API_KEY = 'AIzaSyDTb_aFePI-U1ZZ2JYwrrykLqpAbENP3_Y'
API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}'

TRAY_API_DESCRIPTION = """
Tray API is an accurate and powerful API for food image classification using various machine learning techniques. It is open-source and can be accessed at github.com/ssbdragonfly/tray-api. For more information, you can contact the developers via email at bishtshaurya314@gmail.com.
"""

MAX_CONTEXT_LENGTH = 5 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/', methods=['GET', 'POST'])
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
    return ''.join(sorted(output))

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
        print(f"Search Term: {search_term}")
        print(f"Search Results: {search_results}")
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
    max_length = 500
    if len(reply_text) > max_length:
        reply_text = reply_text[:max_length] + "... (response truncated)"
    return reply_text

def get_chat_context(user_id):
    chat_logs_path = os.path.join('website', 'uploads', f'chat_logs_{user_id}.json')
    try:
        with open(chat_logs_path, 'r') as file:
            logs = json.load(file)
            return logs[-MAX_CONTEXT_LENGTH:]
    except FileNotFoundError:
        return []

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')
    user_id = request.json.get('user_id', 'default_user')  
    context = get_chat_context(user_id)
    
    system_message = TRAY_API_DESCRIPTION
    context_prompt = "\n".join([f"User: {msg['user_message']}\nAssistant: {msg['bot_reply']}" for msg in context])
    user_prompt = f"Chat history:\n{context_prompt}\n\nUser: {user_message}\nAssistant:"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        'contents': [{
            'parts': [
                {'text': system_message},
                {'text': user_prompt}
            ]
        }]
    }
    response = requests.post(API_URL, headers=headers, json=data)
    response_data = response.json()
    
    if response.status_code == 200:
        replies = response_data.get('candidates', [])
        if replies:
            raw_reply = replies[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            reply_text = process_response(raw_reply)
        else:
            reply_text = 'I apologize, but I\'m unable to provide a response at the moment.'
    else:
        reply_text = 'I\'m sorry, but I encountered an error while processing your request. Please try again later.'

    timestamp = datetime.now().isoformat()
    save_chat_log(user_id, user_message, reply_text, timestamp)
    
    return jsonify({'reply': reply_text, 'api_status': response.status_code, 'api_response': response_data})

def save_chat_log(user_id, user_message, bot_reply, timestamp):
    chat_log_entry = {
        'timestamp': timestamp,
        'user_message': user_message,
        'bot_reply': bot_reply
    }
    
    chat_logs_path = os.path.join('website', 'uploads', f'chat_logs_{user_id}.json')
    try:
        with open(chat_logs_path, 'r') as file:
            logs = json.load(file)
    except FileNotFoundError:
        logs = []
    
    logs.append(chat_log_entry)
    logs = logs[-MAX_CONTEXT_LENGTH:]
    with open(chat_logs_path, 'w') as file:
        json.dump(logs, file)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)