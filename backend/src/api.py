from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import json

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth
from .logger import logging

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


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    """
    get all drinks in the drink.short() format
    :return:
    """
    try:
        drinks = db.session.query(Drink).all()
        long_format = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": long_format
        }), 200
    except Exception as err:
        logging.error(err)
        abort(400)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    request_body = request.json
    recipe = str(request_body.get('recipe'))
    title = str(request_body.get('title'))
    recipe = recipe.replace("\'", "\"")
    val_recipe = json.loads(recipe)
    if not validate_long_format(val_recipe):
        abort(400)
    drink = Drink(title, recipe)
    drink.insert()
    return jsonify({
        "success": True,
        "drinks": drink.long()
    }), 200


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(drink_id):
    drink = db.session.query(Drink).get(drink_id)
    if drink is None:
        return abort(404)
    request_body = request.json
    recipe = str(request_body.get('recipe'))
    title = str(request_body.get('title'))
    recipe = recipe.replace("\'", "\"")
    val_recipe = json.loads(recipe)
    if not validate_long_format(val_recipe):
        abort(400)
    drink.title = title
    drink.recipe = recipe
    drink.update()
    return jsonify({
        "success": True,
        "drinks": drink.long()
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    try:
        drink = db.session.query(Drink).get(drink_id)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except Exception as err:
        logging.error(err)
        abort(404)


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


@app.errorhandler(AuthError)
def auth_error(error):
    msg = error.args
    message = msg[0]
    status_code = msg[1]
    return jsonify({
        "success": False,
        "error": status_code,
        "message": message.get('description')
    }), status_code


def validate_long_format(_dict):
    keys = ["name", "color", "parts"]
    for key in keys:
        for data in _dict:
            if key not in data.keys():
                return False
    return True


# Default port:
if __name__ == '__main__':
    app.run()
