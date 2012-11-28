# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import psycopg2

# configuration
DEBUG = True
SECRET_KEY = 'jwj2hw82823j1j23njh1hn2h3h8sk289'
CSRF_ENABLED = False

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/logout')
def logout():
    session.pop("user")
    session.pop("password")
    session.pop("host")
    #return redirect(url_for('home'))
    return render_template('logout.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    opts = {}
    if session.get('user'):
        opts["STATUS"] = "OK"
    else:
        if request.method == 'POST':
            user = request.form["user"]
            password = request.form["password"]
            host = request.form["host"]
            conn_string = "host='%s' dbname='postgres' user='%s' password='%s'" % (host, user, password)
            try:
                conn = psycopg2.connect(conn_string)
                conn.cursor()
                session["user"] = user
                session["password"] = password
                session["host"] = host
                opts["STATUS"] = "OK"
            except:
                opts["errors"] = u"Error en la conexión de la base de datos Verifique el host o el usuario"
    return render_template('index.html', **opts)


if __name__ == '__main__':
    app.run()
