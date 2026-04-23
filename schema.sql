-- ============================================================
--  Conciertos DB - Schema completo
--  Generado desde el código fuente del proyecto
-- ============================================================

CREATE DATABASE IF NOT EXISTS Conciertos;
USE Conciertos;

-- ------------------------------------------------------------
-- CATÁLOGOS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS catGenero (
    ID   INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS catMetodoPago (
    ID   INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS catTiposZona (
    ID   INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL
);

-- ------------------------------------------------------------
-- USUARIOS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tblUsuarios (
    ID       INT AUTO_INCREMENT PRIMARY KEY,
    Nombre   VARCHAR(150) NOT NULL,
    Mail     VARCHAR(150) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Rol      ENUM('Admin', 'Cliente') NOT NULL DEFAULT 'Cliente'
);

-- Usuario admin por defecto (password: admin123)
INSERT INTO tblUsuarios (Nombre, Mail, Password, Rol)
VALUES ('Administrador', 'admin@ticketmaster.com', 'admin123', 'Admin');

-- ------------------------------------------------------------
-- LUGARES / RECINTOS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tblLugares (
    ID             INT AUTO_INCREMENT PRIMARY KEY,
    Nombre         VARCHAR(200) NOT NULL,
    Direccion      VARCHAR(300),
    CapacidadTotal INT
);

-- ------------------------------------------------------------
-- EVENTOS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tblEventos (
    ID             INT AUTO_INCREMENT PRIMARY KEY,
    Nombre         VARCHAR(200) NOT NULL,
    Fecha          DATETIME NOT NULL,
    tblLugares_ID  INT,
    Lugares_ID     INT,
    Descripcion    TEXT,
    Estado         ENUM('Activo', 'Cancelado', 'Finalizado') NOT NULL DEFAULT 'Activo',
    FOREIGN KEY (tblLugares_ID) REFERENCES tblLugares(ID) ON DELETE SET NULL,
    FOREIGN KEY (Lugares_ID)    REFERENCES tblLugares(ID) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- ZONAS DE EVENTOS
-- ------------------------------------------------------------

-- Vista/tabla usada en ventas.py y check_in.py
CREATE TABLE IF NOT EXISTS tblZonasEventos (
    ID           INT AUTO_INCREMENT PRIMARY KEY,
    Eventos_ID   INT NOT NULL,
    NombreZona   VARCHAR(150) NOT NULL,
    Capacidad    INT,
    Precio       DECIMAL(10,2),
    FOREIGN KEY (Eventos_ID) REFERENCES tblEventos(ID) ON DELETE CASCADE
);

-- Tabla usada en eventos.py al publicar un concierto
CREATE TABLE IF NOT EXISTS tblZonas (
    ID               INT AUTO_INCREMENT PRIMARY KEY,
    Nombre           VARCHAR(150),
    Capacidad        INT,
    Precio           DECIMAL(10,2),
    Eventos_ID       INT,
    catTiposZona_ID  INT,
    FOREIGN KEY (Eventos_ID)      REFERENCES tblEventos(ID) ON DELETE CASCADE,
    FOREIGN KEY (catTiposZona_ID) REFERENCES catTiposZona(ID) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- RESERVACIONES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tblReservaciones (
    ID               INT AUTO_INCREMENT PRIMARY KEY,
    Usuarios_ID      INT,
    Eventos_ID       INT,
    FechaReservacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    Total            DECIMAL(10,2),
    Estado           ENUM('Confirmado','Cancelado','Usado') DEFAULT 'Confirmado',
    Cliente          VARCHAR(200),
    FOREIGN KEY (Usuarios_ID) REFERENCES tblUsuarios(ID) ON DELETE SET NULL,
    FOREIGN KEY (Eventos_ID)  REFERENCES tblEventos(ID)  ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- DATOS DE EJEMPLO (opcional, comenta si no los necesitas)
-- ------------------------------------------------------------

INSERT INTO catGenero (Nombre) VALUES ('Rock'), ('Pop'), ('Electrónica'), ('Regional Mexicano');
INSERT INTO catMetodoPago (Nombre) VALUES ('Efectivo'), ('Tarjeta de Crédito'), ('Transferencia');
INSERT INTO catTiposZona (Nombre) VALUES ('General'), ('VIP'), ('Palco'), ('Campo');

INSERT INTO tblLugares (Nombre, Direccion, CapacidadTotal)
VALUES ('Auditorio Norte', 'Av. Principal 100, Monterrey', 5000);