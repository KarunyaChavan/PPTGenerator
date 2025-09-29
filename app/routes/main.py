from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import current_user, login_required
from app.models.presentation import Presentation
from app.models.user import User

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    """Homepage - redirect authenticated users to their dashboards"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    
    # Show stats for anonymous users
    total_presentations = Presentation.query.count()
    total_users = User.query.filter_by(role='user').count()
    approved_presentations = Presentation.query.filter_by(status='approved').count()
    
    stats = {
        'total_presentations': total_presentations,
        'total_users': total_users,
        'approved_presentations': approved_presentations
    }
    
    return render_template('main/index.html', stats=stats)

@bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')