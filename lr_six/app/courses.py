from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from models import db, Course, Category, User, Review
from tools import CoursesFilter, ImageSaver

bp = Blueprint('courses', __name__, url_prefix='/courses')

COURSE_PARAMS = [
    'author_id', 'name', 'category_id', 'short_desc', 'full_desc'
]

def params():
    return { p: request.form.get(p) or None for p in COURSE_PARAMS }

def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': [x for x in request.args.getlist('category_ids') if x],
    }

@bp.route('/')
def index():
    courses = CoursesFilter(**search_params()).perform()
    pagination = db.paginate(courses, per_page=5) ##################
    courses = pagination.items
    categories = db.session.execute(db.select(Category)).scalars()
    return render_template('courses/index.html',
                           courses=courses,
                           categories=categories,
                           pagination=pagination,
                           search_params=search_params())

@bp.route('/my')
@login_required
def my_courses():
    courses = db.session.execute(
        db.select(Course).filter_by(author_id=current_user.id)
    ).scalars().all()
    return render_template('courses/my_courses.html', courses=courses)
    
@bp.route('/new')
@login_required
def new():
    course = Course()
    categories = db.session.execute(db.select(Category)).scalars()
    users = db.session.execute(db.select(User)).scalars()
    return render_template('courses/new.html',
                           categories=categories,
                           users=users,
                           course=course)

@bp.route('/create', methods=['POST'])
@login_required
def create():
    form_data = params()
    f = request.files.get('background_img')
    required_fields = {
        'name': 'Название',
        'category_id': 'Категория',
        'short_desc': 'Краткое описание',
        'full_desc': 'Полное описание'
    }
    errors = []
    for field, label in required_fields.items():
        if not form_data.get(field) or not form_data.get(field).strip():
            errors.append(f'Поле "{label}" обязательно для заполнения.')
            
    if not f or not f.filename:
        errors.append('Необходимо загрузить фоновое изображение.')
    
    if errors:
        for error in errors:
            flash(error, 'danger')
        # сохраняем данные которые ввели, чтобы при перезагрузке ничего не пропало
        categories = db.session.execute(db.select(Category)).scalars()
        users = db.session.execute(db.select(User)).scalars()
        course = Course(**form_data)
        return render_template('courses/new.html', 
                               categories=categories, 
                               users=users, 
                               course=course)
    
    img = None
    course = Course()
    try:
        if f and f.filename:
            img = ImageSaver(f).save()

        image_id = img.id if img else None
        course = Course(**params(), background_image_id=image_id)
        db.session.add(course)
        db.session.commit()
        
    except IntegrityError as err:
        flash(f'Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})', 'danger')
        db.session.rollback()
        categories = db.session.execute(db.select(Category)).scalars()
        users = db.session.execute(db.select(User)).scalars()
        return render_template('courses/new.html',
                            categories=categories,
                            users=users,
                            course=Course(**form_data))

    flash(f'Курс {course.name} был успешно добавлен!', 'success')

    return redirect(url_for('courses.index'))

@bp.route('/<int:course_id>')
def show(course_id):
    course = db.get_or_404(Course, course_id)
    
    reviews = db.session.execute(
        db.select(Review).filter_by(course_id=course_id).order_by(Review.created_at.desc()).limit(5)
        ).scalars().all()
    
    user_review = None
    if current_user.is_authenticated:
        user_review = db.session.execute(
            db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)
            ).scalar()
    
    return render_template('courses/show.html', course=course, reviews=reviews, user_review=user_review)

@bp.route('/<int:course_id>/reviews')
def reviews(course_id):
    course = db.get_or_404(Course, course_id)

    sort_order = request.args.get('sort', 'new')
    
    query = db.select(Review).filter_by(course_id=course_id)
    
    if sort_order == 'positive':
        query = query.order_by(Review.rating.desc())
    elif sort_order == 'negative':
        query = query.order_by(Review.rating.asc())
    else:
        query = query.order_by(Review.created_at.desc())
        
    pagination = db.paginate(query, per_page=5)
    reviews_list = pagination.items
    
    user_review = None
    if current_user.is_authenticated:
        user_review = db.session.execute(
            db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)
        ).scalar()
        
    return render_template('courses/reviews.html', 
                           course=course, 
                           reviews=reviews_list, 
                           pagination=pagination, 
                           sort_order=sort_order,
                           user_review=user_review)
    

@bp.route('/<int:course_id>/reviews/create', methods=['POST'])
@login_required
def create_review(course_id):
    course = db.get_or_404(Course, course_id)
    
    # проверяем на дубликат отзыва, чтобы не оставить второго на всякий
    existing_review = db.session.execute(
        db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)
    ).scalar()
    
    if existing_review:
        flash('Вы уже оставили отзыв.', 'warning')
        return redirect(url_for('courses.show', course_id=course_id))
        
    rating = int(request.form.get('rating', 5))
    text = request.form.get('text')
    
    if not text:
        flash('Текст отзыва не может быть пустым.', 'danger')
        return redirect(url_for('courses.show', course_id=course_id))
        
    try:
        new_review = Review(rating=rating, text=text, course_id=course_id, user_id=current_user.id)
        
        # пересчитываем рейтинг
        course.rating_sum += rating
        course.rating_num += 1
        
        db.session.add(new_review)
        db.session.commit()
        flash('Отзыв успешно добавлен!', 'success')
    except Exception as err:
        db.session.rollback()
        flash(f'Ошибка при сохранении: {err}', 'danger')
        
    return redirect(url_for('courses.show', course_id=course_id))