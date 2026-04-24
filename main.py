import customtkinter as ctk
from tkinter import messagebox
import conexion
import eventos
import ventas
import admin_tools
import check_in
import reportes
import historial_cliente
import cartelera

# --- Configuración de Tema ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppTicketMaster(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("TicketMaster Pro - Dashboard Administrativo")
        self.geometry("550x850")
        self.resizable(False, False)
        
        # Iniciar con el Frame de Login
        self.setup_login_ui()

    def setup_login_ui(self):
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(pady=40, padx=40, fill="both", expand=True)

        ctk.CTkLabel(self.login_frame, text="LIVE EVENTS", font=("Roboto", 34, "bold")).pack(pady=(60, 10))
        ctk.CTkLabel(self.login_frame, text="Control de Acceso y Ventas", text_color="gray").pack(pady=(0, 40))

        self.entry_mail = ctk.CTkEntry(self.login_frame, placeholder_text="Correo Electrónico", width=320, height=45)
        self.entry_mail.pack(pady=12)

        self.entry_pass = ctk.CTkEntry(self.login_frame, placeholder_text="Contraseña", show="*", width=320, height=45)
        self.entry_pass.pack(pady=12)

        self.btn_login = ctk.CTkButton(self.login_frame, text="INICIAR SESIÓN", width=320, height=50, 
                                       font=("Roboto", 16, "bold"), command=self.procesar_login)
        self.btn_login.pack(pady=40)

    def procesar_login(self):
        correo = self.entry_mail.get()
        pwd = self.entry_pass.get()
        
        db = conexion.conectar_db()
        if db:
            try:
                cursor = db.cursor()
                query = "SELECT ID, Nombre, Rol FROM tblUsuarios WHERE Mail = ? AND Password = ?"
                cursor.execute(query, (correo, pwd))
                user = cursor.fetchone()
                
                if user:
                    self.abrir_dashboard(user['Rol'], user['Nombre'], user['ID'])
                else:
                    messagebox.showerror("Acceso Denegado", "Credenciales incorrectas.")
            except Exception as e:
                messagebox.showerror("Error de BD", f"Fallo en la consulta: {e}")
            finally:
                db.close()
        else:
            messagebox.showerror("Error de Conexión", "No se pudo conectar a la base de datos.")

    def abrir_dashboard(self, rol, nombre, usuario_id):
        self.withdraw() # Ocultar login
        
        self.dash = ctk.CTkToplevel()
        self.dash.title(f"TicketMaster - Panel de {nombre}")
        self.dash.geometry("650x900")
        self.dash.protocol("WM_DELETE_WINDOW", self.quit)

        # Header Principal
        header = ctk.CTkFrame(self.dash, height=150, fg_color="#1a1a1a", corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text=f"Bienvenido(a), {nombre}", font=("Roboto", 28, "bold")).pack(pady=(35, 5))
        ctk.CTkLabel(header, text=f"SESIÓN: {rol.upper()}", text_color="#3b8ed0", font=("Roboto", 13, "bold")).pack()

        # Menú Scrollable
        menu = ctk.CTkScrollableFrame(self.dash, fg_color="transparent")
        menu.pack(pady=20, padx=25, fill="both", expand=True)

        es_admin = (rol.lower() == 'admin')

        # --- SECCIÓN: VENTAS (COMÚN) ---
        ctk.CTkLabel(menu, text="TAQUILLA", font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w", padx=15, pady=(10, 5))

        ctk.CTkButton(menu, text="🎭 Cartelera de Eventos", width=500, height=55,
                      fg_color="#1a5276", hover_color="#154360", font=("Roboto", 15, "bold"),
                      command=cartelera.abrir_cartelera).pack(pady=8)

        ctk.CTkButton(menu, text="🛒 Punto de Venta / Compras", width=500, height=65,
                      fg_color="#2ecc71", hover_color="#27ae60", font=("Roboto", 18, "bold"),
                      command=lambda: ventas.abrir_punto_venta(usuario_id, es_admin=es_admin)).pack(pady=10)

        ctk.CTkButton(menu, text="🎫 Mi Historial de Boletos", width=500, height=55,
                      fg_color="#2471a3", hover_color="#1f618d", font=("Roboto", 15, "bold"),
                      command=lambda: historial_cliente.abrir_historial_cliente(usuario_id, es_admin=es_admin)).pack(pady=8)

        # --- SECCIÓN: ADMINISTRACIÓN (SOLO ADMIN) ---
        if es_admin:
            ctk.CTkLabel(menu, text="REPORTES Y OPERACIONES", font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w", padx=15, pady=(20, 5))
            
            # Buscador y Filtros (reportes.py)
            ctk.CTkButton(menu, text="📊 Historial y Filtros de Compra", width=500, height=55,
                          fg_color="#9b59b6", hover_color="#8e44ad", font=("Roboto", 15, "bold"),
                          command=reportes.abrir_buscador_compras).pack(pady=8)

            # Check-in (check_in.py)
            ctk.CTkButton(menu, text="🔍 Validar Entradas (Check-in)", width=500, height=55,
                          fg_color="#e67e22", hover_color="#d35400", font=("Roboto", 15, "bold"),
                          command=check_in.abrir_check_in).pack(pady=8)

            ctk.CTkLabel(menu, text="CONFIGURACIÓN TÉCNICA", font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w", padx=15, pady=(20, 5))

            # Eventos (eventos.py)
            ctk.CTkButton(menu, text="📅 Configurar Eventos y Zonas", width=500, height=50,
                          command=eventos.abrir_gestion_eventos).pack(pady=8)
            
            # Recintos (admin_tools.py)
            ctk.CTkButton(menu, text="🏢 Gestión de Recintos", width=500, height=50,
                          command=admin_tools.abrir_gestion_recintos).pack(pady=8)
            
            # Usuarios (admin_tools.py)
            ctk.CTkButton(menu, text="👥 Usuarios y Permisos", width=500, height=50,
                          fg_color="#5d6d7e", command=admin_tools.abrir_gestion_usuarios).pack(pady=8)
            
            # Catálogos (admin_tools.py)
            ctk.CTkButton(menu, text="⚙️ Configuración de Catálogos", width=500, height=50,
                          fg_color="#5d6d7e", command=admin_tools.abrir_config_catalogos).pack(pady=8)

        # Botón para cerrar sesión
        ctk.CTkButton(self.dash, text="CERRAR SESIÓN", fg_color="#e74c3c", hover_color="#c0392b",
                      width=220, height=45,
                      command=self.cerrar_sesion).pack(pady=30)

    
    def cerrar_sesion(self):
        self.dash.destroy()
        self.entry_mail.delete(0, 'end')
        self.entry_pass.delete(0, 'end')
        self.deiconify()

if __name__ == "__main__":
    conexion.init_db()
    app = AppTicketMaster()
    app.mainloop()