# EventosPRO — Sistema de Gestión de Boletos y Eventos

Sistema de escritorio para la administración de eventos musicales, venta de boletos, control de acceso y generación de reportes. Desarrollado con Python y MySQL.

---

## Características

- **Inicio de sesión** con roles diferenciados (Administrador / Cajero)
- **Punto de venta** con selección de evento, zona y precio dinámico
- **Generación de boletos en PDF** con código QR único por reservación
- **Validación de entradas (Check-in)** por escaneo o captura manual del código QR
- **Historial de compras** con exportación a Excel y reimpresión de boletos
- **Gestión de eventos** — publicar conciertos, configurar zonas y aforo
- **Gestión de recintos, usuarios y catálogos** (solo Administrador)

---

## Tecnologías

| Componente | Tecnología |
|---|---|
| Interfaz gráfica | Python 3 · customtkinter · tkinter |
| Base de datos | MySQL 8 (vía Docker) |
| Generación de PDF | ReportLab |
| Códigos QR | qrcode + Pillow |
| Exportación Excel | pandas + openpyxl |
| Empaquetado | PyInstaller |
| Base de datos (contenedor) | Docker · docker-compose |

---

## Instalación en Windows 10

### Requisitos previos

- **Docker Desktop para Windows**
  - Descarga: https://docs.docker.com/desktop/install/windows-install/
  - Durante la instalación, habilita la opción **"Use WSL 2 instead of Hyper-V"** (recomendado)
  - Reinicia el equipo si el instalador lo solicita

### Paso 1 — Preparar la carpeta de la aplicación

Coloca los siguientes archivos en una misma carpeta (por ejemplo `C:\BoletoPRO\`):

```
BoletoPRO\
├── BoletoPRO.exe          ← ejecutable de la aplicación
├── docker-compose.yml     ← configuración de la base de datos
└── start.bat              ← lanzador (úsalo para abrir la app)
```

> El ejecutable `BoletoPRO.exe` se descarga desde la sección **Actions → Artifacts** del repositorio en GitHub, o lo proporciona el equipo de desarrollo.

### Paso 2 — Iniciar la base de datos por primera vez

1. Abre **Docker Desktop** y espera a que el ícono de la ballena en la barra de tareas deje de moverse (indica que Docker está listo).
2. Abre una ventana de **PowerShell** o **CMD** en la carpeta `BoletoPRO\`.
3. Ejecuta el siguiente comando para crear e inicializar la base de datos:

```powershell
docker-compose up -d
```

4. Espera unos 15–20 segundos para que MySQL termine de iniciar.

### Paso 3 — Cargar el esquema de la base de datos

> Solo es necesario hacerlo **una vez** al instalar.

Con la base de datos corriendo, importa el esquema desde PowerShell:

```powershell
docker exec -i sistema-mysql-1 mysql -u root -pZ2obC9kg1512 Conciertos < schema.sql
```

> Si el nombre del contenedor es diferente, puedes verificarlo con `docker ps`.

### Paso 4 — Iniciar la aplicación

Haz **doble clic** en `start.bat`.

El lanzador verificará que Docker esté activo, iniciará el contenedor de MySQL y abrirá BoletoPRO automáticamente.

---

## Credenciales por defecto

| Campo | Valor |
|---|---|
| Correo | `admin@ticketmaster.com` |
| Contraseña | `admin123` |
| Rol | Administrador |

> Se recomienda cambiar la contraseña desde **Usuarios y Permisos** después del primer inicio de sesión.

---

## Estructura del proyecto

```
Sistema/
├── main.py                  ← punto de entrada y pantalla de login
├── conexion.py              ← configuración de la conexión a MySQL
├── ventas.py                ← punto de venta y generación de boletos PDF
├── check_in.py              ← validación de entradas por código QR
├── reportes.py              ← historial, filtros y exportación a Excel
├── eventos.py               ← gestión de eventos y zonas
├── admin_tools.py           ← recintos, usuarios y catálogos
├── schema.sql               ← esquema completo de la base de datos
├── requirements.txt         ← dependencias de Python
├── main.spec                ← configuración de empaquetado (PyInstaller)
├── docker-compose.yml       ← contenedor MySQL para desarrollo/producción
├── start.bat                ← lanzador para Windows
└── .github/
    └── workflows/
        └── build.yml        ← pipeline de compilación automática del .exe
```

---

## Compilar el ejecutable (desarrolladores)

La compilación se realiza automáticamente en GitHub Actions al hacer `push` a `main`. El archivo `.exe` queda disponible como artefacto en la pestaña **Actions** del repositorio.

Para compilar manualmente en una máquina Windows:

```powershell
pip install -r requirements.txt
pip install pyinstaller
pyinstaller main.spec
```

El ejecutable resultante estará en `dist\BoletoPRO.exe`.

---

## Solución de problemas

| Problema | Solución |
|---|---|
| "No se pudo conectar a la base de datos" | Verifica que Docker Desktop esté abierto y ejecuta `docker-compose up -d` |
| La ventana cierra sola al abrir el .exe | Abre un CMD, navega a la carpeta y ejecuta `BoletoPRO.exe` directamente para ver el error |
| El contenedor tarda en responder | Espera 20–30 segundos adicionales tras iniciar Docker y vuelve a intentarlo |
| Puerto 3306 ocupado | Cierra cualquier instancia local de MySQL o cambia el puerto en `docker-compose.yml` |
