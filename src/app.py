"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory, Blueprint, render_template
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from api.models import db, User, Contact
from api.routes import api , get_all_agenda
from api.admin import setup_admin
from api.commands import setup_commands
# from flask_jwt_extended import JWTManager
import psycopg2

#from models import Person

#ENV = os.getenv("FLASK_DEBUG")
ENV = 0
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

# app.config["JWT_SECRET_KEY"] = "valentino"
# jwt = JWTManager(app)

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type = True)
db.init_app(app)

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == 1:
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append(url)
            jsonify (url)
            return jsonify(links)
        
@app.route("/contacts")
def get_all_contacts():
    contact = Contact.query.all() #way to get all the contacts
    seri_contact= []
    for person in contact:
        seri_contact.append(person.serialize())
    return jsonify(seri_contact), 200

@app.route('/add', methods=['POST'])
def add_contact():
    print(request.method) 
    body = request.get_json()
    contact = Contact(full_name=body['full_name'], email=body['email'], address=body['address'], phone=body['phone'], status=body['status'])
    db.session.add(contact)
    db.session.commit()
    response = jsonify(contact.serialize())
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get(id)
    if contact is None:
        raise APIException('User not found', status_code=404)
    db.session.delete(contact)
    db.session.commit()
    response_body = {
        "msg": "Hello, you just deleted a contact"
    }
    return jsonify(response_body), 200

@app.route('/delete', methods=['DELETE'])
def delete_all_contacts():
    contacts = Contact.query.all()
    for contact in contacts:
        db.session.delete(contact)
    db.session.commit()
    response_body = {
        "msg": "Hello, you just deleted all contacts"
    }
    return jsonify(response_body), 200

@app.route('/update/<int:id>', methods=['PUT'])
def update_contact(id):
    body = request.get_json()
    contact = Contact.query.get(id)
    if contact is None:
        raise APIException('User not found', status_code=404)

    if "full_name" in body:
        contact.full_name = body["full_name"]
    if "email" in body:
        contact.email = body["email"]
    if "address" in body:
        contact.address = body['address']
    if "phone" in body:
        contact.phone = body['phone']
    if "status" in body:
        contact.status = body['status']
    db.session.commit()
    return jsonify(contact.serialize()), 200

# any other endpoint will try to serve it like a static file
# @app.route('/<path:path>', methods=['GET'])
# def serve_any_other_file(path):
#     if not os.path.isfile(os.path.join(static_file_dir, path)):
#         path = 'index.html'
#     response = send_from_directory(static_file_dir, path)
#     response.cache_control.max_age = 0 # avoid cache memory
#     return response


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
