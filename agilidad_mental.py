import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import random
import math
import os

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False


class AgilidadMentalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Programa de Agilidad Mental")
        self.root.geometry("1200x800")  # Más grande para que quepan las operaciones
        self.root.configure(bg="#f0f0f0")

        # Variables globales
        self.nivel = None
        self.nombre = ""
        self.curso = ""
        self.fecha = datetime.now().strftime("%d/%m/%Y")
        self.tabla_max = 10  # Límite actual de tabla para la operación en curso
        self.tabla_actual = 1  # Tabla actual (1, 2, 3, ...)
        self.limites_tablas = {}  # Diccionario para almacenar el límite de cada operación
        self.tiempo_inicio = None
        self.tiempo_total = 0
        self.corriendo = False
        self.finalizado = False  # Para controlar si ya finalizó la operación

        # Resultados
        self.resultados_operacion = {}
        self.operaciones_nivel = []
        self.operacion_actual = ""
        self.ejercicios = []
        self.entries = {}
        self.boton_finalizar = None  # Referencia al botón finalizar
        self.boton_iniciar = None  # Referencia al botón iniciar

        self.mostrar_pantalla_inicio()

    def validar_numero(self, valor):
        """Valida que el input sea un número (permite números negativos y vacío)"""
        if valor == "" or valor == "-":
            return True
        try:
            int(valor)
            return True
        except ValueError:
            return False

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_pantalla_inicio(self):
        self.limpiar_pantalla()

        # Frame principal que se adapta a la ventana
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True)

        # Configurar grid con 2 columnas de igual peso
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Logo (izquierda)
        frame_izq = tk.Frame(main_frame, bg="#f0f0f0")
        frame_izq.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)

        # Centrar contenido del logo
        logo_container = tk.Frame(frame_izq, bg="#f0f0f0")
        logo_container.place(relx=0.5, rely=0.5, anchor="center")

        if PIL_AVAILABLE and os.path.exists("logo.png"):
            img = Image.open("logo.png")
            img = img.resize((280, 280), Image.Resampling.LANCZOS)
            logo = ImageTk.PhotoImage(img)
            label_logo = tk.Label(logo_container, image=logo, bg="#f0f0f0")
            label_logo.image = logo
            label_logo.pack()
        else:
            tk.Label(logo_container, text="LOGO\nINSTITUCIÓN", font=("Arial", 26, "bold"), bg="#f0f0f0", fg="#333",
                     justify="center").pack()

        # Botones niveles (derecha)
        frame_der = tk.Frame(main_frame, bg="#f0f0f0")
        frame_der.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)

        # Centrar contenido de los botones
        botones_container = tk.Frame(frame_der, bg="#f0f0f0")
        botones_container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(botones_container, text="Seleccione el Nivel", font=("Arial", 22, "bold"), bg="#f0f0f0", fg="#4CAF50").pack(pady=(0, 40))

        # Botones con tamaño exactamente igual
        for nivel in [1, 2, 3]:
            btn = tk.Button(botones_container, text=f"Nivel {nivel}", font=("Arial", 20, "bold"),
                            width=15, height=3,
                            bg="#4CAF50", fg="white", relief="raised",
                            command=lambda n=nivel: self.seleccionar_nivel(n))
            btn.pack(pady=15)

    def seleccionar_nivel(self, nivel):
        self.nivel = nivel
        if nivel == 1:
            # Nivel 1: suma y resta, 12 min por operación (extiende a 15)
            self.operaciones_nivel = ["suma", "resta"]
            self.tiempo_principal = 12 * 60  # 12 minutos por operación
            self.tiempo_maximo = 15 * 60     # se extiende hasta 15 minutos
        elif nivel == 2:
            # Nivel 2: suma, resta, multiplicación, división, 10 min por operación (extiende a 12)
            self.operaciones_nivel = ["suma", "resta", "multiplicación", "división"]
            self.tiempo_principal = 10 * 60  # 10 minutos por operación
            self.tiempo_maximo = 12 * 60     # se extiende hasta 12 minutos
        else:
            # Nivel 3: suma, resta, multiplicación, división, potencia, raíz, 10 min por operación (extiende a 12)
            self.operaciones_nivel = ["suma", "resta", "multiplicación", "división", "potencia", "raíz"]
            self.tiempo_principal = 10 * 60  # 10 minutos por operación
            self.tiempo_maximo = 12 * 60     # se extiende hasta 12 minutos

        self.mostrar_pantalla_datos()

    def mostrar_pantalla_datos(self):
        self.limpiar_pantalla()
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(expand=True, fill="both", padx=120, pady=60)

        tk.Label(frame, text="Datos del Estudiante", font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#4CAF50").grid(row=0, column=0, columnspan=2, pady=30)

        tk.Label(frame, text="Nombre:", font=("Arial", 16), bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=12)
        self.entry_nombre = tk.Entry(frame, font=("Arial", 16), width=35)
        self.entry_nombre.grid(row=1, column=1, pady=12)

        tk.Label(frame, text="Curso:", font=("Arial", 16), bg="#f0f0f0").grid(row=2, column=0, sticky="w", pady=12)
        self.combo_curso = ttk.Combobox(frame, values=[
            "Segundo A", "Segundo B", "Tercero A", "Tercero B",
            "Cuarto A", "Cuarto B", "Quinto A", "Quinto B"
        ], state="readonly", font=("Arial", 16), width=33)
        self.combo_curso.grid(row=2, column=1, pady=12)

        tk.Label(frame, text="Fecha:", font=("Arial", 16), bg="#f0f0f0").grid(row=3, column=0, sticky="w", pady=12)

        # Si tkcalendar está disponible, usar DateEntry, sino usar Entry normal
        if TKCALENDAR_AVAILABLE:
            self.entry_fecha = DateEntry(frame, font=("Arial", 16), width=33,
                                        borderwidth=2, date_pattern='dd/mm/yyyy',
                                        locale='es_ES', showweeknumbers=False)
            self.entry_fecha.set_date(datetime.now())
        else:
            self.entry_fecha = tk.Entry(frame, font=("Arial", 16), width=35)
            self.entry_fecha.insert(0, self.fecha)

        self.entry_fecha.grid(row=3, column=1, pady=12)

        tk.Button(frame, text="COMENZAR TEST", font=("Arial", 18, "bold"), width=25, height=2,
                  bg="#4CAF50", fg="white", command=self.validar_datos).grid(row=4, column=0, columnspan=2, pady=50)

    def validar_datos(self):
        nombre = self.entry_nombre.get().strip()
        curso = self.combo_curso.get()
        if not nombre or not curso:
            messagebox.showwarning("Faltan datos", "Complete nombre y curso.")
            return
        self.nombre = nombre
        self.curso = curso

        # Obtener fecha dependiendo del tipo de widget
        if TKCALENDAR_AVAILABLE:
            self.fecha = self.entry_fecha.get_date().strftime("%d/%m/%Y")
        else:
            self.fecha = self.entry_fecha.get()

        self.resultados_operacion = {}
        self.operacion_actual = ""
        self.tabla_actual = 1  # Iniciar desde la tabla 1
        self.limites_tablas = {}  # Resetear límites
        # Solicitar el límite de tabla para la primera operación
        self.solicitar_limite_tabla_operacion()

    def solicitar_limite_tabla_operacion(self):
        """Solicita al usuario el límite de tabla para la operación actual"""
        # Si no hay operación actual, asignar la primera
        if not self.operacion_actual:
            self.operacion_actual = self.operaciones_nivel[0]

        # Mapear nombres de operaciones
        nombres_operaciones = {
            "suma": "Suma",
            "resta": "Resta",
            "multiplicación": "Multiplicación",
            "división": "División",
            "potencia": "Potenciación",
            "raíz": "Radicación"
        }
        nombre_op = nombres_operaciones.get(self.operacion_actual, self.operacion_actual)

        # Crear ventana de diálogo personalizada
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{nombre_op}")
        dialog.configure(bg="#f0f0f0")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Frame principal con padding
        main_frame = tk.Frame(dialog, bg="#f0f0f0")
        main_frame.pack(expand=True, fill="both", padx=40, pady=30)

        # Título con ícono
        title_frame = tk.Frame(main_frame, bg="#f0f0f0")
        title_frame.pack(pady=(0, 25))

        tk.Label(title_frame, text="📊", font=("Arial", 24), bg="#f0f0f0").pack()
        tk.Label(title_frame, text=f"{nombre_op}",
                font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#333").pack(pady=(5, 0))

        # Instrucción
        tk.Label(main_frame, text=f"¿Hasta qué tabla quieres practicar?",
                font=("Arial", 13), bg="#f0f0f0", fg="#555").pack(pady=(0, 20))

        # Frame para el spinbox con estilo
        spin_container = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="solid")
        spin_container.pack(pady=10)

        spin = tk.Spinbox(spin_container, from_=1, to=12, font=("Arial", 20, "bold"),
                         width=8, justify="center", bd=0, relief="flat", fg="#333")
        spin.delete(0, "end")
        spin.insert(0, "1")  # Valor por defecto 1
        spin.pack(padx=10, pady=10)

        resultado = {"confirmado": False}

        def confirmar():
            resultado["confirmado"] = True
            resultado["valor"] = int(spin.get())
            dialog.destroy()

        def cancelar():
            resultado["confirmado"] = False
            dialog.destroy()

        def on_enter_aceptar(e):
            btn_aceptar.config(bg="#45a049")

        def on_leave_aceptar(e):
            btn_aceptar.config(bg="#4CAF50")

        def on_enter_cancelar(e):
            btn_cancelar.config(bg="#d32f2f")

        def on_leave_cancelar(e):
            btn_cancelar.config(bg="#f44336")

        # Frame para botones
        buttons_frame = tk.Frame(main_frame, bg="#f0f0f0")
        buttons_frame.pack(pady=20)

        # Botón ACEPTAR con efecto hover
        btn_aceptar = tk.Button(buttons_frame, text="ACEPTAR", font=("Arial", 14, "bold"),
                               width=12, height=2, bg="#4CAF50", fg="white",
                               bd=0, relief="flat", cursor="hand2",
                               activebackground="#45a049", activeforeground="white",
                               command=confirmar)
        btn_aceptar.pack(side="left", padx=10)
        btn_aceptar.bind("<Enter>", on_enter_aceptar)
        btn_aceptar.bind("<Leave>", on_leave_aceptar)

        # Botón CANCELAR con efecto hover
        btn_cancelar = tk.Button(buttons_frame, text="CANCELAR", font=("Arial", 14, "bold"),
                                width=12, height=2, bg="#f44336", fg="white",
                                bd=0, relief="flat", cursor="hand2",
                                activebackground="#d32f2f", activeforeground="white",
                                command=cancelar)
        btn_cancelar.pack(side="left", padx=10)
        btn_cancelar.bind("<Enter>", on_enter_cancelar)
        btn_cancelar.bind("<Leave>", on_leave_cancelar)

        # Permitir confirmar con Enter y cancelar con Escape
        dialog.bind('<Return>', lambda e: confirmar())
        dialog.bind('<Escape>', lambda e: cancelar())

        # Centrar el diálogo DESPUÉS de crear todos los widgets
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")

        # Esperar a que se cierre el diálogo
        self.root.wait_window(dialog)

        if resultado["confirmado"]:
            self.limites_tablas[self.operacion_actual] = resultado["valor"]
            self.tabla_max = resultado["valor"]
            self.tabla_actual = 1
            self.mostrar_pantalla_ejercicios()
        else:
            # Si cancela, volver a la pantalla de datos
            self.mostrar_pantalla_datos()

    def generar_ejercicios(self, operacion):
        """Genera 12 ejercicios usando la tabla actual (self.tabla_actual)"""
        ejercicios = []
        ejercicios_set = set()  # Para verificar duplicados
        tabla = self.tabla_actual  # Usar la tabla actual

        intentos = 0
        max_intentos = 1000  # Evitar bucle infinito

        while len(ejercicios) < 12 and intentos < max_intentos:
            intentos += 1

            if operacion == "suma":
                # El número de la tabla SIEMPRE debe aparecer en la operación
                if random.choice([True, False]):
                    a = tabla
                    b = random.randint(1, 100)
                else:
                    a = random.randint(1, 100)
                    b = tabla
                resp = a + b
                texto = f"{a} + {b} ="

            elif operacion == "resta":
                # El número de la tabla SIEMPRE debe aparecer en la operación
                if random.choice([True, False]):
                    # tabla aparece como sustraendo
                    a = random.randint(tabla + 1, 200)
                    b = tabla
                else:
                    # tabla aparece como minuendo
                    b = random.randint(1, min(tabla, 100))
                    a = tabla
                resp = a - b
                texto = f"{a} - {b} ="

            elif operacion == "multiplicación":
                # El número de la tabla SIEMPRE debe aparecer como factor
                if random.choice([True, False]):
                    a = tabla
                    b = random.randint(2, 12)
                else:
                    a = random.randint(2, 12)
                    b = tabla
                resp = a * b
                texto = f"{a} × {b} ="

            elif operacion == "división":
                # El número de la tabla SIEMPRE debe aparecer (como dividendo, divisor o en el resultado)
                if random.choice([True, False]):
                    # tabla como divisor
                    b = tabla
                    resp = random.randint(2, 12)
                    a = b * resp
                else:
                    # tabla como dividendo
                    a = tabla
                    b = random.randint(2, min(tabla, 12))
                    resp = a // b
                    a = b * resp  # Ajustar para que sea división exacta
                texto = f"{a} ÷ {b} ="

            elif operacion == "potencia":
                # El número de la tabla debe aparecer como base o exponente
                if random.choice([True, False]) and tabla <= 10:
                    base = tabla
                    exp = random.randint(2, 4)
                else:
                    base = random.randint(2, 10)
                    exp = min(tabla, 5)
                resp = base ** exp
                texto = f"{base}^{exp} ="

            elif operacion == "raíz":
                # Usar cuadrados perfectos relacionados con la tabla
                # Para tabla del 1: √1, √4, √9, etc.
                # Para tabla del 2: √4, √16, √36, etc.
                num = (tabla * random.randint(1, 5)) ** 2
                resp = tabla * random.randint(1, 5)
                texto = f"√{num} ="
            else:
                continue

            # Verificar si el ejercicio ya existe (evitar duplicados)
            if texto not in ejercicios_set:
                ejercicios_set.add(texto)
                ejercicios.append({"texto": texto, "respuesta": resp, "id": len(ejercicios)})

        # Mezclar aleatoriamente los ejercicios
        random.shuffle(ejercicios)
        # Reasignar IDs después de mezclar para mantener el orden visual
        for idx, ej in enumerate(ejercicios):
            ej["id"] = idx

        return ejercicios

    def iniciar_cronometro(self):
        # Verificar si ya fue finalizado
        if self.finalizado:
            messagebox.showinfo("Ya finalizado", "Esta operación ya fue finalizada. No puede volver a iniciar.")
            return

        if not self.corriendo:
            self.tiempo_inicio = datetime.now()
            self.corriendo = True
            # Habilitar los campos de entrada cuando se presiona INICIAR
            for entry in self.entries.values():
                entry.config(state="normal")
            self.actualizar_cronometro()

    def detener_cronometro(self):
        if self.corriendo:
            self.tiempo_total += (datetime.now() - self.tiempo_inicio).total_seconds()
            self.corriendo = False

    def actualizar_cronometro(self):
        if self.corriendo:
            elapsed = (datetime.now() - self.tiempo_inicio).total_seconds() + self.tiempo_total
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)

            # Cambiar color según el tiempo transcurrido
            if elapsed > self.tiempo_maximo:
                # Tiempo excedido - ya no se puede continuar
                self.label_tiempo.config(text=f"Tiempo: {mins:02d}:{secs:02d} - ¡TIEMPO MÁXIMO!", fg="#ff0000", bg="#000000")
                self.detener_cronometro()
                messagebox.showwarning("Tiempo agotado",
                    f"Has excedido el tiempo máximo de {int(self.tiempo_maximo//60)} minutos.\n"
                    "La operación se finalizará automáticamente.")
                self.finalizar_operacion()
                return
            elif elapsed > self.tiempo_principal:
                # Tiempo principal superado - hay penalización
                self.label_tiempo.config(text=f"Tiempo: {mins:02d}:{secs:02d} - Con penalización", fg="#ffff00", bg="#000000")
            else:
                # Dentro del tiempo óptimo
                self.label_tiempo.config(text=f"Tiempo: {mins:02d}:{secs:02d}", fg="#ffffff", bg="#000000")

            self.root.after(1000, self.actualizar_cronometro)

    def mostrar_pantalla_ejercicios(self):
        self.limpiar_pantalla()
        self.corriendo = False
        self.tiempo_total = 0
        self.finalizado = False  # Resetear bandera de finalizado

        # Determinar operación actual
        # Crear clave única para operación + tabla
        clave_actual = f"{self.operacion_actual}_tabla{self.tabla_actual}"

        # Si no hay operación actual o ya se completaron todas las tablas de esta operación
        if not self.operacion_actual or (self.tabla_actual > self.tabla_max):
            # Pasar a la siguiente operación
            idx = 0 if not self.operacion_actual else self.operaciones_nivel.index(self.operacion_actual) + 1
            if idx >= len(self.operaciones_nivel):
                self.mostrar_resultados_finales()
                return
            self.operacion_actual = self.operaciones_nivel[idx]
            self.tabla_actual = 1  # Reiniciar la tabla

        self.ejercicios = self.generar_ejercicios(self.operacion_actual)

        # Frame principal con grid
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)

        # IZQUIERDA: Operaciones (sin fondo, sin bordes)
        left_frame = tk.Frame(main_frame, bg="#f0f0f0")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Mapear nombres de operaciones
        nombres_operaciones = {
            "suma": "Suma",
            "resta": "Resta",
            "multiplicación": "Multiplicación",
            "división": "División",
            "potencia": "Potenciación",
            "raíz": "Radicación"
        }
        nombre_op = nombres_operaciones.get(self.operacion_actual, self.operacion_actual.upper())

        tk.Label(left_frame, text=f"Operaciones de {nombre_op}",
                 font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#4CAF50").pack(anchor="center", pady=(0, 10))

        # Cronómetro con fondo negro y números blancos
        self.label_tiempo = tk.Label(left_frame, text="Tiempo: 00:00", font=("Arial", 20, "bold"),
                                     bg="#000000", fg="#ffffff", padx=20, pady=10)
        self.label_tiempo.pack(pady=(0, 15))

        # Mostrar las 12 operaciones directamente (ajustado para que quepan sin scroll)
        self.entries = {}
        for i, ej in enumerate(self.ejercicios):
            row_frame = tk.Frame(left_frame, bg="#f0f0f0")
            row_frame.pack(pady=6, anchor="w", padx=80)

            # Verificar si es una potencia para usar superíndice
            if "^" in ej["texto"]:
                # Crear un frame para la operación con superíndice
                op_frame = tk.Frame(row_frame, bg="#f0f0f0")
                op_frame.pack(side="left")

                # Extraer base y exponente
                parts = ej["texto"].split("^")
                base = parts[0].strip()
                exp_part = parts[1].replace("=", "").strip()

                # Mostrar base en tamaño normal y exponente en superíndice
                tk.Label(op_frame, text=base, font=("Arial", 18, "bold"), bg="#f0f0f0").pack(side="left")
                tk.Label(op_frame, text=exp_part, font=("Arial", 11, "bold"), bg="#f0f0f0").pack(side="left", anchor="n", pady=(0, 8))
                tk.Label(op_frame, text=" =", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(side="left")

                # Ajustar el ancho para compensar
                tk.Label(row_frame, text="", bg="#f0f0f0", width=8).pack(side="left")
            else:
                tk.Label(row_frame, text=ej["texto"], font=("Arial", 18, "bold"), bg="#f0f0f0", width=14, anchor="e").pack(side="left")

            # Validación para que solo acepte números (incluyendo negativos)
            vcmd = (self.root.register(self.validar_numero), '%P')
            entry = tk.Entry(row_frame, font=("Arial", 18), width=10, justify="center", bd=2, relief="solid",
                           state="disabled", validate="key", validatecommand=vcmd)
            entry.pack(side="left", padx=12)
            self.entries[ej["id"]] = entry

        # DERECHA: Botones verticales
        right_frame = tk.Frame(main_frame, bg="#f0f0f0")
        right_frame.grid(row=0, column=1, sticky="n", pady=50)

        btn_style = {"font": ("Arial", 15, "bold"), "width": 20, "height": 2, "bd": 3, "relief": "raised"}

        # Color verde estandarizado #4CAF50
        # Guardar referencia al botón INICIAR
        self.boton_iniciar = tk.Button(right_frame, text="INICIAR", bg="#4CAF50", fg="white",
                                       command=self.iniciar_cronometro, **btn_style)
        self.boton_iniciar.pack(pady=15)

        # Guardar referencia al botón FINALIZAR
        self.boton_finalizar = tk.Button(right_frame, text="FINALIZAR", bg="#FF9800", fg="white",
                                         command=self.finalizar_operacion, **btn_style)
        self.boton_finalizar.pack(pady=15)

        tk.Button(right_frame, text="RESULTADOS", bg="#2196F3", fg="white",
                  command=self.mostrar_resultados_operacion, **btn_style).pack(pady=15)

        # Solo mostrar el botón SIGUIENTE si no es la última tabla de la operación actual
        # O si no es la última operación del nivel
        idx_actual = self.operaciones_nivel.index(self.operacion_actual)
        es_ultima_operacion = (idx_actual == len(self.operaciones_nivel) - 1)
        es_ultima_tabla = (self.tabla_actual == self.tabla_max)

        # Mostrar SIGUIENTE solo si:
        # - No es la última tabla de la operación actual, O
        # - Es la última tabla pero no es la última operación
        if not (es_ultima_tabla and es_ultima_operacion):
            boton_texto = "SIGUIENTE TABLA →" if self.tabla_actual < self.tabla_max else "SIGUIENTE OPERACIÓN →"
            tk.Button(right_frame, text=boton_texto, bg="#4CAF50", fg="white",
                     command=self.siguiente_operacion, **btn_style).pack(pady=15)

    def finalizar_operacion(self):
        # Verificar si ya fue finalizado
        if self.finalizado:
            messagebox.showinfo("Ya finalizado", "Esta operación ya fue finalizada.")
            return

        if self.tiempo_total == 0 and not self.corriendo:
            messagebox.showwarning("Error", "Primero debe presionar INICIAR")
            return

        self.detener_cronometro()

        correctas = 0
        incorrectas = 0
        for ej in self.ejercicios:
            val = self.entries[ej["id"]].get().strip()
            # Validar que sea un número (permite negativos)
            try:
                if int(val) == ej["respuesta"]:
                    correctas += 1
                else:
                    incorrectas += 1
            except ValueError:
                incorrectas += 1  # Respuesta no válida, se cuenta como incorrecta

        # Deshabilitar todas las entradas, el botón FINALIZAR y el botón INICIAR
        for entry in self.entries.values():
            entry.config(state="disabled")

        if self.boton_finalizar:
            self.boton_finalizar.config(state="disabled")

        if self.boton_iniciar:
            self.boton_iniciar.config(state="disabled")

        self.finalizado = True  # Marcar como finalizado

        # Guardar resultado con clave única (operación + tabla)
        clave = f"{self.operacion_actual}_tabla{self.tabla_actual}"
        self.resultados_operacion[clave] = {
            "operacion": self.operacion_actual,
            "tabla": self.tabla_actual,
            "correctas": correctas,
            "incorrectas": incorrectas,
            "total": 12,
            "tiempo": self.tiempo_total
        }

        # Mapear nombres de operaciones
        nombres_operaciones = {
            "suma": "Suma",
            "resta": "Resta",
            "multiplicación": "Multiplicación",
            "división": "División",
            "potencia": "Potenciación",
            "raíz": "Radicación"
        }
        nombre_op = nombres_operaciones.get(self.operacion_actual, self.operacion_actual)

        messagebox.showinfo("¡Operación Completada!",
                            f"{nombre_op} - TABLA DEL {self.tabla_actual}\n\nAciertos: {correctas}/12\nTiempo usado: {int(self.tiempo_total//60):02d}:{int(self.tiempo_total%60):02d}")

        # Verificar si es la última tabla de la última operación
        idx_actual = self.operaciones_nivel.index(self.operacion_actual)
        es_ultima_operacion = (idx_actual == len(self.operaciones_nivel) - 1)
        es_ultima_tabla = (self.tabla_actual == self.tabla_max)

        if es_ultima_tabla and es_ultima_operacion:
            # Mostrar resultados finales automáticamente
            self.mostrar_resultados_finales()
        elif es_ultima_tabla:
            # Es la última tabla de esta operación pero no la última operación
            self.mostrar_resumen_operacion_completa()

    def siguiente_operacion(self):
        # Verificar si la tabla actual fue finalizada
        clave_actual = f"{self.operacion_actual}_tabla{self.tabla_actual}"
        if clave_actual not in self.resultados_operacion:
            if not messagebox.askyesno("Advertencia", "¿Pasar a la siguiente tabla sin guardar esta?"):
                return

        # Avanzar a la siguiente tabla
        if self.tabla_actual < self.tabla_max:
            self.tabla_actual += 1
            self.tiempo_total = 0
            self.mostrar_pantalla_ejercicios()
        else:
            # Ya completó todas las tablas de esta operación
            # Mostrar resultados de la operación completa antes de pasar a la siguiente
            self.mostrar_resumen_operacion_completa()

    def mostrar_resumen_operacion_completa(self):
        """Muestra el resumen de todas las tablas de la operación actual"""
        # Calcular totales de la operación actual
        correctas_total = 0
        tiempo_total_op = 0
        num_tablas = 0

        for clave, r in self.resultados_operacion.items():
            if r["operacion"] == self.operacion_actual:
                correctas_total += r["correctas"]
                tiempo_total_op += r["tiempo"]
                num_tablas += 1

        total_preguntas = num_tablas * 12

        # Mapear nombres de operaciones
        nombres_operaciones = {
            "suma": "Suma",
            "resta": "Resta",
            "multiplicación": "Multiplicación",
            "división": "División",
            "potencia": "Potenciación",
            "raíz": "Radicación"
        }
        nombre_op = nombres_operaciones.get(self.operacion_actual, self.operacion_actual)

        mensaje = f"RESUMEN DE {nombre_op.upper()}\n\n"
        mensaje += f"Total de aciertos: {correctas_total}/{total_preguntas}\n"
        mensaje += f"Tiempo total: {int(tiempo_total_op//60):02d}:{int(tiempo_total_op%60):02d}\n\n"

        # Verificar si hay más operaciones
        idx_actual = self.operaciones_nivel.index(self.operacion_actual)
        if idx_actual + 1 < len(self.operaciones_nivel):
            # Hay más operaciones
            siguiente_op = self.operaciones_nivel[idx_actual + 1]
            nombre_siguiente = nombres_operaciones.get(siguiente_op, siguiente_op)
            mensaje += f"Presione ACEPTAR para continuar con {nombre_siguiente}"
            messagebox.showinfo("Operación Completada", mensaje)

            # Pasar a la siguiente operación
            self.operacion_actual = siguiente_op
            self.tabla_actual = 1
            self.tiempo_total = 0
            # Solicitar límite de tabla para la siguiente operación
            self.solicitar_limite_tabla_operacion()
        else:
            # No hay más operaciones, mostrar resultados finales
            mensaje += "¡Ha completado todas las operaciones!"
            messagebox.showinfo("Test Completado", mensaje)
            self.mostrar_resultados_finales()

    def mostrar_resultados_operacion(self):
        if not self.resultados_operacion:
            messagebox.showinfo("Sin datos", "Aún no has completado operaciones.")
            return
        texto = "RESULTADOS HASTA AHORA\n\n"
        total_ac = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_pr = len(self.resultados_operacion) * 12

        # Agrupar por operación
        for clave, r in sorted(self.resultados_operacion.items()):
            op = r["operacion"]
            tabla = r["tabla"]
            texto += f"{op.upper()} - Tabla {tabla}: {r['correctas']}/12  |  {int(r['tiempo']//60):02d}:{int(r['tiempo']%60):02d}\n"

        texto += f"\nTOTAL: {total_ac}/{total_pr}"
        messagebox.showinfo("Resultados Parciales", texto)

    def calcular_nota_final(self):
        total_aciertos = sum(r["correctas"] for r in self.resultados_operacion.values())
        # Total de preguntas = número de operaciones × número de tablas × 12 preguntas
        total_preguntas = len(self.operaciones_nivel) * self.tabla_max * 12

        # Calcular nota base por aciertos
        nota = (total_aciertos / total_preguntas) * 100

        # Calcular penalización por tiempo excedido en cada operación+tabla
        penalizacion_total = 0
        for clave, r in self.resultados_operacion.items():
            tiempo_op = r["tiempo"]
            # Si excede el tiempo principal, aplicar penalización
            if tiempo_op > self.tiempo_principal:
                exceso = tiempo_op - self.tiempo_principal
                # Penalización: 2 puntos por cada minuto excedido, máximo 35 puntos por operación
                penalizacion_op = min((exceso / 60) * 2, 35)
                penalizacion_total += penalizacion_op

        # La penalización total puede ser mayor a 100 si se tarda mucho en varias operaciones
        nota_final = max(round(nota - penalizacion_total, 1), 0)
        tiempo_total = sum(r["tiempo"] for r in self.resultados_operacion.values())

        return nota_final, tiempo_total, penalizacion_total

    def imprimir_resultados(self):
        """Genera e imprime un reporte de resultados"""
        import tempfile
        import subprocess
        import platform

        # Mapear nombres de operaciones
        nombres_operaciones = {
            "suma": "Suma",
            "resta": "Resta",
            "multiplicación": "Multiplicación",
            "división": "División",
            "potencia": "Potenciación",
            "raíz": "Radicación"
        }

        nota, tiempo, pen = self.calcular_nota_final()

        # Crear contenido HTML para imprimir
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Resultados - Agilidad Mental</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    color: #333;
                }}
                h1 {{
                    color: #4CAF50;
                    text-align: center;
                    margin-bottom: 10px;
                }}
                .info {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .nota {{
                    text-align: center;
                    font-size: 36px;
                    font-weight: bold;
                    color: {'#4CAF50' if nota >= 70 else '#f44336'};
                    margin: 30px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: bold;
                }}
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .operacion-header {{
                    font-weight: bold;
                    background-color: #e8f5e9;
                    font-size: 14px;
                }}
                .total-row {{
                    font-weight: bold;
                    background-color: #c8e6c9;
                }}
                hr {{
                    border: none;
                    border-top: 2px solid #4CAF50;
                    margin: 30px 0;
                }}
                @media print {{
                    body {{ margin: 20px; }}
                }}
            </style>
        </head>
        <body>
            <h1>RESULTADOS - TEST DE AGILIDAD MENTAL</h1>
            <div class="info">
                <p><strong>Estudiante:</strong> {self.nombre}</p>
                <p><strong>Curso:</strong> {self.curso}</p>
                <p><strong>Fecha:</strong> {self.fecha}</p>
            </div>
            <div class="nota">NOTA FINAL: {nota}/100</div>
            {'<p style="text-align: center; color: #f44336;"><strong>Penalización aplicada: -' + str(pen) + ' puntos (tiempo excedido)</strong></p>' if pen > 0 else ''}

            <hr>

            <h2 style="color: #4CAF50;">DETALLE DE RESULTADOS</h2>

            <table>
                <thead>
                    <tr>
                        <th>Operación</th>
                        <th>Hasta Tabla</th>
                        <th>Correctas</th>
                        <th>Incorrectas</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Agrupar resultados por operación
        resultados_por_operacion = {}
        for clave, r in self.resultados_operacion.items():
            op = r["operacion"]
            if op not in resultados_por_operacion:
                resultados_por_operacion[op] = []
            resultados_por_operacion[op].append(r)

        # Agregar filas a la tabla
        for operacion in self.operaciones_nivel:
            if operacion in resultados_por_operacion:
                nombre_op = nombres_operaciones.get(operacion, operacion)
                tablas = resultados_por_operacion[operacion]

                total_correctas = sum(t["correctas"] for t in tablas)
                total_incorrectas = sum(t["incorrectas"] for t in tablas)
                tabla_max = max(t["tabla"] for t in tablas)

                html_content += f"""
                    <tr class="operacion-header">
                        <td><strong>{nombre_op}</strong></td>
                        <td><strong>{tabla_max}</strong></td>
                        <td><strong>{total_correctas}</strong></td>
                        <td><strong>{total_incorrectas}</strong></td>
                    </tr>
                """

        # Calcular totales generales
        total_general_correctas = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_general_incorrectas = sum(r["incorrectas"] for r in self.resultados_operacion.values())

        html_content += f"""
                    <tr class="total-row">
                        <td colspan="2"><strong>TOTAL GENERAL</strong></td>
                        <td><strong>{total_general_correctas}</strong></td>
                        <td><strong>{total_general_incorrectas}</strong></td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """

        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name

        # Abrir el archivo en el navegador predeterminado
        try:
            if platform.system() == 'Windows':
                os.startfile(temp_file)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', temp_file])
            else:  # Linux
                subprocess.run(['xdg-open', temp_file])

            messagebox.showinfo("Imprimir", "Se abrió el reporte en su navegador.\nUse Ctrl+P para imprimir.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo para imprimir: {e}")

    def mostrar_resultados_finales(self):
        self.limpiar_pantalla()
        nota, tiempo, pen = self.calcular_nota_final()

        # Frame principal sin scroll
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(expand=True, fill="both", padx=40, pady=20)

        # Sección superior: título y datos
        header_frame = tk.Frame(main_frame, bg="#f0f0f0")
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(header_frame, text="¡TEST COMPLETADO!", font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#4CAF50").pack()
        tk.Label(header_frame, text=f"{self.nombre} - {self.curso}", font=("Arial", 16), bg="#f0f0f0").pack()
        tk.Label(header_frame, text=f"Fecha: {self.fecha}", font=("Arial", 14), bg="#f0f0f0").pack()

        # Sección central: nota y penalización
        nota_frame = tk.Frame(main_frame, bg="#f0f0f0")
        nota_frame.pack(fill="x", pady=10)

        color = "#4CAF50" if nota >= 70 else "#f44336"
        tk.Label(nota_frame, text=f"NOTA FINAL: {nota}/100", font=("Arial", 36, "bold"), bg="#f0f0f0", fg=color).pack()

        if pen > 0:
            tk.Label(nota_frame, text=f"Penalización aplicada: -{pen} puntos (tiempo excedido)", font=("Arial", 13), fg="#f44336", bg="#f0f0f0").pack(pady=5)

        # Separador
        tk.Label(main_frame, text="─" * 80, font=("Arial", 10), bg="#f0f0f0", fg="#4CAF50").pack(pady=10)

        # Sección tabla: DETALLE DE RESULTADOS
        tk.Label(main_frame, text="DETALLE DE RESULTADOS", font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#4CAF50").pack(pady=5)

        # Mapear nombres de operaciones
        nombres_operaciones = {
            "suma": "Suma",
            "resta": "Resta",
            "multiplicación": "Multiplicación",
            "división": "División",
            "potencia": "Potenciación",
            "raíz": "Radicación"
        }

        # Agrupar resultados por operación
        resultados_por_operacion = {}
        for clave, r in self.resultados_operacion.items():
            op = r["operacion"]
            if op not in resultados_por_operacion:
                resultados_por_operacion[op] = []
            resultados_por_operacion[op].append(r)

        # Crear tabla de resultados (más compacta)
        table_frame = tk.Frame(main_frame, bg="#f0f0f0")
        table_frame.pack(pady=10)

        # Encabezados de la tabla (sin columna "Total")
        headers = ["Operación", "Hasta Tabla", "Correctas", "Incorrectas"]
        col_widths = [20, 14, 13, 13]

        for col, (header, width) in enumerate(zip(headers, col_widths)):
            tk.Label(table_frame, text=header, font=("Arial", 12, "bold"),
                    bg="#4CAF50", fg="white", width=width,
                    relief="solid", bd=1, padx=8, pady=6).grid(row=0, column=col, sticky="ew")

        # Filas de datos
        row_num = 1
        for operacion in self.operaciones_nivel:
            if operacion in resultados_por_operacion:
                nombre_op = nombres_operaciones.get(operacion, operacion)
                tablas = resultados_por_operacion[operacion]

                # Calcular totales de la operación
                total_correctas = sum(t["correctas"] for t in tablas)
                total_incorrectas = sum(t["incorrectas"] for t in tablas)
                tabla_max = max(t["tabla"] for t in tablas)

                # Color de fondo alternado
                bg_color = "#e8f5e9" if row_num % 2 == 0 else "#f0f0f0"

                # Fila de la operación (sin columna Total)
                data = [nombre_op, str(tabla_max), str(total_correctas), str(total_incorrectas)]
                for col, (value, width) in enumerate(zip(data, col_widths)):
                    tk.Label(table_frame, text=value, font=("Arial", 11, "bold"),
                            bg=bg_color, fg="#333", width=width,
                            relief="solid", bd=1, padx=8, pady=4).grid(row=row_num, column=col, sticky="ew")

                row_num += 1

        # Fila de totales (sin columna Total)
        total_general_correctas = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_general_incorrectas = sum(r["incorrectas"] for r in self.resultados_operacion.values())

        totales = ["TOTAL GENERAL", "", str(total_general_correctas), str(total_general_incorrectas)]
        for col, (value, width) in enumerate(zip(totales, col_widths)):
            tk.Label(table_frame, text=value, font=("Arial", 12, "bold"),
                    bg="#c8e6c9", fg="#333", width=width,
                    relief="solid", bd=2, padx=8, pady=6).grid(row=row_num, column=col, sticky="ew")

        # Separador final
        tk.Label(main_frame, text="─" * 80, font=("Arial", 10), bg="#f0f0f0", fg="#4CAF50").pack(pady=10)

        # Botones
        buttons_frame = tk.Frame(main_frame, bg="#f0f0f0")
        buttons_frame.pack(pady=10)

        tk.Button(buttons_frame, text="IMPRIMIR RESULTADOS", font=("Arial", 15, "bold"), width=22, height=2,
                  bg="#4CAF50", fg="white", command=self.imprimir_resultados).pack(side="left", padx=10)

        tk.Button(buttons_frame, text="CERRAR PROGRAMA", font=("Arial", 15, "bold"), width=22, height=2,
                  bg="#f44336", fg="white", command=self.root.quit).pack(side="left", padx=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = AgilidadMentalApp(root)
    root.mainloop()
