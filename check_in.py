import customtkinter as ctk
from tkinter import messagebox
import conexion
from datetime import datetime

def abrir_check_in():
    ventana = ctk.CTkToplevel()
    ventana.title("Control de Acceso - Escaneo de Boletos")
    ventana.geometry("600x500")
    ventana.after(100, lambda: ventana.focus())

    ctk.CTkLabel(ventana, text="VALIDACIÓN DE ENTRADAS", font=("Roboto", 24, "bold")).pack(pady=20)

    # Entrada de código (Simula el escáner de QR)
    ctk.CTkLabel(ventana, text="Ingresa o escanea el código del boleto:").pack(pady=5)
    ent_codigo = ctk.CTkEntry(ventana, width=400, height=50, font=("Roboto", 18), placeholder_text="Ej: EV-1-RES-10-B1")
    ent_codigo.pack(pady=20)
    ent_codigo.focus()

    # Panel de resultado visual
    frame_res = ctk.CTkFrame(ventana, width=500, height=150, corner_radius=15)
    frame_res.pack(pady=20)
    lbl_status = ctk.CTkLabel(frame_res, text="Esperando escaneo...", font=("Roboto", 16))
    lbl_status.place(relx=0.5, rely=0.5, anchor="center")

    def validar_boleto(event=None):
        codigo = ent_codigo.get().strip()
        if not codigo: return

        db = conexion.conectar_db()
        if db:
            try:
                cursor = db.cursor(dictionary=True)
                # Buscamos el boleto y el nombre del evento/usuario para confirmar
                query = """
                    SELECT b.ID, b.EstadoAcceso, e.Nombre as Evento, u.Nombre as Cliente
                    FROM tblBoletos b
                    JOIN tblDetallesReservacion dr ON b.DetallesReservacion_ID = dr.ID
                    JOIN tblReservaciones r ON dr.Reservaciones_ID = r.ID
                    JOIN tblEventos e ON r.Eventos_ID = e.ID
                    JOIN tblUsuarios u ON r.Usuarios_ID = u.ID
                    WHERE b.CodigoQR = %s
                """
                cursor.execute(query, (codigo,))
                boleto = cursor.fetchone()

                if boleto:
                    if boleto['EstadoAcceso'] == 'Activo':
                        # Marcar como usado
                        cursor.execute("UPDATE tblBoletos SET EstadoAcceso = 'Usado' WHERE ID = %s", (boleto['ID'],))
                        db.commit()
                        
                        frame_res.configure(fg_color="#27ae60") # Verde
                        lbl_status.configure(text=f"✅ ACCESO CONCEDIDO\n\nEvento: {boleto['Evento']}\nCliente: {boleto['Cliente']}")
                    else:
                        frame_res.configure(fg_color="#e74c3c") # Rojo
                        lbl_status.configure(text=f"❌ BOLETO YA USADO\nEste código ya ingresó al evento.")
                else:
                    frame_res.configure(fg_color="#f1c40f") # Amarillo
                    lbl_status.configure(text="⚠️ BOLETO NO ENCONTRADO\nEl código no existe en la base de datos.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error de validación: {e}")
            finally:
                db.close()
                ent_codigo.delete(0, 'end')

    # Vincular la tecla Enter para que funcione rápido como un escáner real
    ent_codigo.bind('<Return>', validar_boleto)
    ctk.CTkButton(ventana, text="VALIDAR MANUALMENTE", command=validar_boleto).pack(pady=10)