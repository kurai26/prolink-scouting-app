from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask import g
import sqlite3

app = Flask(__name__)
app.secret_key = '123456789'


# SQLite database setup for user information
def create_user_table():
  with sqlite3.connect('account_users.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                lastname TEXT NOT NULL,
                firstname TEXT NOT NULL,
                dateofbirth DATE NOT NULL,
                club TEXT,
                school TEXT,
                address1 TEXT,
                address2 TEXT,
                city TEXT,
                country TEXT,
                telephone TEXT,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')


create_user_table()


# SQLite database setup for player information
def create_player_tables():
  with sqlite3.connect('player.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS general_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                birth_country TEXT NOT NULL,
                passport_country TEXT NOT NULL,
                height TEXT NOT NULL,
                weight TEXT NOT NULL,
                foot TEXT NOT NULL,
                position TEXT NOT NULL,
                headshot_path TEXT
            )
        ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS career_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                year TEXT NOT NULL,
                team TEXT NOT NULL,
                competition TEXT NOT NULL,
                games TEXT NOT NULL,
                starting TEXT NOT NULL,
                sub TEXT NOT NULL,
                yellow TEXT NOT NULL,
                red TEXT NOT NULL,
                assist TEXT NOT NULL,
                goal TEXT NOT NULL,
                saves TEXT NOT NULL
            )
        ''')


create_player_tables()


# Helper function to get the database connection
def get_db():
  if 'db' not in g:
    g.db = sqlite3.connect('account_users.db')
    g.db.row_factory = sqlite3.Row  # Access columns by name
  return g.db


@app.teardown_appcontext
def close_db(error):
  if hasattr(g, 'db'):
    g.db.close()


@app.route('/')
def home():
  return render_template('home.html')


@app.route('/about')
def about():
  # Your about page logic here
  return render_template('about.html')


@app.route('/solutions')
def solutions():
  # Your solutions page logic here
  return render_template('solutions.html')


@app.route('/contact')
def contact():
  # Your contact page logic here
  return render_template('contact.html')


@app.route('/user_interface')
def user_interface():
  return render_template('user_interface.html')


@app.route('/general.html', methods=['GET', 'POST'])
@login_required
def general():
  if request.method == 'POST':
    username = current_user.username
    birth_country = request.form['birthCountry']
    passport_country = request.form['passportCountry']
    height = request.form['height']
    weight = request.form['weight']
    foot = request.form['foot']
    position = request.form['position']
    headshot_path = save_headshot(request.files['headshot'], username)

    # Insert data into the general_info table
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
            INSERT INTO general_info (username, birth_country, passport_country, height, weight, foot, position, headshot_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, birth_country, passport_country, height, weight, foot,
              position, headshot_path))
    conn.commit()
    cursor.close()

  return render_template('general.html')


def save_headshot(headshot_file, username):
  if headshot_file:
    # Specify the path where you want to save the headshots
    headshot_path = "static/headshots/{username}.png"
    headshot_file.save(headshot_path)
    return headshot_path
  return None


@app.route('/career.html', methods=['GET', 'POST'])
@login_required
def career():
  if request.method == 'POST':
    username = current_user.username
    year = request.form['year']
    team = request.form['team']
    competition = request.form['competition']
    games = request.form['games']
    starting = request.form['starting']
    sub = request.form['sub']
    yellow = request.form['yellow']
    red = request.form['red']
    assist = request.form['assist']
    goal = request.form['goal']
    saves = request.form['saves']

    # Insert data into the career_info table
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
            INSERT INTO career_info (username, year, team, competition, games, starting, sub, yellow, red, assist, goal, saves)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, year, team, competition, games, starting, sub, yellow,
              red, assist, goal, saves))
    conn.commit()
    cursor.close()

  return render_template('career.html')


@app.route('/account_settings')
@login_required
def account_settings():
  # Get the username of the logged-in user dynamically
  username = current_user.username if current_user.is_authenticated else None

  if username:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username, ))
    user = cursor.fetchone()
    cursor.close()

    if user:
      # Print user information for debugging
      print("User found:", dict(user))

      # Render the account_settings.html template with user information
      return render_template('account_settings.html', user=user)

  # Handle the case where the user is not found or not authenticated
  print("User not found or not authenticated")  # Add this line for debugging
  return render_template('error.html',
                         error_message='User not found or not authenticated')


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    lastname = request.form['lastname']
    firstname = request.form['firstname']
    dateofbirth = request.form['dateofbirth']
    club = request.form['club']
    school = request.form['school']
    address1 = request.form.get('address1', '')
    address2 = request.form.get('address2', '')
    city = request.form['city']
    country = request.form['country']
    telephone = request.form['telephone']
    email = request.form['email']
    password = request.form['password']
    # Get other form fields similarly
    # registered_users.append({'username': username, 'password': password})

    # Insert data into the database
    conn = sqlite3.connect('account_users.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
            INSERT INTO users (username, lastname, firstname, dateofbirth, club, school, 
            address1, address2, city, country, telephone, email, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, lastname, firstname, dateofbirth, club, school,
              address1, address2, city, country, telephone, email, password))
    conn.commit()
    cursor.close()

    # Redirect to homepage after successful registration
    return redirect(url_for('home'))

  return render_template('register.html')


class User(UserMixin):

  def __init__(self, user_id, username):
    self.id = user_id
    self.username = username


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute('SELECT * FROM users WHERE id=?', (user_id, ))
  user_data = cursor.fetchone()
  cursor.close()

  if user_data:
    user = User(user_data['id'], user_data['username'])
    return user
  return None


@app.route('/home', methods=['POST'])
def login():
  if request.method == 'POST':
    # Process login form data
    username = request.form['username']
    password = request.form['password']

    # Check if the user exists in the database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?',
                   (username, password))
    user_data = cursor.fetchone()
    cursor.close()

    if user_data:
      # Create a User object and log in the user
      user = User(user_data['id'], user_data['username'])
      login_user(user)

      # Redirect to user_interface.html upon successful login
      return redirect(url_for('user_interface'))
    else:
      # Handle incorrect login credentials
      return render_template('home.html',
                             error_message='Invalid username or password')

  return redirect(url_for('user_interface'))


@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('home'))


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
