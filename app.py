from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SECRET_KEY'] = '8111'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha256'
app.config['SECURITY_PASSWORD_SALT'] = 'super_secret_salt'

db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    number = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    additional_item = db.Column(db.String(100))
    total_price = db.Column(db.Float, nullable=False)  # New column for total price

# Create database tables
with app.app_context():
    db.create_all()

# Mock user for demonstration
mock_user = {
    'username': 'John Doe'
}

@app.route('/')
def start():
    return render_template('start.html')

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        number = request.form.get('number')
        quantity = request.form.get('quantity')
        order_item = request.form.get('order')
        address = request.form.get('address')
        additional_item = request.form.get('additional_item')
        total_price = request.form.get('total_price')  # Get the total price

        new_order = Order(
            name=name,
            email=email,
            number=number,
            quantity=quantity,
            order=order_item,
            address=address,
            additional_item=additional_item,
            total_price=total_price  # Save the total price
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('user'))
    
    return render_template('order.html')

@app.route('/sign', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('signup'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists. Please use a different email address.', 'danger')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Sign up successful!', 'success')
            return redirect(url_for('start'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'danger')
            return redirect(url_for('signup'))

    return render_template('sign.html')

@app.route('/userin')
def user():
    if 'username' in session:
        username = session['username']
        return render_template('userin.html', username=username)
    else:
        flash('First Enter the username and password!!', 'danger')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = username  # Store username in session
            flash('Login successful!', 'success')
            return redirect(url_for('user'))
        else:
            flash('Login failed. Check your username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('start'))

if __name__ == '__main__':
    app.run(debug=True)
