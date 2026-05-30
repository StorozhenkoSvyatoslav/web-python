import io, csv
from flask import Blueprint, render_template, request, Response
from models import User, VisitLog, db
from sqlalchemy import func
from flask_login import login_required, current_user
from check_rights import check_rights

stats_bp = Blueprint('stats', __name__, url_prefix='/stats')

@stats_bp.route('/visits')
@login_required
def visits_report():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    query = VisitLog.query
    if not current_user.has_role('admin'):
        query = query.filter_by(user_id=current_user.id)
    pagination = query.order_by(VisitLog.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('visits.html', pagination=pagination)

@stats_bp.route('/pages')
@login_required
@check_rights('page_report')
def pages_report():
    report_data = db.session.query(
        VisitLog.path, 
        func.count(VisitLog.id).label('count')
    ).group_by(VisitLog.path).order_by(func.count(VisitLog.id).desc()).all()

    if request.args.get('export') == 'csv':
        return export_csv(report_data, ['№', 'Страница', 'Количество посещений'])

    return render_template('pages_report.html', report_data=report_data)

@stats_bp.route('/users')
@login_required
@check_rights('user_report')
def users_report():
    report_data = db.session.query(
        VisitLog.user_id, 
        func.count(VisitLog.id).label('count')
    ).group_by(VisitLog.user_id).order_by(func.count(VisitLog.id).desc()).all()

    end_data = []
    for user_id, count in report_data:
        user = User.query.get(user_id) if user_id else None
        if user:
            name = f"{user.last_name} {user.first_name} {user.middle_name or ''}".strip()
        else:
            name = 'Неаутентифицированный пользователь'
        end_data.append({'name': name, 'count': count})

    if request.args.get('export') == 'csv':
        return export_csv(end_data, ['№', 'Пользователь', 'Количество посещений'])

    return render_template('users_report.html', report_data=end_data)


def export_csv(data, headers):
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(headers)
    for i, item in enumerate(data, 1):
        if isinstance(item, dict):
            writer.writerow([i, item['name'], item['count']])
        else:
            writer.writerow([i, item[0], item[1]])

    output.seek(0)
    return Response(
        output.getvalue().encode('utf-8-sig'),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=report.csv"}
    )