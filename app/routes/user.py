from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.presentation import Presentation
from app.models.version import PresentationVersion
from app.utils.forms import PresentationForm
from app.services.ppt_generator import PPTGeneratorService
import json
import os
from datetime import datetime

bp = Blueprint('user', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing their presentations"""
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    
    # Get user's presentations with pagination
    page = request.args.get('page', 1, type=int)
    presentations = current_user.authored_presentations.order_by(
        Presentation.created_at.desc()
    ).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Statistics
    stats = {
        'total': current_user.authored_presentations.count(),
        'pending': current_user.authored_presentations.filter_by(status='pending').count(),
        'approved': current_user.authored_presentations.filter_by(status='approved').count(),
        'rejected': current_user.authored_presentations.filter_by(status='rejected').count()
    }
    
    return render_template('user/dashboard.html', presentations=presentations, stats=stats)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_presentation():
    """Create a new presentation"""
    if current_user.is_admin():
        flash('Admins cannot create presentations directly.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    form = PresentationForm()
    
    if form.validate_on_submit():
        try:
            # Parse slides data from JSON
            slides_data = json.loads(form.slides_data.data)
            
            # Create presentation record
            presentation = Presentation(
                title=form.title.data,
                description=form.description.data,
                agenda=form.agenda.data,
                content_data=json.dumps(slides_data),
                author_id=current_user.id
            )
            
            db.session.add(presentation)
            db.session.flush()  # Get the presentation ID
            
            # Generate PPT file
            ppt_service = PPTGeneratorService()
            file_path, filename = ppt_service.generate_presentation(
                presentation, slides_data
            )
            
            # Create initial version
            version = PresentationVersion(
                presentation_id=presentation.id,
                version_number=1,
                filename=filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                created_by=current_user.id,
                change_description='Initial version',
                content_snapshot=json.dumps(slides_data)
            )
            
            db.session.add(version)
            db.session.commit()
            
            flash('Presentation created successfully! It is now pending review.', 'success')
            return redirect(url_for('user.view_presentation', id=presentation.id))
            
        except json.JSONDecodeError:
            flash('Invalid slides data format.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating presentation: {str(e)}', 'error')
    
    return render_template('user/create.html', form=form)

@bp.route('/presentation/<int:id>')
@login_required
def view_presentation(id):
    """View a specific presentation"""
    presentation = Presentation.query.get_or_404(id)
    
    # Check if user owns the presentation or is admin
    if not current_user.is_admin() and presentation.author_id != current_user.id:
        flash('You do not have permission to view this presentation.', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Debug: Print content_data
    print("Content Data:", presentation.content_data)
    if presentation.content_data:
        try:
            print("Parsed Content:", json.loads(presentation.content_data))
        except json.JSONDecodeError as e:
            print("JSON Parse Error:", str(e))
    
    # Get versions
    versions = presentation.versions.order_by(PresentationVersion.version_number.desc()).all()
    
    return render_template('user/view_presentation.html', 
                         presentation=presentation, 
                         versions=versions)

@bp.route('/download/<int:presentation_id>/<int:version_number>')
@login_required
def download_presentation(presentation_id, version_number):
    """Download a specific version of a presentation"""
    presentation = Presentation.query.get_or_404(presentation_id)
    
    # Check permissions
    if not current_user.is_admin() and presentation.author_id != current_user.id:
        flash('You do not have permission to download this presentation.', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Only allow download of approved presentations for regular users
    if not current_user.is_admin() and presentation.status != 'approved':
        flash('This presentation is not yet approved for download.', 'warning')
        return redirect(url_for('user.view_presentation', id=presentation_id))
    
    version = presentation.versions.filter_by(version_number=version_number).first_or_404()
    
    if not version.file_exists():
        flash('The requested file is not available.', 'error')
        return redirect(url_for('user.view_presentation', id=presentation_id))
    
    return send_file(
        version.file_path,
        as_attachment=True,
        download_name=version.get_download_name(),
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )

@bp.route('/presentation/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_presentation(id):
    """Edit an existing presentation (creates a new version)"""
    presentation = Presentation.query.get_or_404(id)
    if presentation.author_id != current_user.id:
        flash('You do not have permission to edit this presentation.', 'error')
        return redirect(url_for('user.dashboard'))

    form = PresentationForm(obj=presentation)
    slides_list = []
    try:
        slides_list = json.loads(presentation.content_data) if presentation.content_data else []
    except Exception:
        slides_list = []

    if form.validate_on_submit():
        try:
            # Parse slides data from JSON
            slides_data = json.loads(form.slides_data.data)
            # Update presentation fields
            presentation.title = form.title.data
            presentation.description = form.description.data
            presentation.agenda = form.agenda.data
            presentation.content_data = json.dumps(slides_data)
            presentation.updated_at = datetime.utcnow()
            # Generate new PPT file
            ppt_service = PPTGeneratorService()
            file_path, filename = ppt_service.generate_presentation(presentation, slides_data)
            # Increment version number
            latest_version = presentation.get_latest_version()
            new_version_number = (latest_version.version_number + 1) if latest_version else 1
            # Create new version record
            version = PresentationVersion(
                presentation_id=presentation.id,
                version_number=new_version_number,
                filename=filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                created_by=current_user.id,
                change_description='Edited by user',
                content_snapshot=json.dumps(slides_data)
            )
            db.session.add(version)
            presentation.current_version = new_version_number
            # Update presentation's file info to match the new version
            presentation_file_attrs = ['filename', 'file_path', 'file_size']
            for attr in presentation_file_attrs:
                setattr(presentation, attr, getattr(version, attr, None))
            db.session.commit()
            flash('Presentation updated successfully! A new version has been created.', 'success')
            return redirect(url_for('user.view_presentation', id=presentation.id))
        except json.JSONDecodeError:
            flash('Invalid slides data format.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating presentation: {str(e)}', 'error')
    # Pre-fill form with current data
    if request.method == 'GET':
        form.title.data = presentation.title
        form.description.data = presentation.description
        form.agenda.data = presentation.agenda
        form.slides_data.data = presentation.content_data
    return render_template('user/edit.html', form=form, presentation=presentation, slides_list=slides_list)
