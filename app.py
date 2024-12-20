from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import string
import random
from urllib.parse import urlparse

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         original_url TEXT NOT NULL,
         short_code TEXT NOT NULL UNIQUE,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

# Generate a random short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Validate URL
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form.get('url')
        
        if not original_url:
            return render_template('index.html', error="Please enter a URL")
        
        if not is_valid_url(original_url):
            return render_template('index.html', error="Please enter a valid URL")
        
        # Generate a unique short code
        while True:
            short_code = generate_short_code()
            conn = sqlite3.connect('urls.db')
            c = conn.cursor()
            
            # Check if code already exists
            existing = c.execute('SELECT id FROM urls WHERE short_code = ?', 
                               (short_code,)).fetchone()
            
            if not existing:
                c.execute('INSERT INTO urls (original_url, short_code) VALUES (?, ?)',
                         (original_url, short_code))
                conn.commit()
                conn.close()
                break
                
            conn.close()
        
        short_url = request.host_url + short_code
        return render_template('index.html', short_url=short_url)
    
    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_url(short_code):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    result = c.execute('SELECT original_url FROM urls WHERE short_code = ?',
                      (short_code,)).fetchone()
    conn.close()
    
    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)