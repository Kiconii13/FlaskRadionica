# 📋 Flask Task Manager - Roadmap za Početnike

Ovaj roadmap će te provesti kroz sve korake potrebne da rekreaš ovu Flask aplikaciju od početka. Pretpostavljamo da nikada nisi radio/la sa Flask-om, pa će sve biti detaljno objašnjeno.

---

## 🔧 Korak 1: Postavljanje Okruženja

### 1.1 Proveri da li imaš Python
Otvori PowerShell i unesi:
```powershell
python --version
```
Trebalo bi da vidis verziju (npr. `Python 3.13.0`). Ako ne radi, preuzmi Python sa [python.org](https://www.python.org).

### 1.2 Kreiraj projekt folder
```powershell
mkdir FlaskRadionica
cd FlaskRadionica
```

### 1.3 Kreiraj virtuelno okruženje
Virtuelno okruženje je izolovano Python okruženje samo za tvoj projekat.
```powershell
python -m venv venv
```

### 1.4 Aktiviraj virtuelno okruženje
```powershell
.\venv\Scripts\Activate.ps1
```
Sada bi trebalo da vidiš `(venv)` na početku linije u PowerShell-u.

---

## 📦 Korak 2: Instalacija Potrebnih Paketa

U aktivnom virtualnom okruženju (`(venv)` je vidljivo), instaliraj sledeće:

### 2.1 Flask
```powershell
pip install flask
```
Flask je main framework koji ćeš koristiti za web aplikaciju.

### 2.2 Flask-SQLAlchemy
```powershell
pip install flask-sqlalchemy
```
SQLAlchemy je ORM (Object-Relational Mapping) koji olakšava rad sa bazom podataka.

### 2.3 Werkzeug
```powershell
pip install werkzeug
```
Werkzeug dolazi standardno sa Flask-om, ali eksplicitno ga intaliramo jer koristimo security funkcije.

---

## 📁 Korak 3: Struktura Projekta

Kreiraj sledeću strukturu foldera i fajlova:

```
FlaskRadionica/
├── models/
│   ├── __init__.py
│   └── user.py
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   └── index.html
├── static/
│   └── style/
│       └── main.css
├── main.py
└── venv/
```

---

## 🗄️ Korak 4: Pravimo Model Korisnika i Zadataka

### 4.1 Kreiraj `models/__init__.py` (prazan fajl)
```powershell
New-Item models/__init__.py
```

### 4.2 Kreiraj `models/user.py`
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Task(db.Model):
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Task {self.name}>'
```

**Objašnjenje:**
- `User` model predstavlja korisnika sa username-om i lozinkom
- `Task` model predstavlja zadatak koji pripada nekom korisniku
- `db.relationship` povezuje usernike i njihove zadatke

---

## 🎨 Korak 5: HTML Šabloni

### 5.1 Kreiraj `templates/base.html`
Ovo je osnovna šablona koju će sve druge proširiti.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %} {% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style/main.css') }}">
</head>
<body>
    <h1> Proton Flask ⚛️</h1>

    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <dialog open>
                <p>{{ messages[0] }}</p>
                <form method="dialog">
                    <button type="submit">U redu</button>
                </form>
            </dialog>
        {% endif %}
    {% endwith %}

    <main>
        {% block content %}
        {% endblock %}
    </main>
</body>
</html>
```

### 5.2 Kreiraj `templates/landing.html`
```html
{% extends "base.html" %}

{% block title %}Dobrodosli{% endblock %}

{% block content %}
    <h2>Dobrodosli u Proton Flask aplikaciju</h2>
    <p>Da biste nastavili, prijavite se ili napravite novi nalog.</p>

    <p>
        <a class="button-link" href="/login">Prijava</a>
    </p>
    <p>
        <a class="button-link" href="/register">Registracija</a>
    </p>
{% endblock %}
```

### 5.3 Kreiraj `templates/login.html`
```html
{% extends "base.html" %}

{% block title %}Prijava{% endblock %}

{% block content %}
    <h2>Prijava</h2>
    <form action="/login" method="post">
        <label for="username">Korisničko ime:</label>
        <input type="text" id="username" name="username" required>

        <label for="password">Lozinka:</label>
        <input type="password" id="password" name="password" required>

        <button type="submit">Prijavi se</button>
    </form>
{% endblock %}
```

### 5.4 Kreiraj `templates/register.html`
```html
{% extends "base.html" %}
    
{% block title %}Registracija{% endblock %}

{% block content %}
    <h2>Registracija</h2>
    <form action="/register" method="post">
        <label for="username">Korisničko ime:</label>
        <input type="text" id="username" name="username" required>

        <label for="password">Lozinka:</label>
        <input type="password" id="password" name="password" required>

        <button type="submit">Registruj se</button>
    </form>
{% endblock %}
```

### 5.5 Kreiraj `templates/index.html`
```html
{% extends "base.html" %}

{% block content %}
    <h1>{{ username }}</h1>
    <p>Trenutno imaš {{ number_of_tasks }} zadataka.</p>

    <form action="/logout" method="post">
        <button type="submit">Odjavi se</button>
    </form>

    <ul>
        {% for task in tasks %}
            <li>
                {{ task.name }}
                <form action="/delete_task/{{ task.id }}" method="post" style="display:inline;">
                    <button type="submit">Obriši</button>
                </form>
            </li>
        {% endfor %}
    </ul>

    <form action="/add_task" method="post">
        <input type="text" name="task" placeholder="Unesi novi zadatak" required>
        <button type="submit">Dodaj zadatak</button>
    </form>

{% endblock %}
```

---

## 🎨 Korak 6: CSS (Stil)

### 6.1 Kreiraj `static/style/main.css`
```css
body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px;
    font-family: Arial, sans-serif;
    background: #e9eef5;
    color: #222;
}

main {
    width: 100%;
    max-width: 700px;
    background: #fff;
    border: 1px solid #d3d9e2;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.button-link,
button {
    display: inline-block;
    padding: 10px 14px;
    border: 1px solid #cfd7e3;
    border-radius: 6px;
    background: #ffffff;
    color: #1f2937;
    font-size: 14px;
    text-decoration: none;
    cursor: pointer;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}

.button-link:hover,
button:hover {
    background: #f5f7fb;
    border-color: #bfc9d8;
}

.button-link:active,
button:active {
    background: #edf1f7;
}

form {
    margin: 10px 0;
}

input {
    padding: 9px 10px;
    border: 1px solid #cfd7e3;
    border-radius: 6px;
}
```

---

## 🚀 Korak 7: Glavna Flask Aplikacija

### 7.1 Kreiraj `main.py`

```python
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models.user import db, User, Task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'tajna'

db.init_app(app)

with app.app_context():
    db.create_all()


# Preuzima trenutno ulogovanog korisnika iz sesije
def get_logged_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)


# Prikazuje landing stranicu ili task dashboard
@app.route('/')
def index():
    current_user = get_logged_user()
    if not current_user:
        return render_template('landing.html')

    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template(
        'index.html',
        username=current_user.username,
        number_of_tasks=len(user_tasks),
        tasks=user_tasks,
    )

# Dodaje novi zadatak za trenutnog korisnika
@app.route('/add_task', methods=['POST'])
def add_task():
    current_user = get_logged_user()
    if not current_user:
        return redirect('/login')

    form = request.form
    task_name = form.get('task')
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    if task_name and task_name not in [task.name for task in user_tasks]:
        new_task = Task(name=task_name, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
    return redirect('/')

# Registruje novog korisnika i automatski ga loguje
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        username = form.get('username')
        password = form.get('password')
        password_hash = generate_password_hash(password)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Korisnik sa tim username-om vec postoji.')
            return redirect('/register')

        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        return redirect('/')
    return render_template('register.html')

# Proverava kredencijale i loguje korisnika
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = request.form
        username = form.get('username')
        password = form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect('/')
        flash('Pogresni kredencijali. Pokusaj ponovo.')
        return redirect('/login')
    return render_template('login.html')


# Briše sesiju korisnika i isloguje ga
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect('/')

# Briše zadatak ako ga je kreirao trenutni korisnik
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    current_user = get_logged_user()
    if not current_user:
        return redirect('/login')

    task = db.session.get(Task, task_id)
    if task and task.owner.id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
```

---

## ▶️ Korak 8: Pokretanje Aplikacije

### 8.1 Pokrenite Flask aplikaciju
Iz foldera `FlaskRadionica`, u PowerShell-u unesi:
```powershell
python main.py
```

Trebalo bi da vidis nešto kao:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 8.2 Otvori u pregledniku
Idi na `http://127.0.0.1:5000` ili `http://localhost:5000`

Trebalo bi da vidiš landing stranicu sa "Prijava" i "Registracija" dugmadima.

---

## ✅ Testiranje Aplikacije

1. **Kreiraj nov nalog**: Klikni na "Registracija", unesi username i lozinku
2. **Loguj se**: Sa novim nalogom, vrati se na landing i klikni "Prijava"
3. **Dodaj zadatak**: Na task stranici, unesi zadatak i klikni "Dodaj zadatak"
4. **Obriši zadatak**: Klikni na "Obriši" pored zadatka
5. **Logout**: Klikni na "Odjavi se" dugme

---

## 🔑 Ključni Koncepti

### Flask Rute
```python
@app.route('/path', methods=['GET', 'POST'])
def function_name():
    return render_template('template.html')
```
- Rute mapiraju URL na Python funkcije
- `methods` određuje koje HTTP metode prihvata (GET = display, POST = submit)

### Sesije
```python
session['user_id'] = user.id  # Sačuva user_id u sesiji
current_user_id = session.get('user_id')  # Preuzima iz sesije
```
- Sesije čuvaju podatke za svakog korisnika između zahteva

### Šabloniranje (Templating)
```html
{% if condition %}
    Show HTML
{% endif %}

{% for item in list %}
    {{ item.name }}
{% endfor %}
```
- Jinja2 šablonski jezik omogućava Python logiku u HTML-u

### Baza Podataka
```python
new_user = User(username=username, password_hash=password_hash)
db.session.add(new_user)
db.session.commit()
```
- SQLAlchemy omogućava rad sa bazom bez SQL pisanja

---

## 🐛 Česte Greške

| Greška | Razlog | Rešenje |
|--------|--------|--------|
| `ModuleNotFoundError: No module named 'flask'` | Flask nije instaliran | `pip install flask` |
| `TemplateNotFound` | Html fajl je u pogrešnoj lokaciji | Proverite da fajl postoji u `templates/` |
| `RuntimeError: The session is unavailable` | Secret key nije postavljen | Dodajte `app.secret_key = 'neka-tajna'` |
| Baza podataka je prazna | Nije pokrenut `db.create_all()` | Ponovo pokrenite aplikaciju |

---

## 📚 Dodatni Resursi

- [Flask Dokumentacija](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Jinja2 Template Engine](https://jinja.palletsprojects.com/)

---

**Sažetak**: Ovaj roadmap te vodi kroz sve korake od postavljanja Python okruženja do potpuno funkcionalne Flask aplikacije sa korisnicima, autentifikacijom i task menadžmentom!
