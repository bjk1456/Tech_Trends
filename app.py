import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys
from datetime import datetime



# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    app.connection_count = app.connection_count + 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

def get_post_count():
    connection = get_db_connection()
    count = connection.execute('SELECT COUNT(id) FROM posts').fetchone()
    connection.close()
    return count[0]

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.connection_count = 0
stdout_fileno = sys.stdout
stderr_fileno = sys.stderr

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      none_text = f"INFO:app:[{datetime.now().isoformat(timespec='minutes')}]Article with post_id of {post_id} doesn't exist!"
      stderr_fileno.write(none_text)
      stdout_fileno.write(none_text + '\n')
      return render_template('404.html'), 404
    else:
      article_text = f"INFO:app:[{datetime.now().isoformat(timespec='minutes')}], Article {post['title']} retrieved!"
      app.logger.info(article_text)
      stdout_fileno.write(article_text)
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    about_text = f"INFO:app:[{datetime.now().isoformat(timespec='minutes')}]GET /metrics HTTP/1.1\" 200 -"
    app.logger.info(about_text)
    stdout_fileno.write(about_text + '\n')
    return render_template('about.html')

#
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/metrics')
def metrics():
    response = app.response_class(
        response=json.dumps({"db_connection_count":get_connection_count(),"post_count":get_post_count()},),
        status=200,
        mimetype='application/json'
    )
    return response

def get_connection_count():
    return app.connection_count

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            new_article = f"INFO:app:[{datetime.now().isoformat(timespec='minutes')}]The new article {title} is created"
            app.logger.info(new_article)
            stdout_fileno.write(new_article + '\n')
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(filename='app.log',level=logging.INFO)
   app.run(host='0.0.0.0', port='7111')
