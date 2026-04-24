import customtkinter as ctk
from tkinter import ttk, messagebox
import conexion
import ventas
import os
import qrcode

def abrir_historial_cliente(usuario_id, es_admin=False):
    ventana = ctk.CTkToplevel()
    ventana.title("Historial de Boletos - TicketMaster Pro")
    ventana.geometry("1150x720")
    ventana.after(100, lambda: ventana.focus())

    header = ctk.CTkFrame(ventana, height=80, fg_color="#1a1a1a")
    header.pack(fill="x", padx=15, pady=15)
    titulo = "BUSCADOR DE BOLETOS (ADMIN)" if es_admin else "MIS BOLETOS COMPRADOS"
    ctk.CTkLabel(header, text=titulo, font=("Roboto", 24, "bold")).pack(pady=20)

    f_busqueda = ctk.CTkFrame(ventana, fg_color="transparent")
    f_busqueda.pack(fill="x", padx=40, pady=5)

    ent_nombre = None
    if es_admin:
        ent_nombre = ctk.CTkEntry(f_busqueda, placeholder_text="Buscar por nombre de cliente...", width=500, height=40)
        ent_nombre.pack(side="left", padx=(0, 10))

    if es_admin:
        columnas = ("Folio", "Cliente", "Evento", "Recinto", "Fecha Evento", "Fecha Compra", "Total", "Estado")
        col_widths = (60, 150, 170, 150, 130, 130, 90, 90)
    else:
        columnas = ("Folio", "Evento", "Recinto", "Fecha Evento", "Fecha Compra", "Total", "Estado")
        col_widths = (60, 200, 160, 140, 140, 100, 90)

    f_tabla = ctk.CTkFrame(ventana)
    f_tabla.pack(fill="both", expand=True, padx=40, pady=10)

    tabla = ttk.Treeview(f_tabla, columns=columnas, show="headings")
    for col, w in zip(columnas, col_widths):
        tabla.heading(col, text=col.upper())
        tabla.column(col, anchor="center", width=w)

    scroll = ttk.Scrollbar(f_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscroll=scroll.set)
    tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    def buscar():
        for i in tabla.get_children():
            tabla.delete(i)

        db = conexion.conectar_db()
        if not db:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return
        try:
            cur = db.cursor()
            if es_admin:
                nombre = ent_nombre.get().strip() if ent_nombre else ""
                if not nombre:
                    messagebox.showwarning("Atención", "Escribe un nombre para buscar.")
                    return
                query = """
                    SELECT r.ID, r.Cliente, e.Nombre,
                           COALESCE((SELECT Nombre FROM tblLugares WHERE ID=e.tblLugares_ID),
                                    (SELECT Nombre FROM tblLugares WHERE ID=e.Lugares_ID), 'N/A'),
                           e.Fecha, r.FechaReservacion, r.Total, r.Estado
                    FROM tblReservaciones r
                    JOIN tblEventos e ON r.Eventos_ID = e.ID
                    WHERE r.Cliente LIKE ?
                    ORDER BY r.FechaReservacion DESC
                """
                cur.execute(query, (f"%{nombre}%",))
            else:
                query = """
                    SELECT r.ID, e.Nombre,
                           COALESCE((SELECT Nombre FROM tblLugares WHERE ID=e.tblLugares_ID),
                                    (SELECT Nombre FROM tblLugares WHERE ID=e.Lugares_ID), 'N/A'),
                           e.Fecha, r.FechaReservacion, r.Total, r.Estado
                    FROM tblReservaciones r
                    JOIN tblEventos e ON r.Eventos_ID = e.ID
                    WHERE r.Usuarios_ID = ?
                    ORDER BY r.FechaReservacion DESC
                """
                cur.execute(query, (usuario_id,))

            filas = cur.fetchall()
            if not filas:
                messagebox.showinfo("Sin resultados", "No se encontraron boletos.")
                return
            for fila in filas:
                tabla.insert("", "end", values=fila)
        except Exception as e:
            messagebox.showerror("Error", f"Error en la consulta: {e}")
        finally:
            db.close()

    btn_texto = "🔍 BUSCAR" if es_admin else "📋 CARGAR MIS BOLETOS"
    ctk.CTkButton(f_busqueda, text=btn_texto, width=200, height=40, command=buscar).pack(side="left")

    def recuperar_boleto_pdf():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Elige un boleto de la lista.")
            return
        datos = tabla.item(seleccion)['values']
        folio = datos[0]
        if es_admin:
            nombre_cliente = datos[1]
            nombre_evento  = datos[2]
            nombre_recinto = datos[3]
            fecha_evento   = datos[4]
            total          = datos[6]
        else:
            nombre_cliente = datos[1]
            nombre_evento  = datos[1]
            nombre_recinto = datos[2]
            fecha_evento   = datos[3]
            total          = datos[5]

        qr_path = os.path.join(ventas.BOLETOS_DIR, f"boleto_{folio}.png")
        if not os.path.exists(qr_path):
            qrcode.make(f"TM_PRO|RECUPERAR|ID:{folio}").save(qr_path)

        try:
            precio_fmt = f"${float(total):,.2f}"
        except (TypeError, ValueError):
            precio_fmt = str(total)

        ventas.generar_pdf_universal({
            "folio":    folio,
            "cliente":  nombre_cliente,
            "evento":   nombre_evento,
            "recinto":  nombre_recinto,
            "fecha":    fecha_evento,
            "zona":     "Ver boleto original",
            "precio":   precio_fmt,
            "qr_path":  qr_path,
        })

    ctk.CTkButton(ventana, text="📥 DESCARGAR BOLETO SELECCIONADO",
                  fg_color="#3498db", hover_color="#2980b9", height=50,
                  font=("Roboto", 16, "bold"), command=recuperar_boleto_pdf).pack(pady=20)

    if not es_admin:
        ventana.after(200, buscar)
