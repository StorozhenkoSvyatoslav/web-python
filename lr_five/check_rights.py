from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user

def check_rights(action):
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Для доступа необходимо авторизироваться!', 'warning')
                return redirect(url_for('login_form'))
            allowed_roles = {
                'create_user': ['admin'], 
                'edit_user': ['admin', 'user'],
                'view_user': ['admin', 'user'],
                'delete_user': ['admin'],
                'visit_report': ['admin', 'user'],
                'page_report': ['admin'],
                'user_report': ['admin'],
                'role_editor': ['admin']
            }
            required_roles = allowed_roles.get(action, [])

            if not any(current_user.has_role(role) for role in required_roles):
                flash('У вас недостаточно прав для доступа к данной странице!', 'warning')
                return redirect(request.referrer or url_for('index'))
            
            target_user_id = kwargs.get('user_id')
            if target_user_id and not current_user.has_role('admin'):
                if current_user.id != int(target_user_id):
                    flash('У вас недостаточно прав для доступа к чужим данным!', 'warning')
                    return redirect(request.referrer or url_for('index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator    
    