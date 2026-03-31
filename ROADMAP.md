# Flask Task Manager - Roadmap za Pocetnike

Ovaj roadmap vodi te korak po korak kako da od nule napravis Flask aplikaciju sa registracijom, prijavom, sesijom korisnika i listom zadataka.

## 1. Postavljanje okruzenja

1. Proveri Python:

```powershell
python --version
```

2. Napravi projekat i udji u folder:

```powershell
mkdir FlaskRadionica
cd FlaskRadionica
```

3. Napravi virtualno okruzenje:

```powershell
python -m venv venv
```

4. Aktiviraj ga (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

Ako vidis `(venv)` na pocetku linije, spreman si.

## 2. Instalacija paketa

Instaliraj pakete:

```powershell
pip install flask flask-sqlalchemy werkzeug
```

## 3. Napravi strukturu projekta

Napravi ovu strukturu:

```text
FlaskRadionica/
├── instance/
├── models/
│   ├── __init__.py
│   └── user.py
├── routes/
│   ├── __init__.py
│   └── web.py
├── static/
│   └── style/
│       └── main.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── landing.html
│   ├── login.html
│   └── register.html
├── main.py
└── ROADMAP.md
```

`instance/` ce Flask koristiti za SQLite fajl baze.

## 4. Models package

### 4.1 Kreiraj models/user.py

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

### 4.2 Kreiraj models/__init__.py

```python
from .user import db, User, Task

__all__ = ['db', 'User', 'Task']
```

Zasto ovo radimo: svuda mozes da pises `from models import db, User, Task`, bez direktnog importa iz `models/user.py`.

## 5. Routes package (Blueprint)

### 5.1 Kreiraj routes/web.py

```python
from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Task

web_bp = Blueprint('web', __name__)


def get_logged_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)


@web_bp.route('/')
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


@web_bp.route('/add_task', methods=['POST'])
def add_task():
    current_user = get_logged_user()
    if not current_user:
        return redirect('/login')

    task_name = request.form.get('task')
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    if task_name and task_name not in [task.name for task in user_tasks]:
        db.session.add(Task(name=task_name, user_id=current_user.id))
        db.session.commit()
    return redirect('/')


@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Korisnik sa tim username-om vec postoji.')
            return redirect('/register')

        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        return redirect('/')
    return render_template('register.html')


@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect('/')

        flash('Pogresni kredencijali. Pokusaj ponovo.')
        return redirect('/login')

    return render_template('login.html')


@web_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect('/')


@web_bp.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    current_user = get_logged_user()
    if not current_user:
        return redirect('/login')

    task = db.session.get(Task, task_id)
    if task and task.owner.id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect('/')
```

### 5.2 Kreiraj routes/__init__.py

```python
from .web import web_bp


def register_routes(app):
    app.register_blueprint(web_bp)
```

Zasto blueprint: kad aplikacija poraste, lako delis rute u vise fajlova (`auth.py`, `tasks.py`, itd.).

## 6. Main aplikacija

Kreiraj main.py:

```python
from flask import Flask

from models import db
from routes import register_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'tajna'

db.init_app(app)

with app.app_context():
    db.create_all()

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
```

## 7. Templates

Napomena: zadrzi sledece fajlove u `templates/`:

1. `base.html` - osnovni layout + prikaz flash poruke (dialog)
2. `landing.html` - stranica za neulogovanog korisnika
3. `login.html` - forma za prijavu
4. `register.html` - forma za registraciju
5. `index.html` - lista zadataka za ulogovanog korisnika

Ako vec imas ove fajlove u projektu, ne moras ih ponovo pisati.

## 8. CSS

Kreiraj `static/style/main.css` sa minimalnim modernim stilom (centar + card izgled + dugmici).

Ako vec postoji fajl, samo ga koristi.

## 9. Pokretanje aplikacije

U root folderu projekta:

```powershell
python main.py
```

Ako je sve dobro, videces:

```text
* Running on http://127.0.0.1:5000
```

Otvori u browseru: `http://127.0.0.1:5000`

## 10. Sta testirati

1. Otvori landing stranicu
2. Registruj novog korisnika
3. Pokusaj registraciju sa istim username-om (treba poruka greske)
4. Logout
5. Login sa pogresnom lozinkom (treba poruka greske)
6. Login sa ispravnom lozinkom
7. Dodaj zadatak
8. Obrisi zadatak

## 11. Ceste greske i resenja

1. `ModuleNotFoundError: No module named 'flask'`
Resenje: aktiviraj `venv` pa uradi `pip install flask`.

2. `TemplateNotFound`
Resenje: proveri da su HTML fajlovi u `templates/`.

3. `The session is unavailable because no secret key was set`
Resenje: proveri da postoji `app.secret_key = '...'`.

4. Import konflikt sa routes
Resenje: koristi `routes` folder sa `__init__.py` i nemoj da imas stari `routes.py` fajl.

5. Baza je prazna
Resenje: proveri da se poziva `db.create_all()` unutar `app.app_context()`.

## 12. Sledeci koraci (kad savladas osnove)

1. Dodaj `status` i `due_date` u Task model
2. Dodaj CSRF zastitu preko Flask-WTF
3. Premesti `secret_key` u environment varijable
4. Dodaj Flask-Migrate za migracije baze
