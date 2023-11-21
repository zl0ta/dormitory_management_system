from flask import Flask, render_template, request, redirect, session
import mysql.connector
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'dormitory'  # Change this to a secure key
csrf = CSRFProtect(app)

# Disable CSRF protection for testing (remove this in production)
app.config['WTF_CSRF_ENABLED'] = False

# MySQL Database Configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'app-dorm',
    'password': 'dorm-system',
    'database': 'systemakademikow',
    'port': '3306',
}

# Route for the login page
@app.route('/')
def login():
    return render_template('index.html')

# Route to handle the login form submission
@app.route('/login', methods=['GET', 'POST'])
def login_post():
    # Clear existing session
    session.clear()

    # Get login credentials from the form
    username = request.form['username']
    password = request.form['password']

    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Check if the user exists in the database
        query = "SELECT * FROM pracownicy WHERE Login = %s AND Haslo = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            # Save user details in the session
            session['user_id'] = user['IdP']
            session['username'] = user['Login']
            session['role'] = user['Stanowisko']

            # Redirect to the main page based on the user's role
            if user['Stanowisko'] == 'Dyrektor':
                return redirect('/dyrektor_main')
            elif user['Stanowisko'] == 'Kierownik':
                return redirect('/kierownik_main')
            elif user['Stanowisko'] == 'Portier':
                return redirect('/portier_main')
        else:
            error_message = "Invalid login credentials. Please try again."
            return render_template('index.html', error=error_message)
    except mysql.connector.Error as err:
        print("Error connecting to the database:", err)
        return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# Route for the main page (dyrektor)
@app.route('/dyrektor_main')
def dyrektor_main_page():
    if 'user_id' in session and session['role'] == 'Dyrektor':
        return render_template('dyrektor_main.html', username=session['username'])
    else:
        return redirect('/')

# Route for the main page (kierownik)
@app.route('/kierownik_main')
def kierownik_main_page():
    if 'user_id' in session and session['role'] == 'Kierownik':
        return render_template('kierownik_main.html', username=session['username'])
    else:
        return redirect('/')

# Route for the main page (portier)
@app.route('/portier_main')
def portier_main_page():
    if 'user_id' in session and session['role'] == 'student':
        return render_template('student.html', username=session['username'])
    else:
        return redirect('/')

# Route to handle logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
