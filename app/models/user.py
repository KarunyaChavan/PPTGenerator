from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user' or 'admin'
    department = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    # All presentations authored by this user
    authored_presentations = db.relationship(
        'Presentation',
        back_populates='author',
        foreign_keys='Presentation.author_id',
        lazy='dynamic'
    )

    # All presentations reviewed by this user (if admin)
    reviewed_presentations = db.relationship(
        'Presentation',
        back_populates='reviewer',
        foreign_keys='Presentation.reviewed_by',
        lazy='dynamic'
    )

    # Versions created by this user
    created_versions = db.relationship(
        'PresentationVersion',
        back_populates='creator',
        foreign_keys='PresentationVersion.created_by',
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'
