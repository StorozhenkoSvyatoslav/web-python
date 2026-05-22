from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import Role, User, db
from database import init_db
import os, re
from validate_reg_data import validate_reg_data
from forms import UserForm
from wtforms.validators import Optional
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '123123123'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'users.db')

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view = 'login_form'
login_manager.login_message = 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации!'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user_from_bd(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/task')
def task():
    return render_template('task.html')

@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember = request.form.get('rememberme') == 'on'
        
        existing_user: User = User.query.filter_by(login = login).first()
        if existing_user and existing_user.check_password(password):
            login_user(existing_user, remember=remember)
            flash('Авторизация прошла успешно!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль!', 'danger')
            return(render_template('login.html', method='GET'))
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def reg_form():
    if request.method == 'POST':
        login = request.form.get('login').strip()
        first_name = request.form.get('first_name').strip()
        last_name = request.form.get('last_name').strip()
        middle_name = request.form.get('middle_name').strip() or None
        password = request.form.get('password', '')
        
        errors = validate_reg_data(login, password, first_name, last_name, middle_name)
        
        if not errors:
            #ПРОВЕРКА НА СУЩЕСТВУЮЩЕГО ЮЗЕРА!
            existing_user = User.query.filter_by(login=login).first()
            if existing_user:
                flash('Логин уже занят! Попробуйте ввести другой!', 'danger')
                return render_template('register.html', method='GET')
            
            new_user = User(
                login = login,
                first_name = first_name,
                last_name = last_name,
                middle_name = middle_name
                )
            
            new_user.set_password(password)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Вы зарегистрировались!', 'success')
                return redirect(url_for('login_form'))
        
            except ValueError as e:
                db.session.rollback()
                flash(f'Ошибка при регистрации: {str(e)}', 'danger')
                
        else:
            return render_template('register.html', errors=errors)
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из аккаунта!', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def my_profile():   
    user_info = {
        'id': current_user.id,
        'login': current_user.login,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'middle_name': current_user.middle_name,
        'role': current_user.role_id,
        'created_at': current_user.created_at
    }
    
    return (render_template('profile.html', user=user_info))

@app.route('/create', methods=['POST', 'GET'])
@login_required
def create_user():
    form = UserForm()
    
    if form.validate_on_submit():
        ex_user = User.query.filter_by(login=form.login.data).first()
        if ex_user:
            flash('Данный логин уже занят! Попробуйте другой!', 'danger')
        else:
            new_user = User(
                login=form.login.data.strip(),
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                middle_name=form.middle_name.data.strip() or None,
                role_id=form.role_id.data if form.role_id.data != 0 else None
            )
            new_user.set_password(form.password.data)
        
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Аккаунт успешно создан!', 'success')
                return redirect(url_for('index'))
            except ValueError as e:
                db.session.rollback()
                flash(f'Ошибка при создании аккаунта: {str(e)}', 'danger')
    
    return render_template(
        'user_form.html',
        form=form,
        title="Создание нового пользователя",
        is_create=True,
        submit_text='Создать'
    )
            
@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user: User = User.query.filter_by(id=int(user_id)).first()
    form = UserForm(obj=user)
    
    form.password.validators = [Optional()]
    form.login.validators = []
    
    if form.validate_on_submit():
        user.first_name = form.first_name.data.strip()
        user.last_name = form.last_name.data.strip()
        user.middle_name = form.middle_name.data.strip() or None
        user.role_id = form.role_id.data if form.role_id.data != 0 else None
        
        try:   
            db.session.commit()
            flash('Данные пользователя обновлены!', 'success')
            return redirect(url_for('index'))
        except ValueError as e:
            db.session.rollback()
            flash(f'Ошибка при редактировании аккаунта: {str(e)}', 'danger')
        
    return render_template(
        'user_form.html',
        form=form,
        title=f"Редактирование пользователя №{user.id}",
        is_create=False,
        submit_text='Сохранить'
    )
    
@app.route('/roles', methods=['POST', 'GET'])
@login_required
def roles():
    all_roles = Role.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name_role').strip()
        desc = request.form.get('desc_role').strip()
        
        ex_role = Role.query.filter_by(name=name).first()
        if ex_role:
            flash('Такая роль уже существует! Попробуйте создать другую!', 'danger')
            return render_template('roles.html', method='GET', roles=all_roles)
        new_role = Role(
            name=name,
            description=desc
        )
        try:
            db.session.add(new_role)
            db.session.commit()
            flash('Роль успешно добавлена!', 'success')
            return render_template('roles.html', method='GET', roles=all_roles)
        except ValueError as e:
            db.session.rollback()
            flash(f'Ошибка при создании роли: {str(e)}', 'danger')
            
    
    return (render_template('roles.html', roles=all_roles))

@app.route('/user/<int:user_id>')
def user_page(user_id):
    user: User = User.query.filter_by(id=int(user_id)).first()
    return (render_template('user.html', user=user))

@app.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user: User = User.query.filter_by(id=int(user_id)).first()
    if not user:
        flash('Пользователь не найден!', 'danger')
    else:
        try:
            db.session.delete(user)
            db.session.commit()
            flash(f'Пользователь {user.last_name} {user.first_name} успешно удалён!', 'success')
        except ValueError as e:
            db.session.rollback()
            flash(f'Ошибка при удалении: {str(e)}!', 'danger')
    
    return redirect(url_for('index'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    errors = {}
    user: User = User.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':
        old_pw = request.form.get('old_pw', '').strip()
        new_pw = request.form.get('new_pw', '').strip()
        new_pw_con = request.form.get('new_pw_con', '').strip()
        
        if not old_pw:
            errors['old_pw'] = 'Введите старый пароль!'
        elif not user.check_password(old_pw):
            errors['old_pw'] = 'Неверный старый пароль!'
        if not new_pw:
            errors['new_pw'] = 'Введите новый пароль!'
        else:
            allowed_symbols = r'^[a-zA-Zа-яА-ЯёЁ0-9~!?@#$%^&*_\-+()\[\]{}></\\|\'".,;:]+$'
            if len(new_pw) < 8:
                errors['new_pw'] = 'Пароль должен содержать не менее 8 символов!'
            elif len(new_pw) > 128:
                errors['new_pw'] = 'Пароль должен содержать не более 128 символов!'
            elif ' ' in new_pw:
                errors['new_pw'] = 'Пароль не должен содержать пробелов!'
            elif not re.search(r'[0-9]', new_pw):
                errors['new_pw'] = 'Пароль должен содержать хотя бы одну цифру!'
            elif not re.match(allowed_symbols, new_pw):
                errors['new_pw'] = 'Пароль содержит недопустимые символы!'
            elif not re.search(r'[A-ZА-Я]', new_pw):
                errors['new_pw'] = 'Пароль должен содержать хотя бы одну заглавную букву!'
            elif not re.search(r'[a-zа-я]', new_pw):
                errors['new_pw'] = 'Пароль должен содержать хотя бы одну строчную букву!'
        if new_pw and new_pw_con and new_pw != new_pw_con:
            errors['new_pw_con'] = 'Пароли не совпадают!'
        
        if not errors: 
            user.set_password(new_pw)
            try:
                db.session.commit()
                flash('Пароль успешно изменен!', 'success')
                return redirect(url_for('index'))
            except ValueError as e:
                db.session.rollback()
                flash(f'Ошибка при смене пароля: {str(e)}!', 'danger')      
    
    return render_template('change_pw.html', errors=errors)

if __name__ == '__main__':
    try:
        init_db(app)
        app.run(debug=True)
    except ValueError as e:
        print("Ошибка:", e)