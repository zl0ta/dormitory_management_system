from datetime import timedelta
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
    'user': 'admin',
    'password': 'admin',
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
    username = request.form['login']
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
            #set session expiration to 2 hours
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=2)

            # Redirect to the main page based on the user's role
            if user['Stanowisko'] == 'Dyrektor':
                return redirect('/dyrektor/main')
            elif user['Stanowisko'] == 'Kierownik':
                return redirect('/kierownik/main')
            elif user['Stanowisko'] == 'Portier':
                return redirect('/portier/main')
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
@app.route('/dyrektor/main')
def dyrektor_main_page():
    if 'user_id' in session and session['role'] == 'Dyrektor':
        return render_template('dyrektor_main.html', username=session['username'])
    else:
        return redirect('/')

# Route for the main page (kierownik)
@app.route('/kierownik/main')
def kierownik_main_page():
    if 'user_id' in session and session['role'] == 'Kierownik':
        return render_template('kierownik_main.html', username=session['username'])
    else:
        return redirect('/')

# Route for the main page (portier)
@app.route('/portier/main')
def portier_main_page():
    if 'user_id' in session and session['role'] == 'student':
        return render_template('student.html', username=session['username'])
    else:
        return redirect('/')
    
# Route for the dyrektor - akademiki page (dyrektor)
@app.route('/dyrektor/akademiki')
def dyrektor_akademiki_page():
    if 'user_id' in session and session['role'] == 'Dyrektor':
        try:
            # Connect to the database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Get the list of dormitories
            query = "SELECT * FROM akademiki"
            cursor.execute(query)
            akademiki = cursor.fetchall()

            return render_template('dyrektor_akademiki.html', username=session['username'], akademiki=akademiki)
        except mysql.connector.Error as err:
            print("Error connecting to the database:", err)
            return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    else:
        return redirect('/')
    
# Route for the dyrektor - akademiki - dodaj page (dyrektor)
@app.route('/dyrektor/akademiki/dodaj', methods=['GET', 'POST'])
def dyrektor_akademiki_dodaj_page():
    if 'user_id' in session and session['role'] == 'Dyrektor':
        if request.method == 'GET':
            return render_template('dyrektor_akademiki_dodaj.html', username=session['username'])
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Add a new dormitory
                query = "INSERT INTO akademiki (SymbolA, NazwaA, LiczbaPokoi, Status, Uwagi) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (request.form['symbol'], request.form['nazwa'], request.form['liczba_pokoi'], request.form['status'], request.form['uwagi']))
                connection.commit()

                return redirect('/dyrektor/akademiki')
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

            finally:
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()
    else:
        return redirect('/')

# Route for the dyrektor - pracownicy page (dyrektor)
@app.route('/dyrektor/pracownicy')
def dyrektor_pracownicy_page():
    if 'user_id' in session and session['role'] == 'Dyrektor':
        try:
            # Connect to the database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Get the list of employees
            query = "SELECT * FROM pracownicy"
            cursor.execute(query)
            pracownicy = cursor.fetchall()

            return render_template('dyrektor_pracownicy.html', username=session['username'], pracownicy=pracownicy)
        except mysql.connector.Error as err:
            print("Error connecting to the database:", err)
            return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    else:
        return redirect('/')

# Route for the dyrektor - pracownicy - dodaj page (dyrektor)
@app.route('/dyrektor/pracownicy/dodaj', methods=['GET', 'POST'])
def dyrektor_pracownicy_dodaj_page():
    if 'user_id' in session and session['role'] == 'Dyrektor':
        if request.method == 'GET':
            return render_template('dyrektor_pracownicy_dodaj.html', username=session['username'])
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Add a new employee
                query = "INSERT INTO pracownicy (Imie, Nazwisko, Login, Haslo, Stanowisko) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (request.form['imie'], request.form['nazwisko'], request.form['login'], request.form['haslo'], request.form['stanowisko']))
                connection.commit()

                return redirect('/dyrektor/pracownicy')
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

            finally:
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()
    else:
        return redirect('/')

# Route for the kierownik - studenci page (kierownik)
@app.route('/kierownik/studenci')
def kierownik_studenci_page():
    if 'user_id' in session and session['role'] == 'Kierownik':
        try:
            # Connect to the database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Get the list of students
            query = "SELECT * FROM studenci"
            cursor.execute(query)
            studenci = cursor.fetchall()

            return render_template('kierownik_studenci.html', username=session['username'], studenci=studenci)
        except mysql.connector.Error as err:
            print("Error connecting to the database:", err)
            return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    else:
        return redirect('/')

# Route for the kierownik - studenci - dodaj page (kierownik)
@app.route('/kierownik/studenci/dodaj', methods=['GET', 'POST'])
def kierownik_studenci_dodaj_page():
    if 'user_id' in session and session['role'] == 'Kierownik':
        if request.method == 'GET':
            return render_template('kierownik_studenci_dodaj.html', username=session['username'])
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Add a new student
                query = "INSERT INTO studenci (Imie, Nazwisko, NrIndeksu, IdA) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (request.form['imie'], request.form['nazwisko'], request.form['nr_indeksu'], request.form['id_akademika']))
                connection.commit()

                return redirect('/kierownik/studenci')
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

            finally:
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()
    else:
        return redirect('/')

# Route for the kierownik - akademik & pracownicy page (kierownik)
@app.route('/kierownik/akademik_pracownicy')
def kierownik_akademik_pracownicy_page():
    if 'user_id' in session and session['role'] == 'Kierownik':
        try:
            # Connect to the database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Get the list of dormitories
            query = "SELECT * FROM akademiki"
            cursor.execute(query)
            akademiki = cursor.fetchall()

            # Get the list of employees
            query = "SELECT * FROM pracownicy"
            cursor.execute(query)
            pracownicy = cursor.fetchall()

            return render_template('kierownik_akademik_pracownicy.html', username=session['username'], akademiki=akademiki, pracownicy=pracownicy)
        except mysql.connector.Error as err:
            print("Error connecting to the database:", err)
            return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    else:
        return redirect('/')

# Route for the portier - studenci page (portier)
@app.route('/portier/studenci')
def portier_studenci_page():
    if 'user_id' in session and session['role'] == 'Portier':
        try:
            # Connect to the database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Get the list of students
            query = "SELECT * FROM studenci"
            cursor.execute(query)
            studenci = cursor.fetchall()

            return render_template('portier_studenci.html', username=session['username'], studenci=studenci)
        except mysql.connector.Error as err:
            print("Error connecting to the database:", err)
            return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    else:
        return redirect('/')

# Route for the portier - usterki page (portier)
@app.route('/portier/usterki')
def portier_usterki_page():
    if 'user_id' in session and session['role'] == 'Portier':
        try:
            # Connect to the database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Get the list of faults
            query = "SELECT * FROM usterki"
            cursor.execute(query)
            usterki = cursor.fetchall()

            return render_template('portier_usterki.html', username=session['username'], usterki=usterki)
        except mysql.connector.Error as err:
            print("Error connecting to the database:", err)
            return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    else:
        return redirect('/')

# Route for the portier - usterki - dodaj page (portier)
@app.route('/portier/usterki/dodaj', methods=['GET', 'POST'])
def portier_usterki_dodaj_page():
    if 'user_id' in session and session['role'] == 'Portier':
        if request.method == 'GET':
            return render_template('portier_usterki_dodaj.html', username=session['username'])
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Add a new fault
                query = "INSERT INTO usterki (Opis, DataZgloszenia, DataNaprawy, IdP) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (request.form['opis'], request.form['data_zgloszenia'], request.form['data_naprawy'], session['user_id']))
                connection.commit()

                return redirect('/portier/usterki')
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

            finally:
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()
    else:
        return redirect('/')

# Route for the portier - akaemik & pracownicy page (portier)
@app.route('/portier/akademik_pracownicy')
def portier_akademik_pracownicy_page():
    if 'user_id' in session and session['role'] == 'Portier':
        try:
            # Connect to the database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Get the list of dormitories
            query = "SELECT * FROM akademiki"
            cursor.execute(query)
            akademiki = cursor.fetchall()

            # Get the list of employees
            query = "SELECT * FROM pracownicy"
            cursor.execute(query)
            pracownicy = cursor.fetchall()

            return render_template('portier_akademik_pracownicy.html', username=session['username'], akademiki=akademiki, pracownicy=pracownicy)
        except mysql.connector.Error as err:
            print("Error connecting to the database:", err)
            return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    else:
        return redirect('/')



# Route to handle logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
