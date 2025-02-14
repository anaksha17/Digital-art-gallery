
app = Flask(__name__)
app.secret_key = 'your_secret_key'
csrf = CSRFProtect(app)

# CSRF protection
csrf = CSRFProtect(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:abc123@localhost/digital_gallery'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define models for different user types
class CustomerUser(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='customer')
    
    def get_id(self):
        return f"customer_{self.id}"
    
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False

class ArtistUser(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='artist')
    artist_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text)
    country = db.Column(db.String(100))

    # Relationship with Artwork
    artworks = db.relationship('Artwork', backref='artists', lazy=True)
    def get_id(self):
        return f"artist_{self.id}"
    
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False

class AdminUser(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='admin')
    
    def get_id(self):
        return f"admin_{self.id}"
    
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False

class CuratorUser(db.Model):
    __tablename__ = 'curator'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='curator')
    
    def get_id(self):
        return f"curator_{self.id}"
    
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False
# Define the form class
class ApproveArtworkForm(FlaskForm):
    artworks = SelectMultipleField("Artworks", validators=[DataRequired()])

# Notification Table
class Notification(db.Model):
    __tablename__ = 'notification'
    notification_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)  # Foreign key to Artist
    notification_date = db.Column(db.DateTime)
    status_message = db.Column(db.String(255))
    message = db.Column(db.Text)

    # Relationship with CUSTOMER
    customer = db.relationship('CustomerUser', backref='notifications', lazy=True)
    artist = db.relationship('ArtistUser', backref='notifications', lazy=True)
# This is the junction table for the many-to-many relationship
auction_artwork = db.Table('auction_artwork',
    db.Column('auction_id', db.Integer, db.ForeignKey('auction.auction_id'), primary_key=True),
    db.Column('artwork_id', db.Integer, db.ForeignKey('artwork.artwork_id'), primary_key=True)
)


# Auction Table
class Auction(db.Model):
    __tablename__ = 'auction'
    auction_id = db.Column(db.Integer, primary_key=True)
    auction_name=db.Column(db.String(50))
    artwork_id = db.Column(db.Integer, db.ForeignKey('artwork.artwork_id'), nullable=False)
    starting_price = db.Column(db.Float)
    auction_status = db.Column(db.String(50))  # Example: "ongoing", "closed"
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    current_highest_bid = db.Column(db.Float)

    # Relationship with BID
    bids = db.relationship('Bid', backref='auction_set', lazy=True)

    # Relationship with ARTWORK (Corrected the backref)
    artwork = db.relationship('Artwork', secondary='auction_artwork',backref='auction_set', lazy='subquery')




# Bid Table
class Bid(db.Model):
    __tablename__ = 'bid'
    bid_id = db.Column(db.Integer, primary_key=True)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artwork.artwork_id'), nullable=False)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.auction_id'), nullable=False)
    bid_date_time = db.Column(db.DateTime)
    bid_amount = db.Column(db.Float)
    bidder_names = db.Column(db.String(255))

    # Relationship with AUCTION and ARTWORK
    auction = db.relationship('Auction', backref='bid_set', lazy=True)
    artwork = db.relationship('Artwork', backref='bid_set', lazy=True)
# Category Table
class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    artwork_category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Relationship with ARTWORK
    artworks = db.relationship('Artwork', backref='category_set', lazy=True)

# Artwork Table
class Artwork(db.Model):
    __tablename__ = 'artwork'
    artwork_id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    artwork_title = db.Column(db.String(100), nullable=False)
    artwork_price = db.Column(db.Float)
    status = db.Column(db.String(50))  # Example status: "available", "approved", etc.
    img_url = db.Column(db.String(255))
    date_of_creation = db.Column(db.Date)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))

    # Relationship with CATEGORY
    category = db.relationship('Category', backref='artwork_set', lazy=True)

    # Relationship with AUCTION
    auctions = db.relationship('Auction',secondary='auction_artwork', backref='artwork_Set', lazy=True)

    # Relationship with BID
    bids = db.relationship('Bid', backref='artwork_Set', lazy=True) 


class dummy(db.Model):
    __tablename__ = 'dummy'
    dummy_id = db.Column(db.Integer, primary_key=True)

    date_of_creation = db.Column(db.Date)
# Map user types to their corresponding models
USER_MODELS = {
    'customer': CustomerUser,
    'artist': ArtistUser,
    'admin': AdminUser,
    'curator': CuratorUser
}

   


@login_manager.user_loader
def load_user(user_id):
    # user_id format: "user_type_id"
    user_type, user_numeric_id = user_id.split('_')
    if user_type in USER_MODELS:
        return USER_MODELS[user_type].query.get(int(user_numeric_id))
    return None

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignupForm()
    if form.validate_on_submit():
        user_type = form.user_type.data
        
        if user_type not in USER_MODELS:
            flash('Invalid user type.')
            return render_template('signup.html', form=form)
            
        # Check if username exists in any table
        for model in USER_MODELS.values():
            existing_user = model.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username already exists. Please choose another one.')
                return render_template('signup.html', form=form)
        
        # Create new user in appropriate table
        UserModel = USER_MODELS[user_type]
        new_user = UserModel(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('home'))
        
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # If already logged in, redirect to home page
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        # Check all tables for the user
        for model in USER_MODELS.values():
            user = model.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                # Redirect based on role
                if user.role == 'curator':
                    return redirect(url_for('curator_dashboard'))
                elif user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'artist':
                    return redirect(url_for('artist_dashboard'))
                elif user.role == 'customer':
                    return redirect(url_for('customer_dashboard'))
                
                
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/home')
@login_required
def home():
    # Redirect based on user type
    if isinstance(current_user, CuratorUser):
        return redirect(url_for('curator_dashboard'))
    elif isinstance(current_user, AdminUser):
        return redirect(url_for('admin_dashboard'))
    elif isinstance(current_user, ArtistUser):
        return redirect(url_for('artist_dashboard'))
    elif isinstance(current_user, CustomerUser):
        return redirect(url_for('customer_dashboard'))
    
    # If no specific dashboard, show generic home
    return render_template('home.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    
@app.route('/curator/dashboard')
@login_required
def curator_dashboard():
    # Here you can fetch curator's data from the database if needed
    return render_template('curator_dashboard.html')
# Schedule Auction
@app.route('/schedule_auction', methods=['GET', 'POST'])
@login_required
def schedule_auction():
    if request.method == 'POST':
        selected_artworks = request.form.getlist('artworks')

        if len(selected_artworks) > 3:
            return "You can only select up to 3 artworks for this auction."
        
        # Check if the curator has already scheduled 3 auctions for today
        today = datetime.today().date()
        auctions_today = Auction.query.filter(Auction.curator_id == current_user.id, db.func.date(Auction.start_date) == today).count()

        if auctions_today >= 3:
            return "You can only schedule 3 auctions per day."
        
        # Create the auction and associate selected artworks
        new_auction = Auction(curator_id=current_user.id)
        db.session.add(new_auction)
        db.session.commit()

        for artwork_id in selected_artworks:
            auction_artwork = auction_artwork(auction_id=new_auction.id, artwork_id=artwork_id)
            db.session.add(auction_artwork)

        db.session.commit()

        return redirect(url_for('schedule_auction'))

    # Get only approved artworks (status='approved')
    artworks = Artwork.query.filter_by(status='approved').all()
    return render_template('schedule_auction.html', artworks=artworks)


from datetime import datetime, timedelta
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

 
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Set the secret key for session management (optional if no sessions are used)
app.secret_key = 'your_secret_key'

# Database connection settings
db_config = {
    'user': 'root',
    'password': 'abc123',
    'host': 'localhost',
    'database': 'digital_gallery'
}
@app.route('/')


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


from flask import flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField,SelectField

 # Route to show the Select Artwork for Auction form
@app.route('/select_artwork_for_auction', methods=['GET'])
def select_artwork_for_auction_form():
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Check if there are artist requests (Artworks submitted by artists for auction)
    cursor.execute("""
        SELECT artwork_id, artwork_title 
        FROM Artwork 
        WHERE status = 'submitted_for_auction'
    """)
    artist_requests = cursor.fetchall()

    # If there are no artist requests, fetch artworks from customers' wishlists
    if not artist_requests:
        cursor.execute("""
            SELECT DISTINCT a.artwork_id, a.artwork_title
            FROM Artwork a
            JOIN Wishlist w ON a.artwork_id = w.artwork_id
        """)
        artworks = cursor.fetchall()
    else:
        artworks = artist_requests

    # Close the database connection
    cursor.close()
    conn.close()

    # Render the form with the fetched artworks
    return render_template('select_artwork_for_auction.html', artworks=artworks)

# Route to handle selecting artwork for auction
@app.route('/select_artwork_for_auction', methods=['POST'])
def select_artwork_for_auction():
    artwork_id = request.form['artwork_id']

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Update the artwork status to 'auction_selected'
    cursor.execute("""
        UPDATE Artwork
        SET status = 'auction_selected'
        WHERE artwork_id = %s
    """, (artwork_id,))
    conn.commit()

    # Flash success message
    flash("Artwork selected successfully for auction!", "success")

    # Close the database connection
    cursor.close()
    conn.close()

    return redirect('/select_artwork_for_auction')


# Route to notify the artist
@app.route('/notify_artist', methods=['GET', 'POST'])
def notify_artist():
    if request.method == 'POST':
        selected_artworks = request.form.getlist('artworks')

        # Notify the artist for each selected artwork
        for artwork_id in selected_artworks:
            artwork = Artwork.query.get(artwork_id)
            artist = User.query.get(artwork.artist_id)  # Fetch the artist associated with the artwork
            
            # Send a notification to the artist
            if artist:
                message = f"Your artwork '{artwork.title}' has been scheduled for auction."
                notification = Notification(message=message, artist_id=artist.id)
                db.session.add(notification)
        
        db.session.commit()
        flash('Notifications sent successfully!', 'success')
        return redirect(url_for('notify_artist'))  # Redirect after sending notifications

    # Fetch only artworks that are approved for auction (status='approved')
    artworks = Artwork.query.filter_by(status='approved').all()
    return render_template('notifications.html', artworks=artworks)



@app.route('/notifications')
def view_notifications():
    # Assuming the user is logged in as an artist
    artist_id = current_user.id
    
    # Fetch unread notifications for the artist (optional if you want to store in DB)
    notifications = Notification.query.filter_by(artist_id=artist_id).order_by(Notification.notification_date.desc()).all()
    
    return render_template('notifications_page.html', notifications=notifications)
if __name__ == "__main__":
    app.run(debug=True)



    