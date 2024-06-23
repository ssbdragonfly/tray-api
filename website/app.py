from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

UPLOAD_FOLDER = os.path.join('website', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class_labels = ['Bread', 'Dairy Product', 'Dessert', 'Egg', 'Fried food', 'Meat', 'Noodles-Pasta', 'Rice', 'Seafood', 'Soup', 'Vegetable-Fruit']

BLOG_POSTS_FILE = 'website/uploads/blog_posts.json'

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

                # Hardcoded prediction for demonstration
                predicted_label = 'Bread'

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
    return '<br>'.join(sorted(output))

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

if __name__ == '__main__':
    app.run(debug=True)
