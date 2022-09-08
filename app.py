# import flask dkk
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# import library pendukung
import jwt
import os
import datetime

# inisiasi objek flask dkk
app = Flask(__name__)
api = Api(app)
db  = SQLAlchemy(app)
CORS(app)

# konfigurasi database
filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///' + os.path.join(filename, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database

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
            return make_response(jsonify({"msg":"Berhasil login"}), 200)
        return make_response(jsonify({"msg":"Login Gagal, Silahkan coba lagi!"}), 400)

api.add_resource(RegisterUser, "/api/register", methods=["POST"])
api.add_resource(LoginUser, "/api/login", methods=["POST"])

if __name__== "__main__":
    app.run(debug=True)

