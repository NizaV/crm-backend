"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Contact
from api.utils import generate_sitemap, APIException

api = Blueprint('api', __name__)


# Handle/serialize errors like a JSON object
@api.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@api.route('/agenda', methods=['GET'])
def get_all_agenda():
    contact = Contact.query.all() #way to get all the contacts
    seri_contact= []
    for person in contact:
        seri_contact.append(person.serialize())
    print(contact)
    return jsonify(seri_contact), 200

@api.route('/add', methods=['POST'])
def add_contact():
    print(request.method)
    body = request.get_json()
    contact = Contact(full_name=body['full_name'], email=body['email'], address=body['address'], phone=body['phone'], status=body['status'])
    db.session.add(contact)
    db.session.commit()
    print(contact)
    return jsonify(contact.serialize()), 200

@api.route('/delete/<int:id>', methods=['DELETE'])
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

@api.route('/delete', methods=['DELETE'])
def delete_all_contacts():
    contacts = Contact.query.all()
    for contact in contacts:
        db.session.delete(contact)
    db.session.commit()
    response_body = {
        "msg": "Hello, you just deleted all contacts"
    }
    return jsonify(response_body), 200

@api.route('/update/<int:id>', methods=['PUT'])
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
