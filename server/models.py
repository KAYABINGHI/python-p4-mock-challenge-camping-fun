from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Relationship: Activity has many Signups
    signups = db.relationship('Signup', back_populates='activity', cascade='all, delete')
    campers = association_proxy('signups', 'camper')

    # Serialization rules
    serialize_rules = ('-signups.activity', '-signups.camper.activities', '-signups.camper.signups')
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # Relationship: Camper has many Signups
    signups = db.relationship('Signup', back_populates='camper', cascade='all, delete')
    activities = association_proxy('signups', 'activity')

    # Serialization rules
    serialize_rules = ('-signups.camper', '-signups.activity.campers', '-signups.activity.signups')

    # Validations
    @validates('name')
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError('Name must be present')
        return value

    @validates('age')
    def validate_age(self, key, value):
        if value is None or not (8 <= value <= 18):
            raise ValueError('Age must be between 8 and 18')
        return value
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    # Relationships
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    camper = db.relationship('Camper', back_populates='signups')
    activity = db.relationship('Activity', back_populates='signups')

    # Serialization rules
    serialize_rules = ('-camper.signups', '-activity.signups', '-camper.activities', '-activity.campers')

    # Validations
    @validates('time')
    def validate_time(self, key, value):
        if value is None or not (0 <= value <= 23):
            raise ValueError('Time must be between 0 and 23')
        return value

    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.