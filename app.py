from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pep_proyect_secret_default')
DATABASE = os.environ.get('DATABASE_PATH', 'sistema_empresas.db')

def init_db():
    if not os.path.exists(DATABASE):
        from setup_db import crear_base_de_datos
        crear_base_de_datos(DATABASE)
        print("Base de datos inicializada para producción.")

init_db() # Run at startup

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    rubros = query_db('SELECT * FROM rubros')
    empresas = query_db('SELECT * FROM empresas LIMIT 9')
    sucripciones = query_db('''
        SELECT e.razon_social, p.nombre as plan_nombre, s.fecha_fin 
        FROM suscripciones s
        JOIN empresas e ON s.empresa_id = e.id
        JOIN planes p ON s.plan_id = p.id
        WHERE s.estado = "Vigente"
        LIMIT 4
    ''')
    resenas = query_db('''
        SELECT r.*, u.nombre as usuario_nombre, e.razon_social 
        FROM resenas r
        JOIN usuarios u ON r.usuario_id = u.id
        JOIN empresas e ON r.empresa_id = e.id
        LIMIT 3
    ''')
    return render_template('index.html', rubros=rubros, empresas=empresas, resenas=resenas, suscripciones=sucripciones)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = query_db('SELECT * FROM usuarios WHERE email = ? AND password_hash = ?', [email, password], one=True)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            session['user_role'] = user['tipo']
            return redirect(url_for('index'))
        else:
            return "Login Fallido. Intente admin@example.com / admin123"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    counts = {
        'usuarios': query_db('SELECT COUNT(*) as c FROM usuarios', one=True)['c'],
        'empresas': query_db('SELECT COUNT(*) as c FROM empresas', one=True)['c'],
        'rubros': query_db('SELECT COUNT(*) as c FROM rubros', one=True)['c'],
        'planes': query_db('SELECT COUNT(*) as c FROM planes', one=True)['c']
    }
    
    all_empresas = query_db('''
        SELECT e.*, r.nombre as rubro_nombre, u.nombre as usuario_nombre 
        FROM empresas e
        LEFT JOIN rubros r ON e.rubro_id = r.id
        LEFT JOIN usuarios u ON e.usuario_id = u.id
    ''')
    all_usuarios = query_db('SELECT * FROM usuarios')
    all_rubros = query_db('SELECT * FROM rubros')
    all_planes = query_db('SELECT * FROM planes')
    
    return render_template('admin.html', 
                         counts=counts, 
                         empresas=all_empresas, 
                         usuarios=all_usuarios, 
                         rubros=all_rubros, 
                         planes=all_planes)

# EMPRESAS CRUD
@app.route('/admin/empresa/add', methods=['POST'])
def add_empresa():
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    db = get_db()
    db.execute('INSERT INTO empresas (usuario_id, rubro_id, razon_social, nit, matricula_seprec, estado) VALUES (?, ?, ?, ?, ?, ?)',
               [request.form['usuario_id'], request.form['rubro_id'], request.form['razon_social'], request.form['nit'], request.form['matricula'], 'Activo'])
    db.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/empresa/delete/<int:id>')
def delete_empresa(id):
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    db = get_db()
    db.execute('DELETE FROM empresas WHERE id = ?', [id])
    db.commit()
    return redirect(url_for('admin_dashboard'))

# USUARIOS CRUD
@app.route('/admin/usuario/add', methods=['POST'])
def add_usuario():
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    db = get_db()
    db.execute('INSERT INTO usuarios (nombre, email, password_hash, tipo, fecha_registro) VALUES (?, ?, ?, ?, ?)',
               [request.form['nombre'], request.form['email'], request.form['password'], request.form['tipo'], str(datetime.now())])
    db.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/usuario/delete/<int:id>')
def delete_usuario(id):
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    db = get_db()
    db.execute('DELETE FROM usuarios WHERE id = ?', [id])
    db.commit()
    return redirect(url_for('admin_dashboard'))

# RUBROS CRUD
@app.route('/admin/rubro/add', methods=['POST'])
def add_rubro():
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    db = get_db()
    db.execute('INSERT INTO rubros (nombre, descripcion) VALUES (?, ?)',
               [request.form['nombre'], request.form['descripcion']])
    db.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/rubro/delete/<int:id>')
def delete_rubro(id):
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    db = get_db()
    db.execute('DELETE FROM rubros WHERE id = ?', [id])
    db.commit()
    return redirect(url_for('admin_dashboard'))

# PLANES CRUD
@app.route('/admin/plan/add', methods=['POST'])
def add_plan():
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    db = get_db()
    db.execute('INSERT INTO planes (nombre, precio_mensual, precio_anual, sello_destacado) VALUES (?, ?, ?, ?)',
               [request.form['nombre'], request.form['precio_m'], request.form['precio_a'], request.form.get('destacado', 0)])
    db.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/plan/delete/<int:id>')
def delete_plan(id):
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    db = get_db()
    db.execute('DELETE FROM planes WHERE id = ?', [id])
    db.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    from datetime import datetime
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
