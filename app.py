import os
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from models import db, User, Tierlist, Category, Element
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tierlist.db'
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Carpeta donde se guardarán las imágenes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite de tamaño de archivo a 16 MB

db.init_app(app)
CORS(app)
migrate = Migrate(app, db)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST']) # CREATE ELEMENT IMG
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'filename': filename}), 201
    return jsonify({'error': 'File not allowed'}), 400

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE']) # SAY HI!
def main():
    return jsonify({"msg": "Hola, Tierlist"}), 200

#
# CRUD USERS ENDPOINTS
#

@app.route('/users', methods=['GET'])  # ALL USERS
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@app.route('/users/<int:id>', methods=['GET'])  # SINGLE USER
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.serialize())

@app.route('/users', methods=['POST'])  # NEW USER
def create_user():
    data = request.get_json()
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

@app.route('/users/<int:id>', methods=['DELETE'])  # DELETE USER
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

#
# CRUD TIERLIST ENDPOINTS
#

@app.route('/tierlists', methods=['GET'])  # GET ALL
def get_tierlists():
    tierlists = Tierlist.query.all()
    return jsonify([tierlist.serialize() for tierlist in tierlists])

@app.route('/tierlists/<int:id>', methods=['GET'])
def get_tierlist(id):
    tierlist = Tierlist.query.get(id)
    if tierlist:
        response = {
            'id': tierlist.id,
            'title': tierlist.title,
            'created_by': tierlist.created_by,
            'description': tierlist.description,
            'categories': [cat.serialize() for cat in tierlist.categories]
        }
        return jsonify(response)
    else:
        return jsonify({'error': 'Tierlist not found'}), 404

@app.route('/tierlists', methods=['POST'])  # CREATE NEW TIERLIST
def create_tierlist():
    data = request.get_json()
    new_tierlist = Tierlist(
        title=data['title'],
        description=data.get('description'),
        created_by=data['created_by']
    )
    db.session.add(new_tierlist)
    db.session.commit()
    return jsonify(new_tierlist.serialize()), 201

@app.route('/tierlists/<int:tierlist_id>', methods=['PUT'])  # UPDATE TIERLIST
def update_tierlist(tierlist_id):
    data = request.get_json()
    tierlist = Tierlist.query.get(tierlist_id)
    if tierlist is None:
        return jsonify({'error': 'Tierlist not found'}), 404
    tierlist.title = data['title']
    tierlist.description = data.get('description')
    db.session.commit()
    return jsonify(tierlist.serialize())

@app.route('/tierlists/<int:tierlist_id>', methods=['DELETE'])  # DELETE TIERLIST
def delete_tierlist(tierlist_id):
    tierlist = Tierlist.query.get(tierlist_id)
    if tierlist is None:
        return jsonify({'error': 'Tierlist not found'}), 404
    db.session.delete(tierlist)
    db.session.commit()
    return jsonify({'message': 'Tierlist deleted'})

#
# CRUD CATEGORIES ENDPOINTS
#

@app.route('/categories', methods=['GET'])  # GET ALL CATEGORIES
def get_categories():
    categories = Category.query.all()
    return jsonify([category.serialize() for category in categories])

@app.route('/categories/<int:category_id>', methods=['GET'])  # GET SINGLE CATEGORY
def get_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'error': 'Category not found'}), 404
    return jsonify(category.serialize())

@app.route('/categories', methods=['POST'])  # CREATE NEW CATEGORY
def create_category():
    data = request.get_json()
    new_category = Category(
        tierlist_id=data['tierlist_id'],
        name=data['name'],
        order=data['order']
    )
    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.serialize()), 201

@app.route('/categories/<int:category_id>', methods=['PUT'])  # UPDATE CATEGORY
def update_category(category_id):
    data = request.get_json()
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'error': 'Category not found'}), 404
    category.name = data['name']
    category.order = data['order']
    db.session.commit()
    return jsonify(category.serialize())

@app.route('/categories/<int:category_id>', methods=['DELETE'])  # DELETE SINGLE CATEGORY
def delete_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'error': 'Category not found'}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted'})

#
# CRUD ELEMENT ENDPOINTS
#

@app.route('/elements', methods=['GET'])  # GET ALL ELEMENTS
def get_elements():
    elements = Element.query.all()
    return jsonify([element.serialize() for element in elements])

@app.route('/elements', methods=['POST'])  # CREATE NEW ELEMENT
def create_element():
    data = request.form
    file = request.files.get('img')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_element = Element(
            category_id=data['category_id'],
            name=data['name'],
            img=filename
        )
        db.session.add(new_element)
        db.session.commit()
        return jsonify(new_element.serialize()), 201
    return jsonify({'error': 'File not allowed or missing'}), 400

@app.route('/elements/<int:element_id>', methods=['PUT'])  # UPDATE ELEMENT
def update_element(element_id):
    data = request.get_json()
    element = Element.query.get(element_id)
    if element is None:
        return jsonify({'error': 'Element not found'}), 404
    element.name = data['name']
    if 'img' in request.files:
        file = request.files['img']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            element.img = filename
    db.session.commit()
    return jsonify(element.serialize())

@app.route('/elements/<int:element_id>', methods=['DELETE'])  # DELETE ELEMENT
def delete_element(element_id):
    element = Element.query.get(element_id)
    if element is None:
        return jsonify({'error': 'Element not found'}), 404
    db.session.delete(element)
    db.session.commit()
    return jsonify({'message': 'Element deleted'})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
