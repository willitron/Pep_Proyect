import sqlite3
import random
from datetime import datetime, timedelta

def crear_base_de_datos(db_name="sistema_empresas.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Table creation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            tipo TEXT NOT NULL,
            fecha_registro TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rubros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio_mensual REAL NOT NULL,
            precio_anual REAL NOT NULL,
            sello_destacado INTEGER DEFAULT 0
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            rubro_id INTEGER NOT NULL,
            razon_social TEXT NOT NULL,
            nit TEXT,
            matricula_seprec TEXT,
            latitud REAL,
            longitud REAL,
            whatsapp TEXT,
            sello_verificado INTEGER DEFAULT 0,
            estado TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (rubro_id) REFERENCES rubros(id) ON DELETE RESTRICT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (plan_id) REFERENCES planes(id) ON DELETE RESTRICT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resenas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            calificacion INTEGER NOT NULL,
            comentario TEXT,
            fecha TEXT NOT NULL,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
    """)

    # Populate with data (at least 10 records per table where possible)
    
    # 1. Usuarios
    usuarios = [
        ('Admin User', 'admin@example.com', 'admin123', 'admin', str(datetime.now())),
        ('Juan Perez', 'juan@example.com', 'user123', 'usuario', str(datetime.now())),
        ('Maria Gomez', 'maria@example.com', 'user123', 'usuario', str(datetime.now())),
        ('Pedro Picapiedra', 'pedro@example.com', 'user123', 'usuario', str(datetime.now())),
        ('Ana Rojas', 'ana@example.com', 'user123', 'usuario', str(datetime.now())),
        ('Carlos Ruiz', 'carlos@example.com', 'user123', 'usuario', str(datetime.now())),
        ('Lucia Fernandez', 'lucia@example.com', 'user123', 'usuario', str(datetime.now())),
        ('Roberto Sosa', 'roberto@example.com', 'user123', 'usuario', str(datetime.now())),
        ('Elena Paz', 'elena@example.com', 'user123', 'usuario', str(datetime.now())),
        ('Mario Bros', 'mario@example.com', 'user123', 'usuario', str(datetime.now()))
    ]
    cursor.executemany("INSERT OR IGNORE INTO usuarios (nombre, email, password_hash, tipo, fecha_registro) VALUES (?, ?, ?, ?, ?)", usuarios)

    # 2. Rubros
    rubros = [
        ('Tecnología', 'Empresas de software y hardware'),
        ('Gastronomía', 'Restaurantes y servicios de comida'),
        ('Salud', 'Clínicas y farmacias'),
        ('Educación', 'Colegios y universidades'),
        ('Construcción', 'Materiales y obras'),
        ('Transporte', 'Logística y viajes'),
        ('Moda', 'Ropa y accesorios'),
        ('Finanzas', 'Bancos y seguros'),
        ('Turismo', 'Hoteles y tours'),
        ('Deportes', 'Gimnasios y artículos deportivos')
    ]
    cursor.executemany("INSERT OR IGNORE INTO rubros (nombre, descripcion) VALUES (?, ?)", rubros)

    # 3. Planes
    planes = [
        ('Básico', 10.0, 100.0, 0),
        ('Pro', 25.0, 250.0, 1),
        ('Enterprise', 50.0, 500.0, 1),
        ('Gratis', 0.0, 0.0, 0),
        ('Platino', 100.0, 1000.0, 1),
        ('Mensual', 15.0, 150.0, 0),
        ('Anual Silver', 20.0, 200.0, 1),
        ('Premium', 40.0, 400.0, 1),
        ('Start-up', 5.0, 50.0, 0),
        ('Pyme', 12.0, 120.0, 0)
    ]
    cursor.executemany("INSERT OR IGNORE INTO planes (nombre, precio_mensual, precio_anual, sello_destacado) VALUES (?, ?, ?, ?)", planes)

    # 4. Empresas
    empresas = []
    for i in range(1, 11):
        empresas.append((
            random.randint(1, 10), # usuario_id
            random.randint(1, 10), # rubro_id
            f'Empresa {i} S.A.', # razon_social
            f'NIT-{1000 + i}', # nit
            f'MAT-{2000 + i}', # matricula
            -16.5 + random.uniform(-0.1, 0.1), # lat
            -68.1 + random.uniform(-0.1, 0.1), # lon
            f'+591 7000000{i-1}', # whatsapp
            random.randint(0, 1), # sello_verificado
            'Activo' # estado
        ))
    cursor.executemany("INSERT OR IGNORE INTO empresas (usuario_id, rubro_id, razon_social, nit, matricula_seprec, latitud, longitud, whatsapp, sello_verificado, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", empresas)

    # 5. Suscripciones
    suscripciones = []
    for i in range(1, 11):
        suscripciones.append((
            i, # empresa_id
            random.randint(1, 10), # plan_id
            str(datetime.now().date()), # inicio
            str((datetime.now() + timedelta(days=365)).date()), # fin
            'Vigente'
        ))
    cursor.executemany("INSERT OR IGNORE INTO suscripciones (empresa_id, plan_id, fecha_inicio, fecha_fin, estado) VALUES (?, ?, ?, ?, ?)", suscripciones)

    # 6. Reseñas
    resenas = []
    for i in range(1, 11):
        resenas.append((
            random.randint(1, 10), # empresa_id
            random.randint(1, 10), # usuario_id
            random.randint(4, 5), # calificacion
            f'Excelente servicio de la empresa {i}.', # comentario
            str(datetime.now())
        ))
    cursor.executemany("INSERT OR IGNORE INTO resenas (empresa_id, usuario_id, calificacion, comentario, fecha) VALUES (?, ?, ?, ?, ?)", resenas)

    conn.commit()
    conn.close()
    print(f"Base de datos '{db_name}' creada y poblada exitosamente.")

if __name__ == "__main__":
    crear_base_de_datos()
