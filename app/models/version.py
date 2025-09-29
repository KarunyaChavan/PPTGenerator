from datetime import datetime
import os
from app import db

class PresentationVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentation.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    
    # Version metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    change_description = db.Column(db.Text)
    
    # Content snapshot (for rollback purposes)
    content_snapshot = db.Column(db.Text)  # JSON string of content at this version
    
    # Relationships
    presentation = db.relationship(
        'Presentation',
        back_populates='versions'
    )
    creator = db.relationship(
        'User',
        foreign_keys=[created_by],
        back_populates='created_versions'
    )
    
    def get_file_size_mb(self):
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    def file_exists(self):
        return os.path.exists(self.file_path)
    
    def delete_file(self):
        if self.file_exists():
            try:
                os.remove(self.file_path)
                return True
            except OSError:
                return False
        return False
    
    def get_download_name(self):
        presentation = self.presentation
        safe_title = "".join(c for c in presentation.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return f"{safe_title}_v{self.version_number}.pptx"
    
    def __repr__(self):
        return f'<PresentationVersion {self.presentation.title} v{self.version_number}>'
    
    __table_args__ = (db.UniqueConstraint('presentation_id', 'version_number'),)
