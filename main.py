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

# Briše sesiju korisnika i izloguje ga
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