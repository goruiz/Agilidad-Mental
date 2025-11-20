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

        tk.Label(botones_container, text="Seleccione el Nivel", font=("Arial", 22, "bold"), bg="#f0f0f0", fg="#003366").pack(pady=(0, 40))

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

        tk.Label(frame, text="Datos del Estudiante", font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#003366").grid(row=0, column=0, columnspan=2, pady=30)

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
        self.entry_fecha = tk.Entry(frame, font=("Arial", 16), width=35)
        self.entry_fecha.insert(0, self.fecha)
        self.entry_fecha.grid(row=3, column=1, pady=12)

        tk.Button(frame, text="COMENZAR TEST", font=("Arial", 18, "bold"), width=25, height=2,
                  bg="#2196F3", fg="white", command=self.validar_datos).grid(row=4, column=0, columnspan=2, pady=50)

    def validar_datos(self):
        nombre = self.entry_nombre.get().strip()
        curso = self.combo_curso.get()
        if not nombre or not curso:
            messagebox.showwarning("Faltan datos", "Complete nombre y curso.")
            return
        self.nombre = nombre
        self.curso = curso
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
        dialog.title(f"Configurar {nombre_op}")
        dialog.geometry("450x200")
        dialog.configure(bg="#f0f0f0")
        dialog.transient(self.root)
        dialog.grab_set()

        # Centrar el diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"+{x}+{y}")

        tk.Label(dialog, text=f"Ingrese hasta qué tabla desea\nrealizar en la {nombre_op}:",
                font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#003366").pack(pady=20)

        spin_frame = tk.Frame(dialog, bg="#f0f0f0")
        spin_frame.pack(pady=10)

        spin = tk.Spinbox(spin_frame, from_=2, to=12, font=("Arial", 16), width=10)
        spin.pack()

        resultado = {"confirmado": False}

        def confirmar():
            resultado["confirmado"] = True
            resultado["valor"] = int(spin.get())
            dialog.destroy()

        tk.Button(dialog, text="ACEPTAR", font=("Arial", 14, "bold"), width=15,
                 bg="#4CAF50", fg="white", command=confirmar).pack(pady=20)

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
        tabla = self.tabla_actual  # Usar la tabla actual

        for i in range(12):
            if operacion == "suma":
                # Una de las operaciones siempre será el número de la tabla actual
                if random.choice([True, False]):
                    a = tabla
                    b = random.randint(1, 100)
                else:
                    a = random.randint(1, 100)
                    b = tabla
                resp = a + b
                texto = f"{a} + {b} ="

            elif operacion == "resta":
                # Una de las operaciones involucra el número de la tabla actual
                if random.choice([True, False]):
                    a = random.randint(tabla + 10, 200)
                    b = tabla
                else:
                    a = tabla
                    b = random.randint(1, tabla - 1) if tabla > 1 else 0
                resp = a - b
                texto = f"{a} - {b} ="

            elif operacion == "multiplicación":
                # Una de las operaciones siempre será el número de la tabla actual
                if random.choice([True, False]):
                    a = tabla
                    b = random.randint(2, 12)
                else:
                    a = random.randint(2, 12)
                    b = tabla
                resp = a * b
                texto = f"{a} × {b} ="

            elif operacion == "división":
                # El divisor o resultado involucra la tabla actual
                if random.choice([True, False]):
                    b = tabla
                    resp = random.randint(2, 12)
                else:
                    b = random.randint(2, 12)
                    resp = tabla
                a = b * resp
                texto = f"{a} ÷ {b} ="

            elif operacion == "potencia":
                # La base o exponente involucra la tabla actual
                if random.choice([True, False]) and tabla <= 10:
                    base = tabla
                    exp = random.randint(2, 3)
                else:
                    base = random.randint(2, min(tabla + 2, 10))
                    exp = min(tabla, 4)
                resp = base ** exp
                texto = f"{base}^{exp} ="

            elif operacion == "raíz":
                # Raíces cuadradas que involucran la tabla actual
                # Generar cuadrados perfectos relacionados con la tabla
                if tabla <= 20:
                    num = tabla ** 2
                    resp = tabla
                else:
                    cuadrados = [16,25,36,49,64,81,100,121,144,169,196,225,256,289,324,361,400]
                    num = random.choice(cuadrados)
                    resp = int(math.sqrt(num))
                texto = f"√{num} ="
            else:
                continue
            ejercicios.append({"texto": texto, "respuesta": resp, "id": i})

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
                self.label_tiempo.config(text=f"Tiempo: {mins:02d}:{secs:02d} - ¡TIEMPO MÁXIMO!", fg="darkred")
                self.detener_cronometro()
                messagebox.showwarning("Tiempo agotado",
                    f"Has excedido el tiempo máximo de {int(self.tiempo_maximo//60)} minutos.\n"
                    "La operación se finalizará automáticamente.")
                self.finalizar_operacion()
                return
            elif elapsed > self.tiempo_principal:
                # Tiempo principal superado - hay penalización
                self.label_tiempo.config(text=f"Tiempo: {mins:02d}:{secs:02d} - Con penalización", fg="orange")
            else:
                # Dentro del tiempo óptimo
                self.label_tiempo.config(text=f"Tiempo: {mins:02d}:{secs:02d}", fg="red")

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
                 font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#003366").pack(anchor="center", pady=(0, 10))

        self.label_tiempo = tk.Label(left_frame, text="Tiempo: 00:00", font=("Arial", 20, "bold"),
                                     bg="#f0f0f0", fg="red")
        self.label_tiempo.pack(pady=(0, 15))

        # Mostrar las 12 operaciones directamente (ajustado para que quepan sin scroll)
        self.entries = {}
        for i, ej in enumerate(self.ejercicios):
            row_frame = tk.Frame(left_frame, bg="#f0f0f0")
            row_frame.pack(pady=6, anchor="w", padx=80)

            tk.Label(row_frame, text=ej["texto"], font=("Arial", 18, "bold"), bg="#f0f0f0", width=14, anchor="e").pack(side="left")
            entry = tk.Entry(row_frame, font=("Arial", 18), width=10, justify="center", bd=2, relief="solid", state="disabled")
            entry.pack(side="left", padx=12)
            self.entries[ej["id"]] = entry

        # DERECHA: Botones verticales
        right_frame = tk.Frame(main_frame, bg="#f0f0f0")
        right_frame.grid(row=0, column=1, sticky="n", pady=50)

        btn_style = {"font": ("Arial", 15, "bold"), "width": 20, "height": 2, "bd": 3, "relief": "raised"}

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
            tk.Button(right_frame, text=boton_texto, bg="#9C27B0", fg="white",
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
        for ej in self.ejercicios:
            val = self.entries[ej["id"]].get().strip()
            # Validar que sea un número (permite negativos)
            try:
                if int(val) == ej["respuesta"]:
                    correctas += 1
            except ValueError:
                pass  # Respuesta no válida, se cuenta como incorrecta

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

    def mostrar_resultados_finales(self):
        self.limpiar_pantalla()
        nota, tiempo, pen = self.calcular_nota_final()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(expand=True, fill="both", padx=80, pady=60)

        tk.Label(frame, text="¡TEST COMPLETADO!", font=("Arial", 32, "bold"), bg="#f0f0f0", fg="#2e8b57").pack(pady=30)
        tk.Label(frame, text=f"{self.nombre} - {self.curso}", font=("Arial", 20), bg="#f0f0f0").pack(pady=10)
        tk.Label(frame, text=f"Fecha: {self.fecha}", font=("Arial", 16), bg="#f0f0f0").pack(pady=5)

        color = "#1e90ff" if nota >= 70 else "#ff4500"
        tk.Label(frame, text=f"NOTA FINAL: {nota}/100", font=("Arial", 48, "bold"), bg="#f0f0f0", fg=color).pack(pady=40)

        if pen > 0:
            tk.Label(frame, text=f"Penalización aplicada: -{pen} puntos (tiempo excedido)", font=("Arial", 16), fg="red", bg="#f0f0f0").pack(pady=10)

        tk.Button(frame, text="CERRAR PROGRAMA", font=("Arial", 18, "bold"), width=25, height=2,
                  bg="#f44336", fg="white", command=self.root.quit).pack(pady=50)


if __name__ == "__main__":
    root = tk.Tk()
    app = AgilidadMentalApp(root)
    root.mainloop()
