from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
import random
from functools import wraps

app = Flask(__name__)

# ==========================================
# CONFIGURACIÓN
# ==========================================

app.secret_key = "clave-demo-sorteoweb"

CONTRASENA_ADMIN = "1234"

DATABASE = "sorteo.db"


# ==========================================
# BASE DE DATOS
# ==========================================

def conectar():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_base_datos():

    conexion = conectar()
    cursor = conexion.cursor()

    # Tabla de sorteos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sorteos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            premio TEXT NOT NULL,
            descripcion TEXT,
            fecha TEXT,
            activo INTEGER DEFAULT 1
        )
    """)

    # Tabla de participantes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            telefono TEXT NOT NULL,
            sorteo_id INTEGER
        )
    """)

    # Si la tabla ya existía de una versión anterior,
    # intentamos agregar sorteo_id.
    try:
        cursor.execute(
            "ALTER TABLE participantes ADD COLUMN sorteo_id INTEGER"
        )
    except sqlite3.OperationalError:
        pass

    conexion.commit()

    # Crear un sorteo de prueba si no existe ninguno
    cursor.execute("SELECT COUNT(*) AS cantidad FROM sorteos")
    cantidad = cursor.fetchone()["cantidad"]

    if cantidad == 0:
        cursor.execute("""
            INSERT INTO sorteos
            (nombre, premio, descripcion, fecha, activo)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Gran Sorteo Promocional",
            "Premio sorpresa",
            "Participa gratuitamente en nuestro sorteo promocional.",
            "2026-12-31",
            1
        ))

    conexion.commit()
    conexion.close()


# ==========================================
# PROTECCIÓN DEL ADMINISTRADOR
# ==========================================

def requiere_admin(funcion):

    @wraps(funcion)
    def protegida(*args, **kwargs):

        if not session.get("admin"):
            return redirect(url_for("login"))

        return funcion(*args, **kwargs)

    return protegida


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.route("/")
def inicio():

    conexion = conectar()

    sorteos = conexion.execute("""
        SELECT *
        FROM sorteos
        WHERE activo = 1
        ORDER BY id DESC
    """).fetchall()

    conexion.close()

    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SorteoWeb | Sorteos promocionales</title>

        <style>
            * { box-sizing: border-box; }

            body {
                margin: 0;
                min-height: 100vh;
                font-family: Arial, Helvetica, sans-serif;
                color: #14213d;
                background:
                    radial-gradient(circle at 8% 12%, rgba(255, 207, 74, .25), transparent 24%),
                    radial-gradient(circle at 92% 18%, rgba(37, 99, 235, .22), transparent 28%),
                    linear-gradient(135deg, #07142f 0%, #0b2d63 52%, #1452a0 100%);
                overflow-x: hidden;
            }

            .decoracion {
                position: fixed;
                z-index: 0;
                font-size: 34px;
                opacity: .25;
                pointer-events: none;
                animation: flotar 5s ease-in-out infinite;
            }

            .d1 { top: 14%; left: 4%; }
            .d2 { top: 28%; right: 5%; animation-delay: 1s; }
            .d3 { bottom: 15%; left: 7%; animation-delay: 2s; }
            .d4 { bottom: 24%; right: 8%; animation-delay: 3s; }

            @keyframes flotar {
                0%,100% { transform: translateY(0) rotate(0deg); }
                50% { transform: translateY(-14px) rotate(6deg); }
            }

            .topbar {
                position: relative;
                z-index: 2;
                max-width: 1120px;
                margin: auto;
                padding: 22px 24px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: white;
            }

            .logo {
                font-size: 27px;
                font-weight: 900;
                letter-spacing: -.5px;
            }

            .logo span { color: #ffd34f; }

            .tag {
                padding: 9px 15px;
                border-radius: 999px;
                background: rgba(255,255,255,.10);
                border: 1px solid rgba(255,255,255,.25);
                font-size: 13px;
                font-weight: 700;
            }

            .container {
                position: relative;
                z-index: 1;
                max-width: 1120px;
                margin: 12px auto 45px;
                padding: 0 22px;
            }

            .hero {
                position: relative;
                overflow: hidden;
                display: grid;
                grid-template-columns: 1.15fr .85fr;
                gap: 30px;
                align-items: center;
                padding: 52px;
                border-radius: 32px;
                background: rgba(255,255,255,.97);
                box-shadow: 0 28px 70px rgba(0,0,0,.28);
            }

            .hero:before, .hero:after {
                content: "";
                position: absolute;
                border-radius: 50%;
                pointer-events: none;
            }

            .hero:before {
                width: 260px;
                height: 260px;
                top: -150px;
                left: -80px;
                background: rgba(255,211,79,.18);
            }

            .hero:after {
                width: 300px;
                height: 300px;
                right: -150px;
                bottom: -170px;
                background: rgba(37,99,235,.10);
            }

            .hero-content { position: relative; z-index: 1; }

            .badge {
                display: inline-flex;
                align-items: center;
                gap: 7px;
                padding: 8px 13px;
                border-radius: 999px;
                background: #edf5ff;
                color: #1757ad;
                font-size: 13px;
                font-weight: 800;
                margin-bottom: 18px;
            }

            h1 {
                margin: 0;
                max-width: 700px;
                font-size: clamp(40px, 6vw, 68px);
                line-height: 1.02;
                letter-spacing: -2px;
                color: #0b2550;
            }

            h1 span { color: #e2a914; }

            .subtitle {
                margin: 20px 0 0;
                max-width: 650px;
                color: #5c687c;
                font-size: 18px;
                line-height: 1.65;
            }

            .free {
                display: inline-flex;
                margin-top: 20px;
                padding: 10px 15px;
                border-radius: 10px;
                background: #fff7d7;
                color: #8c6500;
                font-weight: 800;
            }

            .visual {
                position: relative;
                z-index: 1;
                min-height: 270px;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .gift-card {
                width: 245px;
                height: 245px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                border-radius: 34px;
                background: linear-gradient(145deg, #ffd85b, #f0b72b);
                box-shadow: 0 22px 38px rgba(180,132,18,.28);
                transform: rotate(2deg);
            }

            .gift-card .gift { font-size: 92px; }
            .gift-card strong {
                margin-top: 8px;
                color: #654900;
                font-size: 18px;
            }

            .sorteos {
                margin-top: 25px;
                display: grid;
                gap: 22px;
            }

            .sorteo-card {
                position: relative;
                overflow: hidden;
                padding: 30px;
                border-radius: 24px;
                background: white;
                box-shadow: 0 17px 45px rgba(0,0,0,.17);
            }

            .sorteo-card:before {
                content: "";
                position: absolute;
                left: 0; right: 0; top: 0;
                height: 6px;
                background: linear-gradient(90deg, #2166dc, #ffd34f, #2166dc);
            }

            .card-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 15px;
                margin-bottom: 17px;
            }

            .active {
                display: inline-flex;
                align-items: center;
                gap: 7px;
                padding: 7px 11px;
                border-radius: 999px;
                background: #eaf8ef;
                color: #18733c;
                font-size: 12px;
                font-weight: 800;
            }

            .dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #23a455;
            }

            .sorteo-card h2 {
                margin: 0;
                font-size: 29px;
                color: #102b59;
            }

            .prize {
                display: inline-block;
                margin: 2px 0 14px;
                padding: 10px 14px;
                border-radius: 11px;
                background: #fff7d9;
                color: #936b00;
                font-size: 21px;
                font-weight: 900;
            }

            .description {
                margin: 0;
                color: #5e6a7e;
                line-height: 1.65;
                font-size: 16px;
            }

            .details {
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin-top: 20px;
            }

            .detail {
                padding: 10px 13px;
                border-radius: 10px;
                background: #f4f7fb;
                color: #526078;
                font-size: 14px;
            }

            .participar {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                margin-top: 22px;
                padding: 15px 24px;
                border-radius: 13px;
                background: linear-gradient(135deg, #2166e0, #104cae);
                color: white;
                text-decoration: none;
                font-size: 17px;
                font-weight: 900;
                box-shadow: 0 10px 24px rgba(33,102,224,.28);
                transition: .2s;
            }

            .participar:hover {
                transform: translateY(-2px);
                box-shadow: 0 14px 28px rgba(33,102,224,.35);
            }

            .beneficios {
                display: grid;
                grid-template-columns: repeat(3,1fr);
                gap: 16px;
                margin-top: 22px;
            }

            .beneficio {
                padding: 22px;
                border-radius: 18px;
                background: rgba(255,255,255,.96);
                box-shadow: 0 12px 28px rgba(0,0,0,.12);
            }

            .beneficio .icon { font-size: 28px; }
            .beneficio strong {
                display: block;
                margin-top: 9px;
                color: #17345f;
            }

            .beneficio p {
                margin: 6px 0 0;
                color: #69758a;
                font-size: 13px;
                line-height: 1.5;
            }

            .empty {
                padding: 45px;
                text-align: center;
                background: white;
                border-radius: 22px;
                color: #68758a;
            }

            footer {
                position: relative;
                z-index: 1;
                padding: 0 20px 30px;
                text-align: center;
                color: rgba(255,255,255,.70);
                font-size: 13px;
            }

            @media (max-width: 760px) {
                .topbar { padding: 18px 16px; }
                .tag { display: none; }
                .container { padding: 0 12px; margin-top: 0; }
                .hero {
                    grid-template-columns: 1fr;
                    padding: 35px 23px;
                    border-radius: 25px;
                    text-align: center;
                }
                h1 { letter-spacing: -1px; }
                .subtitle { font-size: 16px; }
                .visual { min-height: 220px; }
                .gift-card { width: 205px; height: 205px; }
                .gift-card .gift { font-size: 75px; }
                .sorteo-card { padding: 25px 20px; }
                .card-top { align-items: flex-start; flex-direction: column; }
                .beneficios { grid-template-columns: 1fr; }
                .participar { width: 100%; }
            }
        </style>
    </head>

    <body>
        <div class="decoracion d1">🎁</div>
        <div class="decoracion d2">✨</div>
        <div class="decoracion d3">🎉</div>
        <div class="decoracion d4">🎁</div>

        <header class="topbar">
            <div class="logo">🎁 Sorteo<span>Web</span></div>
            <div class="tag">✨ Sorteos promocionales</div>
        </header>

        <main class="container">
            <section class="hero">
                <div class="hero-content">
                    <div class="badge">🏆 GRAN SORTEO PROMOCIONAL</div>
                    <h1>¡Participa y <span>podrías ganar!</span></h1>
                    <p class="subtitle">
                        Regístrate gratis en nuestros sorteos promocionales.
                        Obtén tu número de participación y descubre si eres el próximo ganador.
                    </p>
                    <div class="free">🎟️ Participación 100% gratuita</div>
                </div>

                <div class="visual">
                    <div class="gift-card">
                        <div class="gift">🎁</div>
                        <strong>¡Premio sorpresa!</strong>
                    </div>
                </div>
            </section>

            <section class="sorteos">
                {% if sorteos %}
                    {% for sorteo in sorteos %}
                        <article class="sorteo-card">
                            <div class="card-top">
                                <h2>{{ sorteo["nombre"] }}</h2>
                                <div class="active"><span class="dot"></span> SORTEO ACTIVO</div>
                            </div>

                            <div class="prize">🎁 {{ sorteo["premio"] }}</div>

                            <p class="description">{{ sorteo["descripcion"] }}</p>

                            <div class="details">
                                <div class="detail">📅 <strong>Fecha:</strong> {{ sorteo["fecha"] }}</div>
                                <div class="detail">🆓 Participación gratuita</div>
                                <div class="detail">🎟️ Número automático</div>
                            </div>

                            <a class="participar"
                               href="{{ url_for('participar', sorteo_id=sorteo['id']) }}">
                                🎟️ Participar
                            </a>
                        </article>
                    {% endfor %}
                {% else %}
                    <div class="empty">
                        <h2>No hay sorteos activos</h2>
                        <p>Vuelve pronto para participar en nuestro próximo sorteo.</p>
                    </div>
                {% endif %}
            </section>

            <section class="beneficios">
                <div class="beneficio">
                    <div class="icon">🆓</div>
                    <strong>100% gratuito</strong>
                    <p>La participación no tiene costo.</p>
                </div>
                <div class="beneficio">
                    <div class="icon">⚡</div>
                    <strong>Fácil y rápido</strong>
                    <p>Regístrate en pocos pasos y recibe tu número.</p>
                </div>
                <div class="beneficio">
                    <div class="icon">🏆</div>
                    <strong>Sorteo promocional</strong>
                    <p>Consulta la información del sorteo antes de participar.</p>
                </div>
            </section>
        </main>

        <footer>
            <div>SorteoWeb · Sorteos promocionales</div>
            <div style="margin-top:10px;">
                📸 Síguenos en
                <a href="https://" + "www.instagram.com/ta_premia_o/" target="_blank"
                   style="color:#ffd45c; font-weight:800; text-decoration:none;">
                    @ta_premia_o
                </a>
            </div>
        </footer>
    </body>
    </html>
    """


    return render_template_string(html, sorteos=sorteos)


# ==========================================
# PARTICIPAR
# ==========================================

@app.route("/participar/<int:sorteo_id>", methods=["GET", "POST"])
def participar(sorteo_id):

    conexion = conectar()

    sorteo = conexion.execute("""
        SELECT *
        FROM sorteos
        WHERE id = ? AND activo = 1
    """, (sorteo_id,)).fetchone()

    if not sorteo:
        conexion.close()
        return "Sorteo no encontrado."

    if request.method == "POST":

        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        telefono = request.form.get("telefono", "").strip()

        if not nombre or not correo or not telefono:
            conexion.close()

            return render_template_string("""
                <h2>Faltan datos</h2>
                <p>Debes completar todos los campos.</p>
                <a href="javascript:history.back()">Volver</a>
            """)

        # Evitar que el mismo correo se registre
        # dos veces en el mismo sorteo.
        existente = conexion.execute("""
            SELECT id
            FROM participantes
            WHERE correo = ? AND sorteo_id = ?
        """, (correo, sorteo_id)).fetchone()

        if existente:

            conexion.close()

            return render_template_string("""
                <h2>⚠️ Ya estás registrado</h2>

                <p>
                    Este correo ya participa en este sorteo.
                </p>

                <a href="/">Volver al inicio</a>
            """)

        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO participantes
            (nombre, correo, telefono, sorteo_id)
            VALUES (?, ?, ?, ?)
        """, (
            nombre,
            correo,
            telefono,
            sorteo_id
        ))

        numero = cursor.lastrowid

        conexion.commit()
        conexion.close()

        return render_template_string("""
            <!DOCTYPE html>

            <html lang="es">

            <head>
                <meta charset="UTF-8">

                <meta name="viewport"
                      content="width=device-width, initial-scale=1.0">

                <title>Registro exitoso</title>

                <style>

                    body {
                        font-family: Arial;
                        background: #f4f6f8;
                        text-align: center;
                        padding: 50px;
                    }

                    .tarjeta {
                        background: white;
                        max-width: 500px;
                        margin: auto;
                        padding: 35px;
                        border-radius: 15px;
                        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                    }

                    .numero {
                        font-size: 50px;
                        font-weight: bold;
                        color: #2563eb;
                    }

                    a {
                        display: inline-block;
                        margin-top: 20px;
                        background: #2563eb;
                        color: white;
                        padding: 12px 20px;
                        border-radius: 8px;
                        text-decoration: none;
                    }

                </style>

            </head>

            <body>

                <div class="tarjeta">

                    <h1>✅ Registro exitoso</h1>

                    <p>Gracias por participar.</p>

                    <p>Tu número de participación es:</p>

                    <div class="numero">
                        #{{ numero }}
                    </div>

                    <a href="/">
                        Volver al inicio
                    </a>

                </div>

            </body>

            </html>
        """, numero=numero)

    conexion.close()

    html = """
    <!DOCTYPE html>

    <html lang="es">

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Participar</title>

        <style>

            body {
                font-family: Arial;
                background: #f4f6f8;
                padding: 30px;
            }

            .tarjeta {
                max-width: 500px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }

            input {
                width: 100%;
                box-sizing: border-box;
                padding: 12px;
                margin: 8px 0 18px;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 16px;
            }

            button {
                width: 100%;
                padding: 14px;
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 17px;
                cursor: pointer;
            }

        </style>

    </head>

    <body>

        <div class="tarjeta">

            <h1>🎁 {{ sorteo["nombre"] }}</h1>

            <h2>{{ sorteo["premio"] }}</h2>

            <p>
                {{ sorteo["descripcion"] }}
            </p>

            <hr>

            <h3>Datos del participante</h3>

            <form method="POST">

                <label>Nombre completo</label>

                <input
                    type="text"
                    name="nombre"
                    required
                >

                <label>Correo electrónico</label>

                <input
                    type="email"
                    name="correo"
                    required
                >

                <label>Teléfono</label>

                <input
                    type="tel"
                    name="telefono"
                    required
                >

                <button type="submit">
                    Participar
                </button>

            </form>

        </div>

    </body>

    </html>
    """

    return render_template_string(html, sorteo=sorteo)


# ==========================================
# LOGIN DEL ADMINISTRADOR
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        contrasena = request.form.get("contrasena", "")

        if contrasena == CONTRASENA_ADMIN:

            session["admin"] = True

            return redirect(url_for("admin"))

        return render_template_string("""
            <h2>Contraseña incorrecta</h2>
            <a href="/login">Intentar nuevamente</a>
        """)

    return render_template_string("""
        <!DOCTYPE html>

        <html lang="es">

        <head>
            <meta charset="UTF-8">
            <title>Administrador</title>

            <style>

                body {
                    font-family: Arial;
                    background: #f4f6f8;
                    padding: 50px;
                }

                .tarjeta {
                    background: white;
                    max-width: 400px;
                    margin: auto;
                    padding: 30px;
                    border-radius: 15px;
                }

                input {
                    width: 100%;
                    box-sizing: border-box;
                    padding: 12px;
                    margin: 10px 0;
                }

                button {
                    width: 100%;
                    padding: 12px;
                    background: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 8px;
                }

            </style>

        </head>

        <body>

            <div class="tarjeta">

                <h2>🔐 Panel de administrador</h2>

                <form method="POST">

                    <input
                        type="password"
                        name="contrasena"
                        placeholder="Contraseña"
                        required
                    >

                    <button type="submit">
                        Entrar
                    </button>

                </form>

            </div>

        </body>

        </html>
    """)


# ==========================================
# PANEL ADMINISTRADOR
# ==========================================

@app.route("/admin")
@requiere_admin
def admin():

    conexion = conectar()

    sorteos = conexion.execute("""
        SELECT *
        FROM sorteos
        ORDER BY id DESC
    """).fetchall()

    participantes = conexion.execute("""
        SELECT
            participantes.*,
            sorteos.nombre AS sorteo_nombre
        FROM participantes
        LEFT JOIN sorteos
        ON participantes.sorteo_id = sorteos.id
        ORDER BY participantes.id DESC
    """).fetchall()

    conexion.close()

    html = """
    <!DOCTYPE html>

    <html lang="es">

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Panel administrador</title>

        <style>

            body {
                font-family: Arial;
                background: #f4f6f8;
                margin: 0;
            }

            header {
                background: #111827;
                color: white;
                padding: 25px;
            }

            .contenedor {
                max-width: 1100px;
                margin: auto;
                padding: 30px;
            }

            .tarjeta {
                background: white;
                padding: 25px;
                margin-bottom: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }

            .boton {
                display: inline-block;
                padding: 10px 15px;
                background: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                margin: 5px;
            }

            .verde {
                background: #16a34a;
            }

            .rojo {
                background: #dc2626;
            }

            table {
                width: 100%;
                border-collapse: collapse;
            }

            th, td {
                padding: 10px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }

        </style>

    </head>

    <body>

        <header>

            <h1>🔐 Panel de administrador</h1>

            <a class="boton rojo"
               href="/logout">
                Cerrar sesión
            </a>

        </header>

        <div class="contenedor">

            <div class="tarjeta">

                <h2>🎁 Sorteos</h2>

                <a class="boton verde"
                   href="/crear-sorteo">
                    ➕ Crear nuevo sorteo
                </a>

                {% for sorteo in sorteos %}

                    <hr>

                    <h3>
                        {{ sorteo["nombre"] }}
                    </h3>

                    <p>
                        🎁 {{ sorteo["premio"] }}
                    </p>

                    <p>
                        📅 {{ sorteo["fecha"] }}
                    </p>

                    <p>
                        Estado:
                        {% if sorteo["activo"] %}
                            🟢 Activo
                        {% else %}
                            🔴 Inactivo
                        {% endif %}
                    </p>

                    <a class="boton"
                       href="/ganador/{{ sorteo['id'] }}">
                        🎉 Elegir ganador
                    </a>

                {% endfor %}

            </div>


            <div class="tarjeta">

                <h2>👥 Participantes</h2>

                <table>

                    <tr>
                        <th>#</th>
                        <th>Nombre</th>
                        <th>Correo</th>
                        <th>Teléfono</th>
                        <th>Sorteo</th>
                    </tr>

                    {% for participante in participantes %}

                    <tr>

                        <td>
                            {{ participante["id"] }}
                        </td>

                        <td>
                            {{ participante["nombre"] }}
                        </td>

                        <td>
                            {{ participante["correo"] }}
                        </td>

                        <td>
                            {{ participante["telefono"] }}
                        </td>

                        <td>
                            {{ participante["sorteo_nombre"] or "—" }}
                        </td>

                    </tr>

                    {% endfor %}

                </table>

            </div>

        </div>

    </body>

    </html>
    """

    return render_template_string(
        html,
        sorteos=sorteos,
        participantes=participantes
    )


# ==========================================
# CREAR SORTEO
# ==========================================

@app.route("/crear-sorteo", methods=["GET", "POST"])
@requiere_admin
def crear_sorteo():

    if request.method == "POST":

        nombre = request.form.get("nombre", "").strip()
        premio = request.form.get("premio", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        fecha = request.form.get("fecha", "").strip()

        if not nombre or not premio or not fecha:

            return """
            <h2>Faltan datos</h2>
            <p>Nombre, premio y fecha son obligatorios.</p>
            <a href="/crear-sorteo">Volver</a>
            """

        conexion = conectar()

        conexion.execute("""
            INSERT INTO sorteos
            (nombre, premio, descripcion, fecha, activo)
            VALUES (?, ?, ?, ?, 1)
        """, (
            nombre,
            premio,
            descripcion,
            fecha
        ))

        conexion.commit()
        conexion.close()

        return redirect(url_for("admin"))

    return render_template_string("""
        <!DOCTYPE html>

        <html lang="es">

        <head>

            <meta charset="UTF-8">

            <title>Crear sorteo</title>

            <style>

                body {
                    font-family: Arial;
                    background: #f4f6f8;
                    padding: 30px;
                }

                .tarjeta {
                    max-width: 600px;
                    margin: auto;
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                }

                input, textarea {
                    width: 100%;
                    box-sizing: border-box;
                    padding: 12px;
                    margin: 8px 0 20px;
                }

                button {
                    width: 100%;
                    padding: 14px;
                    background: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                }

            </style>

        </head>

        <body>

            <div class="tarjeta">

                <h1>➕ Crear nuevo sorteo</h1>

                <form method="POST">

                    <label>Nombre del sorteo</label>

                    <input
                        type="text"
                        name="nombre"
                        required
                    >

                    <label>Premio</label>

                    <input
                        type="text"
                        name="premio"
                        required
                    >

                    <label>Descripción</label>

                    <textarea
                        name="descripcion"
                        rows="5"
                    ></textarea>

                    <label>Fecha del sorteo</label>

                    <input
                        type="date"
                        name="fecha"
                        required
                    >

                    <button type="submit">
                        Crear sorteo
                    </button>

                </form>

            </div>

        </body>

        </html>
    """)


# ==========================================
# ELEGIR GANADOR
# ==========================================

@app.route("/ganador/<int:sorteo_id>")
@requiere_admin
def ganador(sorteo_id):

    conexion = conectar()

    sorteo = conexion.execute("""
        SELECT *
        FROM sorteos
        WHERE id = ?
    """, (sorteo_id,)).fetchone()

    participantes = conexion.execute("""
        SELECT *
        FROM participantes
        WHERE sorteo_id = ?
    """, (sorteo_id,)).fetchall()

    conexion.close()

    if not sorteo:
        return "Sorteo no encontrado."

    if not participantes:

        return render_template_string("""
            <h2>⚠️ No hay participantes</h2>

            <p>
                Todavía no hay participantes en este sorteo.
            </p>

            <a href="/admin">
                Volver al panel
            </a>
        """)

    ganador = random.choice(participantes)

    return render_template_string("""
        <!DOCTYPE html>

        <html lang="es">

        <head>

            <meta charset="UTF-8">

            <title>Ganador</title>

            <style>

                body {
                    font-family: Arial;
                    background: #111827;
                    color: white;
                    text-align: center;
                    padding: 50px;
                }

                .tarjeta {
                    background: white;
                    color: #111;
                    max-width: 600px;
                    margin: auto;
                    padding: 40px;
                    border-radius: 20px;
                }

                .numero {
                    font-size: 55px;
                    color: #2563eb;
                    font-weight: bold;
                }

                a {
                    display: inline-block;
                    margin-top: 25px;
                    padding: 12px 20px;
                    background: #2563eb;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                }

            </style>

        </head>

        <body>

            <div class="tarjeta">

                <h1>🎉 ¡Ganador!</h1>

                <h2>
                    {{ sorteo["nombre"] }}
                </h2>

                <p>
                    Premio:
                    <strong>{{ sorteo["premio"] }}</strong>
                </p>

                <hr>

                <h2>
                    {{ ganador["nombre"] }}
                </h2>

                <div class="numero">
                    #{{ ganador["id"] }}
                </div>

                <p>
                    Participante ganador
                </p>

                <a href="/admin">
                    Volver al panel
                </a>

            </div>

        </body>

        </html>
    """, sorteo=sorteo, ganador=ganador)


# ==========================================
# CERRAR SESIÓN
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("inicio"))


# ==========================================
# INICIAR PROGRAMA
# ==========================================

if __name__ == "__main__":

    crear_base_datos()

    app.run(
        host="0.0.0.0",
        port=int(__import__("os").environ.get("PORT", 5000)),
        debug=False
    )