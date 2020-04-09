import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from flask_rbac import RBAC

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


# ROUTES
# NO AUTH REQUIRED -- PUBLIC ENDPOINT
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]
    return jsonify({
        "drinks": drinks,
        "success": True
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]
        return jsonify({
            "drinks": drinks,
            "success": True
        }), 200
    except AuthError as err:
        abort(401)


# Create a new beverage ☕
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(token):
    try:
        body = request.get_json()
        user_input = {
            "title": body.get('title', None),
            "recipe": json.dumps(body.get('recipe', None))
        }
        if (user_input['title'] is None or user_input['recipe'] is None):
            raise Exception('Invalid input')

        drink = Drink(title=user_input['title'], recipe=user_input['recipe'])

        db.session.add(drink)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as err:
        db.session.rollback()
        db.session.close()
        return jsonify({"success": False, "error": str(err)})


# Update an existing beverage
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token, drink_id):
    try:
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            raise Exception("Drink of ID %s was not found" % (drink_id))
        user_input = {
            "title": body.get('title', drink.title),
            "recipe": json.dumps(body.get('recipe', drink.recipe))
        }
        drink.title = user_input['title']
        drink.recipe = user_input['recipe']
        drink.update()
        return jsonify({"success": True, "updated_drink": drink.long()})
    except Exception as err:
        db.session.rollback()
        db.session.close()
        return jsonify({"success": False, "error": str(err)})


# Delete a drink
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            raise Exception('Drink with ID %s not found' % (drink_id))
        db.session.delete(drink)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as err:
        return jsonify({"success": False, "error": str(err)})


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Route not found"
    }), 404


@app.errorhandler(401)
def user_unauthenticated(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "User not authenticated"
    }), 401


@app.errorhandler(AuthError)
def user_is_unauthenticated(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "User not authenticated"
    }), 401
