from models import db, Role

def init_db(app):
    with app.app_context():
        db.create_all()
        if not Role.query.filter_by(name='admin').first():
            db.session.add(Role(name='admin', description='Администратор'))
        if not Role.query.filter_by(name='user').first():
            db.session.add(Role(name='user', description='Пользователь'))
        db.session.commit()