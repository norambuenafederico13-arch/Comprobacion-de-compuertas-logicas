import tkinter as tk
import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
import time

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AppCompuertas(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tester de Circuitos Integrados - ESP32-S3")
        self.geometry("750x650")  
        self.resizable(False, False)

        self.serial_esp32 = None
        self.ic_seleccionado = ctk.StringVar(value="CD4081BE (AND)")

        self.frame_conexion = ctk.CTkFrame(self)
        self.frame_conexion.pack(pady=15, padx=20, fill="x")

        self.label_puerto = ctk.CTkLabel(self.frame_conexion, text="Puerto COM:", font=("Arial", 12, "bold"))
        self.label_puerto.pack(side="left", padx=10, pady=10)

        self.combo_puertos = ctk.CTkComboBox(self.frame_conexion, values=self.listar_puertos())
        self.combo_puertos.pack(side="left", padx=10, pady=10)

        self.btn_refrescar = ctk.CTkButton(self.frame_conexion, text="🔄", width=35, command=self.actualizar_combo_puertos)
        self.btn_refrescar.pack(side="left", padx=2)

        self.btn_conectar = ctk.CTkButton(self.frame_conexion, text="Conectar", command=self.toggle_conexion)
        self.btn_conectar.pack(side="left", padx=10, pady=10)

        self.lbl_estado_conexion = ctk.CTkLabel(self.frame_conexion, text="🔴 Desconectado", text_color="#e74c3c", font=("Arial", 11, "bold"))
        self.lbl_estado_conexion.pack(side="right", padx=15)

        self.frame_menu = ctk.CTkFrame(self)
        self.frame_menu.pack(pady=10, padx=20, fill="x")

        self.lbl_menu = ctk.CTkLabel(self.frame_menu, text="Seleccione el integrado a comprobar:", font=("Arial", 13, "bold"))
        self.lbl_menu.pack(pady=5)

        self.opciones_ic = ["CD4081BE (AND)", "CD4071BE (OR)", "CD4069BE (NOT)"]
        self.combo_ic = ctk.CTkOptionMenu(self.frame_menu, values=self.opciones_ic, variable=self.ic_seleccionado, command=self.on_ic_change)
        self.combo_ic.pack(pady=5)

        self.btn_probar = ctk.CTkButton(
            self.frame_menu, 
            text="⚙️ INICIAR PRUEBA", 
            font=("Arial", 14, "bold"), 
            fg_color="#2c3e50", 
            hover_color="#34495e", 
            state="disabled", 
            command=self.enviar_prueba
        )
        self.btn_probar.pack(pady=12)
        
        self.lbl_resultado_general = ctk.CTkLabel(self, text="Esperando inicio de prueba...", font=("Arial", 16, "bold"), text_color="gray")
        self.lbl_resultado_general.pack(pady=10)

        self.frame_compuertas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_compuertas.pack(pady=10, padx=20, fill="both", expand=True)

        self.cuadros_compuertas = []
        self.labels_compuertas = []

        self.crear_matriz_compuertas(4)

    def crear_matriz_compuertas(self, cantidad):
        for cuadro in self.cuadros_compuertas:
            cuadro.destroy()
        self.cuadros_compuertas.clear()
        self.labels_compuertas.clear()

        columnas_totales = 3 if cantidad == 6 else 2

        for i in range(cantidad):
            fila = i // columnas_totales
            columna = i % columnas_totales
            
            frame_comp = ctk.CTkFrame(self.frame_compuertas, border_width=2, border_color="gray")
            frame_comp.grid(row=fila, column=columna, padx=12, pady=10, sticky="nsew")
            
            self.frame_compuertas.grid_columnconfigure(columna, weight=1)
            self.frame_compuertas.grid_rowconfigure(fila, weight=1)

            lbl = ctk.CTkLabel(frame_comp, text=f"Compuerta {i+1}\n-- Sin evaluar --", font=("Arial", 13, "bold"), text_color="gray")
            lbl.pack(expand=True, pady=15)
            
            self.cuadros_compuertas.append(frame_comp)
            self.labels_compuertas.append(lbl)

    def on_ic_change(self, choice):
        if "69" in choice or "NOT" in choice:
            self.crear_matriz_compuertas(6)
        else:
            self.crear_matriz_compuertas(4)
        self.lbl_resultado_general.configure(text="Esperando inicio de prueba...", text_color="gray")

    def listar_puertos(self):
        puertos = [port.device for port in serial.tools.list_ports.comports()]
        return puertos if puertos else ["No se detectaron puertos"]

    def actualizar_combo_puertos(self):
        nuevos_puertos = self.listar_puertos()
        self.combo_puertos.configure(values=nuevos_puertos)
        self.combo_puertos.set(nuevos_puertos[0])

    def toggle_conexion(self):
        if self.serial_esp32 is None:
            puerto = self.combo_puertos.get()
            if puerto == "No se detectaron puertos":
                return
            try:
                self.serial_esp32 = serial.Serial(puerto, 115200, timeout=2)
                time.sleep(1.5)
                self.lbl_estado_conexion.configure(text="🟢 Conectado", text_color="#2ecc71")
                self.btn_conectar.configure(text="Desconectar")
                self.btn_probar.configure(state="normal")
            except Exception:
                self.lbl_estado_conexion.configure(text="❌ Error de conexión", text_color="#e74c3c")
        else:
            try:
                self.serial_esp32.close()
            except Exception:
                pass
            self.serial_esp32 = None
            self.lbl_estado_conexion.configure(text="🔴 Desconectado", text_color="#e74c3c")
            self.btn_conectar.configure(text="Conectar")
            self.btn_probar.configure(state="disabled")

    def enviar_prueba(self):
        """Envía el byte identificador al microcontrolador con protección contra congelamiento."""
        if not self.serial_esp32:
            return

        self.btn_probar.configure(state="disabled")
        self.lbl_resultado_general.configure(text="Evaluando integrado...", text_color="orange")

        seleccion = self.ic_seleccionado.get()
        if "AND" in seleccion:
            comando = b'A'
        elif "OR" in seleccion:
            comando = b'O'
        elif "NOT" in seleccion:
            comando = b'N'
        else:
            self.lbl_resultado_general.configure(text="Error: Selección no válida", text_color="red")
            self.btn_probar.configure(state="normal")
            return

        # Uso de hilos para mantener la GUI fluida
        hilo = threading.Thread(target=self._procedimiento_serial, args=(comando,))
        hilo.daemon = True
        hilo.start()

    def _procedimiento_serial(self, comando):
        """Ejecuta el envío de datos y lectura en segundo plano."""
        try:
            self.serial_esp32.reset_input_buffer()
            self.serial_esp32.write(comando)
            
            linea = self.serial_esp32.readline().decode('utf-8').strip()
            
            if linea.startswith("STATUS:"):
                self.after(0, self._actualizar_interfaz_exito, linea)
            else:
                self.after(0, self._actualizar_interfaz_error, "Respuesta inesperada del hardware")
        except Exception as e:
            self.after(0, self._actualizar_interfaz_error, f"Error de comunicación: {str(e)}")

    def _actualizar_interfaz_exito(self, datos_raw):
        """Parsea la respuesta del firmware y actualiza los recuadros gráficos."""
        try:
            partes = datos_raw.replace("STATUS:", "").split(",")
            estado_general = partes[0]
            
            if estado_general == "GOOD":
                self.lbl_resultado_general.configure(text="✨ INTEGRADO EN PERFECTO ESTADO (GOOD) ✨", text_color="#2ecc71")
            else:
                self.lbl_resultado_general.configure(text="❌ INTEGRADO DEFECTUOSO O FALLIDO (BAD) ❌", text_color="#e74c3c")

            for parte in partes[1:]:
                if ":" in parte:
                    compuerta_str, resultado = parte.split(":")
                    idx = int(compuerta_str.replace("C", "")) - 1
                    
                    if idx < len(self.labels_compuertas):
                        if resultado == "OK":
                            self.cuadros_compuertas[idx].configure(border_color="#2ecc71")
                            self.labels_compuertas[idx].configure(text=f"Compuerta {idx+1}\n🟢 OK", text_color="#2ecc71")
                        else:
                            self.cuadros_compuertas[idx].configure(border_color="#e74c3c")
                            self.labels_compuertas[idx].configure(text=f"Compuerta {idx+1}\n🔴 FAIL", text_color="#e74c3c")
        except Exception:
            self._actualizar_interfaz_error("Error de formato al procesar datos")
        finally:
            self.btn_probar.configure(state="normal")

    def _actualizar_interfaz_error(self, mensaje):
        """Muestra excepciones o desconexiones físicas imprevistas."""
        self.lbl_resultado_general.configure(text=mensaje, text_color="#e74c3c")
        self.btn_probar.configure(state="normal")

if __name__ == "__main__":
    app = AppCompuertas()
    app.mainloop()
