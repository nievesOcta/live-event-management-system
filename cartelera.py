import customtkinter as ctk
from tkinter import messagebox
import conexion

def abrir_cartelera():
    ventana = ctk.CTkToplevel()
    ventana.title("Cartelera de Eventos - TicketMaster Pro")
    ventana.geometry("1000x780")
    ventana.after(100, lambda: ventana.focus())

    header = ctk.CTkFrame(ventana, height=90, fg_color="#0d1b2a", corner_radius=0)
    header.pack(fill="x")
    ctk.CTkLabel(header, text="🎤  CARTELERA DE EVENTOS",
                 font=("Roboto", 28, "bold"), text_color="#f0e68c").pack(pady=25)

    scroll = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=20, pady=20)

    db = conexion.conectar_db()
    if not db:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
        return

    try:
        cur = db.cursor()
        cur.execute("""
            SELECT e.ID, e.Nombre, e.Fecha,
                   COALESCE((SELECT Nombre     FROM tblLugares WHERE ID=e.tblLugares_ID),
                            (SELECT Nombre     FROM tblLugares WHERE ID=e.Lugares_ID), 'N/A'),
                   COALESCE((SELECT Direccion  FROM tblLugares WHERE ID=e.tblLugares_ID),
                            (SELECT Direccion  FROM tblLugares WHERE ID=e.Lugares_ID), ''),
                   e.Descripcion
            FROM tblEventos e
            WHERE e.Estado = 'Activo'
            ORDER BY e.Fecha
        """)
        eventos = cur.fetchall()

        if not eventos:
            ctk.CTkLabel(scroll, text="No hay eventos activos en este momento.",
                         font=("Roboto", 18), text_color="gray").pack(pady=100)
            return

        for ev in eventos:
            ev_id, nombre, fecha, recinto, direccion, descripcion = (
                ev[0], ev[1], ev[2], ev[3], ev[4], ev[5]
            )

            card = ctk.CTkFrame(scroll, corner_radius=15, fg_color="#1e2d3d",
                                border_width=1, border_color="#3b8ed0")
            card.pack(fill="x", pady=10, padx=5)

            ctk.CTkLabel(card, text=nombre.upper(),
                         font=("Roboto", 22, "bold"), text_color="#f0e68c").pack(anchor="w", padx=20, pady=(15, 4))

            ctk.CTkLabel(card, text=f"📅  {fecha}",
                         font=("Roboto", 13), text_color="#a8d8ea").pack(anchor="w", padx=20)

            lugar_texto = recinto
            if direccion:
                lugar_texto += f"  —  {direccion}"
            ctk.CTkLabel(card, text=f"📍  {lugar_texto}",
                         font=("Roboto", 12), text_color="#b0bec5").pack(anchor="w", padx=20, pady=(2, 4))

            if descripcion and descripcion.strip():
                ctk.CTkLabel(card, text=descripcion.strip(),
                             font=("Roboto", 12), text_color="#cfd8dc",
                             wraplength=920, justify="left").pack(anchor="w", padx=20, pady=(0, 6))

            cur.execute("""
                SELECT tz.Nombre, z.Capacidad, z.Precio
                FROM tblZonas z
                JOIN catTiposZona tz ON z.catTiposZona_ID = tz.ID
                WHERE z.Eventos_ID = ?
                ORDER BY z.Precio DESC
            """, (ev_id,))
            zonas = cur.fetchall()

            f_zonas = ctk.CTkFrame(card, fg_color="#152535", corner_radius=10)
            f_zonas.pack(fill="x", padx=20, pady=(4, 15))

            ctk.CTkLabel(f_zonas, text="ZONAS DISPONIBLES",
                         font=("Roboto", 11, "bold"), text_color="#888888").pack(anchor="w", padx=15, pady=(8, 4))

            if zonas:
                for zona in zonas:
                    tipo_zona, cap, precio = zona[0], zona[1], zona[2]
                    try:
                        precio_fmt = f"${float(precio):,.2f}"
                    except (TypeError, ValueError):
                        precio_fmt = str(precio)
                    texto = f"  •  {tipo_zona}   |   Capacidad: {cap}   |   Precio: {precio_fmt}"
                    ctk.CTkLabel(f_zonas, text=texto,
                                 font=("Roboto", 12), text_color="#e0e0e0").pack(anchor="w", padx=15, pady=2)
            else:
                ctk.CTkLabel(f_zonas, text="  Sin zonas configuradas.",
                             font=("Roboto", 11), text_color="#78909c").pack(anchor="w", padx=15, pady=4)

            ctk.CTkLabel(f_zonas, text="").pack(pady=2)

    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar la cartelera: {e}")
    finally:
        db.close()
