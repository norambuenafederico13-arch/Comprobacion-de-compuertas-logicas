import threading
import time
import tkinter as tk

import customtkinter as ctk
import serial
import serial.tools.list_ports


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppCompuertas(ctk.CTk):
    TIEMPO_MAXIMO_PRUEBA = 15

    def __init__(self):
        super().__init__()

        self.title("Tester de Circuitos Integrados - ESP32-S3")
        self.geometry("900x700")
        self.minsize(680, 540)

        self.serial_esp32 = None
        self.prueba_en_curso = False
        self.cerrando = False
        self.pantalla_completa = False

        self.ic_seleccionado = tk.StringVar(
            master=self,
            value="CD4081BE (AND)"
        )

        self.bind("<F11>", self.alternar_pantalla_completa)
        self.bind("<Escape>", self.salir_pantalla_completa)
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        self.crear_interfaz()
        self.actualizar_puertos()

    def alternar_pantalla_completa(self, event=None):
        self.pantalla_completa = not self.pantalla_completa
        self.attributes("-fullscreen", self.pantalla_completa)
        return "break"

    def salir_pantalla_completa(self, event=None):
        self.pantalla_completa = False
        self.attributes("-fullscreen", False)
        return "break"

    def crear_interfaz(self):
        contenedor = ctk.CTkFrame(self, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=14, pady=14)

        frame_conexion = ctk.CTkFrame(contenedor, corner_radius=12)
        frame_conexion.pack(fill="x", padx=8, pady=(8, 6))

        ctk.CTkLabel(
            frame_conexion,
            text="Puerto COM",
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=(14, 8), pady=12)

        self.combo_puertos = ctk.CTkComboBox(
            frame_conexion,
            values=["No se detectaron puertos"],
            width=190
        )
        self.combo_puertos.pack(side="left", padx=5, pady=12)

        self.btn_refrescar = ctk.CTkButton(
            frame_conexion,
            text="⟳",
            width=42,
            command=self.actualizar_puertos
        )
        self.btn_refrescar.pack(side="left", padx=5, pady=12)

        self.btn_conectar = ctk.CTkButton(
            frame_conexion,
            text="Conectar",
            command=self.toggle_conexion
        )
        self.btn_conectar.pack(side="left", padx=8, pady=12)

        self.lbl_estado_conexion = ctk.CTkLabel(
            frame_conexion,
            text="● Desconectado",
            text_color="#ff6b6b",
            font=("Arial", 12, "bold")
        )
        self.lbl_estado_conexion.pack(side="right", padx=16)

        frame_prueba = ctk.CTkFrame(contenedor, corner_radius=12)
        frame_prueba.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(
            frame_prueba,
            text="Integrado",
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=(14, 8), pady=12)

        self.combo_ic = ctk.CTkOptionMenu(
            frame_prueba,
            values=[
                "CD4081BE (AND)",
                "CD4071BE (OR)",
                "CD4069BE (NOT)"
            ],
            variable=self.ic_seleccionado
        )
        self.combo_ic.pack(side="left", padx=8, pady=12)

        self.btn_probar = ctk.CTkButton(
            frame_prueba,
            text="▶  Iniciar prueba",
            font=("Arial", 12, "bold"),
            state="disabled",
            command=self.enviar_prueba
        )
        self.btn_probar.pack(side="right", padx=14, pady=12)

        self.lbl_resultado = ctk.CTkLabel(
            contenedor,
            text="Conecta el ESP32 para iniciar una prueba.",
            font=("Arial", 17, "bold"),
            text_color="#b7c0c8",
            wraplength=760,
            justify="center"
        )
        self.lbl_resultado.pack(fill="x", padx=12, pady=(12, 4))

        ctk.CTkLabel(
            contenedor,
            text=(
                "Haz clic en una compuerta para consultar "
                "sus pruebas individuales. F11: pantalla completa."
            ),
            font=("Arial", 12),
            text_color="#9ca3af",
            wraplength=760,
            justify="center"
        ).pack(fill="x", padx=12, pady=(0, 8))

        self.panel_compuertas = ctk.CTkScrollableFrame(
            contenedor,
            fg_color="#191c22",
            corner_radius=14
        )
        self.panel_compuertas.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(4, 8)
        )

        self.mostrar_mensaje_panel(
            "Aún no hay resultados.\n\n"
            "Conecta el ESP32 y presiona «Iniciar prueba»."
        )

    def cantidad_compuertas_seleccionada(self):
        return 6 if "(NOT)" in self.ic_seleccionado.get() else 4

    def mostrar_mensaje_panel(self, texto):
        for widget in self.panel_compuertas.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.panel_compuertas,
            text=texto,
            font=("Arial", 13),
            text_color="#9ca3af",
            justify="center",
            wraplength=650
        ).pack(fill="x", padx=12, pady=28)

    def actualizar_puertos(self):
        puertos = [
            puerto.device
            for puerto in serial.tools.list_ports.comports()
        ]

        if not puertos:
            puertos = ["No se detectaron puertos"]

        self.combo_puertos.configure(values=puertos)
        self.combo_puertos.set(puertos[0])

    def toggle_conexion(self):
        if self.serial_esp32 is None:
            self.conectar()
        else:
            self.desconectar()

    def conectar(self):
        puerto = self.combo_puertos.get()

        if puerto == "No se detectaron puertos":
            self.lbl_estado_conexion.configure(
                text="● No hay puertos",
                text_color="#ff6b6b"
            )
            return

        try:
            self.serial_esp32 = serial.Serial(
                port=puerto,
                baudrate=115200,
                timeout=1,
                write_timeout=3
            )

            time.sleep(1.5)
            self.serial_esp32.reset_input_buffer()

            self.lbl_estado_conexion.configure(
                text=f"● Conectado ({puerto})",
                text_color="#2ecc71"
            )
            self.btn_conectar.configure(text="Desconectar")
            self.btn_probar.configure(state="normal")

        except (serial.SerialException, OSError) as error:
            self.serial_esp32 = None

            self.lbl_estado_conexion.configure(
                text="● Error de conexión",
                text_color="#ff6b6b"
            )
            self.lbl_resultado.configure(
                text=f"No se pudo abrir el puerto: {error}",
                text_color="#ff6b6b"
            )

    def desconectar(self):
        if self.prueba_en_curso:
            return

        try:
            if self.serial_esp32 is not None:
                self.serial_esp32.close()
        except (serial.SerialException, OSError):
            pass

        self.serial_esp32 = None

        self.lbl_estado_conexion.configure(
            text="● Desconectado",
            text_color="#ff6b6b"
        )
        self.btn_conectar.configure(text="Conectar")
        self.btn_probar.configure(state="disabled")

    def enviar_prueba(self):
        if (
            self.serial_esp32 is None
            or not self.serial_esp32.is_open
        ):
            self.lbl_resultado.configure(
                text="No hay una conexión serial abierta.",
                text_color="#ff6b6b"
            )
            return

        if self.prueba_en_curso:
            return

        seleccion = self.ic_seleccionado.get()

        if "(AND)" in seleccion:
            comando = b"A"
            nombre_tipo = "AND"
        elif "(OR)" in seleccion:
            comando = b"O"
            nombre_tipo = "OR"
        else:
            comando = b"N"
            nombre_tipo = "NOT"

        self.prueba_en_curso = True
        self.btn_probar.configure(state="disabled")
        self.btn_conectar.configure(state="disabled")
        self.combo_ic.configure(state="disabled")

        self.lbl_resultado.configure(
            text=f"⏳ Probando el integrado {nombre_tipo}...",
            text_color="#f1c40f"
        )

        self.mostrar_compuertas_pendientes()

        threading.Thread(
            target=self.leer_resultados,
            args=(comando, nombre_tipo),
            daemon=True
        ).start()

    def mostrar_compuertas_pendientes(self):
        for widget in self.panel_compuertas.winfo_children():
            widget.destroy()

        cantidad = self.cantidad_compuertas_seleccionada()

        for numero in range(1, cantidad + 1):
            tarjeta = ctk.CTkFrame(
                self.panel_compuertas,
                fg_color="#252a34",
                corner_radius=12
            )
            tarjeta.pack(fill="x", padx=8, pady=6)

            ctk.CTkLabel(
                tarjeta,
                text=f"▸   Compuerta {numero}     EN ESPERA",
                anchor="w",
                height=42,
                fg_color="#303744",
                text_color="#9ca3af",
                corner_radius=8,
                font=("Arial", 13, "bold")
            ).pack(fill="x", padx=8, pady=8)

    def leer_resultados(self, comando, tipo_esperado):
        pruebas = []
        resumen = None

        try:
            self.serial_esp32.reset_input_buffer()
            self.serial_esp32.write(comando)
            self.serial_esp32.flush()

            limite = time.monotonic() + self.TIEMPO_MAXIMO_PRUEBA

            while time.monotonic() < limite:
                linea = self.serial_esp32.readline().decode(
                    "utf-8",
                    errors="replace"
                ).strip()

                if not linea:
                    continue

                partes = linea.split(",")

                if partes[0] == "TEST":
                    if len(partes) != 7:
                        raise ValueError(
                            f"Formato TEST incorrecto: {linea}"
                        )

                    (
                        _,
                        tipo,
                        compuerta,
                        entrada_a,
                        entrada_b,
                        esperado,
                        medido
                    ) = partes

                    if tipo != tipo_esperado:
                        raise ValueError(
                            f"El ESP32 envió una prueba {tipo}, "
                            f"pero se esperaba {tipo_esperado}."
                        )

                    esperado_int = int(esperado)
                    medido_int = int(medido)

                    pruebas.append({
                        "tipo": tipo,
                        "compuerta": int(compuerta),
                        "entrada_a": entrada_a,
                        "entrada_b": entrada_b,
                        "esperado": esperado_int,
                        "medido": medido_int,
                        "correcta": esperado_int == medido_int
                    })

                elif partes[0] == "DONE":
                    if len(partes) != 3:
                        raise ValueError(
                            f"Formato DONE incorrecto: {linea}"
                        )

                    _, tipo, estado = partes
                    resumen = (tipo, estado)
                    break

                elif partes[0] == "ERROR":
                    raise ValueError(
                        "El ESP32 indicó un error: " + linea
                    )

            if resumen is None:
                raise TimeoutError(
                    "El ESP32 no envió el resumen DONE. "
                    "Revisa el firmware y la conexión."
                )

            tipo_recibido, estado_general = resumen

            if tipo_recibido != tipo_esperado:
                raise ValueError(
                    f"Se esperaba una prueba {tipo_esperado}, "
                    f"pero el ESP32 respondió {tipo_recibido}."
                )

            if estado_general not in ("GOOD", "BAD"):
                raise ValueError(
                    f"Estado general no reconocido: {estado_general}"
                )

            if not pruebas:
                raise ValueError(
                    "El ESP32 terminó la prueba, pero no envió lecturas."
                )

            self.ejecutar_en_interfaz(
                self.mostrar_resultados,
                pruebas,
                estado_general
            )

        except Exception as error:
            self.ejecutar_en_interfaz(
                self.mostrar_error,
                str(error)
            )

    def ejecutar_en_interfaz(self, funcion, *args):
        if self.cerrando:
            return

        try:
            self.after(0, funcion, *args)
        except tk.TclError:
            pass

    def mostrar_resultados(self, pruebas, estado_general):
        cantidad = self.cantidad_compuertas_seleccionada()
        resultados_por_compuerta = {
            numero: [] for numero in range(1, cantidad + 1)
        }

        for prueba in pruebas:
            numero = prueba["compuerta"]

            if numero in resultados_por_compuerta:
                resultados_por_compuerta[numero].append(prueba)

        for widget in self.panel_compuertas.winfo_children():
            widget.destroy()

        for numero in range(1, cantidad + 1):
            pruebas_compuerta = resultados_por_compuerta[numero]

            if pruebas_compuerta:
                compuerta_ok = all(
                    prueba["correcta"]
                    for prueba in pruebas_compuerta
                )
                estado = "OK" if compuerta_ok else "FALLA"
                color_estado = (
                    "#2ecc71" if compuerta_ok else "#ff6b6b"
                )
            else:
                estado = "SIN DATOS"
                color_estado = "#f1c40f"

            self.crear_tarjeta_compuerta(
                numero,
                estado,
                color_estado,
                pruebas_compuerta
            )

        if estado_general == "GOOD":
            self.lbl_resultado.configure(
                text="✨ INTEGRADO EN BUEN ESTADO",
                text_color="#2ecc71"
            )
        else:
            self.lbl_resultado.configure(
                text="❌ INTEGRADO DEFECTUOSO O FALLIDO",
                text_color="#ff6b6b"
            )

        self.finalizar_prueba()

    def crear_tarjeta_compuerta(
        self,
        numero,
        estado,
        color_estado,
        pruebas
    ):
        tarjeta = ctk.CTkFrame(
            self.panel_compuertas,
            fg_color="#252a34",
            corner_radius=12
        )
        tarjeta.pack(fill="x", padx=8, pady=6)

        detalle = ctk.CTkFrame(
            tarjeta,
            fg_color="#1d222a",
            corner_radius=10
        )

        estado_expandida = {"valor": False}

        boton = ctk.CTkButton(
            tarjeta,
            text=f"▸   Compuerta {numero}     {estado}",
            anchor="w",
            height=42,
            fg_color="#303744",
            hover_color="#3a4352",
            text_color=color_estado,
            font=("Arial", 13, "bold")
        )
        boton.pack(fill="x", padx=8, pady=8)

        self.construir_detalle_compuerta(detalle, pruebas)

        def alternar_detalle(
            boton_local=boton,
            detalle_local=detalle,
            expandida=estado_expandida,
            numero_local=numero,
            estado_local=estado,
            color_local=color_estado
        ):
            expandida["valor"] = not expandida["valor"]

            if expandida["valor"]:
                boton_local.configure(
                    text=f"▾   Compuerta {numero_local}     {estado_local}",
                    text_color=color_local
                )
                detalle_local.pack(
                    fill="x",
                    padx=10,
                    pady=(0, 10)
                )
            else:
                boton_local.configure(
                    text=f"▸   Compuerta {numero_local}     {estado_local}",
                    text_color=color_local
                )
                detalle_local.pack_forget()

        boton.configure(command=alternar_detalle)

    def construir_detalle_compuerta(self, contenedor, pruebas):
        encabezado = ctk.CTkFrame(
            contenedor,
            fg_color="#252a34",
            corner_radius=8
        )
        encabezado.pack(fill="x", padx=8, pady=(8, 5))

        pesos = [3, 1, 1, 1]
        titulos = ["ENTRADAS", "ESPERADO", "MEDIDO", "RESULTADO"]

        for indice, peso in enumerate(pesos):
            encabezado.grid_columnconfigure(indice, weight=peso)

        for indice, titulo in enumerate(titulos):
            ctk.CTkLabel(
                encabezado,
                text=titulo,
                font=("Arial", 10, "bold"),
                text_color="#9ca3af"
            ).grid(
                row=0,
                column=indice,
                padx=8,
                pady=9,
                sticky="w"
            )

        if not pruebas:
            ctk.CTkLabel(
                contenedor,
                text="No se recibieron datos para esta compuerta.",
                font=("Arial", 12),
                text_color="#9ca3af"
            ).pack(fill="x", padx=12, pady=12)
            return

        for prueba in pruebas:
            correcta = prueba["correcta"]
            color_fondo = "#173328" if correcta else "#3a2024"
            color_estado = "#2ecc71" if correcta else "#ff6b6b"

            fila = ctk.CTkFrame(
                contenedor,
                fg_color=color_fondo,
                corner_radius=8
            )
            fila.pack(fill="x", padx=8, pady=3)

            for indice, peso in enumerate(pesos):
                fila.grid_columnconfigure(indice, weight=peso)

            if prueba["entrada_b"] == "-":
                entradas = f"A = {prueba['entrada_a']}"
            else:
                entradas = (
                    f"A = {prueba['entrada_a']}     "
                    f"B = {prueba['entrada_b']}"
                )

            valores = [
                (entradas, "#cbd5e1", ("Arial", 12)),
                (
                    str(prueba["esperado"]),
                    "#e5e7eb",
                    ("Arial", 12, "bold")
                ),
                (
                    str(prueba["medido"]),
                    color_estado,
                    ("Arial", 12, "bold")
                ),
                (
                    "✓ OK" if correcta else "✕ FALLA",
                    color_estado,
                    ("Arial", 11, "bold")
                )
            ]

            for indice, (texto, color, fuente) in enumerate(valores):
                ctk.CTkLabel(
                    fila,
                    text=texto,
                    text_color=color,
                    font=fuente
                ).grid(
                    row=0,
                    column=indice,
                    padx=8,
                    pady=8,
                    sticky="w"
                )

    def mostrar_error(self, mensaje):
        self.lbl_resultado.configure(
            text=f"Error durante la prueba: {mensaje}",
            text_color="#ff6b6b"
        )
        self.mostrar_mensaje_panel(mensaje)
        self.finalizar_prueba()

    def finalizar_prueba(self):
        self.prueba_en_curso = False

        self.btn_conectar.configure(state="normal")
        self.combo_ic.configure(state="normal")

        conectado = (
            self.serial_esp32 is not None
            and self.serial_esp32.is_open
        )
        self.btn_probar.configure(
            state="normal" if conectado else "disabled"
        )

    def cerrar_aplicacion(self):
        self.cerrando = True

        try:
            if self.serial_esp32 is not None:
                self.serial_esp32.close()
        except (serial.SerialException, OSError):
            pass

        self.destroy()


if __name__ == "__main__":
    app = AppCompuertas()
    app.mainloop()
