import re

def validate_reg_data(login, password, fn, ln, mn=None):
    #словарь для хранения ошибок каждого поля в регистрационной форме
    errors = {}
    
    #блок проверки логина
    if not login:
        errors['login'] = 'Поле "Логин" не может быть пустым!'
    elif len(login) < 5:
        errors['login'] = 'Логин должен содержать не менее 5 символов!'
    elif not re.match(r'^[a-zA-Z0-9]+$', login):
        errors['login'] = 'Логин должен содержать только латинские буквы и цифры!'
        
    #блок проверки ФИО
    if not fn:
        errors['first_name'] = 'Поле "Имя" не может быть пустым!'
    if not ln:
        errors['last_name'] = 'Поле "Фамилия" не может быть пустым!'
        
    
    #блок проверки пароля
    allowed_symbols = r'^[a-zA-Zа-яА-ЯёЁ0-9~!?@#$%^&*_\-+()\[\]{}></\\|\'".,;:]+$'
    if not password:
        errors['password'] = 'Поле "Пароль" не может быть пустым!'
    else:
        if len(password) < 8:
            errors['password'] = 'Пароль должен содержать не менее 8 символов!'
        elif len(password) > 128:
            errors['password'] = 'Пароль должен содержать не более 128 символов!'
        elif ' ' in password:
            errors['password'] = 'Пароль не должен содержать пробелов!'
        elif not re.search(r'[0-9]', password):
            errors['password'] = 'Пароль должен содержать хотя бы одну цифру!'
        elif not re.match(allowed_symbols, password):
            errors['password'] = 'Пароль содержит недопустимые символы!'
        elif not re.search(r'[A-ZА-Я]', password):
            errors['password'] = 'Пароль должен содержать хотя бы одну заглавную букву!'
        elif not re.search(r'[a-zа-я]', password):
            errors['password'] = 'Пароль должен содержать хотя бы одну строчную букву!'
    
    return errors
        
    