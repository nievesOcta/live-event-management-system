import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import conexion
from conexion import BASE_DIR
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os


def abrir_buscador_compras():
    ventana = ctk.CTkToplevel()
    ventana.title("Buscador y Exportación de Ventas")
    ventana.geometry("1200x760")
    ventana.after(100, lambda: ventana.focus())

    # --- HEADER ---
    header = ctk.CTkFrame(ventana, height=70, fg_color="#1a1a1a")
    header.pack(fill="x", padx=15, pady=15)
    ctk.CTkLabel(header, text="HISTORIAL Y EXPORTACIÓN DE VENTAS",
                 font=("Roboto", 22, "bold")).pack(pady=18)

    # --- FILTROS ---
    f_filtros = ctk.CTkFrame(ventana, fg_color="transparent")
    f_filtros.pack(fill="x", padx=30, pady=(0, 5))

    ent_cliente = ctk.CTkEntry(f_filtros, placeholder_text="Buscar por cliente...",
                               width=200, height=38)
    ent_cliente.pack(side="left", padx=5)

    ent_evento = ctk.CTkEntry(f_filtros, placeholder_text="Buscar por evento...",
                              width=200, height=38)
    ent_evento.pack(side="left", padx=5)

    combo_estado = ctk.CTkComboBox(
        f_filtros,
        values=["Todos", "Confirmado", "Cancelado", "Usado"],
        width=140, height=38
    )
    combo_estado.set("Todos")
    combo_estado.pack(side="left", padx=5)

    lbl_total = ctk.CTkLabel(f_filtros, text="", text_color="gray",
                             font=("Roboto", 12))
    lbl_total.pack(side="right", padx=20)

    # --- TABLA ---
    f_tabla = ctk.CTkFrame(ventana)
    f_tabla.pack(fill="both", expand=True, padx=30, pady=10)

    columnas = ("ID", "Cliente", "Evento", "Fecha Compra", "Total", "Estado")
    col_widths = (60, 190, 230, 170, 110, 110)

    tabla = ttk.Treeview(f_tabla, columns=columnas, show="headings")
    for col, w in zip(columnas, col_widths):
        tabla.heading(col, text=col.upper())
        tabla.column(col, anchor="center", width=w)

    scroll_v = ttk.Scrollbar(f_tabla, orient="vertical", command=tabla.yview)
    scroll_h = ttk.Scrollbar(f_tabla, orient="horizontal", command=tabla.xview)
    tabla.configure(yscroll=scroll_v.set, xscroll=scroll_h.set)
    scroll_v.pack(side="right", fill="y")
    scroll_h.pack(side="bottom", fill="x")
    tabla.pack(side="left", fill="both", expand=True)

    # --- LÓGICA DE BÚSQUEDA ---
    def buscar():
        for i in tabla.get_children():
            tabla.delete(i)

        db = conexion.conectar_db()
        if not db:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return
        try:
            cur = db.cursor()
            cliente_f = f"%{ent_cliente.get().strip()}%"
            evento_f = f"%{ent_evento.get().strip()}%"
            estado_f = combo_estado.get()

            if estado_f == "Todos":
                cur.execute("""
                    SELECT r.ID, r.Cliente, e.Nombre, r.FechaReservacion, r.Total, r.Estado
                    FROM tblReservaciones r
                    JOIN tblEventos e ON r.Eventos_ID = e.ID
                    WHERE r.Cliente LIKE ? AND e.Nombre LIKE ?
                    ORDER BY r.FechaReservacion DESC
                """, (cliente_f, evento_f))
            else:
                cur.execute("""
                    SELECT r.ID, r.Cliente, e.Nombre, r.FechaReservacion, r.Total, r.Estado
                    FROM tblReservaciones r
                    JOIN tblEventos e ON r.Eventos_ID = e.ID
                    WHERE r.Cliente LIKE ? AND e.Nombre LIKE ? AND r.Estado = ?
                    ORDER BY r.FechaReservacion DESC
                """, (cliente_f, evento_f, estado_f))

            filas = cur.fetchall()
            for fila in filas:
                vals = list(fila)
                try:
                    vals[4] = f"${float(vals[4]):,.2f}"
                except (TypeError, ValueError):
                    pass
                tabla.insert("", "end", values=vals)

            lbl_total.configure(text=f"Registros encontrados: {len(filas)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la consulta: {e}")
        finally:
            db.close()

    ctk.CTkButton(f_filtros, text="🔍 BUSCAR", width=120, height=38,
                  command=buscar).pack(side="left", padx=5)

    # --- EXPORTAR EXCEL ---
    def exportar_excel():
        datos = [tabla.item(r)['values'] for r in tabla.get_children()]
        if not datos:
            messagebox.showwarning("Vacío", "No hay datos para exportar. Realiza una búsqueda primero.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="reporte_ventas.xlsx"
        )
        if not file_path:
            return

        df = pd.DataFrame(datos, columns=["ID", "Cliente", "Evento", "Fecha Compra", "Total", "Estado"])
        try:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Éxito", "Reporte de ventas exportado correctamente.")
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))

    # --- GENERAR PDF DEL BOLETO SELECCIONADO ---
    def generar_pdf_boleto():
        sel = tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un registro de la lista.")
            return

        datos = tabla.item(sel[0])['values']
        # datos: [ID, Cliente, Evento, Fecha Compra, Total (str formateado), Estado]

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Boleto_{datos[0]}_{str(datos[2]).replace(' ', '_')}.pdf"
        )
        if not file_path:
            return

        try:
            c = canvas.Canvas(file_path, pagesize=letter)

            # Cabecera
            c.setFillColorRGB(0.08, 0.12, 0.25)
            c.rect(0, 650, 612, 142, fill=1, stroke=0)
            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", 26)
            c.drawString(70, 740, "LIVE EVENTS PRO")
            c.setFont("Helvetica", 12)
            c.drawString(70, 720, "COMPROBANTE DE COMPRA")

            # Recuadro info
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setFillColorRGB(0.98, 0.98, 0.98)
            c.roundRect(50, 460, 512, 185, 10, fill=1, stroke=1)

            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(80, 615, f"EVENTO: {datos[2]}")
            c.setFont("Helvetica", 12)
            c.drawString(80, 593, f"CLIENTE: {datos[1]}")
            c.drawString(80, 573, f"FECHA DE COMPRA: {datos[3]}")
            c.drawString(80, 553, f"ESTADO: {datos[5]}")
            c.drawString(80, 533, f"FOLIO: #{datos[0]}")

            c.setFont("Helvetica-Bold", 15)
            c.setFillColorRGB(0.1, 0.5, 0.2)
            c.drawString(380, 533, f"TOTAL: {datos[4]}")

            # QR si existe
            qr_path = os.path.join(BASE_DIR, "boletos_generados", f"boleto_{datos[0]}.png")
            if os.path.exists(qr_path):
                c.drawImage(qr_path, 390, 555, width=130, height=130)

            c.save()
            messagebox.showinfo("PDF", "Boleto generado exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el PDF: {e}")

    # --- BOTONES DE ACCIÓN ---
    frame_botones = ctk.CTkFrame(ventana, fg_color="transparent")
    frame_botones.pack(pady=15)

    ctk.CTkButton(frame_botones, text="📥 Exportar Excel (Ventas)",
                  fg_color="#27ae60", hover_color="#1e8449",
                  width=230, height=48, font=("Roboto", 14, "bold"),
                  command=exportar_excel).pack(side="left", padx=10)

    ctk.CTkButton(frame_botones, text="📄 Imprimir Boleto Seleccionado",
                  fg_color="#3498db", hover_color="#2980b9",
                  width=260, height=48, font=("Roboto", 14, "bold"),
                  command=generar_pdf_boleto).pack(side="left", padx=10)

    # Carga automática al abrir
    ventana.after(200, buscar)
