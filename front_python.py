from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
import mysql.connector
 
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
 
from werkzeug.security import generate_password_hash, check_password_hash
 
from datetime import datetime





#app.config['SECRET_KEY'] = 'art'


# Database connection settings
db_config = {
    'user': 'root',
    'password': 'abc123',
    'host': 'localhost',
    
    'database': 'digital_gallery'
}
 
app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/') 
def home_():
    try:
        # Establish a connection to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to fetch the 6 most recently added artworks
        query = "SELECT title, image_url, description FROM artwork ORDER BY creation_date DESC LIMIT 6"
        cursor.execute(query)
        artworks = cursor.fetchall()

        # Render the HTML page with the artworks
        return render_template('html_front.html', artworks=artworks)
    
    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
            
# Function to get artworks
def get_artworks():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT title, image_url, description FROM artwork ORDER BY creation_date DESC"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# View all artworks route
@app.route('/artwork')
def all_artworks():
    artworks = get_artworks()
    return render_template('artwork.html', artworks=artworks)

            



# Route to display artwork details
@app.route('/artwork/<int:artwork_id>')
def artwork_detail(artwork_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to fetch detailed information about the artwork
        query = """
            SELECT a.artwork_id, a.title, a.description, a.creation_date, a.price, a.image_url, a.status,
                   ar.name AS artist_name, ar.biography AS artist_bio, ar.profile_picture AS artist_picture,
                   au.status AS auction_status, au.start_date, au.end_date, au.current_highest_bid
            FROM artwork a
            LEFT JOIN artist ar ON a.artist_id = ar.artist_id
            LEFT JOIN auction au ON a.artwork_id = au.artwork_id
            WHERE a.artwork_id = %s
        """
        cursor.execute(query, (artwork_id,))
        artwork = cursor.fetchone()

        if not artwork:
            return "Artwork not found", 404

        # Check if the user is logged in
        user_logged_in = 'user_id' in session

        return render_template('artwork_detail.html', artwork=artwork, user_logged_in=user_logged_in)

    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

 
 

# Define the user models for each type (admin, curator, customer, artist)
USER_MODELS = {
    'customer': 'Customer',
    'curator': 'Curator',
    'admin': 'Admin',
    'artist': 'Artist'
}


# Assuming you have a table 'users' for all user types in your database

from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, name, user_type):
        self.id = id
        self.name = name
        self.user_type = user_type


@login_manager.user_loader
def load_user(user_id):
    # Dictionary to map user types to their respective ID column names
    user_id_column = {
        'customer': 'customer_id',  # Replace with actual column name for Customer
        'curator': 'curator_id',    # Replace with actual column name for Curator
        'admin': 'admin_id',        # Replace with actual column name for Admin
        'artist': 'artist_id'       # Replace with actual column name for Artist
    }

    for user_type, table in USER_MODELS.items():
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Use the correct ID column for each table
        cursor.execute(f"SELECT * FROM {table} WHERE {user_id_column[user_type]} = %s", (user_id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(id=user_data[user_id_column[user_type]], name=user_data['name'], user_type=user_type)
    
    return None  # Return None if user not found in any table


 
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        user_type = request.form.get('user_type')
        name = request.form.get('name')  # Replaced "username" with "name"
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

        # Check if name exists in any table
        for table in USER_MODELS.values():
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM {table} WHERE name = %s', (name,))
            existing_user = cursor.fetchone()
            connection.close()

            if existing_user:
                flash('Name already exists. Please choose another one.')
                return render_template('signup.html')

        # Insert new user into the appropriate table
        if user_type not in USER_MODELS:
            flash('Invalid user type.')
            return render_template('signup.html')

        table = USER_MODELS[user_type]
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO {table} (name, email, password) VALUES (%s, %s, %s)', (name, email, password))
        connection.commit()
        connection.close()

        # After signup, log the user in manually
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {table} WHERE name = %s', (name,))
        user_data = cursor.fetchone()
        connection.close()

        # Store user data in the session
        session['user_id'] = user_data[0]  # Assuming user_data[0] is the user ID
        session['name'] = user_data[1]  # Assuming user_data[1] is the name
        session['user_type'] = user_type  # Store the user type (role)

        return redirect(url_for('home'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')  # Use get() to handle potential missing keys
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        # Ensure all fields are provided
        if not name or not password or not user_type:
            flash("All fields are required!")
            return redirect(url_for('index'))

        if user_type in USER_MODELS:
            table = USER_MODELS[user_type]
            
            # Fetch user by name
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table} WHERE name = %s", (name,))
            user = cursor.fetchone()
            conn.close()

            # Check if user exists and if password matches
            if user and check_password_hash(user['password'], password):  # Assuming password is in 'password' column
                flash(f"Welcome, {user['name']}!")
                
                # Create a User object and log in
                user_obj = User(id=user['id'], name=user['name'], user_type=user_type)
                login_user(user_obj)

                return redirect(url_for('curator/dashboard', user_type=user_type, user_id=user['id']))
            else:
                flash("Invalid credentials. Please try again.")
        else:
            flash("Invalid user type. Please select a valid role.")

    return render_template('login.html')
@app.route('/curator/dashboard')
@login_required
def curator_dashboard():
    # Here you can fetch curator's data from the database if needed
    return render_template('curator_dashboard.html')
# Route to show the Organize Auction form
@app.route('/organize_auction', methods=['GET'])
def organize_auction_form():
    return render_template('organize_auction.html')

# Route to handle organizing an auction
@app.route('/organize_auction', methods=['POST'])
def organize_auction():
    # Get form data
    auction_name = request.form['auction_name']
    auction_date = request.form['auction_date']
    time_slot = request.form['time_slot']

    # Split the time slot into start time and end time
    start_time, end_time = time_slot.split('-')
    # Combine the auction date with the times to create full datetime values
    start_datetime = datetime.strptime(f"{auction_date} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(f"{auction_date} {end_time}", "%Y-%m-%d %H:%M")

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Check for overlapping auctions in the database
    query = """
        SELECT COUNT(*) 
        FROM Auction
        WHERE (%s BETWEEN start_date AND end_date OR %s BETWEEN start_date AND end_date)
    """
    cursor.execute(query, (start_datetime, end_datetime))
    conflict_count = cursor.fetchone()[0]

    if conflict_count > 0:
        # Flash error message if there is a conflict
        flash("Another auction is already scheduled at the same date and time!", "error")
    else:
        # Insert the auction data into the database
        query = """
            INSERT INTO Auction (auction_name, start_date, end_date)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (auction_name, start_datetime, end_datetime))
        conn.commit()
        # Flash success message
        flash("Auction organized successfully!", "success")

    # Close the database connection
    cursor.close()
    conn.close()

    return redirect('/organize_auction')

@app.route('/<user_type>/dashboard')
@login_required
def dashboard(user_type):
    if user_type == "curator":
        return render_template('curator_dashboard.html')
    elif user_type == "customer":
        return render_template('customer_dashboard.html')
    elif user_type == "admin":
        return render_template('admin_dashboard.html')
    else:
        flash("Invalid user type.")
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)


