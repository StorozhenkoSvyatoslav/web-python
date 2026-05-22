from flask import Flask, render_template, request, make_response
from phone_valid import phone_number_valid

app = Flask(__name__)
applications = app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/url_params')
def url_parametres():
    req = request.args.to_dict() #получаем параметры URL и передаем их на страницу
    return render_template('url_params.html', title='Параметры URL', params=req)

@app.route('/header_request')
def header_request():
    headers_req = dict(request.headers)
    return render_template('header_request.html', title='Заголовки запроса', headers=headers_req)

@app.route('/cookies')
def cookie_info():
    cookies = dict(request.cookies)
    return render_template('cookie_info.html', title='Cookies', cookies=cookies)

@app.route('/login-form', methods=['GET', 'POST'])
def form_params():
    form_data = None
    if request.method == 'POST':
        form_data = {
            'username': request.form.get('username', ''),
            'email': request.form.get('email', ''),
            'password': request.form.get('password', '')
        }
        response = make_response(render_template('form_params.html', title='Авторизация', method='POST', form_data=form_data))
        return response
    
    return render_template('form_params.html', title='Авторизация', method='GET')

@app.route('/phone', methods=['GET', 'POST'])
def phone_form():
    result = None
    error = None
    phone_input = ''
    if request.method == 'POST':
        phone_input = request.form.get('phone', '').strip()
        try:    
            result = phone_number_valid(phone_input)
        except ValueError as err:
            error = str(err)
        
        return render_template('phone_form.html', title='Номер телефона', method='POST', result=result, error=error)
    
    return render_template('phone_form.html', title='Номер телефона', method='GET')

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except ValueError as e:
        print("Ошибка:", e)