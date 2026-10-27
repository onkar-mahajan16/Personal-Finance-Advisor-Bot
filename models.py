import json
from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

PROFILE_TYPES = ("salaried", "student", "freelancer", "household")

# (name, kind) - kind is "essential" or "discretionary"
DEFAULT_CATEGORIES = [
    ("Rent", "essential"),
    ("Groceries", "essential"),
    ("Utilities", "essential"),
    ("Transport", "essential"),
    ("Healthcare", "essential"),
    ("Education", "essential"),
    ("Dining out", "discretionary"),
    ("Entertainment", "discretionary"),
    ("Shopping", "discretionary"),
    ("Subscriptions", "discretionary"),
    ("Other", "discretionary"),
]


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_type = db.Column(db.String(20), nullable=False, default="salaried")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email,
                "profile_type": self.profile_type}


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    name = db.Column(db.String(60), nullable=False)
    kind = db.Column(db.String(20), nullable=False, default="discretionary")
    __table_args__ = (db.UniqueConstraint("user_id", "name", name="uq_category_user_name"),)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "kind": self.kind}


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    source = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    note = db.Column(db.String(200))

    def to_dict(self):
        return {"id": self.id, "source": self.source, "amount": self.amount,
                "date": self.date.isoformat(), "note": self.note or ""}


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    note = db.Column(db.String(200))
    category = db.relationship("Category")

    def to_dict(self):
        return {"id": self.id, "category_id": self.category_id,
                "category": self.category.name, "amount": self.amount,
                "date": self.date.isoformat(), "note": self.note or ""}


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    month = db.Column(db.String(7), nullable=False)  # YYYY-MM
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    limit_amount = db.Column(db.Float, nullable=False, default=0)
    __table_args__ = (db.UniqueConstraint("user_id", "month", "category_id",
                                          name="uq_budget_user_month_cat"),)


class SavingsGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    saved_amount = db.Column(db.Float, nullable=False, default=0)
    deadline = db.Column(db.Date)

    def to_dict(self):
        today = date.today()
        remaining = max(self.target_amount - self.saved_amount, 0)
        monthly_needed = None
        if self.deadline and remaining > 0:
            months_left = max((self.deadline.year - today.year) * 12
                              + (self.deadline.month - today.month), 1)
            monthly_needed = round(remaining / months_left, 2)
        return {
            "id": self.id, "name": self.name, "target_amount": self.target_amount,
            "saved_amount": self.saved_amount, "remaining": round(remaining, 2),
            "progress": round(min(self.saved_amount / self.target_amount, 1) * 100, 1)
            if self.target_amount else 0,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "monthly_needed": monthly_needed,
        }


class MonthlyReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    month = db.Column(db.String(7), nullable=False)
    payload = db.Column(db.Text, nullable=False)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("user_id", "month", name="uq_report_user_month"),)

    def to_dict(self):
        data = json.loads(self.payload)
        data["month"] = self.month
        data["created_at"] = self.created_at.isoformat()
        return data


def seed_categories(user_id):
    for name, kind in DEFAULT_CATEGORIES:
        db.session.add(Category(user_id=user_id, name=name, kind=kind))
