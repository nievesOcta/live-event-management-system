"""
Seeder de datos de prueba para TicketMaster Pro.
Ejecutar directamente: python seeder.py
"""
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conciertos.db")

def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # --- CATÁLOGOS (INSERT OR IGNORE por si ya existen) ---
    cur.executemany("INSERT OR IGNORE INTO catGenero (ID, Nombre) VALUES (?, ?)", [
        (1, "Rock"), (2, "Pop"), (3, "Electrónica"), (4, "Regional Mexicano"),
        (5, "Jazz"), (6, "Hip-Hop"),
    ])

    cur.executemany("INSERT OR IGNORE INTO catMetodoPago (ID, Nombre) VALUES (?, ?)", [
        (1, "Efectivo"), (2, "Tarjeta de Crédito"), (3, "Transferencia"),
    ])

    cur.executemany("INSERT OR IGNORE INTO catTiposZona (ID, Nombre) VALUES (?, ?)", [
        (1, "General"), (2, "VIP"), (3, "Palco"), (4, "Campo"),
    ])

    # --- LUGARES ---
    cur.executemany(
        "INSERT OR IGNORE INTO tblLugares (ID, Nombre, Direccion, CapacidadTotal) VALUES (?, ?, ?, ?)", [
        (1, "Auditorio Norte",      "Av. Principal 100, Monterrey",          5000),
        (2, "Arena Monterrey",      "Av. Lincoln 700, Monterrey",           18000),
        (3, "Parque Fundidora",     "Av. Fundidora S/N, Monterrey",         30000),
        (4, "Teatro de la Ciudad",  "Zaragoza 800, Centro, Monterrey",       1200),
        (5, "Foro Independencia",   "Av. Constitución 400, Monterrey",       3500),
    ])

    # --- USUARIOS (clientes de prueba) ---
    cur.executemany(
        "INSERT OR IGNORE INTO tblUsuarios (ID, Nombre, Mail, Password, Rol) VALUES (?, ?, ?, ?, ?)", [
        (1,  "Administrador",    "admin@ticketmaster.com", "admin123",   "Admin"),
        (2,  "Carlos Ramírez",   "carlos@mail.com",        "pass123",    "Cliente"),
        (3,  "María González",   "maria@mail.com",         "pass123",    "Cliente"),
        (4,  "Luis Hernández",   "luis@mail.com",          "pass123",    "Cliente"),
        (5,  "Ana Martínez",     "ana@mail.com",           "pass123",    "Cliente"),
        (6,  "Jorge Pérez",      "jorge@mail.com",         "pass123",    "Cliente"),
        (7,  "Sofía López",      "sofia@mail.com",         "pass123",    "Cliente"),
        (8,  "Roberto Torres",   "roberto@mail.com",       "pass123",    "Cliente"),
        (9,  "Valentina Cruz",   "valentina@mail.com",     "pass123",    "Cliente"),
        (10, "Diego Flores",     "diego@mail.com",         "pass123",    "Cliente"),
    ])

    # --- EVENTOS ---
    hoy = datetime.now()
    def fecha(dias): return (hoy + timedelta(days=dias)).strftime("%Y-%m-%d 20:00")

    cur.executemany(
        "INSERT OR IGNORE INTO tblEventos (ID, Nombre, Fecha, tblLugares_ID, Descripcion, Estado) VALUES (?, ?, ?, ?, ?, ?)", [
        (1, "Maná en Concierto",         fecha(15),  2, "Gira 'Rayando el Sol' 2026",          "Activo"),
        (2, "Festival Neon",             fecha(30),  3, "Festival de música electrónica",        "Activo"),
        (3, "Natalia Lafourcade",        fecha(45),  4, "Noche íntima de jazz y pop",            "Activo"),
        (4, "Calle 13 Reggaeton Fest",   fecha(60),  1, "Lo mejor del urbano latino",            "Activo"),
        (5, "Los Tigres del Norte",      fecha(10),  2, "Noche de Regional Mexicano",            "Activo"),
        (6, "Imagine Dragons",           fecha(90),  3, "Tour 'Loom' 2026",                      "Activo"),
        (7, "Concierto de Jazz Local",   fecha(-30), 4, "Edición especial de verano",            "Finalizado"),
        (8, "Rock en tu Idioma",         fecha(-15), 1, "Lo mejor del rock en español",          "Finalizado"),
    ])

    # --- ZONAS POR EVENTO (tblZonasEventos) ---
    zonas = []
    ze_id = 1
    configs_zonas = [
        # (evento_id, nombre, capacidad, precio)
        (1, "Campo",   8000,  850.0),
        (1, "General", 7000,  1200.0),
        (1, "VIP",     2000,  3500.0),
        (1, "Palco",   1000,  6000.0),
        (2, "Campo",  15000,  600.0),
        (2, "General", 8000,  900.0),
        (2, "VIP",     3000,  2500.0),
        (3, "General",  800,  750.0),
        (3, "VIP",      400,  1800.0),
        (4, "General", 2000,  500.0),
        (4, "VIP",      500,  1500.0),
        (5, "Campo",   9000,  700.0),
        (5, "General", 6000,  1000.0),
        (5, "VIP",     2000,  3000.0),
        (5, "Palco",    800,  5500.0),
        (6, "Campo",  15000,  1100.0),
        (6, "General", 8000,  1600.0),
        (6, "VIP",     4000,  4200.0),
        (7, "General",  900,  400.0),
        (7, "VIP",      300,  1200.0),
        (8, "General", 2500,  550.0),
        (8, "VIP",      500,  1800.0),
    ]
    for (ev_id, nombre, cap, precio) in configs_zonas:
        zonas.append((ze_id, ev_id, nombre, cap, precio))
        ze_id += 1

    cur.executemany(
        "INSERT OR IGNORE INTO tblZonasEventos (ID, Eventos_ID, NombreZona, Capacidad, Precio) VALUES (?, ?, ?, ?, ?)",
        zonas
    )

    # --- ZONAS (tblZonas, tabla alternativa) ---
    cur.executemany(
        "INSERT OR IGNORE INTO tblZonas (ID, Nombre, Capacidad, Precio, Eventos_ID, catTiposZona_ID) VALUES (?, ?, ?, ?, ?, ?)", [
        (1,  "Campo",   8000,  850.0,  1, 4),
        (2,  "General", 7000,  1200.0, 1, 1),
        (3,  "VIP",     2000,  3500.0, 1, 2),
        (4,  "Palco",   1000,  6000.0, 1, 3),
        (5,  "Campo",  15000,  600.0,  2, 4),
        (6,  "General", 8000,  900.0,  2, 1),
        (7,  "VIP",     3000,  2500.0, 2, 2),
        (8,  "General",  800,  750.0,  3, 1),
        (9,  "VIP",      400,  1800.0, 3, 2),
        (10, "General", 2000,  500.0,  4, 1),
        (11, "VIP",      500,  1500.0, 4, 2),
    ])

    # --- RESERVACIONES ---
    reservaciones = [
        # (id, usuario_id, evento_id, fecha_reservacion, total, estado, cliente)
        (1,  2,  1, "2026-04-01 10:30:00", 1200.0,  "Confirmado", "Carlos Ramírez"),
        (2,  3,  1, "2026-04-02 11:00:00", 3500.0,  "Confirmado", "María González"),
        (3,  4,  2, "2026-04-03 09:15:00", 600.0,   "Confirmado", "Luis Hernández"),
        (4,  5,  2, "2026-04-03 14:00:00", 2500.0,  "Confirmado", "Ana Martínez"),
        (5,  6,  3, "2026-04-05 16:45:00", 750.0,   "Confirmado", "Jorge Pérez"),
        (6,  7,  5, "2026-04-06 10:00:00", 1000.0,  "Confirmado", "Sofía López"),
        (7,  8,  5, "2026-04-07 12:30:00", 5500.0,  "Confirmado", "Roberto Torres"),
        (8,  9,  6, "2026-04-08 18:00:00", 1600.0,  "Confirmado", "Valentina Cruz"),
        (9,  10, 6, "2026-04-09 20:00:00", 4200.0,  "Confirmado", "Diego Flores"),
        (10, 2,  7, "2026-03-01 09:00:00", 400.0,   "Usado",      "Carlos Ramírez"),
        (11, 3,  7, "2026-03-02 10:00:00", 1200.0,  "Usado",      "María González"),
        (12, 4,  8, "2026-03-10 11:00:00", 550.0,   "Usado",      "Luis Hernández"),
        (13, 5,  8, "2026-03-11 15:00:00", 1800.0,  "Usado",      "Ana Martínez"),
        (14, 6,  1, "2026-04-10 09:30:00", 850.0,   "Cancelado",  "Jorge Pérez"),
        (15, 2,  3, "2026-04-12 17:00:00", 1800.0,  "Confirmado", "Carlos Ramírez"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO tblReservaciones (ID, Usuarios_ID, Eventos_ID, FechaReservacion, Total, Estado, Cliente) VALUES (?, ?, ?, ?, ?, ?, ?)",
        reservaciones
    )

    conn.commit()
    conn.close()

    print(f"Seeder completado en: {DB_PATH}")
    print("  5  lugares")
    print("  9  usuarios (1 admin + 8 clientes)")
    print("  8  eventos (6 activos, 2 finalizados)")
    print(f"  {len(zonas)}  zonas (tblZonasEventos)")
    print(" 11  zonas (tblZonas)")
    print(" 15  reservaciones")

if __name__ == "__main__":
    seed()
