from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    tierlists = db.relationship('Tierlist', backref='creator', lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'tierlists': [tier_list.serialize() for tier_list in self.tierlists]
        }

class Tierlist(db.Model):
    __tablename__ = 'tierlists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    categories = db.relationship('Category', backref='tierlist', lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'categories': [category.serialize() for category in self.categories]
        }

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    tierlist_id = db.Column(db.Integer, db.ForeignKey('tierlists.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    elements = db.relationship('Element', backref='category', lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'tierlist_id': self.tierlist_id,
            'name': self.name,
            'order': self.order,
            'elements': [element.serialize() for element in self.elements]
        }

class Element(db.Model):
    __tablename__ = 'elements'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    img = db.Column(db.String(255), nullable=True)  # Campo para almacenar la URL o el nombre del archivo de la foto

    def serialize(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'img': self.img  
        }
