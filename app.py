from datetime import timedelta
from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'dormitory'  # Change this to a secure key

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
            app.permanent_session_lifetime = timedelta(hours=1)

            # Redirect to the main page based on the user's role
            if user['Stanowisko'] == 'Dyrektor':
                return redirect('/dyrektor/main')
            elif user['Stanowisko'] == 'Kierownik':
                session['id_akademika'] = user['IdA']
                return redirect('/kierownik/main')
            elif user['Stanowisko'] == 'Portier':
                session['id_akademika'] = user['IdA']
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
    if 'user_id' in session and session['role'] == 'Portier':
        return render_template('portier_main.html', username=session['username'])
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
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Get the list of status options
                query = "SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'akademiki' AND COLUMN_NAME = 'Status'"
                cursor.execute(query)
                result = cursor.fetchone()
                status_options = eval(result['COLUMN_TYPE'].replace('enum', ''))

                # Get the list of praconicy with the role of kierownik and are not assigned to a dormitory yet ()
                query = "SELECT * FROM pracownicy WHERE Stanowisko = 'Kierownik' AND IdA IS NULL"
                cursor.execute(query)
                kierownicy = cursor.fetchall()

                # Get list of akademiki
                query = "SELECT * FROM akademiki"
                cursor.execute(query)
                akademiki = cursor.fetchall()
                akademiki = [akademik['SymbolA'] for akademik in akademiki]

                return render_template('dyrektor_dodawanie_akademika.html', username=session['username'], status_options=status_options, kierownicy=kierownicy, akademiki=akademiki)
            
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")
            
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                query = "INSERT INTO akademiki (SymbolA, NazwaA, Adres, LiczbaPokoi, Status, Uwagi) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (request.form['symbol'], request.form['nazwa'], request.form['adres'], request.form['liczba_pokoi'], request.form['status'], request.form['uwagi']))
                connection.commit()

                #add akademik to all chosen kierownicy (there may be more than one)
                # pracownicy (IdP, Imie, Nazwisko, Stanowisko, IdA), IdA - FK to akademiki.SymbolA
                query = "UPDATE pracownicy SET IdA = %s WHERE IdP = %s"
                for kierownik in request.form.getlist('kierownik'):
                    cursor.execute(query, (request.form['symbol'], kierownik))
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

# Route for the dyrektor - akademiki - edytuj page (dyrektor)
@app.route('/dyrektor/akademiki/edytuj/<string:symbol>', methods=['GET', 'POST'])
def dyrektor_akademiki_edytuj_page(symbol):
    if 'user_id' in session and session['role'] == 'Dyrektor':
        if request.method == 'GET':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Get the dormitory details
                query = "SELECT * FROM akademiki WHERE SymbolA = %s"
                cursor.execute(query, (symbol,))
                akademik = cursor.fetchone()

                # Get the list of status options
                query = "SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'akademiki' AND COLUMN_NAME = 'Status'"
                cursor.execute(query)
                result = cursor.fetchone()
                status_options = eval(result['COLUMN_TYPE'].replace('enum', ''))

                # Get the list of praconicy with the role of kierownik that are not assigned to a dormitory yet
                query = "SELECT * FROM pracownicy WHERE Stanowisko = 'Kierownik' AND (IdA IS NULL OR IdA = %s)"
                cursor.execute(query, (symbol,))
                kierownicy = cursor.fetchall()

                # Get list of akademiki
                query = "SELECT * FROM akademiki"
                cursor.execute(query)
                akademiki = cursor.fetchall()
                akademiki = [akademik['SymbolA'] for akademik in akademiki]

                return render_template('dyrektor_edytowanie_akademika.html', username=session['username'], akademik=akademik, status_options=status_options, kierownicy=kierownicy, akademiki=akademiki)
            
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")
            
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Update the dormitory details
                query = "UPDATE akademiki SET NazwaA = %s, Adres = %s, LiczbaPokoi = %s, Status = %s, Uwagi = %s WHERE SymbolA = %s"
                cursor.execute(query, (request.form['nazwa'], request.form['adres'], request.form['liczba_pokoi'], request.form['status'], request.form['uwagi'], symbol))
                connection.commit()

                #remove akademik from previous kierownik
                query = "UPDATE pracownicy SET IdA = NULL WHERE IdA = %s"
                cursor.execute(query, (symbol,))
                connection.commit()

                #add akademik to chosen kierownik
                # pracownicy (IdP, Imie, Nazwisko, Stanowisko, IdA), IdA - FK to akademiki.SymbolA
                query = "UPDATE pracownicy SET IdA = %s WHERE IdP = %s"
                cursor.execute(query, (symbol, request.form['kierownik']))
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
            # delete line with dyrektor
            for pracownik in pracownicy:
                if pracownik['IdP'] == session['user_id']:
                    pracownicy.remove(pracownik)
                    break

            # delete password from pracownicy
            for pracownik in pracownicy:
                del pracownik['Haslo']

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
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Get the list of stanowisko options
                query = "SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'pracownicy' AND COLUMN_NAME = 'Stanowisko'"
                cursor.execute(query)
                result = cursor.fetchone()
                role_options = eval(result['COLUMN_TYPE'].replace('enum', ''))

                return render_template('dyrektor_dodawanie_pracownika.html', username=session['username'], role_options=role_options)
            
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")

            finally:
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                #generate login from imie and nazwisko: Imie_Nazwisko
                login = request.form['imie'] + '_' + request.form['nazwisko']
                # check if login is unique
                not_unique = True
                i = 2
                old_login = login
                while not_unique:
                    query = "SELECT * FROM pracownicy WHERE Login = %s"
                    cursor.execute(query, (login,))
                    pracownik = cursor.fetchone()
                    if pracownik:
                        login = old_login + '_' + str(i)
                        i += 1
                    else:
                        not_unique = False

                # Add a new employee
                query = "INSERT INTO pracownicy (Nazwisko, Imie, Stanowisko, DUr, DZatr, Pensja, Pensum, Telefon, E_mail, Login, Haslo, Uwagi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (request.form['nazwisko'], request.form['imie'], request.form['stanowisko'], request.form['data_urodzenia'], request.form['data_zatrudnienia'], request.form['pensja'], request.form['pensum'], request.form['telefon'], request.form['email'], login, request.form['password'], request.form['uwagi']))
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

# Route for the dyrektor - pracownicy - edytuj page (dyrektor)
@app.route('/dyrektor/pracownicy/edytuj/<int:id>', methods=['GET', 'POST'])
def dyrektor_pracownicy_edytuj_page(id):
    if 'user_id' in session and session['role'] == 'Dyrektor':
        if request.method == 'GET':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Get the employee details
                query = "SELECT * FROM pracownicy WHERE IdP = %s"
                cursor.execute(query, (id,))
                pracownik = cursor.fetchone()

                # Get the list of stanowisko options
                query = "SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'pracownicy' AND COLUMN_NAME = 'Stanowisko'"
                cursor.execute(query)
                result = cursor.fetchone()
                role_options = eval(result['COLUMN_TYPE'].replace('enum', ''))

                # Get list of akademiki
                query = "SELECT * FROM akademiki"
                cursor.execute(query)
                akademiki = cursor.fetchall()
                akademiki = [akademik['SymbolA'] for akademik in akademiki]

                return render_template('dyrektor_edytowanie_pracownika.html', username=session['username'], pracownik=pracownik, role_options=role_options, akademiki=akademiki)
            
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")
            
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)
                
                # Update the employee details
                akademik = request.form['akademik']
                if (akademik == 'Brak'): akademik = None
                query = "UPDATE pracownicy SET Nazwisko = %s, Imie = %s, Stanowisko = %s, DUr = %s, DZatr = %s, Pensja = %s, Pensum = %s, Telefon = %s, E_mail = %s, IdA = %s, Uwagi = %s WHERE IdP = %s"
                cursor.execute(query, (request.form['nazwisko'], request.form['imie'], request.form['stanowisko'], request.form['data_urodzenia'], request.form['data_zatrudnienia'], request.form['pensja'], request.form['pensum'], request.form['telefon'], request.form['email'], akademik, request.form['uwagi'], id))
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
            query = "SELECT * FROM mieszkancy WHERE IdA = %s"
            cursor.execute(query, (session['id_akademika'],))
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
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Get the list of enum of akademiki.SymbolA, status = 'Otwarty'
                query = "SELECT SymbolA FROM akademiki WHERE Status = 'Otwarty'"
                cursor.execute(query)
                akademiki = cursor.fetchall()
                akademiki = [akademik['SymbolA'] for akademik in akademiki]

                #Get the list of all taken indekses
                query = "SELECT Indeks FROM mieszkancy"
                cursor.execute(query)
                indeksy = cursor.fetchall()
                indeksy = [indeks['Indeks'] for indeks in indeksy]

                return render_template('kierownik_dodawanie_studentow.html', username=session['username'], akademiki=akademiki, indeksy=indeksy)
            
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")
            
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Add a new student
                query = "INSERT INTO mieszkancy (Nazwisko, Imie, Indeks, IdA, Pokoj, Telefon, E_mail, Uwagi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (request.form['nazwisko'], request.form['imie'], request.form['indeks'], session['id_akademika'], request.form['pokoj'], request.form['telefon'], request.form['email'], request.form['uwagi']))
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

# Route for the kierownik - studenci - edytuj page (kierownik)
@app.route('/kierownik/studenci/edytuj/<int:id>', methods=['GET', 'POST'])
def kierownik_studenci_edytuj_page(id):
    if 'user_id' in session and session['role'] == 'Kierownik':
        if request.method == 'GET':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)
                
                # Get the student details
                query = "SELECT * FROM mieszkancy WHERE IdM = %s"
                cursor.execute(query, (id,))
                student = cursor.fetchone()

                # Get all indeksy
                query = "SELECT Indeks FROM mieszkancy"
                cursor.execute(query)
                indeksy = cursor.fetchall()
                indeksy = [indeks['Indeks'] for indeks in indeksy]

                return render_template('kierownik_edytowanie_studentow.html', username=session['username'], student=student, indeksy=indeksy)
            
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")
            
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)
                
                # Update the student details
                query = "UPDATE mieszkancy SET Nazwisko = %s, Imie = %s, Indeks = %s, Pokoj = %s, Telefon = %s, E_mail = %s, Uwagi = %s WHERE IdM = %s"
                cursor.execute(query, (request.form['nazwisko'], request.form['imie'], request.form['indeks'], request.form['pokoj'], request.form['telefon'], request.form['email'], request.form['uwagi'], id))
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
        return redirect

# Route for the kierownik - akademik & pracownicy page (kierownik)
@app.route('/kierownik/akademik_pracownicy')
def kierownik_akademik_pracownicy_page():
    if 'user_id' in session and session['role'] == 'Kierownik':
        try:
            # Connect to the database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Get the kierownik dormitory
            query = "SELECT * FROM akademiki WHERE SymbolA = %s"
            cursor.execute(query, (session['id_akademika'],))
            result = cursor.fetchone()
            akademik = ''

            if result['Adres'] == None:
                akademik = result['SymbolA'] + ', ' + result['Status']
            else:
                # concating adres
                akademik = result['SymbolA'] + ", " + result['Adres'] + ", " + result['Status']

            # Get the list of employees oprócz kierownika + dyrektory
            query = "SELECT * FROM pracownicy WHERE (IdA = %s AND IdP != %s) OR Stanowisko = 'Dyrektor'"
            cursor.execute(query, (session['id_akademika'], session['user_id']))
            pracownicy = cursor.fetchall()

            return render_template('kierownik_akademik_pracownicy.html', username=session['username'], akademik=akademik, pracownicy=pracownicy)
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

            # Get the list of students of the dormitory the portier works in
            if 'id_akademika' not in session:
                studenci=[]
            else:
                query = "SELECT * FROM mieszkancy WHERE IdA = %s"
                cursor.execute(query, (session['id_akademika'],))
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
            query = "SELECT * FROM usterki WHERE IdA = %s"
            cursor.execute(query, (session['id_akademika'],))
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
            return render_template('portier_dodawanie_usterki.html', username=session['username'])
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Add a new fault
                query = "INSERT INTO usterki (IdA, Pokoj, DZgloszenia, Status, Opis) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (session['id_akademika'], request.form['pokoj'], request.form['data_zgloszenia'], 'Nowa', request.form['opis']))
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

# Route for the portier - usterki - edytuj page (portier)
@app.route('/portier/usterki/edytuj/<int:id>', methods=['GET', 'POST'])
def portier_usterki_edytuj_page(id):
    if 'user_id' in session and session['role'] == 'Portier':
        if request.method == 'GET':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

                # Get the fault details
                query = "SELECT * FROM usterki WHERE IdU = %s"
                cursor.execute(query, (id,))
                usterka = cursor.fetchone()

                # Get the list of status options
                query = "SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'usterki' AND COLUMN_NAME = 'Status'"
                cursor.execute(query)
                result = cursor.fetchone()
                status_options = eval(result['COLUMN_TYPE'].replace('enum', ''))

                return render_template('portier_edytowanie_usterki.html', username=session['username'], usterka=usterka, status_options=status_options)
            
            except mysql.connector.Error as err:
                print("Error connecting to the database:", err)
                return render_template('error.html', error_message="Error connecting to the database. Please try again later.")
            
        elif request.method == 'POST':
            try:
                # Connect to the database
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)
                
                # Update the fault details
                query = "UPDATE usterki SET Pokoj = %s, Status = %s, Opis = %s WHERE IdU = %s"
                cursor.execute(query, (request.form['pokoj'], request.form['status'], request.form['opis'], id))
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

            # Get akaemik w którym pracuje portier
            query = "SELECT * FROM akademiki WHERE SymbolA = %s"
            cursor.execute(query, (session['id_akademika'],))
            result = cursor.fetchone()
            akademik = ''

            if result['Adres'] == None:
                akademik = result['SymbolA'] + ', ' + result['Status']
            else:
                # concating adres
                akademik = result['SymbolA'] + ", " + result['Adres'] + ", " + result['Status']

            # Get the list of employees oprócz portiera i pracowników z innego akademika
            query = "SELECT * FROM pracownicy WHERE (IdA = %s AND IdP != %s) OR Stanowisko = 'Dyrektor'"
            cursor.execute(query, (session['id_akademika'], session['user_id']))
            pracownicy = cursor.fetchall()

            return render_template('portier_akademik_pracownicy.html', username=session['username'], akademik=akademik, pracownicy=pracownicy)
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