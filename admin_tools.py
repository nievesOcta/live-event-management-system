import customtkinter as ctk
from tkinter import ttk, messagebox
import conexion

# --- 1. GESTIÓN DE USUARIOS ---
def abrir_gestion_usuarios():
    ventana = ctk.CTkToplevel()
    ventana.title("Panel de Usuarios")
    ventana.geometry("1000x700")
    ventana.after(100, lambda: ventana.focus())

    tabview = ctk.CTkTabview(ventana)
    tabview.pack(pady=10, padx=20, fill="both", expand=True)
    tab_lista = tabview.add("Usuarios Registrados")
    tab_nuevo = tabview.add("Agregar Nuevo Usuario")

    columnas = ("ID", "Nombre", "Correo", "Rol")
    tabla = ttk.Treeview(tab_lista, columns=columnas, show="headings")
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=200, anchor="center")
    tabla.pack(expand=True, fill="both", padx=10, pady=10)

    def cargar_usuarios():
        for i in tabla.get_children(): tabla.delete(i)
        db = conexion.conectar_db()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT ID, Nombre, Mail, Rol FROM tblUsuarios")
            for fila in cursor.fetchall(): tabla.insert("", "end", values=tuple(fila))
            db.close()

    # Formulario de registro (Pestaña Nuevo)
    ctk.CTkLabel(tab_nuevo, text="NUEVO REGISTRO", font=("Roboto", 20, "bold")).pack(pady=20)
    en_nom = ctk.CTkEntry(tab_nuevo, placeholder_text="Nombre", width=400)
    en_nom.pack(pady=10)
    en_mail = ctk.CTkEntry(tab_nuevo, placeholder_text="Correo", width=400)
    en_mail.pack(pady=10)
    en_pass = ctk.CTkEntry(tab_nuevo, placeholder_text="Password", show="*", width=400)
    en_pass.pack(pady=10)
    cb_rol = ctk.CTkComboBox(tab_nuevo, values=["Cliente", "Admin"], width=400)
    cb_rol.set("Cliente")
    cb_rol.pack(pady=10)

    def guardar():
        db = conexion.conectar_db()
        if db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO tblUsuarios (Nombre, Mail, Password, Rol) VALUES (?, ?, ?, ?)",
                           (en_nom.get(), en_mail.get(), en_pass.get(), cb_rol.get()))
            db.commit(); db.close()
            messagebox.showinfo("Éxito", "Usuario guardado"); cargar_usuarios()
            tabview.set("Usuarios Registrados")

    ctk.CTkButton(tab_nuevo, text="Guardar", command=guardar, fg_color="#2ecc71").pack(pady=20)
    cargar_usuarios()

# --- 2. GESTIÓN DE RECINTOS (El que te daba error) ---
def abrir_gestion_recintos():
    ventana = ctk.CTkToplevel()
    ventana.title("Gestión de Recintos")
    ventana.geometry("900x600")
    ventana.after(100, lambda: ventana.focus())

    tabview = ctk.CTkTabview(ventana)
    tabview.pack(pady=10, padx=20, fill="both", expand=True)
    t_lista = tabview.add("Lista de Recintos")
    t_nuevo = tabview.add("Nuevo Recinto")

    cols = ("ID", "Nombre", "Dirección", "Capacidad")
    tabla = ttk.Treeview(t_lista, columns=cols, show="headings")
    for c in cols: tabla.heading(c, text=c); tabla.column(c, width=150)
    tabla.pack(expand=True, fill="both", padx=10, pady=10)

    def cargar():
        for i in tabla.get_children(): tabla.delete(i)
        db = conexion.conectar_db()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT ID, Nombre, Direccion, CapacidadTotal FROM tblLugares")
            for r in cursor.fetchall(): tabla.insert("", "end", values=tuple(r))
            db.close()

    en_n = ctk.CTkEntry(t_nuevo, placeholder_text="Nombre", width=400)
    en_n.pack(pady=10)
    en_d = ctk.CTkEntry(t_nuevo, placeholder_text="Dirección", width=400)
    en_d.pack(pady=10)
    en_c = ctk.CTkEntry(t_nuevo, placeholder_text="Capacidad", width=400)
    en_c.pack(pady=10)

    def guardar_r():
        nombre = en_n.get().strip()
        direccion = en_d.get().strip()
        capacidad = en_c.get().strip()
        if not nombre or not direccion or not capacidad:
            messagebox.showwarning("Campos incompletos", "Todos los campos son obligatorios.")
            return
        try:
            cap = int(capacidad)
        except ValueError:
            messagebox.showerror("Error", "La capacidad debe ser un número entero.")
            return
        db = conexion.conectar_db()
        if db:
            try:
                cursor = db.cursor()
                cursor.execute("INSERT INTO tblLugares (Nombre, Direccion, CapacidadTotal) VALUES (?, ?, ?)",
                               (nombre, direccion, cap))
                db.commit()
                messagebox.showinfo("Éxito", f"Recinto '{nombre}' guardado correctamente.")
                en_n.delete(0, 'end')
                en_d.delete(0, 'end')
                en_c.delete(0, 'end')
                cargar()
                tabview.set("Lista de Recintos")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el recinto: {e}")
            finally:
                db.close()

    ctk.CTkButton(t_nuevo, text="Guardar Recinto", command=guardar_r).pack(pady=20)
    cargar()

# --- 3. CONFIGURACIÓN DE CATÁLOGOS ---
def abrir_config_catalogos():
    ventana = ctk.CTkToplevel()
    ventana.title("Catálogos")
    ventana.geometry("800x600")
    tabview = ctk.CTkTabview(ventana)
    tabview.pack(pady=10, padx=20, fill="both", expand=True)
    t_gen = tabview.add("Géneros"); t_pag = tabview.add("Pagos"); t_zon = tabview.add("Zonas")

    def setup_tab(tab, tabla_db):
        en = ctk.CTkEntry(tab, placeholder_text="Nuevo...", width=300); en.pack(pady=10)
        tree = ttk.Treeview(tab, columns=("ID", "Nombre"), show="headings")
        tree.heading("ID", text="ID"); tree.heading("Nombre", text="Nombre"); tree.pack(fill="both", expand=True)

        def ref():
            for i in tree.get_children(): tree.delete(i)
            db = conexion.conectar_db(); cursor = db.cursor()
            cursor.execute(f"SELECT * FROM {tabla_db}"); [tree.insert("", "end", values=tuple(f)) for f in cursor.fetchall()]
            db.close()
        def add():
            db = conexion.conectar_db(); cursor = db.cursor()
            cursor.execute(f"INSERT INTO {tabla_db} (Nombre) VALUES (?)", (en.get(),))
            db.commit(); db.close(); en.delete(0, 'end'); ref()

        ctk.CTkButton(tab, text="Agregar", command=add).pack(pady=5)
        ref()

    setup_tab(t_gen, "catGenero")
    setup_tab(t_pag, "catMetodoPago")
    setup_tab(t_zon, "catTiposZona")