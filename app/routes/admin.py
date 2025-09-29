from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from app import db
from app.models.presentation import Presentation
from app.models.version import PresentationVersion
from app.models.user import User
from app.utils.forms import ReviewForm

bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    # Get statistics
    stats = {
        'total_presentations': Presentation.query.count(),
        'pending_presentations': Presentation.query.filter_by(status='pending').count(),
        'approved_presentations': Presentation.query.filter_by(status='approved').count(),
        'rejected_presentations': Presentation.query.filter_by(status='rejected').count(),
        'total_users': User.query.filter_by(role='user').count(),
        'total_versions': PresentationVersion.query.count()
    }
    
    # Recent presentations needing review
    recent_pending = Presentation.query.filter_by(status='pending')\
        .order_by(Presentation.created_at.desc())\
        .limit(5)\
        .all()
    
    # Recent activity
    recent_activity = Presentation.query\
        .order_by(Presentation.updated_at.desc())\
        .limit(10)\
        .all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_presentations=recent_activity,  # <-- add this line
                         recent_pending=recent_pending,
                         recent_activity=recent_activity)

@bp.route('/presentations')
@login_required
@admin_required
def list_presentations():
    """List all presentations with filtering"""
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = Presentation.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    presentations = query.order_by(Presentation.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/presentations.html', 
                         presentations=presentations, 
                         status_filter=status_filter)

@bp.route('/presentation/<int:id>/review', methods=['GET', 'POST'])
@login_required
@admin_required
def review_presentation(id):
    """Review a specific presentation"""
    presentation = Presentation.query.get_or_404(id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        presentation.status = form.status.data
        presentation.review_notes = form.feedback.data
        presentation.reviewed_at = datetime.utcnow()
        presentation.reviewed_by = current_user.id
        
        try:
            db.session.commit()
            flash(f'Presentation "{presentation.title}" has been {form.status.data}.', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating presentation. Please try again.', 'danger')
    
    # Pre-fill form if presentation was already reviewed
    if presentation.review_notes:
        form.feedback.data = presentation.review_notes
        form.status.data = presentation.status
    
    # Get all versions
    versions = presentation.versions.order_by(PresentationVersion.version_number.desc()).all()
    
    return render_template('admin/review.html', 
                         presentation=presentation, 
                         versions=versions,
                         form=form)

@bp.route('/presentation/<int:id>/versions')
@login_required
@admin_required
def view_versions(id):
    """View all versions of a presentation"""
    presentation = Presentation.query.get_or_404(id)
    versions = presentation.versions.order_by(PresentationVersion.version_number.desc()).all()
    return render_template('admin/versions.html', presentation=presentation, versions=versions)

@bp.route('/presentation/<int:presentation_id>/rollback/<int:version_number>', methods=['POST'])
@login_required
@admin_required
def rollback_version(presentation_id, version_number):
    """Rollback to a specific version"""
    presentation = Presentation.query.get_or_404(presentation_id)
    target_version = presentation.versions.filter_by(version_number=version_number).first_or_404()
    try:
        # Update current version
        presentation.current_version = version_number
        # Restore content and file info
        presentation.content_data = target_version.content_snapshot
        presentation.updated_at = target_version.created_at
        # Optionally update title/description/agenda if you want full rollback
        # presentation.title = ...
        # presentation.description = ...
        # presentation.agenda = ...
        db.session.commit()
        flash(f'Successfully rolled back to version {version_number}. Status reset to pending.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error rolling back version: {str(e)}', 'error')
    return redirect(url_for('admin.view_versions', id=presentation_id))

@bp.route('/users')
@login_required
@admin_required
def list_users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.filter_by(role='user')\
        .order_by(User.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users)

@bp.route('/user/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(id):
    """Toggle user active status"""
    user = User.query.get_or_404(id)
    
    if user.role == 'admin':
        flash('Cannot modify admin user status.', 'error')
        return redirect(url_for('admin.list_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    
    return redirect(url_for('admin.list_users'))