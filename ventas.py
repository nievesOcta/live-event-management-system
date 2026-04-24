import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import conexion
from conexion import BASE_DIR
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from datetime import datetime

# Directorio de almacenamiento junto al ejecutable / script
BOLETOS_DIR = os.path.join(BASE_DIR, "boletos_generados")
if not os.path.exists(BOLETOS_DIR):
    os.makedirs(BOLETOS_DIR)

# --- GENERADOR DE BOLETOS PDF ---
def generar_pdf_universal(datos):
    archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=f"Boleto_{datos['folio']}_{datos['evento'].replace(' ', '_')}.pdf"
    )
    if not archivo: return

    try:
        c = canvas.Canvas(archivo, pagesize=letter)
        # Diseño de Cabecera
        c.setFillColorRGB(0.08, 0.12, 0.25)
        c.rect(0, 650, 612, 142, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 26)
        c.drawString(70, 740, "LIVE EVENTS PRO")
        c.setFont("Helvetica", 12)
        c.drawString(70, 725, "COMPROBANTE OFICIAL DE ACCESO")

        # Recuadro de Información Principal
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setFillColorRGB(0.98, 0.98, 0.98)
        c.roundRect(50, 480, 512, 190, 10, fill=1, stroke=1)
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(80, 630, f"EVENTO: {datos['evento']}")
        c.setFont("Helvetica", 12)
        c.drawString(80, 605, f"LUGAR: {datos['recinto']}")
        c.drawString(80, 585, f"FECHA: {datos['fecha']}")
        c.drawString(80, 565, f"ZONA: {datos['zona']}")
        c.drawString(80, 545, f"CLIENTE: {datos['cliente']}")
        
        # Total y Folio
        c.setFont("Helvetica-Bold", 15)
        c.setFillColorRGB(0.1, 0.5, 0.2)
        c.drawString(380, 545, f"TOTAL: {datos['precio']}")
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(380, 530, f"FOLIO: #{datos['folio']}")

        if os.path.exists(datos['qr_path']):
            c.drawImage(datos['qr_path'], 430, 570, width=110, height=110)
        
        c.save()
        messagebox.showinfo("Éxito", "El boleto se ha guardado correctamente.")
    except Exception as e:
        messagebox.showerror("Error PDF", f"No se pudo crear el archivo: {e}")

# --- INTERFAZ PRINCIPAL DE VENTAS ---
def abrir_punto_venta(usuario_id, es_admin=False):
    ventana = ctk.CTkToplevel()
    ventana.title("Punto de Venta - TicketMaster Pro")
    ventana.geometry("1100x750")
    ventana.grid_columnconfigure(0, weight=1)
    ventana.grid_columnconfigure(1, weight=1)

    # Variables de control de la UI
    var_evento = ctk.StringVar()
    var_zona = ctk.StringVar()
    var_precio = ctk.DoubleVar(value=0.0)

    # --- PANEL DE SELECCIÓN (IZQUIERDA) ---
    f_izq = ctk.CTkFrame(ventana, corner_radius=15)
    f_izq.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    ctk.CTkLabel(f_izq, text="REGISTRO DE VENTA", font=("Roboto", 22, "bold"), text_color="#3b8ed0").pack(pady=20)
    
    ent_cliente = ctk.CTkEntry(f_izq, placeholder_text="Nombre Completo del Cliente", width=380, height=45)
    ent_cliente.pack(pady=10)

    # Cargar eventos desde la BD
    def obtener_eventos():
        db = conexion.conectar_db()
        cursor = db.cursor()
        cursor.execute("SELECT Nombre FROM tblEventos WHERE Estado = 'Activo'")
        lista = [r[0] for r in cursor.fetchall()]
        db.close()
        return lista

    combo_ev = ctk.CTkComboBox(f_izq, values=obtener_eventos(), variable=var_evento, width=380, height=40)
    combo_ev.set("Seleccionar Evento")
    combo_ev.pack(pady=15)

    combo_zona = ctk.CTkComboBox(f_izq, values=[], variable=var_zona, width=380, height=40)
    combo_zona.set("Elige un evento primero")
    combo_zona.pack(pady=15)

    # --- PANEL DE VISTA PREVIA (DERECHA) ---
    f_der = ctk.CTkFrame(ventana, corner_radius=15, fg_color="#1a1a1a")
    f_der.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    t_ui = ctk.CTkFrame(f_der, fg_color="white", corner_radius=12, width=420, height=250)
    t_ui.pack(pady=30); t_ui.pack_propagate(False)

    l_ev_preview = ctk.CTkLabel(t_ui, text="BIENVENIDO", font=("Helvetica", 20, "bold"), text_color="black")
    l_ev_preview.pack(pady=(40, 5))
    l_inf_preview = ctk.CTkLabel(t_ui, text="Complete los datos para generar ticket", font=("Helvetica", 12), text_color="#555")
    l_inf_preview.pack()
    l_zona_preview = ctk.CTkLabel(t_ui, text="", font=("Helvetica", 15, "bold"), text_color="#3b8ed0")
    l_zona_preview.pack(pady=15)

    l_total_big = ctk.CTkLabel(f_der, text="$ 0.00", font=("Roboto", 55, "bold"), text_color="#2ecc71")
    l_total_big.pack(pady=20)

    # --- LÓGICA DINÁMICA DE LA BD ---
    def actualizar_evento(choice):
        db = conexion.conectar_db()
        cur = db.cursor()
        # Traer ID, Fecha y Nombre de Recinto
        query = """
            SELECT e.ID, e.Nombre, e.Fecha, (SELECT Nombre FROM tblLugares WHERE ID=e.tblLugares_ID) as Recinto
            FROM tblEventos e WHERE e.Nombre = ?
        """
        cur.execute(query, (choice,))
        ev = cur.fetchone()
        if ev:
            l_ev_preview.configure(text=ev['Nombre'].upper())
            l_inf_preview.configure(text=f"{ev['Recinto']} | {ev['Fecha']}")
            # Filtrar zonas del evento
            cur.execute("SELECT NombreZona FROM tblZonasEventos WHERE Eventos_ID = ?", (ev['ID'],))
            zonas = [z['NombreZona'] for z in cur.fetchall()]
            combo_zona.configure(values=zonas)
            if zonas:
                combo_zona.set(zonas[0])
                actualizar_precio(zonas[0])
        db.close()

    def actualizar_precio(choice):
        db = conexion.conectar_db()
        cur = db.cursor()
        query = """
            SELECT Precio FROM tblZonasEventos ze
            JOIN tblEventos e ON ze.Eventos_ID = e.ID
            WHERE e.Nombre = ? AND ze.NombreZona = ?
        """
        cur.execute(query, (var_evento.get(), choice))
        res = cur.fetchone()
        if res:
            p = float(res[0])
            var_precio.set(p)
            l_total_big.configure(text=f"$ {p:,.2f}")
            l_zona_preview.configure(text=f"ZONA: {choice.upper()}")
        db.close()

    combo_ev.configure(command=actualizar_evento)
    combo_zona.configure(command=actualizar_precio)

    # --- FINALIZACIÓN DE VENTA ---
    def finalizar_venta():
        cliente = ent_cliente.get().strip()
        evento = var_evento.get()
        zona = var_zona.get()

        if not cliente or evento == "Seleccionar Evento":
            messagebox.showwarning("Error", "Debes ingresar el nombre del cliente y elegir un evento.")
            return

        db = conexion.conectar_db()
        try:
            cur = db.cursor()
            # 1. Obtener datos finales del evento para el registro
            cur.execute("""
                SELECT e.ID, (SELECT Nombre FROM tblLugares WHERE ID=e.tblLugares_ID) as Recinto, e.Fecha
                FROM tblEventos e WHERE e.Nombre = ?""", (evento,))
            ev_final = cur.fetchone()

            # 2. Insertar reservación en BD
            sql = """INSERT INTO tblReservaciones
                     (Usuarios_ID, Eventos_ID, FechaReservacion, Total, Estado, Cliente)
                     VALUES (?, ?, ?, ?, ?, ?)"""
            cur.execute(sql, (usuario_id, ev_final['ID'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), var_precio.get(), 'Confirmado', cliente))
            db.commit()
            
            folio = cur.lastrowid
            
            # 3. Generar el código QR único
            qr_path = os.path.join(BOLETOS_DIR, f"boleto_{folio}.png")
            img_qr = qrcode.make(f"TM_PRO|ID:{folio}|USER:{cliente}")
            img_qr.save(qr_path)
            
            # 4. Ofrecer la descarga del PDF
            if messagebox.askyesno("Éxito", f"¡Venta Registrada!\nFolio: #{folio}\n\n¿Deseas descargar el boleto ahora?"):
                generar_pdf_universal({
                    "folio": folio, "cliente": cliente, "evento": evento,
                    "recinto": ev_final['Recinto'], "fecha": ev_final['Fecha'],
                    "zona": zona, "precio": f"${var_precio.get():,.2f}", "qr_path": qr_path
                })
            ventana.destroy()
        except Exception as e:
            db.rollback()
            messagebox.showerror("Error", f"Ocurrió un error al procesar la venta: {e}")
        finally:
            db.close()

    btn_vender = ctk.CTkButton(f_der, text="CONFIRMAR PAGO", fg_color="#2ecc71", 
                               hover_color="#27ae60", height=60, font=("Roboto", 18, "bold"),
                               command=finalizar_venta)
    btn_vender.pack(side="bottom", fill="x", padx=40, pady=40)