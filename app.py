from flask import Flask, request, render_template, redirect #se importan de Flask (el framework). Formato: from <la libreria> import herramientas entre comas
import requests #Modulo, para utilizar las herramientas de esta libreria para consumir la API
#el FRAMEWORK tiene una estructura de como utilizar y las librerias tienen funciones sueltas.
import os

from models import db
from models import Favorite

app = Flask(__name__)

# configuracion de base de datos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'app.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}' #config es un diccionario de configuraciond de sqlalchemy. 
#Las tres barras indican que lo siguiente sera la ruta local
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Es false para no hacer el seguimiento interno de las modificaciones 

db.init_app(app) #Permite conectar el objeto db a la aplicacion

with app.app_context():   #hace que se ejecute algo y se cierre de forma automatica
    db.create_all()

#URL de la API
API_URL = 'https://rickandmortyapi.com/api/character'
@app.route("/")
def index():
    # request que envia el usuario desde el html
    page = request.args.get('page', 1) #Se pasa la pagina principal nro 1 de forma predeterminada

    # obtenemos el aprametrno name de la url y se guarda en name
    name = request.args.get('name')

    if name:
        #hacer la peticion get a la api
        response = requests.get(API_URL, params={'name': name})

        if response.status_code != 200:
            return render_template('index.html', characters=[], search=True, error_message='personaje no encontrado')
        
        data=response.json()
        return render_template('index.html', characters=['result'], search=True)

    # requests a la api
    response = requests.get (API_URL, params={'page': page})

    # convertir response que esta en estructura json a estructura de python
    data=response.json()

    # characters es una VARIABLE
    return render_template('index.html', characters=data['results'], info=data['info'], page=int(page), search=False)


# ruta para guardar los personajes
@app.route ('/save', methods=['POST'])
def save():

    api_id = request.form['api_id']
    name = request.form['name']
    image = request.form['image']
    page = request.form.get('page', 1)

# esto permite guardar en la base de datos solo si el dato todavia no existe 
    if not Favorite.query.filter_by(api_id).first(): #Llamar a la clase, hacer consulta, filtrar
        fav = Favorite(api_id=api_id, name=name, image=image)

        db.session.add(fav)
        db.session.commit()

    return redirect(f'/?page={page}') 


@app.route("/favorites")
def favorites():
    favorites = Favorite.query.all()
    return render_template("favorites.html", favorites=favorites)

#ruta eliminar personajes
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    fav = Favorite.query.get(id)
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return redirect("/favorites")