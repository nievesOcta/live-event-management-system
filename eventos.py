import customtkinter as ctk
from tkinter import ttk, messagebox
import conexion

def abrir_gestion_eventos():
    ventana = ctk.CTkToplevel()
    ventana.title("Configuración de Eventos y Aforo")
    ventana.geometry("1100x850")
    ventana.after(100, lambda: ventana.focus())

    tabview = ctk.CTkTabview(ventana)
    tabview.pack(fill="both", expand=True, padx=15, pady=15)
    t_crear = tabview.add("Publicar Nuevo Concierto")
    t_lista = tabview.add("Eventos Activos")

    # --- VARIABLES DE CONTROL ---
    lista_zonas_evento = []

    # --- PESTAÑA CREAR EVENTO ---
    frame_scroll = ctk.CTkScrollableFrame(t_crear)
    frame_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(frame_scroll, text="DATOS DEL EVENTO", font=("Roboto", 18, "bold")).pack(pady=10)
    
    ent_nom = ctk.CTkEntry(frame_scroll, placeholder_text="Nombre del Concierto", width=450)
    ent_nom.pack(pady=5)
    
    ent_fec = ctk.CTkEntry(frame_scroll, placeholder_text="Fecha (AAAA-MM-DD HH:MM:SS)", width=450)
    ent_fec.pack(pady=5)

    combo_lugar = ctk.CTkComboBox(frame_scroll, width=450, state="readonly")
    combo_lugar.set("Seleccionar Recinto...")
    combo_lugar.pack(pady=5)

    # NUEVO: CAMPO DE DESCRIPCIÓN
    ctk.CTkLabel(frame_scroll, text="Descripción del Evento:").pack(pady=(10, 0))
    txt_desc = ctk.CTkTextbox(frame_scroll, width=450, height=100, border_width=2)
    txt_desc.pack(pady=5)

    # --- SECCIÓN DINÁMICA DE ÁREAS ---
    ctk.CTkLabel(frame_scroll, text="CONFIGURACIÓN DE ÁREAS / ZONAS", font=("Roboto", 16, "bold")).pack(pady=20)
    
    frame_add_zona = ctk.CTkFrame(frame_scroll)
    frame_add_zona.pack(pady=10, fill="x", padx=20)

    combo_tipo_zona = ctk.CTkComboBox(frame_add_zona, width=200, state="readonly")
    combo_tipo_zona.set("Tipo de Zona")
    combo_tipo_zona.grid(row=0, column=0, padx=10, pady=10)

    ent_cap = ctk.CTkEntry(frame_add_zona, placeholder_text="Capacidad", width=100)
    ent_cap.grid(row=0, column=1, padx=10)

    ent_pre = ctk.CTkEntry(frame_add_zona, placeholder_text="Precio $", width=100)
    ent_pre.grid(row=0, column=2, padx=10)

    # Tabla visual de zonas
    columnas = ("Tipo", "Capacidad", "Precio")
    tabla_zonas = ttk.Treeview(frame_scroll, columns=columnas, show="headings", height=5)
    for col in columnas:
        tabla_zonas.heading(col, text=col)
        tabla_zonas.column(col, width=150, anchor="center")
    tabla_zonas.pack(pady=10, padx=20, fill="x")

    def agregar_zona_a_lista():
        tipo = combo_tipo_zona.get()
        cap = ent_cap.get()
        pre = ent_pre.get()

        if tipo == "Tipo de Zona" or not cap or not pre:
            messagebox.showwarning("Faltan datos", "Completa el tipo, capacidad y precio de la zona.")
            return

        id_tipo = tipo.split(" - ")[0]
        nombre_tipo = tipo.split(" - ")[1]
        
        lista_zonas_evento.append({"id_tipo": id_tipo, "capacidad": cap, "precio": pre})
        tabla_zonas.insert("", "end", values=(nombre_tipo, cap, f"${pre}"))
        
        ent_cap.delete(0, 'end')
        ent_pre.delete(0, 'end')

    ctk.CTkButton(frame_add_zona, text="+ Agregar Área", command=agregar_zona_a_lista, fg_color="#3498db").grid(row=0, column=3, padx=10)

    # --- LÓGICA DE CARGA Y GUARDADO ---
    def cargar_datos():
        db = conexion.conectar_db()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT ID, Nombre FROM tblLugares")
            combo_lugar.configure(values=[f"{r[0]} - {r[1]}" for r in cursor.fetchall()])
            cursor.execute("SELECT ID, Nombre FROM catTiposZona")
            combo_tipo_zona.configure(values=[f"{r[0]} - {r[1]}" for r in cursor.fetchall()])
            db.close()

    def publicar_evento():
        nombre = ent_nom.get()
        fecha = ent_fec.get()
        lugar = combo_lugar.get()
        descripcion = txt_desc.get("1.0", "end-1c") # Obtiene todo el texto del CTkTextbox

        if not nombre or not fecha or lugar == "Seleccionar Recinto..." or not lista_zonas_evento:
            messagebox.showwarning("Incompleto", "Llene todos los campos y agregue al menos una zona.")
            return

        db = conexion.conectar_db()
        if db:
            try:
                cursor = db.cursor()
                id_lugar = lugar.split(" - ")[0]
                
                # 1. Insertar Evento (Asegúrate de que la columna 'Descripcion' exista en tblEventos)
                sql_ev = "INSERT INTO tblEventos (Nombre, Fecha, Lugares_ID, Descripcion) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_ev, (nombre, fecha, id_lugar, descripcion))
                id_evento = cursor.lastrowid

                # 2. Insertar cada Zona
                for z in lista_zonas_evento:
                    sql_z = """INSERT INTO tblZonas (Nombre, Capacidad, Precio, Eventos_ID, catTiposZona_ID) 
                               VALUES (%s, %s, %s, %s, %s)"""
                    cursor.execute(sql_z, (nombre, z['capacidad'], z['precio'], id_evento, z['id_tipo']))

                db.commit()
                messagebox.showinfo("Éxito", f"Evento '{nombre}' publicado correctamente.")
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error SQL", f"No se pudo guardar: {e}")
            finally:
                db.close()

    ctk.CTkButton(frame_scroll, text="GUARDAR Y PUBLICAR CONCIERTO", 
                  command=publicar_evento, fg_color="#2ecc71", height=50).pack(pady=40)

    cargar_datos()