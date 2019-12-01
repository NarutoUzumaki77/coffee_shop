import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth
from logger import logging

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET, POST, PATCH, DELETE, OPTIONS')
    return response


db_drop_and_create_all()


@app.route('/drinks')
def get_drinks():
    """
    get all drinks in the drink.short() format
    :return:
    """
    try:
        drinks = db.session.query(Drink).all()
        short_format = [drink.short() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": short_format
        }), 200
    except Exception as err:
        logging.error(err)
        abort(400)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where 
    drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where 
    drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where 
    drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id 
    is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": error.code,
        "message": "Unprocessable"
    }), error.code


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": error.code,
        "message": "Resource not found"
    }), error.code


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        'error': error.code,
        'message': "Authorization Failed"
    }), error.code


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        'error': error.code,
        'message': "Permission Denied"
    }), 403


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        'error': error.code,
        'message': "Bad Request"
    }), 400


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        'error': error.code,
        'message': "Internal Server Error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

# Default port:
if __name__ == '__main__':
    app.run()
