from flask import Flask, render_template, send_from_directory
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
import click
from models import db, Category, Image, Course, Review
from auth import bp as auth_bp, init_login_manager
from courses import bp as courses_bp

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

db.init_app(app)
migrate = Migrate(app, db)

init_login_manager(app)

@app.cli.command('delete-review')
@click.argument('review_id', type=int)
def delete_review(review_id):
    """Delete a review and recalculate the course rating."""
    review = db.session.get(Review, review_id)
    if review is None:
        click.echo(f'Review {review_id} not found.')
        return

    course = db.session.get(Course, review.course_id)
    if course is None:
        click.echo(f'Course {review.course_id} not found.')
        return

    if course.rating_num > 0:
        course.rating_sum = max(0, course.rating_sum - review.rating)
        course.rating_num = max(0, course.rating_num - 1)
    else:
        course.rating_sum = 0
        course.rating_num = 0

    db.session.delete(review)
    db.session.commit()
    click.echo(f'Deleted review {review_id} and updated course {course.id} rating.')

@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(err):
    error_msg = ('Возникла ошибка при подключении к базе данных. '
                 'Повторите попытку позже.')
    return f'{error_msg} (Подробнее: {err})', 500

app.register_blueprint(auth_bp)
app.register_blueprint(courses_bp)

@app.route('/')
def index():
    categories = db.session.execute(db.select(Category)).scalars()
    return render_template(
        'index.html',
        categories=categories,
    )

@app.route('/images/<image_id>')
def image(image_id):
    img = db.get_or_404(Image, image_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               img.storage_filename)
