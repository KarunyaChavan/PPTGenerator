from datetime import datetime
import json
from app import db
from app.models.version import PresentationVersion

class Presentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Author information
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Presentation content
    agenda = db.Column(db.Text)  # JSON string for agenda items
    content_data = db.Column(db.Text)  # JSON string for all slide content

    # Admin review
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviewed_at = db.Column(db.DateTime)
    review_notes = db.Column(db.Text)

    # Current version tracking
    current_version = db.Column(db.Integer, default=1)

    # Relationships
    author = db.relationship(
        'User',
        foreign_keys=[author_id],
        back_populates='authored_presentations'
    )
    reviewer = db.relationship(
        'User',
        foreign_keys=[reviewed_by],
        back_populates='reviewed_presentations'
    )
    versions = db.relationship(
        'PresentationVersion',
        back_populates='presentation',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def get_current_version(self):
        return self.versions.filter_by(version_number=self.current_version).first()

    def get_latest_version(self):
        return self.versions.order_by(PresentationVersion.version_number.desc()).first()
        
    @property
    def slides(self):
        """Get slides from content_data JSON"""
        if not self.content_data:
            return []
        try:
            # Try parsing as direct list of slides
            data = json.loads(self.content_data)
            if isinstance(data, list):
                return data
            # Try as nested structure
            if isinstance(data, dict) and 'slides' in data:
                return data['slides']
            return []
        except json.JSONDecodeError:
            return []

    def approve(self, admin_user, notes=None):
        self.status = 'approved'
        self.reviewed_by = admin_user.id
        self.reviewed_at = datetime.utcnow()
        if notes:
            self.review_notes = notes
        db.session.commit()

    def reject(self, admin_user, notes=None):
        self.status = 'rejected'
        self.reviewed_by = admin_user.id
        self.reviewed_at = datetime.utcnow()
        if notes:
            self.review_notes = notes
        db.session.commit()

    def reset_to_pending(self):
        self.status = 'pending'
        self.reviewed_by = None
        self.reviewed_at = None
        self.review_notes = None
        db.session.commit()

    def __repr__(self):
        return f'<Presentation {self.title}>'
