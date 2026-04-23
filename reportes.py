import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import conexion
import pandas as pd # Para exportar a Excel
from reportlab.pdfgen import canvas # Para generar el boleto PDF
from reportlab.lib.pagesizes import letter
import os

def abrir_buscador_compras():
    ventana = ctk.CTkToplevel()
    ventana.title("Buscador y Exportación de Ventas")
    ventana.geometry("1100x750")

    # ... (Mantener el código de filtros anterior) ...

    def exportar_excel():
        # Obtener datos de la tabla actual
        datos = []
        for row_id in tabla.get_children():
            datos.append(tabla.item(row_id)['values'])
        
        if not datos:
            messagebox.showwarning("Vacio", "No hay datos para exportar")
            return

        df = pd.DataFrame(datos, columns=["ID", "Cliente", "Evento", "Fecha", "Monto", "Estado", "Pago"])
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Éxito", "Reporte de ventas exportado correctamente")

    def generar_pdf_boleto():
        sel = tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona una compra de la lista")
            return
        
        datos = tabla.item(sel)['values']
        # datos = [ID, Cliente, Evento, Fecha, Monto, Estado, Pago]
        
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                filetypes=[("PDF files", "*.pdf")])
        if not file_path: return

        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            # Diseño del Boleto
            c.setStrokeColorRGB(0.2, 0.5, 0.8)
            c.rect(50, 600, 500, 200, stroke=1, fill=0) # Marco del boleto
            
            c.setFont("Helvetica-Bold", 18)
            c.drawString(70, 760, "TICKET MASTER PRO - COMPROBANTE")
            
            c.setFont("Helvetica", 12)
            c.drawString(70, 730, f"FOLIO: #{datos[0]}")
            c.drawString(70, 710, f"CLIENTE: {datos[1]}")
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(70, 680, f"EVENTO: {datos[2]}")
            
            c.setFont("Helvetica", 12)
            c.drawString(70, 660, f"FECHA DE COMPRA: {datos[3]}")
            c.drawString(70, 640, f"MÉTODO DE PAGO: {datos[6]}")
            
            c.setFont("Helvetica-Bold", 16)
            c.setFillColorRGB(0.1, 0.6, 0.2)
            c.drawString(400, 620, f"TOTAL: {datos[4]}")
            
            # Nota: Para el QR, el sistema ya genera una imagen en 'boletos_generados/'
            # Buscamos si existe la imagen con el ID de la reservación
            qr_path = f"boletos_generados/boleto_{datos[0]}.png"
            if os.path.exists(qr_path):
                c.drawImage(qr_path, 400, 670, width=100, height=100)
            
            c.save()
            messagebox.showinfo("PDF", "Boleto generado exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el PDF: {e}")

    # --- BOTONES DE ACCIÓN ---
    frame_csv = ctk.CTkFrame(ventana, fg_color="transparent")
    frame_csv.pack(pady=10)

    ctk.CTkButton(frame_csv, text="📥 Exportar Excel (Ventas)", fg_color="#27ae60", command=exportar_excel).pack(side="left", padx=10)
    ctk.CTkButton(frame_csv, text="📄 Imprimir Boleto Seleccionado", fg_color="#3498db", command=generar_pdf_boleto).pack(side="left", padx=10)

    # ... (Resto del código de la tabla y búsqueda) ...