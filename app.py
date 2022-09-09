# import flask dkk
from urllib.request import Request
from webbrowser import get
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# import library pendukung
import jwt
import os
import datetime

# import library untuk membuat decorator
from functools import wraps

# inisiasi objek flask dkk
app = Flask(__name__)
api = Api(app)
db  = SQLAlchemy(app)
CORS(app)

# konfigurasi database
filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///' + os.path.join(filename, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database

#konfigurasi secrect key
app.config['SECRET_KEY'] = "inisecretkeyya"

# decorator authenticate endpoint
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        # token akan diparsing melalui parameter di endpoint
        token = request.args.get('token')

        # cek token ada atau tidak
        if not token:
            return make_response(jsonify({
                "msg" : "token not found"
            }), 404)

        # decode token yang diterima
        try:
            output = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            # output = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # return output
            return make_response(jsonify({"msg":"token invalid"}), 400)
        
        return f(*args, **kwargs)
    return decorator

# membuat schema model database authenticate (login, register)
class AuthModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))

# membuat schema model blog
class BlogModel(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    judul   = db.Column(db.String(100))
    konten  = db.Column(db.Text)
    penulis = db.Column(db.String(50))

# create model database kedalam file db.sqlite
db.create_all()

# membuat routing endpoint
# routing authenticate
class RegisterUser(Resource):
    # posting data dari frontend 
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')

        # cek apakah username & password ada
        if dataUsername and dataPassword :
            # tulis data authenticate ke db.sqlite
            result = AuthModel(username=dataUsername, password=dataPassword)
            db.session.add(result)
            db.session.commit()

            return make_response(jsonify({"msg":"Registrasi berhasil"}), 200)
        return make_response(jsonify({"msg":"Username dan Password tidak boleh kosong"}), 400)

class LoginUser(Resource):
    def post(self):
        dataUsername = request.form.get('username')     
        dataPassword = request.form.get('password')

        # query matching kecocokan data
        queryUsername = [data.username for data in AuthModel.query.all()]
        queryPassword = [data.password for data in AuthModel.query.all()]

        if dataUsername in queryUsername and dataPassword in queryPassword :
            # generate token authenticate 
            token = jwt.encode({
                "username":queryUsername, "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            return make_response(jsonify({"msg":"Berhasil login", "token":token}), 200)
        return make_response(jsonify({"msg":"Login Gagal, Silahkan coba lagi!"}), 400)

class AddArticle(Resource):
    @token_required
    def post(self):
        dataTitle   = request.form.get('judul')
        dataContent = request.form.get('konten')
        dataWritter = request.form.get('penulis')

        data = BlogModel(judul=dataTitle,konten=dataContent,penulis=dataWritter)
        db.session.add(data)
        db.session.commit()

        return make_response(jsonify({"msg":"Data berhasil ditambahkan"}), 200)

class ShowArticle(Resource):
    @token_required
    def get(self):
        result = BlogModel.query.all()

        output = [{
            "id"    : data.id,
            "title" : data.judul,
            "content" : data.konten,
            "writter" : data.penulis
        } for data in result]

        return make_response(jsonify(output), 200)

api.add_resource(RegisterUser, "/api/register", methods=["POST"])
api.add_resource(LoginUser, "/api/login", methods=["POST"])
api.add_resource(AddArticle, "/api/blog-post", methods=["POST"])
api.add_resource(ShowArticle, "/api/blog-show", methods=["GET"])

if __name__== "__main__":
    app.run(debug=True)

