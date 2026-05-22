from flask import Flask, render_template, session, request, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
applications = app
app.secret_key = '123123123'

login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view = 'auth_form'
login_manager.login_message = 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации!'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, id, login, password):
        self.id = id
        self.login = login
        self.password = password
        
# имитируем бд, типо список зарегавшихся юзеров
users = {
    'user': User(1, 'user', 'qwerty'),
    'user1': User(2, 'user1', 'qwerty1'),
}

@login_manager.user_loader
def load_user_from_bd(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None
        

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guest-count')
def guest_count():
    if 'visit_count' in session:
        session['visit_count'] += 1 #добавляем +1 если уже посещали
    else:
        session['visit_count'] = 1 #первое посещение
    
    count_visits = session.get('visit_count')
    return render_template('guest_count.html', count=count_visits)

@app.route('/auth', methods=['GET', 'POST'])
def auth_form():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember = request.form.get('rememberme') == 'on'
        
        user = users.get(login)
        if user and user.password == password:
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            return(redirect(url_for('index')))
        else:
            flash('Неверный логин или пароль!', 'danger')
            return(render_template('auth.html', method='GET'))
        
    return render_template('auth.html')

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('Вы вышли из аккаунта!', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def my_profile():
    user_id = current_user.id
    user_login = current_user.login
    
    user_info = {
        'id': user_id,
        'login': user_login
    }
    
    return (render_template('profile.html', user=user_info))

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except ValueError as e:
        print("Ошибка:", e)