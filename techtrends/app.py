import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, Response
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get total posts
def get_total_posts():
    connection = get_db_connection()
    total_posts = connection.execute('SELECT count(*) FROM posts').fetchone()
    connection.close()
    return total_posts[0]

# Function to get total db connections
def set_new_db_connection():
    connection = get_db_connection()
    connection.execute('UPDATE db_transactions set tx_count = tx_count + 1 WHERE id = 1')
    connection.commit()
    connection.close()

# Function to get total db connections
def get_total_db_connections():
    connection = get_db_connection()
    total_connections = connection.execute('SELECT tx_count FROM db_transactions where id = 1').fetchone()
    connection.close()
    return total_connections[0]

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

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
      app.logger.info('Post does not exist')
      return render_template('404.html'), 404
    else:
      app.logger.info("Article " + post['title'] + " retrieved!")
      set_new_db_connection()
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About us page was reached')
    return render_template('about.html')

# Define the Healthz page
@app.route("/healthz")
def healthz():
    app.logger.info('Healthz endpoint was reached')
    return Response(json.dumps({"result": "OK healthy"}), status = 200, mimetype='application/json')

# Define the Metrics page
@app.route("/metrics")
def metrics():
    total_posts = get_total_posts()
    total_connections = get_total_db_connections()
    app.logger.info('Metrics endpoint was reached')
    return Response(json.dumps({"status":"success","code":0, "data":{"db_connection_count": total_connections,"post_count": total_posts}}), status=200, mimetype='application/json')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            set_new_db_connection()
            app.logger.info('A new post was created. The title is ' + title)
            return redirect(url_for('index'))
    
    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111', debug=True)
