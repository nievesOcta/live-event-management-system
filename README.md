# EventosPRO — Sistema de Gestión de Boletos y Eventos

Sistema de escritorio para la administración de eventos musicales, venta de boletos, control de acceso y generación de reportes. Desarrollado con Python y SQLite.

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
| Base de datos | SQLite 3 (integrado en Python, sin instalación adicional) |
| Generación de PDF | ReportLab |
| Códigos QR | qrcode + Pillow |
| Exportación Excel | pandas + openpyxl |
| Empaquetado | PyInstaller |

> No se requiere Docker, MySQL ni ningún servidor de base de datos externo. La base de datos es un archivo local (`conciertos.db`) que se crea automáticamente al iniciar la aplicación por primera vez.

---

## Instalación en Windows 10

### Requisitos previos

Ninguno. No se necesita instalar Docker, MySQL ni ningún software adicional.

### Paso 1 — Obtener el ejecutable

Descarga el archivo `BoletoPRO.exe` desde la sección **Actions → Artifacts** del repositorio en GitHub, o solicítalo al equipo de desarrollo.

Colócalo en una carpeta de tu elección, por ejemplo:

```
C:\BoletoPRO\
└── BoletoPRO.exe
```

### Paso 2 — Iniciar la aplicación

Haz **doble clic** en `BoletoPRO.exe`.

En el primer arranque, la aplicación crea automáticamente la base de datos (`conciertos.db`) en la misma carpeta que el ejecutable y carga el esquema inicial. No es necesario ejecutar ningún comando adicional.

> Asegúrate de que `BoletoPRO.exe` se encuentre en una carpeta donde tengas permisos de escritura (por ejemplo `C:\BoletoPRO\`). Evita ejecutarlo directamente desde la carpeta `Descargas` o desde un dispositivo de solo lectura.

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
├── conexion.py              ← configuración de la conexión a SQLite
├── ventas.py                ← punto de venta y generación de boletos PDF
├── check_in.py              ← validación de entradas por código QR
├── reportes.py              ← historial, filtros y exportación a Excel
├── eventos.py               ← gestión de eventos y zonas
├── admin_tools.py           ← recintos, usuarios y catálogos
├── schema.sql               ← esquema completo de la base de datos (se empaqueta en el .exe)
├── requirements.txt         ← dependencias de Python
├── main.spec                ← configuración de empaquetado (PyInstaller)
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
| La ventana cierra sola al abrir el .exe | Abre un CMD, navega a la carpeta y ejecuta `BoletoPRO.exe` directamente para ver el error |
| "Error al conectar a SQLite" | Verifica que el .exe esté en una carpeta con permisos de escritura y vuelve a intentarlo |
| La base de datos aparece corrupta o vacía | Elimina el archivo `conciertos.db` de la carpeta del ejecutable; se recreará al siguiente inicio |
| Antivirus bloquea el .exe | Agrega una excepción para la carpeta de la aplicación; el ejecutable es generado por PyInstaller y puede activar falsos positivos |
