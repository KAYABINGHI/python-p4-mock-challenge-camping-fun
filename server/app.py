#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class CampersResource(Resource):
    def get(self):
        campers = Camper.query.all()
        return [camper.to_dict(only=('id', 'name', 'age')) for camper in campers], 200

    def post(self):
        data = request.get_json()
        try:
            camper = Camper(name=data.get('name'), age=data.get('age'))
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(only=('id', 'name', 'age')), 201
        except Exception as e:
            return {"errors": ["validation errors"]}, 400

class CamperByIdResource(Resource):
    def get(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return {"error": "Camper not found"}, 404
        camper_dict = camper.to_dict()
        camper_dict['signups'] = [signup.to_dict() for signup in camper.signups]
        return camper_dict, 200

    def patch(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return {"error": "Camper not found"}, 404
        data = request.get_json()
        try:
            if 'name' in data:
                camper.name = data['name']
            if 'age' in data:
                camper.age = data['age']
            db.session.commit()
            return camper.to_dict(only=('id', 'name', 'age')), 202
        except Exception as e:
            return {"errors": ["validation errors"]}, 400

class ActivitiesResource(Resource):
    def get(self):
        activities = Activity.query.all()
        return [activity.to_dict(only=('id', 'name', 'difficulty')) for activity in activities], 200

class ActivityByIdResource(Resource):
    def delete(self, id):
        activity = Activity.query.get(id)
        if not activity:
            return {"error": "Activity not found"}, 404
        db.session.delete(activity)
        db.session.commit()
        return '', 204

class SignupsResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            signup = Signup(
                camper_id=data.get('camper_id'),
                activity_id=data.get('activity_id'),
                time=data.get('time')
            )
            db.session.add(signup)
            db.session.commit()
            signup_dict = signup.to_dict()
            signup_dict['activity'] = signup.activity.to_dict(only=('id', 'name', 'difficulty'))
            signup_dict['camper'] = signup.camper.to_dict(only=('id', 'name', 'age'))
            return signup_dict, 201
        except Exception as e:
            return {"errors": ["validation errors"]}, 400

api.add_resource(CampersResource, '/campers')
api.add_resource(CamperByIdResource, '/campers/<int:id>')
api.add_resource(ActivitiesResource, '/activities')
api.add_resource(ActivityByIdResource, '/activities/<int:id>')
api.add_resource(SignupsResource, '/signups')

@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)