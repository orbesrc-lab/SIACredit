from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

def generate_id():
    return uuid.uuid4().hex[:9]

class Factor(db.Model):
    __tablename__ = 'factors'
    id = db.Column(db.String(20), primary_key=True, default=generate_id)
    number = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    weight = db.Column(db.Float, default=0)

    characteristics = db.relationship('Characteristic', backref='factor', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'name': self.name,
            'weight': self.weight,
            'characteristics': [c.to_dict() for c in self.characteristics]
        }

class Characteristic(db.Model):
    __tablename__ = 'characteristics'
    id = db.Column(db.String(20), primary_key=True, default=generate_id)
    factor_id = db.Column(db.String(20), db.ForeignKey('factors.id'), nullable=False)
    number = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    weight = db.Column(db.Float, default=0)

    aspects = db.relationship('Aspect', backref='characteristic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'name': self.name,
            'weight': self.weight,
            'aspects': [a.to_dict() for a in self.aspects]
        }

class Aspect(db.Model):
    __tablename__ = 'aspects'
    id = db.Column(db.String(20), primary_key=True, default=generate_id)
    char_id = db.Column(db.String(20), db.ForeignKey('characteristics.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text
        }

class Evidence(db.Model):
    __tablename__ = 'evidences'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aspect_id = db.Column(db.String(20), db.ForeignKey('aspects.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='revision')
    description = db.Column(db.Text)
    table_data = db.Column(db.JSON)
    date = db.Column(db.String(50))
    user_email = db.Column(db.String(150))

    def to_dict(self):
        return {
            'name': self.name,
            'status': self.status,
            'date': self.date,
            'user': self.user_email
        }

class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    char_id = db.Column(db.String(20), db.ForeignKey('characteristics.id'), nullable=False, unique=True)
    rating = db.Column(db.Float, default=0)
    just = db.Column(db.Text)

    def to_dict(self):
        return {
            'rating': self.rating,
            'just': self.just
        }

class ExternalReport(db.Model):
    __tablename__ = 'external_reports'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    char_id = db.Column(db.String(20), db.ForeignKey('characteristics.id'), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(50))

    def to_dict(self):
        return {
            'name': self.name,
            'date': self.date
        }

class StatisticData(db.Model):
    __tablename__ = 'statistics'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    table_id = db.Column(db.String(50), nullable=False, unique=True)
    data_json = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'table_id': self.table_id,
            'data': self.data_json
        }

class Institution(db.Model):
    __tablename__ = 'institution'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default="Universidad Institucional")
    logo_url = db.Column(db.String(500), default="")
    description = db.Column(db.Text, default="")

    def to_dict(self):
        return {
            'name': self.name,
            'logo_url': self.logo_url,
            'description': self.description
        }
