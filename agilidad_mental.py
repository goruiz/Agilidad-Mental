import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import random
import math
import os
import tempfile
import subprocess
import platform

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


# ==================== CONSTANTES ====================
class Config:
    """Configuración y constantes del programa"""

    # Dimensiones de ventana
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

    # Colores
    COLOR_PRIMARY = "#4CAF50"
    COLOR_BACKGROUND = "#f0f0f0"
    COLOR_WARNING = "#FF9800"
    COLOR_INFO = "#2196F3"
    COLOR_DANGER = "#b81206"
    COLOR_SUCCESS = "#4CAF50"
    COLOR_TIMER_BG = "#000000"
    COLOR_TIMER_NORMAL = "#ffffff"
    COLOR_TIMER_WARNING = "#ffff00"
    COLOR_TIMER_DANGER = "#ff0000"

    # Tiempos por nivel (en segundos)
    NIVEL_1_TIEMPO_PRINCIPAL = 12 * 60  # 12 minutos
    NIVEL_1_TIEMPO_MAXIMO = 15 * 60     # 15 minutos
    NIVEL_2_TIEMPO_PRINCIPAL = 10 * 60  # 10 minutos
    NIVEL_2_TIEMPO_MAXIMO = 12 * 60     # 12 minutos
    NIVEL_3_TIEMPO_PRINCIPAL = 10 * 60  # 10 minutos
    NIVEL_3_TIEMPO_MAXIMO = 12 * 60     # 12 minutos

    # Ejercicios
    EJERCICIOS_POR_TABLA = 12
    MAX_INTENTOS_GENERACION = 1000

    # Penalización
    PENALIZACION_POR_MINUTO = 2
    PENALIZACION_MAXIMA = 35

    # Nombres de operaciones
    NOMBRES_OPERACIONES = {
        "suma": "Suma",
        "resta": "Resta",
        "multiplicación": "Multiplicación",
        "división": "División",
        "potencia": "Potenciación",
        "raíz": "Radicación"
    }

    # Cursos disponibles
    CURSOS = [
        "Segundo A", "Segundo B", "Tercero A", "Tercero B",
        "Cuarto A", "Cuarto B", "Quinto A", "Quinto B"
    ]


# ==================== CLASE PRINCIPAL ====================
class AgilidadMentalApp:
    """
    Aplicación principal de Agilidad Mental.
    Gestiona el flujo completo del test: nivel, datos del estudiante, ejercicios y resultados.
    """

    def __init__(self, root):
        self.root = root
        self._configurar_ventana()
        self._inicializar_variables()
        self.mostrar_pantalla_inicio()

    # ==================== INICIALIZACIÓN ====================

    def _configurar_ventana(self):
        """Configura la ventana principal de la aplicación"""
        self.root.title("ACADEMIA NAVAL CAP. LEONARDOABAD GUERRA")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.configure(bg=Config.COLOR_BACKGROUND)

    def _inicializar_variables(self):
        """Inicializa todas las variables de estado de la aplicación"""
        # Datos del estudiante
        self.nivel = None
        self.nombre = ""
        self.curso = ""
        self.fecha = datetime.now().strftime("%d/%m/%Y")

        # Control de tablas
        self.tabla_max = 10
        self.tabla_actual = 1
        self.limites_tablas = {}

        # Control de tiempo
        self.tiempo_inicio = None
        self.tiempo_total = 0
        self.tiempo_principal = 0
        self.tiempo_maximo = 0
        self.corriendo = False
        self.finalizado = False

        # Operaciones y resultados
        self.resultados_operacion = {}
        self.operaciones_nivel = []
        self.operacion_actual = ""
        self.ejercicios = []

        # Referencias a widgets
        self.entries = {}
        self.boton_finalizar = None
        self.boton_iniciar = None
        self.label_tiempo = None

    # ==================== UTILIDADES ====================

    def validar_numero(self, valor):
        """Valida que el input sea un número válido (permite números negativos y vacío)"""
        if valor == "" or valor == "-":
            return True
        try:
            int(valor)
            return True
        except ValueError:
            return False

    def limpiar_pantalla(self):
        """Elimina todos los widgets de la pantalla actual"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def obtener_nombre_operacion(self, operacion):
        """Retorna el nombre legible de una operación"""
        return Config.NOMBRES_OPERACIONES.get(operacion, operacion.upper())

    def obtener_tabla_minima(self, operacion):
        """Retorna la tabla mínima para una operación específica"""
        # Multiplicación, división, potenciación y radicación empiezan desde tabla 2
        return 2 if operacion in ["multiplicación", "división", "potencia", "raíz"] else 1

    # ==================== PANTALLAS ====================

    def mostrar_pantalla_inicio(self):
        """Pantalla inicial con selección de nivel"""
        self.limpiar_pantalla()

        main_frame = tk.Frame(self.root, bg=Config.COLOR_BACKGROUND)
        main_frame.pack(fill="both", expand=True)

        # Configurar grid de 2 columnas
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Logo (columna izquierda)
        self._crear_seccion_logo(main_frame)

        # Botones de nivel (columna derecha)
        self._crear_seccion_niveles(main_frame)

    def _crear_seccion_logo(self, parent):
        """Crea la sección del logo en la pantalla de inicio"""
        frame_izq = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        frame_izq.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)

        logo_container = tk.Frame(frame_izq, bg=Config.COLOR_BACKGROUND)
        logo_container.place(relx=0.5, rely=0.5, anchor="center")

        if PIL_AVAILABLE and os.path.exists("logo.png"):
            img = Image.open("logo.png")
            img = img.resize((280, 280), Image.Resampling.LANCZOS)
            logo = ImageTk.PhotoImage(img)
            label_logo = tk.Label(logo_container, image=logo, bg=Config.COLOR_BACKGROUND)
            label_logo.image = logo
            label_logo.pack()
        else:
            tk.Label(
                logo_container,
                text="LOGO\nINSTITUCIÓN",
                font=("Arial", 26, "bold"),
                bg=Config.COLOR_BACKGROUND,
                fg="#333",
                justify="center"
            ).pack()

    def _crear_seccion_niveles(self, parent):
        """Crea la sección de selección de niveles"""
        frame_der = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        frame_der.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)

        botones_container = tk.Frame(frame_der, bg=Config.COLOR_BACKGROUND)
        botones_container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            botones_container,
            text="Seleccione el Nivel",
            font=("Arial", 22, "bold"),
            bg=Config.COLOR_BACKGROUND,
            fg=Config.COLOR_PRIMARY
        ).pack(pady=(0, 40))

        for nivel in [1, 2, 3]:
            btn = tk.Button(
                botones_container,
                text=f"Nivel {nivel}",
                font=("Arial", 20, "bold"),
                width=15,
                height=3,
                bg=Config.COLOR_PRIMARY,
                fg="white",
                relief="raised",
                command=lambda n=nivel: self.seleccionar_nivel(n)
            )
            btn.pack(pady=15)

    def mostrar_pantalla_datos(self):
        """Pantalla para ingresar datos del estudiante"""
        self.limpiar_pantalla()

        main_frame = tk.Frame(self.root, bg=Config.COLOR_BACKGROUND)
        main_frame.pack(fill="both", expand=True)

        # Configurar grid de 2 columnas
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Panel izquierdo (datos del estudiante)
        frame = tk.Frame(main_frame, bg=Config.COLOR_BACKGROUND)
        frame.grid(row=0, column=0, sticky="nsew", padx=(120, 40), pady=60)

        tk.Label(
            frame,
            text="Datos del Estudiante",
            font=("Arial", 28, "bold"),
            bg=Config.COLOR_BACKGROUND,
            fg=Config.COLOR_PRIMARY
        ).grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # Campo Nombre
        tk.Label(
            frame,
            text="Nombre:",
            font=("Arial", 16),
            bg=Config.COLOR_BACKGROUND
        ).grid(row=1, column=0, sticky="w", pady=12)

        self.entry_nombre = tk.Entry(frame, font=("Arial", 16), width=35)
        self.entry_nombre.grid(row=1, column=1, pady=12)

        # Campo Curso
        tk.Label(
            frame,
            text="Curso:",
            font=("Arial", 16),
            bg=Config.COLOR_BACKGROUND
        ).grid(row=2, column=0, sticky="w", pady=12)

        self.combo_curso = ttk.Combobox(
            frame,
            values=Config.CURSOS,
            state="readonly",
            font=("Arial", 16),
            width=33
        )
        self.combo_curso.grid(row=2, column=1, pady=12)

        # Campo Fecha
        tk.Label(
            frame,
            text="Fecha:",
            font=("Arial", 16),
            bg=Config.COLOR_BACKGROUND
        ).grid(row=3, column=0, sticky="w", pady=12)

        if TKCALENDAR_AVAILABLE:
            self.entry_fecha = DateEntry(
                frame,
                font=("Arial", 16),
                width=33,
                borderwidth=2,
                date_pattern='dd/mm/yyyy',
                locale='es_ES',
                showweeknumbers=False
            )
            self.entry_fecha.set_date(datetime.now())
        else:
            self.entry_fecha = tk.Entry(frame, font=("Arial", 16), width=35)
            self.entry_fecha.insert(0, self.fecha)

        self.entry_fecha.grid(row=3, column=1, pady=12)

        # Frame para botones
        buttons_frame = tk.Frame(frame, bg=Config.COLOR_BACKGROUND)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=30)

        # Botón Comenzar
        tk.Button(
            buttons_frame,
            text="COMENZAR TEST",
            font=("Arial", 18, "bold"),
            width=20,
            height=2,
            bg=Config.COLOR_PRIMARY,
            fg="white",
            command=self.validar_datos
        ).pack(side="left", padx=10)

        # Botón Volver
        tk.Button(
            buttons_frame,
            text="VOLVER",
            font=("Arial", 18, "bold"),
            width=15,
            height=2,
            bg=Config.COLOR_DANGER,
            fg="white",
            command=self.mostrar_pantalla_inicio
        ).pack(side="left", padx=10)

        # Panel derecho (logo) - alineado a la altura de los campos
        frame_logo = tk.Frame(main_frame, bg=Config.COLOR_BACKGROUND)
        frame_logo.grid(row=0, column=1, sticky="nsew", padx=(20, 80), pady=60)

        # Contenedor para el logo alineado con los campos
        logo_container = tk.Frame(frame_logo, bg=Config.COLOR_BACKGROUND)
        logo_container.pack(pady=(80, 0))  # Alineado con el inicio de los campos

        if PIL_AVAILABLE and os.path.exists("logo.png"):
            img = Image.open("logo.png")
            img = img.resize((250, 250), Image.Resampling.LANCZOS)
            logo = ImageTk.PhotoImage(img)
            label_logo = tk.Label(logo_container, image=logo, bg=Config.COLOR_BACKGROUND)
            label_logo.image = logo
            label_logo.pack()
        else:
            tk.Label(
                logo_container,
                text="LOGO\nINSTITUCIÓN",
                font=("Arial", 24, "bold"),
                bg=Config.COLOR_BACKGROUND,
                fg="#333",
                justify="center"
            ).pack()

    def mostrar_pantalla_ejercicios(self):
        """Pantalla principal con los ejercicios de la operación actual"""
        self.limpiar_pantalla()
        self.corriendo = False
        self.tiempo_total = 0
        self.finalizado = False

        # Verificar si debe avanzar a la siguiente operación
        if self.tabla_actual > self.tabla_max:
            idx = self.operaciones_nivel.index(self.operacion_actual) + 1
            if idx >= len(self.operaciones_nivel):
                self.mostrar_resultados_finales()
                return
            self.operacion_actual = self.operaciones_nivel[idx]
            # Usar la tabla mínima de la nueva operación
            self.tabla_actual = self.obtener_tabla_minima(self.operacion_actual)

        self.ejercicios = self.generar_ejercicios(self.operacion_actual)

        # Frame principal con 3 columnas
        main_frame = tk.Frame(self.root, bg=Config.COLOR_BACKGROUND)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        main_frame.grid_columnconfigure(0, weight=2)  # Ejercicios
        main_frame.grid_columnconfigure(1, weight=1)  # Botones
        main_frame.grid_columnconfigure(2, weight=1)  # Cronómetro/Nombre

        # Columna 1: Ejercicios
        self._crear_panel_ejercicios(main_frame)

        # Columna 2: Botones de acción
        self._crear_panel_botones(main_frame)

        # Columna 3: Cronómetro y nombre
        self._crear_panel_cronometro(main_frame)

    def _crear_panel_ejercicios(self, parent):
        """Crea el panel con los ejercicios (columna 1)"""
        ejercicios_frame = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        ejercicios_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)

        tk.Label(
            ejercicios_frame,
            text=f"Operaciones de {nombre_op}",
            font=("Arial", 24, "bold"),
            bg=Config.COLOR_BACKGROUND,
            fg=Config.COLOR_PRIMARY
        ).pack(anchor="center", pady=(0, 25))

        # Ejercicios
        self.entries = {}
        for i, ej in enumerate(self.ejercicios):
            self._crear_ejercicio(ejercicios_frame, ej)

    def _crear_ejercicio(self, parent, ejercicio):
        """Crea una fila con un ejercicio individual"""
        row_frame = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        row_frame.pack(pady=6, anchor="w", padx=80)

        # Manejar potencias con superíndice
        if "^" in ejercicio["texto"]:
            self._crear_ejercicio_potencia(row_frame, ejercicio)
        else:
            tk.Label(
                row_frame,
                text=ejercicio["texto"],
                font=("Arial", 18, "bold"),
                bg=Config.COLOR_BACKGROUND,
                width=14,
                anchor="e"
            ).pack(side="left")

        # Entry para la respuesta
        vcmd = (self.root.register(self.validar_numero), '%P')
        entry = tk.Entry(
            row_frame,
            font=("Arial", 18),
            width=10,
            justify="center",
            bd=2,
            relief="solid",
            state="disabled",
            validate="key",
            validatecommand=vcmd
        )
        entry.pack(side="left", padx=12)
        self.entries[ejercicio["id"]] = entry

    def _crear_ejercicio_potencia(self, parent, ejercicio):
        """Crea un ejercicio de potencia con superíndice"""
        op_frame = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        op_frame.pack(side="left")

        parts = ejercicio["texto"].split("^")
        base = parts[0].strip()
        exp_part = parts[1].replace("=", "").strip()

        tk.Label(
            op_frame,
            text=base,
            font=("Arial", 18, "bold"),
            bg=Config.COLOR_BACKGROUND
        ).pack(side="left")

        tk.Label(
            op_frame,
            text=exp_part,
            font=("Arial", 11, "bold"),
            bg=Config.COLOR_BACKGROUND
        ).pack(side="left", anchor="n", pady=(0, 8))

        tk.Label(
            op_frame,
            text=" =",
            font=("Arial", 18, "bold"),
            bg=Config.COLOR_BACKGROUND
        ).pack(side="left")

        tk.Label(
            parent,
            text="",
            bg=Config.COLOR_BACKGROUND,
            width=8
        ).pack(side="left")

    def _crear_panel_botones(self, parent):
        """Crea el panel con los botones de acción (columna 2)"""
        botones_frame = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        botones_frame.grid(row=0, column=1, sticky="n", padx=15, pady=50)

        btn_style = {
            "font": ("Arial", 15, "bold"),
            "width": 20,
            "height": 2,
            "bd": 3,
            "relief": "raised"
        }

        # Botón INICIAR
        self.boton_iniciar = tk.Button(
            botones_frame,
            text="INICIAR",
            bg=Config.COLOR_SUCCESS,
            fg="white",
            command=self.iniciar_cronometro,
            **btn_style
        )
        self.boton_iniciar.pack(pady=15)

        # Botón FINALIZAR
        self.boton_finalizar = tk.Button(
            botones_frame,
            text="FINALIZAR",
            bg=Config.COLOR_PRIMARY,
            fg="white",
            command=self.finalizar_operacion,
            **btn_style
        )
        self.boton_finalizar.pack(pady=15)

        # Botón RESULTADOS
        tk.Button(
            botones_frame,
            text="RESULTADOS",
            bg=Config.COLOR_PRIMARY,
            fg="white",
            command=self.mostrar_resultados_operacion,
            **btn_style
        ).pack(pady=15)

        # Botón SIGUIENTE (condicional)
        if self._debe_mostrar_boton_siguiente():
            boton_texto = self._obtener_texto_boton_siguiente()
            tk.Button(
                botones_frame,
                text=boton_texto,
                bg=Config.COLOR_PRIMARY,
                fg="white",
                command=self.siguiente_operacion,
                **btn_style
            ).pack(pady=15)

    def _crear_panel_cronometro(self, parent):
        """Crea el panel con el cronómetro y nombre del estudiante (columna 3)"""
        cronometro_frame = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        cronometro_frame.grid(row=0, column=2, sticky="n", padx=(15, 0), pady=65)

        # Cronómetro - del alto de dos botones
        self.label_tiempo = tk.Label(
            cronometro_frame,
            text="Tiempo: 00:00",
            font=("Arial", 18, "bold"),
            bg=Config.COLOR_TIMER_BG,
            fg=Config.COLOR_TIMER_NORMAL,
            width=20,
            height=5,
            relief="solid",
            bd=3
        )
        self.label_tiempo.pack(pady=(0, 15))

        # Recuadro con nombre del estudiante
        label_nombre = tk.Label(
            cronometro_frame,
            text=self.nombre,
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333",
            width=20,
            height=2,
            relief="solid",
            bd=2
        )
        label_nombre.pack(pady=(0, 15))

    def _debe_mostrar_boton_siguiente(self):
        """Determina si debe mostrarse el botón SIGUIENTE"""
        idx_actual = self.operaciones_nivel.index(self.operacion_actual)
        es_ultima_operacion = (idx_actual == len(self.operaciones_nivel) - 1)
        es_ultima_tabla = (self.tabla_actual == self.tabla_max)
        return not (es_ultima_tabla and es_ultima_operacion)

    def _obtener_texto_boton_siguiente(self):
        """Retorna el texto apropiado para el botón SIGUIENTE"""
        if self.tabla_actual < self.tabla_max:
            return "SIGUIENTE TABLA →"
        return "SIGUIENTE\nOPERACIÓN →"

    def mostrar_resultados_finales(self):
        """Pantalla final con todos los resultados del test"""
        self.limpiar_pantalla()

        nota, tiempo, pen = self.calcular_nota_final()

        # Canvas con scrollbar para contenido adaptable
        canvas = tk.Canvas(self.root, bg=Config.COLOR_BACKGROUND, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)

        main_frame = tk.Frame(canvas, bg=Config.COLOR_BACKGROUND)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=15)

        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)

        main_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)

        # Encabezado
        self._crear_encabezado_resultados(main_frame)

        # Nota final
        self._crear_seccion_nota(main_frame, nota, pen)

        # Separador
        tk.Label(
            main_frame,
            text="─" * 80,
            font=("Arial", 8),
            bg=Config.COLOR_BACKGROUND,
            fg=Config.COLOR_PRIMARY
        ).pack(pady=5)

        # Tabla de resultados
        self._crear_tabla_resultados(main_frame)

        # Separador
        tk.Label(
            main_frame,
            text="─" * 80,
            font=("Arial", 8),
            bg=Config.COLOR_BACKGROUND,
            fg=Config.COLOR_PRIMARY
        ).pack(pady=5)

        # Botones finales
        self._crear_botones_finales(main_frame)

    def _crear_encabezado_resultados(self, parent):
        """Crea el encabezado de la pantalla de resultados finales"""
        header_frame = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        header_frame.pack(fill="x", pady=(0, 5))

        tk.Label(
            header_frame,
            text="¡TEST COMPLETADO!",
            font=("Arial", 20, "bold"),
            bg=Config.COLOR_BACKGROUND,
            fg=Config.COLOR_PRIMARY
        ).pack()

        tk.Label(
            header_frame,
            text=f"{self.nombre} - {self.curso}",
            font=("Arial", 12),
            bg=Config.COLOR_BACKGROUND
        ).pack()

        tk.Label(
            header_frame,
            text=f"Fecha: {self.fecha}",
            font=("Arial", 11),
            bg=Config.COLOR_BACKGROUND
        ).pack()

    def _crear_seccion_nota(self, parent, nota, penalizacion):
        """Crea la sección de la nota final"""
        nota_frame = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        nota_frame.pack(fill="x", pady=5)

        color = Config.COLOR_SUCCESS if nota >= 70 else Config.COLOR_DANGER

        tk.Label(
            nota_frame,
            text=f"NOTA FINAL: {nota}/100",
            font=("Arial", 26, "bold"),
            bg=Config.COLOR_BACKGROUND,
            fg=color
        ).pack()

        if penalizacion > 0:
            tk.Label(
                nota_frame,
                text=f"Penalización: -{penalizacion} pts (tiempo excedido)",
                font=("Arial", 10),
                fg=Config.COLOR_DANGER,
                bg=Config.COLOR_BACKGROUND
            ).pack(pady=3)

    def _crear_tabla_resultados(self, parent):
        """Crea la tabla detallada de resultados"""
        tk.Label(
            parent,
            text="DETALLE DE RESULTADOS",
            font=("Arial", 14, "bold"),
            bg=Config.COLOR_BACKGROUND,
            fg=Config.COLOR_PRIMARY
        ).pack(pady=3)

        table_frame = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        table_frame.pack(pady=5)

        # Encabezados
        headers = ["Operación", "Hasta Tabla", "Correctas", "Incorrectas"]
        col_widths = [18, 12, 11, 11]

        for col, (header, width) in enumerate(zip(headers, col_widths)):
            tk.Label(
                table_frame,
                text=header,
                font=("Arial", 10, "bold"),
                bg=Config.COLOR_PRIMARY,
                fg="white",
                width=width,
                relief="solid",
                bd=1,
                padx=5,
                pady=4
            ).grid(row=0, column=col, sticky="ew")

        # Filas de datos
        row_num = self._agregar_filas_tabla_resultados(table_frame, col_widths)

        # Fila de totales
        self._agregar_fila_totales(table_frame, row_num, col_widths)

    def _agregar_filas_tabla_resultados(self, parent, col_widths):
        """Agrega las filas de datos a la tabla de resultados"""
        resultados_por_operacion = self._agrupar_resultados_por_operacion()

        row_num = 1
        for operacion in self.operaciones_nivel:
            if operacion in resultados_por_operacion:
                nombre_op = self.obtener_nombre_operacion(operacion)
                tablas = resultados_por_operacion[operacion]

                total_correctas = sum(t["correctas"] for t in tablas)
                total_incorrectas = sum(t["incorrectas"] for t in tablas)
                tabla_max = max(t["tabla"] for t in tablas)

                bg_color = "#e8f5e9" if row_num % 2 == 0 else Config.COLOR_BACKGROUND

                data = [nombre_op, str(tabla_max), str(total_correctas), str(total_incorrectas)]

                for col, (value, width) in enumerate(zip(data, col_widths)):
                    tk.Label(
                        parent,
                        text=value,
                        font=("Arial", 10, "bold"),
                        bg=bg_color,
                        fg="#333",
                        width=width,
                        relief="solid",
                        bd=1,
                        padx=5,
                        pady=3
                    ).grid(row=row_num, column=col, sticky="ew")

                row_num += 1

        return row_num

    def _agregar_fila_totales(self, parent, row_num, col_widths):
        """Agrega la fila de totales a la tabla de resultados"""
        total_correctas = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_incorrectas = sum(r["incorrectas"] for r in self.resultados_operacion.values())

        totales = ["TOTAL GENERAL", "", str(total_correctas), str(total_incorrectas)]

        for col, (value, width) in enumerate(zip(totales, col_widths)):
            tk.Label(
                parent,
                text=value,
                font=("Arial", 10, "bold"),
                bg="#c8e6c9",
                fg="#333",
                width=width,
                relief="solid",
                bd=2,
                padx=5,
                pady=4
            ).grid(row=row_num, column=col, sticky="ew")

    def _crear_botones_finales(self, parent):
        """Crea los botones de la pantalla final"""
        buttons_frame = tk.Frame(parent, bg=Config.COLOR_BACKGROUND)
        buttons_frame.pack(pady=8)

        tk.Button(
            buttons_frame,
            text="IMPRIMIR RESULTADOS",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            bg=Config.COLOR_PRIMARY,
            fg="white",
            command=self.imprimir_resultados
        ).pack(side="left", padx=8)

        tk.Button(
            buttons_frame,
            text="REINICIAR APLICATIVO",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            bg=Config.COLOR_INFO,
            fg="white",
            command=self.reiniciar_aplicativo
        ).pack(side="left", padx=8)

        tk.Button(
            buttons_frame,
            text="CERRAR PROGRAMA",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            bg=Config.COLOR_DANGER,
            fg="white",
            command=self.root.quit
        ).pack(side="left", padx=8)

    def reiniciar_aplicativo(self):
        """Reinicia el aplicativo desde la selección del nivel"""
        self._inicializar_variables()
        self.mostrar_pantalla_inicio()

    # ==================== SELECCIÓN Y VALIDACIÓN ====================

    def seleccionar_nivel(self, nivel):
        """Configura las operaciones y tiempos según el nivel seleccionado"""
        self.nivel = nivel

        if nivel == 1:
            self.operaciones_nivel = ["suma", "resta"]
            self.tiempo_principal = Config.NIVEL_1_TIEMPO_PRINCIPAL
            self.tiempo_maximo = Config.NIVEL_1_TIEMPO_MAXIMO
        elif nivel == 2:
            self.operaciones_nivel = ["suma", "resta", "multiplicación", "división"]
            self.tiempo_principal = Config.NIVEL_2_TIEMPO_PRINCIPAL
            self.tiempo_maximo = Config.NIVEL_2_TIEMPO_MAXIMO
        else:
            self.operaciones_nivel = ["suma", "resta", "multiplicación", "división", "potencia", "raíz"]
            self.tiempo_principal = Config.NIVEL_3_TIEMPO_PRINCIPAL
            self.tiempo_maximo = Config.NIVEL_3_TIEMPO_MAXIMO

        self.mostrar_pantalla_datos()

    def validar_datos(self):
        """Valida los datos del estudiante antes de comenzar el test"""
        nombre = self.entry_nombre.get().strip()
        curso = self.combo_curso.get()

        if not nombre or not curso:
            messagebox.showwarning("Faltan datos", "Complete nombre y curso.")
            return

        self.nombre = nombre
        self.curso = curso

        if TKCALENDAR_AVAILABLE:
            self.fecha = self.entry_fecha.get_date().strftime("%d/%m/%Y")
        else:
            self.fecha = self.entry_fecha.get()

        self.resultados_operacion = {}
        self.operacion_actual = ""
        self.tabla_actual = 1
        self.limites_tablas = {}

        self.solicitar_limite_tabla_operacion()

    def solicitar_limite_tabla_operacion(self):
        """Solicita al usuario el límite de tabla para la operación actual"""
        if not self.operacion_actual:
            self.operacion_actual = self.operaciones_nivel[0]

        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)
        tabla_minima = self.obtener_tabla_minima(self.operacion_actual)

        # Crear ventana de diálogo
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{nombre_op}")
        dialog.configure(bg=Config.COLOR_BACKGROUND)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        main_frame = tk.Frame(dialog, bg=Config.COLOR_BACKGROUND)
        main_frame.pack(expand=True, fill="both", padx=40, pady=30)

        # Título
        title_frame = tk.Frame(main_frame, bg=Config.COLOR_BACKGROUND)
        title_frame.pack(pady=(0, 25))

        tk.Label(
            title_frame,
            text="📊",
            font=("Arial", 24),
            bg=Config.COLOR_BACKGROUND
        ).pack()

        tk.Label(
            title_frame,
            text=f"{nombre_op}",
            font=("Arial", 18, "bold"),
            bg=Config.COLOR_BACKGROUND,
            fg="#333"
        ).pack(pady=(5, 0))

        # Instrucción
        texto_instruccion = "¿Hasta qué tabla quieres practicar?"
        if tabla_minima == 2:
            texto_instruccion += "\n(Esta operación comienza desde la tabla 2)"

        tk.Label(
            main_frame,
            text=texto_instruccion,
            font=("Arial", 13),
            bg=Config.COLOR_BACKGROUND,
            fg="#555",
            justify="center"
        ).pack(pady=(0, 20))

        # Spinbox
        spin_container = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="solid")
        spin_container.pack(pady=10)

        spin = tk.Spinbox(
            spin_container,
            from_=tabla_minima,
            to=12,
            font=("Arial", 20, "bold"),
            width=8,
            justify="center",
            bd=0,
            relief="flat",
            fg="#333"
        )
        spin.delete(0, "end")
        spin.insert(0, str(tabla_minima))
        spin.pack(padx=10, pady=10)

        resultado = {"confirmado": False}

        def confirmar():
            resultado["confirmado"] = True
            resultado["valor"] = int(spin.get())
            dialog.destroy()

        def cancelar():
            resultado["confirmado"] = False
            dialog.destroy()

        # Botones
        buttons_frame = tk.Frame(main_frame, bg=Config.COLOR_BACKGROUND)
        buttons_frame.pack(pady=20)

        btn_aceptar = tk.Button(
            buttons_frame,
            text="ACEPTAR",
            font=("Arial", 14, "bold"),
            width=12,
            height=2,
            bg=Config.COLOR_SUCCESS,
            fg="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=confirmar
        )
        btn_aceptar.pack(side="left", padx=10)
        btn_aceptar.bind("<Enter>", lambda e: btn_aceptar.config(bg="#45a049"))
        btn_aceptar.bind("<Leave>", lambda e: btn_aceptar.config(bg=Config.COLOR_SUCCESS))

        btn_cancelar = tk.Button(
            buttons_frame,
            text="CANCELAR",
            font=("Arial", 14, "bold"),
            width=12,
            height=2,
            bg=Config.COLOR_DANGER,
            fg="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=cancelar
        )
        btn_cancelar.pack(side="left", padx=10)
        btn_cancelar.bind("<Enter>", lambda e: btn_cancelar.config(bg="#d32f2f"))
        btn_cancelar.bind("<Leave>", lambda e: btn_cancelar.config(bg=Config.COLOR_DANGER))

        dialog.bind('<Return>', lambda e: confirmar())
        dialog.bind('<Escape>', lambda e: cancelar())

        # Centrar diálogo
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")

        self.root.wait_window(dialog)

        if resultado["confirmado"]:
            self.limites_tablas[self.operacion_actual] = resultado["valor"]
            self.tabla_max = resultado["valor"]
            # La tabla actual debe iniciar desde tabla_minima
            self.tabla_actual = tabla_minima
            self.mostrar_pantalla_ejercicios()
        else:
            self.mostrar_pantalla_datos()

    # ==================== GENERACIÓN DE EJERCICIOS ====================

    def generar_ejercicios(self, operacion):
        """Genera 12 ejercicios para la operación y tabla actual"""
        ejercicios = []
        ejercicios_set = set()
        tabla = self.tabla_actual
        intentos = 0

        while len(ejercicios) < Config.EJERCICIOS_POR_TABLA and intentos < Config.MAX_INTENTOS_GENERACION:
            intentos += 1

            ejercicio = self._generar_ejercicio_por_tipo(operacion, tabla)
            if ejercicio is None:
                continue

            texto = ejercicio["texto"]
            if texto not in ejercicios_set:
                ejercicios_set.add(texto)
                ejercicio["id"] = len(ejercicios)
                ejercicios.append(ejercicio)

        random.shuffle(ejercicios)

        # Reasignar IDs después de mezclar
        for idx, ej in enumerate(ejercicios):
            ej["id"] = idx

        return ejercicios

    def _generar_ejercicio_por_tipo(self, operacion, tabla):
        """Genera un ejercicio individual según el tipo de operación"""
        generadores = {
            "suma": self._generar_suma,
            "resta": self._generar_resta,
            "multiplicación": self._generar_multiplicacion,
            "división": self._generar_division,
            "potencia": self._generar_potencia,
            "raíz": self._generar_raiz
        }

        generador = generadores.get(operacion)
        if generador:
            return generador(tabla)
        return None

    def _generar_suma(self, tabla):
        """Genera un ejercicio de suma"""
        # La suma siempre inicia con el número de la tabla
        a = tabla
        b = random.randint(1, 100)

        return {
            "texto": f"{a} + {b} =",
            "respuesta": a + b
        }

    def _generar_resta(self, tabla):
        """Genera un ejercicio de resta"""
        # Para evitar números negativos:
        # - Si tabla = 1, debe ser A - 1 donde A >= 2
        # - Si tabla > 1, puede ser tabla - X donde X < tabla
        if tabla == 1:
            # Caso especial: tabla = 1, entonces debe ser A - 1 donde A >= 2
            a = random.randint(2, 100)
            b = tabla
        else:
            # Caso general: tabla - X donde X < tabla
            a = tabla
            b = random.randint(1, tabla - 1)

        return {
            "texto": f"{a} - {b} =",
            "respuesta": a - b
        }

    def _generar_multiplicacion(self, tabla):
        """Genera un ejercicio de multiplicación"""
        # La multiplicación siempre inicia con el número de la tabla
        a = tabla
        b = random.randint(2, 12)

        return {
            "texto": f"{a} × {b} =",
            "respuesta": a * b
        }

    def _generar_division(self, tabla):
        """Genera un ejercicio de división"""
        # Para evitar decimales, generamos A ÷ tabla donde A = tabla * resp
        # Esto garantiza divisiones exactas y que el número de la tabla aparezca
        # Nota: La división siempre comienza desde tabla 2
        b = tabla
        resp = random.randint(2, 12)
        a = b * resp

        return {
            "texto": f"{a} ÷ {b} =",
            "respuesta": resp
        }

    def _generar_potencia(self, tabla):
        """Genera un ejercicio de potenciación"""
        # El exponente es igual al número de la serie (tabla)
        exp = tabla

        # La base es un número aleatorio entre 2 y 15 para tener más variedad
        base = random.randint(2, 15)

        return {
            "texto": f"{base}^{exp} =",
            "respuesta": base ** exp
        }

    def _generar_raiz(self, tabla):
        """Genera un ejercicio de radicación"""
        # El índice de la raíz es igual al número de la serie (tabla)
        indice_raiz = tabla

        # La base es un número aleatorio entre 2 y 15 para tener más variedad
        base = random.randint(2, 15)

        # Calcular el número del que se sacará la raíz
        num = base ** indice_raiz
        resp = base

        # Mostrar según el índice de la raíz
        if indice_raiz == 1:
            texto = f"∜{num} =".replace("∜", "¹√")  # Raíz 1
        elif indice_raiz == 2:
            texto = f"√{num} ="  # Raíz cuadrada (común)
        elif indice_raiz == 3:
            texto = f"∛{num} ="  # Raíz cúbica
        else:
            texto = f"ⁿ√{num} =".replace("ⁿ", str(indice_raiz))  # Raíz n-ésima

        return {
            "texto": texto,
            "respuesta": resp
        }

    # ==================== CONTROL DE TIEMPO ====================

    def iniciar_cronometro(self):
        """Inicia el cronómetro y habilita los campos de respuesta"""
        if self.finalizado:
            messagebox.showinfo(
                "Ya finalizado",
                "Esta operación ya fue finalizada. No puede volver a iniciar."
            )
            return

        if not self.corriendo:
            self.tiempo_inicio = datetime.now()
            self.corriendo = True

            for entry in self.entries.values():
                entry.config(state="normal")

            self.actualizar_cronometro()

    def detener_cronometro(self):
        """Detiene el cronómetro"""
        if self.corriendo:
            self.tiempo_total += (datetime.now() - self.tiempo_inicio).total_seconds()
            self.corriendo = False

    def actualizar_cronometro(self):
        """Actualiza el cronómetro cada segundo"""
        if not self.corriendo:
            return

        elapsed = (datetime.now() - self.tiempo_inicio).total_seconds() + self.tiempo_total
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)

        if elapsed > self.tiempo_maximo:
            self._manejar_tiempo_agotado(mins, secs)
        elif elapsed > self.tiempo_principal:
            self._mostrar_tiempo_con_penalizacion(mins, secs)
        else:
            self._mostrar_tiempo_normal(mins, secs)
            self.root.after(1000, self.actualizar_cronometro)

    def _mostrar_tiempo_normal(self, mins, secs):
        """Muestra el tiempo en estado normal"""
        self.label_tiempo.config(
            text=f"Tiempo: {mins:02d}:{secs:02d}",
            fg=Config.COLOR_TIMER_NORMAL,
            bg=Config.COLOR_TIMER_BG
        )

    def _mostrar_tiempo_con_penalizacion(self, mins, secs):
        """Muestra el tiempo cuando hay penalización"""
        self.label_tiempo.config(
            text=f"Tiempo: {mins:02d}:{secs:02d} - Con penalización",
            fg=Config.COLOR_TIMER_WARNING,
            bg=Config.COLOR_TIMER_BG
        )
        self.root.after(1000, self.actualizar_cronometro)

    def _manejar_tiempo_agotado(self, mins, secs):
        """Maneja el caso cuando se agota el tiempo máximo"""
        self.label_tiempo.config(
            text=f"Tiempo: {mins:02d}:{secs:02d} - ¡TIEMPO MÁXIMO!",
            fg=Config.COLOR_TIMER_DANGER,
            bg=Config.COLOR_TIMER_BG
        )
        self.detener_cronometro()

        messagebox.showwarning(
            "Tiempo agotado",
            f"Has excedido el tiempo máximo de {int(self.tiempo_maximo//60)} minutos.\n"
            "La operación se finalizará automáticamente."
        )
        self.finalizar_operacion()

    # ==================== FINALIZACIÓN Y NAVEGACIÓN ====================

    def finalizar_operacion(self):
        """Finaliza la operación actual y calcula los resultados"""
        if self.finalizado:
            messagebox.showinfo("Ya finalizado", "Esta operación ya fue finalizada.")
            return

        if self.tiempo_total == 0 and not self.corriendo:
            messagebox.showwarning("Error", "Primero debe presionar INICIAR")
            return

        self.detener_cronometro()

        correctas, incorrectas = self._evaluar_respuestas()

        self._deshabilitar_controles()
        self.finalizado = True

        self._guardar_resultado(correctas, incorrectas)
        self._mostrar_mensaje_finalizacion(correctas)

        self._verificar_y_avanzar()

    def _evaluar_respuestas(self):
        """Evalúa las respuestas del usuario"""
        correctas = 0
        incorrectas = 0

        for ej in self.ejercicios:
            val = self.entries[ej["id"]].get().strip()
            try:
                if int(val) == ej["respuesta"]:
                    correctas += 1
                else:
                    incorrectas += 1
            except ValueError:
                incorrectas += 1

        return correctas, incorrectas

    def _deshabilitar_controles(self):
        """Deshabilita todos los controles después de finalizar"""
        for entry in self.entries.values():
            entry.config(state="disabled")

        if self.boton_finalizar:
            self.boton_finalizar.config(state="disabled")

        if self.boton_iniciar:
            self.boton_iniciar.config(state="disabled")

    def _guardar_resultado(self, correctas, incorrectas):
        """Guarda el resultado de la operación actual"""
        clave = f"{self.operacion_actual}_tabla{self.tabla_actual}"
        self.resultados_operacion[clave] = {
            "operacion": self.operacion_actual,
            "tabla": self.tabla_actual,
            "correctas": correctas,
            "incorrectas": incorrectas,
            "total": Config.EJERCICIOS_POR_TABLA,
            "tiempo": self.tiempo_total
        }

    def _mostrar_mensaje_finalizacion(self, correctas):
        """Muestra mensaje informativo al finalizar una operación"""
        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)

        messagebox.showinfo(
            "¡Operación Completada!",
            f"{nombre_op} - TABLA DEL {self.tabla_actual}\n\n"
            f"Aciertos: {correctas}/{Config.EJERCICIOS_POR_TABLA}\n"
            f"Tiempo usado: {int(self.tiempo_total//60):02d}:{int(self.tiempo_total%60):02d}"
        )

    def _verificar_y_avanzar(self):
        """Verifica si debe avanzar automáticamente o mostrar resumen"""
        idx_actual = self.operaciones_nivel.index(self.operacion_actual)
        es_ultima_operacion = (idx_actual == len(self.operaciones_nivel) - 1)
        es_ultima_tabla = (self.tabla_actual == self.tabla_max)

        if es_ultima_tabla and es_ultima_operacion:
            self.mostrar_resultados_finales()
        elif es_ultima_tabla:
            self.mostrar_resumen_operacion_completa()

    def siguiente_operacion(self):
        """Avanza a la siguiente tabla u operación"""
        clave_actual = f"{self.operacion_actual}_tabla{self.tabla_actual}"

        if clave_actual not in self.resultados_operacion:
            if not messagebox.askyesno(
                "Advertencia",
                "¿Pasar a la siguiente tabla sin guardar esta?"
            ):
                return

        if self.tabla_actual < self.tabla_max:
            self.tabla_actual += 1
            self.tiempo_total = 0
            self.mostrar_pantalla_ejercicios()
        else:
            self.mostrar_resumen_operacion_completa()

    def mostrar_resumen_operacion_completa(self):
        """Muestra el resumen de todas las tablas de la operación actual"""
        correctas_total, tiempo_total_op, num_tablas = self._calcular_totales_operacion()
        total_preguntas = num_tablas * Config.EJERCICIOS_POR_TABLA

        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)

        mensaje = f"RESUMEN DE {nombre_op.upper()}\n\n"
        mensaje += f"Total de aciertos: {correctas_total}/{total_preguntas}\n"
        mensaje += f"Tiempo total: {int(tiempo_total_op//60):02d}:{int(tiempo_total_op%60):02d}\n\n"

        idx_actual = self.operaciones_nivel.index(self.operacion_actual)

        if idx_actual + 1 < len(self.operaciones_nivel):
            siguiente_op = self.operaciones_nivel[idx_actual + 1]
            nombre_siguiente = self.obtener_nombre_operacion(siguiente_op)
            mensaje += f"Presione ACEPTAR para continuar con {nombre_siguiente}"

            messagebox.showinfo("Operación Completada", mensaje)

            self.operacion_actual = siguiente_op
            # Usar la tabla mínima de la nueva operación
            self.tabla_actual = self.obtener_tabla_minima(siguiente_op)
            self.tiempo_total = 0
            self.solicitar_limite_tabla_operacion()
        else:
            mensaje += "¡Ha completado todas las operaciones!"
            messagebox.showinfo("Test Completado", mensaje)
            self.mostrar_resultados_finales()

    def _calcular_totales_operacion(self):
        """Calcula los totales de la operación actual"""
        correctas_total = 0
        tiempo_total_op = 0
        num_tablas = 0

        for clave, r in self.resultados_operacion.items():
            if r["operacion"] == self.operacion_actual:
                correctas_total += r["correctas"]
                tiempo_total_op += r["tiempo"]
                num_tablas += 1

        return correctas_total, tiempo_total_op, num_tablas

    # ==================== RESULTADOS ====================

    def mostrar_resultados_operacion(self):
        """Muestra los resultados parciales hasta el momento"""
        if not self.resultados_operacion:
            messagebox.showinfo("Sin datos", "Aún no has completado operaciones.")
            return

        texto = "RESULTADOS HASTA AHORA\n\n"
        total_ac = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_pr = len(self.resultados_operacion) * Config.EJERCICIOS_POR_TABLA

        for clave, r in sorted(self.resultados_operacion.items()):
            op = r["operacion"]
            tabla = r["tabla"]
            mins = int(r["tiempo"] // 60)
            secs = int(r["tiempo"] % 60)
            texto += f"{op.upper()} - Tabla {tabla}: {r['correctas']}/{Config.EJERCICIOS_POR_TABLA}  |  {mins:02d}:{secs:02d}\n"

        texto += f"\nTOTAL: {total_ac}/{total_pr}"
        messagebox.showinfo("Resultados Parciales", texto)

    def calcular_nota_final(self):
        """Calcula la nota final con penalización por tiempo"""
        total_aciertos = sum(r["correctas"] for r in self.resultados_operacion.values())

        # Calcular el total de preguntas basado en las tablas realmente realizadas
        total_preguntas = 0
        for operacion in self.operaciones_nivel:
            tabla_max_op = self.limites_tablas.get(operacion, self.tabla_max)
            tabla_min_op = self.obtener_tabla_minima(operacion)
            num_tablas = tabla_max_op - tabla_min_op + 1
            total_preguntas += num_tablas * Config.EJERCICIOS_POR_TABLA

        nota = (total_aciertos / total_preguntas) * 100

        penalizacion_total = 0
        for clave, r in self.resultados_operacion.items():
            tiempo_op = r["tiempo"]
            if tiempo_op > self.tiempo_principal:
                exceso = tiempo_op - self.tiempo_principal
                penalizacion_op = min(
                    (exceso / 60) * Config.PENALIZACION_POR_MINUTO,
                    Config.PENALIZACION_MAXIMA
                )
                penalizacion_total += penalizacion_op

        nota_final = max(round(nota - penalizacion_total, 1), 0)
        tiempo_total = sum(r["tiempo"] for r in self.resultados_operacion.values())

        return nota_final, tiempo_total, round(penalizacion_total, 1)

    def _agrupar_resultados_por_operacion(self):
        """Agrupa los resultados por tipo de operación"""
        resultados_agrupados = {}

        for clave, r in self.resultados_operacion.items():
            op = r["operacion"]
            if op not in resultados_agrupados:
                resultados_agrupados[op] = []
            resultados_agrupados[op].append(r)

        return resultados_agrupados

    # ==================== IMPRESIÓN ====================

    def imprimir_resultados(self):
        """Genera e imprime un reporte HTML de resultados"""
        nota, tiempo, pen = self.calcular_nota_final()

        html_content = self._generar_html_reporte(nota, pen)

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.html',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(html_content)
            temp_file = f.name

        self._abrir_archivo_en_navegador(temp_file)

    def _generar_html_reporte(self, nota, penalizacion):
        """Genera el contenido HTML del reporte"""
        color_nota = Config.COLOR_SUCCESS if nota >= 70 else Config.COLOR_DANGER

        html = f"""<!DOCTYPE html>
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
            color: {Config.COLOR_PRIMARY};
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
            color: {color_nota};
            margin: 30px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background-color: {Config.COLOR_PRIMARY};
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
            border-top: 2px solid {Config.COLOR_PRIMARY};
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
    {self._generar_mensaje_penalizacion_html(penalizacion)}
    <hr>
    <h2 style="color: {Config.COLOR_PRIMARY};">DETALLE DE RESULTADOS</h2>
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
{self._generar_filas_tabla_html()}
        </tbody>
    </table>
</body>
</html>"""

        return html

    def _generar_mensaje_penalizacion_html(self, penalizacion):
        """Genera el mensaje de penalización en HTML"""
        if penalizacion > 0:
            return f'<p style="text-align: center; color: {Config.COLOR_DANGER};"><strong>Penalización aplicada: -{penalizacion} puntos (tiempo excedido)</strong></p>'
        return ''

    def _generar_filas_tabla_html(self):
        """Genera las filas de la tabla en HTML"""
        resultados_por_operacion = self._agrupar_resultados_por_operacion()
        filas = ""

        for operacion in self.operaciones_nivel:
            if operacion in resultados_por_operacion:
                nombre_op = self.obtener_nombre_operacion(operacion)
                tablas = resultados_por_operacion[operacion]

                total_correctas = sum(t["correctas"] for t in tablas)
                total_incorrectas = sum(t["incorrectas"] for t in tablas)
                tabla_max = max(t["tabla"] for t in tablas)

                filas += f"""
            <tr class="operacion-header">
                <td><strong>{nombre_op}</strong></td>
                <td><strong>{tabla_max}</strong></td>
                <td><strong>{total_correctas}</strong></td>
                <td><strong>{total_incorrectas}</strong></td>
            </tr>"""

        # Totales
        total_correctas = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_incorrectas = sum(r["incorrectas"] for r in self.resultados_operacion.values())

        filas += f"""
            <tr class="total-row">
                <td colspan="2"><strong>TOTAL GENERAL</strong></td>
                <td><strong>{total_correctas}</strong></td>
                <td><strong>{total_incorrectas}</strong></td>
            </tr>"""

        return filas

    def _abrir_archivo_en_navegador(self, archivo):
        """Abre un archivo en el navegador predeterminado"""
        try:
            sistema = platform.system()

            if sistema == 'Windows':
                os.startfile(archivo)
            elif sistema == 'Darwin':
                subprocess.run(['open', archivo])
            else:
                subprocess.run(['xdg-open', archivo])

            messagebox.showinfo(
                "Imprimir",
                "Se abrió el reporte en su navegador.\nUse Ctrl+P para imprimir."
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el archivo para imprimir: {e}"
            )


# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = AgilidadMentalApp(root)
    root.mainloop()
