"""Database models shared by the school website and its private administration area."""
from datetime import datetime, timezone
import uuid

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Submission(db.Model):
    __table_args__ = (
        db.CheckConstraint("kind IN ('contact', 'visit', 'admission')", name="submission_kind"),
        db.CheckConstraint("status IN ('new', 'contacted', 'closed')", name="submission_status"),
    )
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(20), unique=True, nullable=False,
                          default=lambda: 'QW-' + uuid.uuid4().hex[:12].upper())
    kind = db.Column(db.String(20), nullable=False, index=True)
    parent_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    child_first_name = db.Column(db.String(80))
    age_range = db.Column(db.String(40))
    programme = db.Column(db.String(60))
    preferred_date = db.Column(db.Date)
    message = db.Column(db.Text, nullable=False, default='')
    consent = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='new', index=True)
    notes = db.Column(db.Text, nullable=False, default='')
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False, index=True)


class NewsPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    title = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(40), nullable=False, default='Learning at home')
    excerpt = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)
    image_key = db.Column(db.String(30), nullable=False, default='discover')
    published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
