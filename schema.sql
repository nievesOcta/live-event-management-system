-- Conciertos DB - SQLite Schema

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS catGenero (
    ID     INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS catMetodoPago (
    ID     INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS catTiposZona (
    ID     INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tblUsuarios (
    ID       INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre   TEXT NOT NULL,
    Mail     TEXT NOT NULL UNIQUE,
    Password TEXT NOT NULL,
    Rol      TEXT NOT NULL DEFAULT 'Cliente' CHECK(Rol IN ('Admin', 'Cliente'))
);

CREATE TABLE IF NOT EXISTS tblLugares (
    ID             INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre         TEXT NOT NULL,
    Direccion      TEXT,
    CapacidadTotal INTEGER
);

CREATE TABLE IF NOT EXISTS tblEventos (
    ID            INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre        TEXT NOT NULL,
    Fecha         TEXT NOT NULL,
    tblLugares_ID INTEGER,
    Lugares_ID    INTEGER,
    Descripcion   TEXT,
    Estado        TEXT NOT NULL DEFAULT 'Activo' CHECK(Estado IN ('Activo', 'Cancelado', 'Finalizado')),
    FOREIGN KEY (tblLugares_ID) REFERENCES tblLugares(ID) ON DELETE SET NULL,
    FOREIGN KEY (Lugares_ID)    REFERENCES tblLugares(ID) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tblZonasEventos (
    ID         INTEGER PRIMARY KEY AUTOINCREMENT,
    Eventos_ID INTEGER NOT NULL,
    NombreZona TEXT NOT NULL,
    Capacidad  INTEGER,
    Precio     REAL,
    FOREIGN KEY (Eventos_ID) REFERENCES tblEventos(ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tblZonas (
    ID              INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT,
    Capacidad       INTEGER,
    Precio          REAL,
    Eventos_ID      INTEGER,
    catTiposZona_ID INTEGER,
    FOREIGN KEY (Eventos_ID)      REFERENCES tblEventos(ID) ON DELETE CASCADE,
    FOREIGN KEY (catTiposZona_ID) REFERENCES catTiposZona(ID) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tblReservaciones (
    ID               INTEGER PRIMARY KEY AUTOINCREMENT,
    Usuarios_ID      INTEGER,
    Eventos_ID       INTEGER,
    FechaReservacion TEXT DEFAULT (datetime('now', 'localtime')),
    Total            REAL,
    Estado           TEXT DEFAULT 'Confirmado' CHECK(Estado IN ('Confirmado', 'Cancelado', 'Usado')),
    Cliente          TEXT,
    FOREIGN KEY (Usuarios_ID) REFERENCES tblUsuarios(ID) ON DELETE SET NULL,
    FOREIGN KEY (Eventos_ID)  REFERENCES tblEventos(ID)  ON DELETE SET NULL
);

-- Seed data (INSERT OR IGNORE so re-running is safe)
INSERT OR IGNORE INTO tblUsuarios (ID, Nombre, Mail, Password, Rol)
VALUES (1, 'Administrador', 'admin@ticketmaster.com', 'admin123', 'Admin');

INSERT OR IGNORE INTO catGenero (ID, Nombre) VALUES
    (1, 'Rock'), (2, 'Pop'), (3, 'Electrónica'), (4, 'Regional Mexicano');

INSERT OR IGNORE INTO catMetodoPago (ID, Nombre) VALUES
    (1, 'Efectivo'), (2, 'Tarjeta de Crédito'), (3, 'Transferencia');

INSERT OR IGNORE INTO catTiposZona (ID, Nombre) VALUES
    (1, 'General'), (2, 'VIP'), (3, 'Palco'), (4, 'Campo');

INSERT OR IGNORE INTO tblLugares (ID, Nombre, Direccion, CapacidadTotal)
VALUES (1, 'Auditorio Norte', 'Av. Principal 100, Monterrey', 5000);
