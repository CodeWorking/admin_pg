# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import psycopg2

# configuration
DEBUG = True
SECRET_KEY = 'jwj2hw82823j1j23njh1hn2h3h8sk289'

app = Flask(__name__)
app.config.from_object(__name__)


CASO_USO = {"Caso 1": ["GRANT select on emjav_data_horario_wl_banderas to %s",
                       "GRANT insert on emjav_data_horario_wl_banderas to %s"],
            "Caso 2": ["GRANT select on emjav_data_horario_wl_banderas to %s",
                       "GRANT insert on emjav_data_horario_wl_banderas to %s"],}

@app.route('/logout')
def logout():
    session.pop("user")
    session.pop("password")
    session.pop("host")
    #return redirect(url_for('home'))
    return render_template('logout.html')

@app.route('/createuser', methods=['GET', 'POST'])
def createuser():
    opts={}
    if session.get('user'):
        if request.method == 'POST':
            conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (session.get("host"), session.get("dbname"), session.get("user"), session.get("password"))
            try:
                username = request.form["username"]
                userpass = request.form["userpass"]
                conn = psycopg2.connect(conn_string)
                cursor = conn.cursor()
                cursor.execute ("create user %s with password '%s'" % (username,userpass))
                conn.commit()
            except:
                opts["errors"] = u"Error en la conexión de la base de datos. Verifique el host o el usuario"
    else:
        return redirect(url_for('home'))
    return render_template('createuser.html', **opts)

@app.route('/users')
def users():
    opts={}
    if session.get('user'):
        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (session.get("host"), session.get("dbname"), session.get("user"), session.get("password"))
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            opts["users"] = []
            cursor.execute ("select * from pg_roles where rolname != '%s'" % (session.get("user")))
            for record in cursor:
				opts["users"].append({"name":record[0], "id":record[-1]})
            session["users"] = opts["users"]
        except:
            opts["errors"] = u"Error en la conexión de la base de datos. Verifique el host o el usuario"
    else:
        return redirect(url_for('home'))
    return render_template('users.html', **opts)

@app.route('/user/<user_id>/', methods=['GET', 'POST'])
def userid(user_id):
    opts={}
    if session.get("user"):
        opts["users"] = session.get("users")
        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (session.get("host"), session.get("dbname"), session.get("user"), session.get("password"))
        try:
            conn = psycopg2.connect(conn_string)
            if request.method == 'POST':
                cursor = conn.cursor()
                cursor.execute ("select tablename from pg_tables where schemaname = 'public';")
                tablas = cursor.fetchall()
                for tabla in tablas:
                    cursor = conn.cursor()
                    cursor.execute("revoke all privileges on %s from %s" %(tabla[0],user_id))
                    print "revoke all privileges on %s from %s" %(tabla[0],user_id)
                for k in request.form.keys():
                    if k.startswith("caso_uso_"):
                        for gg in CASO_USO[k.replace("caso_uso_", "")]:
                            cursor = conn.cursor()
                            cursor.execute(gg % (user_id))
                    else:
                        for pr in request.values.getlist(k):
                            cursor = conn.cursor()
                            cursor.execute("grant %s on %s to %s" %(pr,k,user_id))

                conn.commit()
                
            opts["tables"] = []
            opts["casos_uso"] = []
            cursor = conn.cursor()
            cursor.execute ("select * from pg_tables where schemaname = 'public'")
            for table in cursor:
                tabs = {}
                cursor1 = conn.cursor()
                cursor1.execute ("select privilege_type from information_schema.role_table_grants as tabs where table_name = '%s' and tabs.grantee = '%s'" %(table[1],user_id))
                opts["tables"].append({"name":table[1], "privs":[i[0] for i in cursor1.fetchall()]})
            for cc in CASO_USO:
                opts["casos_uso"].append({"name":cc, "selected":False})
        except:
            opts["errors"] = u"Error en la conexión de la base de datos. Verifique el host o el usuario"
    else:
        return redirect(url_for('home'))
    return render_template('user.html', **opts)

@app.route('/', methods=['GET', 'POST'])
def home():
    opts = {}
    if session.get('user'):
        return redirect(url_for('users'))
    else:
        if request.method == 'POST':
            user = request.form["user"]
            password = request.form["password"]
            host = request.form["host"]
            dbname = request.form["dbname"]
            conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (host, dbname, user, password)
            try:
                conn = psycopg2.connect(conn_string)
                conn.cursor()
                session["user"] = user
                session["password"] = password
                session["host"] = host
                session["dbname"] = dbname
                return redirect(url_for('users'))
            except Exception as ee:
                print ee
                opts["errors"] = u"Error en la conexión de la base de datos Verifique el host o el usuario"
    return render_template('index.html', **opts)

if __name__ == '__main__':
    app.run()
