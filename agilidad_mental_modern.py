import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
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

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False


# ==================== CONSTANTES ====================
class Config:
    """Configuración y constantes del programa"""

    # Dimensiones de ventana
    WINDOW_WIDTH = 1300
    WINDOW_HEIGHT = 850

    # Colores modernos y amigables para niños
    COLOR_PRIMARY = "#4CAF50"
    COLOR_SECONDARY = "#2196F3"
    COLOR_BACKGROUND = "#F5F7FA"
    COLOR_WARNING = "#FF9800"
    COLOR_INFO = "#2196F3"
    COLOR_DANGER = "#E53935"
    COLOR_SUCCESS = "#4CAF50"
    COLOR_TIMER_BG = "#1E1E1E"
    COLOR_TIMER_NORMAL = "#FFFFFF"
    COLOR_TIMER_WARNING = "#FFC107"
    COLOR_TIMER_DANGER = "#FF5252"

    # Colores para niveles
    COLOR_NIVEL_1 = "#4CAF50"  # Verde
    COLOR_NIVEL_2 = "#FF9800"  # Naranja
    COLOR_NIVEL_3 = "#E91E63"  # Rosa/Magenta

    # Tiempos por nivel (en segundos)
    NIVEL_1_TIEMPO_PRINCIPAL = 12 * 60  # 12 minutos
    NIVEL_1_TIEMPO_MAXIMO = 15 * 60     # 15 minutos
    NIVEL_2_TIEMPO_PRINCIPAL = 10 * 60  # 10 minutos
    NIVEL_2_TIEMPO_MAXIMO = 12 * 60     # 12 minutos
    NIVEL_3_TIEMPO_PRINCIPAL = 10 * 60  # 10 minutos
    NIVEL_3_TIEMPO_MAXIMO = 12 * 60     # 12 minutos

    # Ejercicios
    EJERCICIOS_POR_TABLA = 13  # Máximo de ejercicios (suma, multiplicación, división, potencia, raíz)
    # Nota: Resta tiene tabla+1 ejercicios (ej: tabla 3 = 4 ejercicios)
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

    # Emojis para operaciones
    EMOJIS_OPERACIONES = {
        "suma": "➕",
        "resta": "➖",
        "multiplicación": "✖️",
        "división": "➗",
        "potencia": "🔼",
        "raíz": "√"
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
        # Configurar tema de CustomTkinter
        ctk.set_appearance_mode("light")  # Modo claro para niños
        ctk.set_default_color_theme("green")  # Tema verde

        self.root.title("ACADEMIA NAVAL CAP. LEONARDO ABAD GUERRA - Test de Agilidad Mental")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")

        # Centrar ventana
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

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
        self.historial_ejercicios = []  # Guarda todos los ejercicios realizados

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

    def obtener_emoji_operacion(self, operacion):
        """Retorna el emoji de una operación"""
        return Config.EMOJIS_OPERACIONES.get(operacion, "📝")

    def obtener_tabla_minima(self, operacion):
        """Retorna la tabla mínima para una operación específica"""
        # Multiplicación, división, potenciación y radicación empiezan desde tabla 2
        return 2 if operacion in ["multiplicación", "división", "potencia", "raíz"] else 1

    def obtener_color_nivel(self, nivel):
        """Retorna el color asociado a un nivel"""
        colores = {
            1: Config.COLOR_NIVEL_1,
            2: Config.COLOR_NIVEL_2,
            3: Config.COLOR_NIVEL_3
        }
        return colores.get(nivel, Config.COLOR_PRIMARY)

    # ==================== PANTALLAS ====================

    def mostrar_pantalla_inicio(self):
        """Pantalla inicial con selección de nivel"""
        self.limpiar_pantalla()

        # Frame principal con gradiente visual
        main_frame = ctk.CTkFrame(self.root, fg_color=Config.COLOR_BACKGROUND)
        main_frame.pack(fill="both", expand=True)

        # Contenedor centrado
        center_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo y título
        self._crear_header_inicio(center_container)

        # Separador decorativo
        separator = ctk.CTkFrame(center_container, height=3, fg_color=Config.COLOR_PRIMARY)
        separator.pack(pady=20, fill="x", padx=50)

        # Botones de nivel
        self._crear_botones_nivel(center_container)

        # Footer con instrucciones
        footer = ctk.CTkLabel(
            center_container,
            text="💡 Selecciona tu nivel para comenzar el test de agilidad mental",
            font=("Arial", 14),
            text_color="#666666"
        )
        footer.pack(pady=(30, 0))

    def _crear_header_inicio(self, parent):
        """Crea el encabezado de la pantalla de inicio"""
        # Logo
        logo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        logo_frame.pack(pady=(0, 20))

        if PIL_AVAILABLE and os.path.exists("logo.png"):
            try:
                img = Image.open("logo.png")
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                logo = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 200))
                label_logo = ctk.CTkLabel(logo_frame, image=logo, text="")
                label_logo.pack()
            except:
                ctk.CTkLabel(
                    logo_frame,
                    text="🎓",
                    font=("Arial", 80)
                ).pack()
        else:
            ctk.CTkLabel(
                logo_frame,
                text="🎓",
                font=("Arial", 80)
            ).pack()

        # Título principal
        ctk.CTkLabel(
            parent,
            text="TEST DE AGILIDAD MENTAL",
            font=("Arial", 32, "bold"),
            text_color=Config.COLOR_PRIMARY
        ).pack()

        # Subtítulo
        ctk.CTkLabel(
            parent,
            text="Academia Naval Cap. Leonardo Abad Guerra",
            font=("Arial", 16),
            text_color="#666666"
        ).pack(pady=(5, 0))

    def _crear_botones_nivel(self, parent):
        """Crea los botones de selección de nivel"""
        botones_frame = ctk.CTkFrame(parent, fg_color="transparent")
        botones_frame.pack(pady=20)

        nivel_info = [
            (1, "🌟 NIVEL 1", "Suma y Resta", Config.COLOR_NIVEL_1),
            (2, "⭐ NIVEL 2", "Suma, Resta, Multiplicación y División", Config.COLOR_NIVEL_2),
            (3, "✨ NIVEL 3", "Todas las operaciones + Potencia y Raíz", Config.COLOR_NIVEL_3)
        ]

        for nivel, titulo, descripcion, color in nivel_info:
            # Frame contenedor para cada botón
            nivel_container = ctk.CTkFrame(botones_frame, fg_color="transparent")
            nivel_container.pack(pady=12)

            # Botón principal
            btn = ctk.CTkButton(
                nivel_container,
                text=titulo,
                font=("Arial", 24, "bold"),
                width=400,
                height=70,
                corner_radius=20,
                fg_color=color,
                hover_color=self._oscurecer_color(color),
                command=lambda n=nivel: self.seleccionar_nivel(n)
            )
            btn.pack()

            # Descripción debajo del botón
            ctk.CTkLabel(
                nivel_container,
                text=descripcion,
                font=("Arial", 12),
                text_color="#888888"
            ).pack(pady=(5, 0))

    def _oscurecer_color(self, color_hex):
        """Oscurece un color en formato hex para efectos hover"""
        # Convertir hex a RGB
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))

        # Oscurecer (reducir cada componente en 20%)
        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)

        return f'#{r:02x}{g:02x}{b:02x}'

    def mostrar_pantalla_datos(self):
        """Pantalla para ingresar datos del estudiante"""
        self.limpiar_pantalla()

        main_frame = ctk.CTkFrame(self.root, fg_color=Config.COLOR_BACKGROUND)
        main_frame.pack(fill="both", expand=True)

        # Botón de volver (esquina superior izquierda)
        boton_volver = ctk.CTkButton(
            main_frame,
            text="← Volver",
            font=("Arial", 16, "bold"),
            width=120,
            height=40,
            corner_radius=10,
            fg_color="transparent",
            hover_color="#E0E0E0",
            text_color="#666666",
            command=self.mostrar_pantalla_inicio
        )
        boton_volver.place(x=20, y=20)

        # Contenedor centrado
        center_frame = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=20,
            border_width=2,
            border_color=Config.COLOR_PRIMARY
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Contenido del formulario
        content_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        content_frame.pack(padx=60, pady=50)

        # Título con emoji
        color_nivel = self.obtener_color_nivel(self.nivel)
        ctk.CTkLabel(
            content_frame,
            text=f"📝 Nivel {self.nivel} - Datos del Estudiante",
            font=("Arial", 28, "bold"),
            text_color=color_nivel
        ).pack(pady=(0, 30))

        # Campo Nombre
        self._crear_campo_formulario(
            content_frame,
            "👤 Nombre Completo:",
            "entry_nombre",
            "Ingresa tu nombre completo"
        )

        # Campo Curso
        ctk.CTkLabel(
            content_frame,
            text="📚 Curso:",
            font=("Arial", 16, "bold"),
            text_color="#333333",
            anchor="w"
        ).pack(fill="x", pady=(15, 5))

        self.combo_curso = ctk.CTkComboBox(
            content_frame,
            values=Config.CURSOS,
            font=("Arial", 16),
            width=400,
            height=40,
            corner_radius=10,
            button_color=Config.COLOR_PRIMARY,
            button_hover_color=self._oscurecer_color(Config.COLOR_PRIMARY),
            dropdown_fg_color="white",
            dropdown_hover_color="#E8F5E9"
        )
        self.combo_curso.pack(pady=(0, 15))
        self.combo_curso.set("Selecciona tu curso")

        # Campo Fecha
        ctk.CTkLabel(
            content_frame,
            text="📅 Fecha:",
            font=("Arial", 16, "bold"),
            text_color="#333333",
            anchor="w"
        ).pack(fill="x", pady=(15, 5))

        fecha_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        fecha_frame.pack(fill="x")

        if TKCALENDAR_AVAILABLE:
            self.entry_fecha = DateEntry(
                fecha_frame,
                font=("Arial", 16),
                width=38,
                borderwidth=2,
                date_pattern='dd/mm/yyyy',
                locale='es_ES',
                showweeknumbers=False
            )
            self.entry_fecha.set_date(datetime.now())
        else:
            self.entry_fecha = ctk.CTkEntry(
                fecha_frame,
                font=("Arial", 16),
                width=400,
                height=40,
                corner_radius=10
            )
            self.entry_fecha.insert(0, self.fecha)

        self.entry_fecha.pack()

        # Botón Comenzar
        btn_comenzar = ctk.CTkButton(
            content_frame,
            text="🚀 COMENZAR TEST",
            font=("Arial", 20, "bold"),
            width=300,
            height=60,
            corner_radius=15,
            fg_color=color_nivel,
            hover_color=self._oscurecer_color(color_nivel),
            command=self.validar_datos
        )
        btn_comenzar.pack(pady=(30, 0))

    def _crear_campo_formulario(self, parent, label_text, attr_name, placeholder):
        """Crea un campo de formulario con etiqueta y entrada"""
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Arial", 16, "bold"),
            text_color="#333333",
            anchor="w"
        ).pack(fill="x", pady=(15, 5))

        entry = ctk.CTkEntry(
            parent,
            font=("Arial", 16),
            width=400,
            height=40,
            corner_radius=10,
            placeholder_text=placeholder,
            border_color=Config.COLOR_PRIMARY
        )
        entry.pack(pady=(0, 15))
        setattr(self, attr_name, entry)

    def mostrar_pantalla_ejercicios(self):
        """Pantalla principal con los ejercicios de la operación actual"""
        self.limpiar_pantalla()
        # Pausar el cronómetro pero no reiniciar el tiempo
        self.corriendo = False
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

        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color=Config.COLOR_BACKGROUND)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Configurar grid
        main_frame.grid_columnconfigure(0, weight=2)  # Ejercicios
        main_frame.grid_columnconfigure(1, weight=1)  # Controles
        main_frame.grid_rowconfigure(0, weight=1)

        # Panel izquierdo: Ejercicios
        self._crear_panel_ejercicios_moderno(main_frame)

        # Panel derecho: Controles y cronómetro
        self._crear_panel_controles_moderno(main_frame)

    def _crear_panel_ejercicios_moderno(self, parent):
        """Crea el panel con los ejercicios (moderno y colorido)"""
        ejercicios_container = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=20,
            border_width=2,
            border_color=Config.COLOR_PRIMARY
        )
        ejercicios_container.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        # Scrollable frame para ejercicios
        scroll_frame = ctk.CTkScrollableFrame(
            ejercicios_container,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Encabezado
        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)
        emoji_op = self.obtener_emoji_operacion(self.operacion_actual)

        header_frame = ctk.CTkFrame(scroll_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=15)
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text=f"{emoji_op} {nombre_op} - Tabla del {self.tabla_actual}",
            font=("Arial", 24, "bold"),
            text_color="white"
        ).pack(pady=15)

        # Ejercicios
        self.entries = {}
        for i, ej in enumerate(self.ejercicios):
            self._crear_ejercicio_moderno(scroll_frame, ej, i)

    def _crear_ejercicio_moderno(self, parent, ejercicio, index):
        """Crea una fila con un ejercicio individual (versión moderna)"""
        # Frame contenedor con color alternado
        bg_color = "#F8F9FA" if index % 2 == 0 else "white"

        row_frame = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=10
        )
        row_frame.pack(fill="x", pady=5, padx=10)

        # Contenido interno
        content_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)

        # Número del ejercicio
        ctk.CTkLabel(
            content_frame,
            text=f"{index + 1}.",
            font=("Arial", 16, "bold"),
            text_color=Config.COLOR_PRIMARY,
            width=40
        ).pack(side="left", padx=(0, 10))

        # Manejar potencias con superíndice
        if "^" in ejercicio["texto"]:
            self._crear_ejercicio_potencia_moderno(content_frame, ejercicio)
        else:
            ctk.CTkLabel(
                content_frame,
                text=ejercicio["texto"],
                font=("Arial", 18, "bold"),
                text_color="#333333",
                width=200,
                anchor="e"
            ).pack(side="left", padx=(0, 20))

        # Entry para la respuesta
        vcmd = (self.root.register(self.validar_numero), '%P')
        entry = ctk.CTkEntry(
            content_frame,
            font=("Arial", 18),
            width=120,
            height=40,
            justify="center",
            corner_radius=10,
            state="disabled",
            border_color=Config.COLOR_PRIMARY,
            fg_color="white"
        )
        entry.pack(side="left")
        self.entries[ejercicio["id"]] = entry

    def _crear_ejercicio_potencia_moderno(self, parent, ejercicio):
        """Crea un ejercicio de potencia con superíndice (versión moderna)"""
        from tkinter import Label, Frame

        op_frame = Frame(parent, bg=parent.cget("fg_color")[1] if isinstance(parent.cget("fg_color"), tuple) else parent.cget("fg_color"))
        op_frame.pack(side="left", padx=(0, 20))

        parts = ejercicio["texto"].split("^")
        base = parts[0].strip()
        exp_part = parts[1].replace("=", "").strip()

        Label(
            op_frame,
            text=base,
            font=("Arial", 18, "bold"),
            bg=op_frame.cget("bg"),
            fg="#333333"
        ).pack(side="left")

        Label(
            op_frame,
            text=exp_part,
            font=("Arial", 11, "bold"),
            bg=op_frame.cget("bg"),
            fg="#333333"
        ).pack(side="left", anchor="n")

        Label(
            op_frame,
            text=" =",
            font=("Arial", 18, "bold"),
            bg=op_frame.cget("bg"),
            fg="#333333"
        ).pack(side="left")

    def _crear_panel_controles_moderno(self, parent):
        """Crea el panel de controles y cronómetro (moderno)"""
        controles_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controles_frame.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        # Cronómetro
        cronometro_frame = ctk.CTkFrame(
            controles_frame,
            fg_color=Config.COLOR_TIMER_BG,
            corner_radius=15,
            border_width=3,
            border_color=Config.COLOR_PRIMARY
        )
        cronometro_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            cronometro_frame,
            text="⏱️ TIEMPO",
            font=("Arial", 16, "bold"),
            text_color=Config.COLOR_TIMER_NORMAL
        ).pack(pady=(15, 5))

        mins = int(self.tiempo_total // 60)
        secs = int(self.tiempo_total % 60)

        self.label_tiempo = ctk.CTkLabel(
            cronometro_frame,
            text=f"{mins:02d}:{secs:02d}",
            font=("Arial", 48, "bold"),
            text_color=Config.COLOR_TIMER_NORMAL
        )
        self.label_tiempo.pack(pady=(0, 15))

        # Información del estudiante
        info_frame = ctk.CTkFrame(
            controles_frame,
            fg_color="white",
            corner_radius=15,
            border_width=2,
            border_color=Config.COLOR_PRIMARY
        )
        info_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            info_frame,
            text="👤 Estudiante",
            font=("Arial", 14, "bold"),
            text_color=Config.COLOR_PRIMARY
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            info_frame,
            text=self.nombre,
            font=("Arial", 16, "bold"),
            text_color="#333333"
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            info_frame,
            text=self.curso,
            font=("Arial", 14),
            text_color="#666666"
        ).pack(pady=(0, 15))

        # Botones de acción
        self._crear_botones_accion_modernos(controles_frame)

    def _crear_botones_accion_modernos(self, parent):
        """Crea los botones de acción (versión moderna)"""
        # Botón INICIAR
        self.boton_iniciar = ctk.CTkButton(
            parent,
            text="▶️ INICIAR",
            font=("Arial", 18, "bold"),
            width=200,
            height=60,
            corner_radius=15,
            fg_color=Config.COLOR_SUCCESS,
            hover_color=self._oscurecer_color(Config.COLOR_SUCCESS),
            command=self.iniciar_cronometro
        )
        self.boton_iniciar.pack(pady=(0, 15))

        # Botón FINALIZAR (bloqueado inicialmente)
        self.boton_finalizar = ctk.CTkButton(
            parent,
            text="⏹️ FINALIZAR",
            font=("Arial", 18, "bold"),
            width=200,
            height=60,
            corner_radius=15,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#666666",
            command=self.finalizar_operacion,
            state="disabled"
        )
        self.boton_finalizar.pack(pady=(0, 15))

        # Botón RESULTADOS
        ctk.CTkButton(
            parent,
            text="📊 RESULTADOS",
            font=("Arial", 18, "bold"),
            width=200,
            height=60,
            corner_radius=15,
            fg_color=Config.COLOR_INFO,
            hover_color=self._oscurecer_color(Config.COLOR_INFO),
            command=self.mostrar_resultados_operacion
        ).pack(pady=(0, 15))

        # Botón SIGUIENTE (condicional)
        if self._debe_mostrar_boton_siguiente():
            boton_texto = self._obtener_texto_boton_siguiente()
            ctk.CTkButton(
                parent,
                text=f"➡️ {boton_texto}",
                font=("Arial", 16, "bold"),
                width=200,
                height=60,
                corner_radius=15,
                fg_color=Config.COLOR_PRIMARY,
                hover_color=self._oscurecer_color(Config.COLOR_PRIMARY),
                command=self.siguiente_operacion
            ).pack(pady=(0, 15))

    def _debe_mostrar_boton_siguiente(self):
        """Determina si debe mostrarse el botón SIGUIENTE"""
        idx_actual = self.operaciones_nivel.index(self.operacion_actual)
        es_ultima_operacion = (idx_actual == len(self.operaciones_nivel) - 1)
        es_ultima_tabla = (self.tabla_actual == self.tabla_max)
        return not (es_ultima_tabla and es_ultima_operacion)

    def _obtener_texto_boton_siguiente(self):
        """Retorna el texto apropiado para el botón SIGUIENTE"""
        if self.tabla_actual < self.tabla_max:
            return "SIGUIENTE TABLA"
        return "SIGUIENTE OPERACIÓN"

    def mostrar_resultados_finales(self):
        """Pantalla final con todos los resultados del test"""
        self.limpiar_pantalla()

        nota, tiempo, pen = self.calcular_nota_final()

        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color=Config.COLOR_BACKGROUND)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=20
        )
        scroll_frame.pack(fill="both", expand=True)

        # Encabezado
        self._crear_encabezado_resultados_moderno(scroll_frame, nota, pen)

        # Separador
        ctk.CTkFrame(
            scroll_frame,
            height=3,
            fg_color=Config.COLOR_PRIMARY
        ).pack(fill="x", pady=20, padx=50)

        # Tabla de resultados
        self._crear_tabla_resultados_moderna(scroll_frame)

        # Separador
        ctk.CTkFrame(
            scroll_frame,
            height=3,
            fg_color=Config.COLOR_PRIMARY
        ).pack(fill="x", pady=20, padx=50)

        # Botones finales
        self._crear_botones_finales_modernos(scroll_frame)

    def _crear_encabezado_resultados_moderno(self, parent, nota, penalizacion):
        """Crea el encabezado de resultados (versión moderna)"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(pady=(20, 10))

        # Emoji según la nota
        emoji = "🎉" if nota >= 90 else "😊" if nota >= 70 else "💪"

        ctk.CTkLabel(
            header_frame,
            text=emoji,
            font=("Arial", 60)
        ).pack()

        ctk.CTkLabel(
            header_frame,
            text="¡TEST COMPLETADO!",
            font=("Arial", 32, "bold"),
            text_color=Config.COLOR_PRIMARY
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            header_frame,
            text=f"{self.nombre} - {self.curso}",
            font=("Arial", 18),
            text_color="#666666"
        ).pack()

        ctk.CTkLabel(
            header_frame,
            text=f"📅 {self.fecha}",
            font=("Arial", 16),
            text_color="#888888"
        ).pack(pady=(5, 20))

        # Nota final
        color = Config.COLOR_SUCCESS if nota >= 70 else Config.COLOR_DANGER

        nota_frame = ctk.CTkFrame(
            header_frame,
            fg_color=color,
            corner_radius=20
        )
        nota_frame.pack()

        ctk.CTkLabel(
            nota_frame,
            text=f"NOTA FINAL: {nota}/100",
            font=("Arial", 36, "bold"),
            text_color="white"
        ).pack(padx=40, pady=20)

        if penalizacion > 0:
            ctk.CTkLabel(
                header_frame,
                text=f"⚠️ Penalización: -{penalizacion} pts (tiempo excedido)",
                font=("Arial", 14),
                text_color=Config.COLOR_DANGER
            ).pack(pady=(10, 0))

    def _crear_tabla_resultados_moderna(self, parent):
        """Crea la tabla de resultados (versión moderna)"""
        ctk.CTkLabel(
            parent,
            text="📋 DETALLE DE RESULTADOS",
            font=("Arial", 24, "bold"),
            text_color=Config.COLOR_PRIMARY
        ).pack(pady=(10, 20))

        # Frame para la tabla
        table_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        table_frame.pack(padx=50, fill="x")

        # Encabezados
        headers_frame = ctk.CTkFrame(table_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=10)
        headers_frame.pack(fill="x", pady=(0, 5))

        headers = ["Operación", "Hasta Tabla", "Correctas", "Incorrectas"]
        for header in headers:
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="white",
                width=150
            ).pack(side="left", padx=10, pady=12, expand=True)

        # Filas de datos
        self._agregar_filas_tabla_resultados_modernas(table_frame)

    def _agregar_filas_tabla_resultados_modernas(self, parent):
        """Agrega las filas de datos a la tabla (versión moderna)"""
        resultados_por_operacion = self._agrupar_resultados_por_operacion()

        row_num = 0
        total_correctas = 0
        total_incorrectas = 0

        for operacion in self.operaciones_nivel:
            if operacion in resultados_por_operacion:
                nombre_op = self.obtener_nombre_operacion(operacion)
                emoji_op = self.obtener_emoji_operacion(operacion)
                tablas = resultados_por_operacion[operacion]

                correctas = sum(t["correctas"] for t in tablas)
                incorrectas = sum(t["incorrectas"] for t in tablas)
                tabla_max = max(t["tabla"] for t in tablas)

                total_correctas += correctas
                total_incorrectas += incorrectas

                bg_color = "#F8F9FA" if row_num % 2 == 0 else "white"

                row_frame = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=10)
                row_frame.pack(fill="x", pady=2)

                data = [
                    f"{emoji_op} {nombre_op}",
                    str(tabla_max),
                    str(correctas),
                    str(incorrectas)
                ]

                for value in data:
                    ctk.CTkLabel(
                        row_frame,
                        text=value,
                        font=("Arial", 13),
                        text_color="#333333",
                        width=150
                    ).pack(side="left", padx=10, pady=10, expand=True)

                row_num += 1

        # Fila de totales
        total_frame = ctk.CTkFrame(parent, fg_color="#C8E6C9", corner_radius=10)
        total_frame.pack(fill="x", pady=(10, 0))

        totales = ["TOTAL GENERAL", "", str(total_correctas), str(total_incorrectas)]

        for value in totales:
            ctk.CTkLabel(
                total_frame,
                text=value,
                font=("Arial", 14, "bold"),
                text_color="#333333",
                width=150
            ).pack(side="left", padx=10, pady=15, expand=True)

    def _crear_botones_finales_modernos(self, parent):
        """Crea los botones de la pantalla final (versión moderna)"""
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(pady=30)

        botones = [
            ("📝 VER RESPUESTAS", Config.COLOR_INFO, self.mostrar_ventana_respuestas),
            ("🖨️ IMPRIMIR RESULTADOS", Config.COLOR_PRIMARY, self.imprimir_resultados),
            ("🔄 NUEVO TEST", Config.COLOR_SUCCESS, self.reiniciar_aplicativo),
            ("❌ CERRAR", Config.COLOR_DANGER, self.root.quit)
        ]

        for texto, color, comando in botones:
            ctk.CTkButton(
                buttons_frame,
                text=texto,
                font=("Arial", 16, "bold"),
                width=200,
                height=50,
                corner_radius=15,
                fg_color=color,
                hover_color=self._oscurecer_color(color),
                command=comando
            ).pack(side="left", padx=10)

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

        if not nombre or curso == "Selecciona tu curso":
            messagebox.showwarning("⚠️ Faltan datos", "Por favor completa tu nombre y selecciona tu curso.")
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
        emoji_op = self.obtener_emoji_operacion(self.operacion_actual)
        tabla_minima = self.obtener_tabla_minima(self.operacion_actual)
        color_nivel = self.obtener_color_nivel(self.nivel)

        # Crear ventana de diálogo moderna
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"{nombre_op}")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Frame principal
        main_frame = ctk.CTkFrame(
            dialog,
            fg_color="white",
            corner_radius=20
        )
        main_frame.pack(padx=40, pady=40, fill="both", expand=True)

        # Título con emoji
        ctk.CTkLabel(
            main_frame,
            text=emoji_op,
            font=("Arial", 50)
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            main_frame,
            text=f"{nombre_op}",
            font=("Arial", 26, "bold"),
            text_color=color_nivel
        ).pack()

        # Instrucción
        texto_instruccion = "¿Hasta qué tabla quieres practicar?"
        if tabla_minima == 2:
            texto_instruccion += "\n(Esta operación comienza desde la tabla 2)"

        ctk.CTkLabel(
            main_frame,
            text=texto_instruccion,
            font=("Arial", 16),
            text_color="#666666",
            justify="center"
        ).pack(pady=(15, 25))

        # Frame para el slider
        slider_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=15)
        slider_frame.pack(fill="x", padx=30, pady=10)

        # Label para mostrar el valor actual
        valor_label = ctk.CTkLabel(
            slider_frame,
            text=f"Tabla {tabla_minima}",
            font=("Arial", 36, "bold"),
            text_color=color_nivel
        )
        valor_label.pack(pady=(20, 10))

        # Slider para seleccionar la tabla
        def actualizar_valor(value):
            valor_label.configure(text=f"Tabla {int(value)}")

        slider = ctk.CTkSlider(
            slider_frame,
            from_=tabla_minima,
            to=12,
            number_of_steps=12-tabla_minima,
            width=300,
            height=20,
            button_color=color_nivel,
            button_hover_color=self._oscurecer_color(color_nivel),
            progress_color=color_nivel,
            command=actualizar_valor
        )
        slider.set(tabla_minima)
        slider.pack(pady=(0, 20), padx=20)

        resultado = {"confirmado": False}

        def confirmar():
            resultado["confirmado"] = True
            resultado["valor"] = int(slider.get())
            dialog.destroy()

        def cancelar():
            resultado["confirmado"] = False
            dialog.destroy()

        # Botones
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(25, 15))

        ctk.CTkButton(
            buttons_frame,
            text="✓ ACEPTAR",
            font=("Arial", 18, "bold"),
            width=150,
            height=50,
            corner_radius=15,
            fg_color=Config.COLOR_SUCCESS,
            hover_color=self._oscurecer_color(Config.COLOR_SUCCESS),
            command=confirmar
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            buttons_frame,
            text="✗ CANCELAR",
            font=("Arial", 18, "bold"),
            width=150,
            height=50,
            corner_radius=15,
            fg_color=Config.COLOR_DANGER,
            hover_color=self._oscurecer_color(Config.COLOR_DANGER),
            command=cancelar
        ).pack(side="left", padx=10)

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
        """Genera ejercicios según la operación y tabla actual"""
        ejercicios = []
        tabla = self.tabla_actual
        numeros = list(range(0, 13))  # [0, 1, 2, ..., 12] - para operaciones que usan todos

        # Generar ejercicios según el tipo de operación
        if operacion == "resta":
            # Para resta: solo números de 0 hasta tabla (tabla + 1 ejercicios)
            # Ejemplo: Tabla 3 -> 3-0, 3-1, 3-2, 3-3 (4 ejercicios)
            numeros_validos = list(range(0, tabla + 1))  # [0, 1, ..., tabla]

            for num in numeros_validos:
                ejercicio = {
                    "texto": f"{tabla} - {num} =",
                    "respuesta": tabla - num
                }
                ejercicios.append(ejercicio)

        elif operacion == "división":
            # Para división: siempre 13 ejercicios (números del 0 al 12)
            # El número de la tabla va en SEGUNDO lugar (denominador)
            # Ejemplo Tabla 2: 0÷2=0, 2÷2=1, 4÷2=2, ..., 24÷2=12
            for num in numeros:  # num va de 0 a 12
                dividendo = tabla * num  # Así el resultado es num
                ejercicio = {
                    "texto": f"{dividendo} ÷ {tabla} =",
                    "respuesta": num
                }
                ejercicios.append(ejercicio)
        else:
            # Para suma, multiplicación, potencia y raíz: usar todos los números del 0 al 12
            for num in numeros:
                ejercicio = self._generar_ejercicio_por_tipo(operacion, tabla, num)
                if ejercicio:
                    ejercicios.append(ejercicio)

        # Mezclar ejercicios de forma aleatoria
        random.shuffle(ejercicios)

        # Reasignar IDs después de mezclar
        for idx, ej in enumerate(ejercicios):
            ej["id"] = idx

        return ejercicios

    def _generar_ejercicio_por_tipo(self, operacion, tabla, num):
        """Genera un ejercicio individual según el tipo de operación con un número específico"""
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
            return generador(tabla, num)
        return None

    def _generar_suma(self, tabla, num):
        """Genera un ejercicio de suma"""
        # La suma siempre inicia con el número de la tabla
        a = tabla
        b = num  # Usar el número proporcionado (0 a 12)

        return {
            "texto": f"{a} + {b} =",
            "respuesta": a + b
        }

    def _generar_resta(self, tabla, num):
        """Genera un ejercicio de resta"""
        # La resta siempre es tabla - num para evitar negativos
        # Esto ya está manejado en generar_ejercicios()
        # Este método no debería ser llamado directamente para resta
        return {
            "texto": f"{tabla} - {num} =",
            "respuesta": tabla - num
        }

    def _generar_multiplicacion(self, tabla, num):
        """Genera un ejercicio de multiplicación"""
        # La multiplicación siempre inicia con el número de la tabla
        a = tabla
        b = num  # Usar el número proporcionado (0 a 12)

        return {
            "texto": f"{a} × {b} =",
            "respuesta": a * b
        }

    def _generar_division(self, tabla, num):
        """Genera un ejercicio de división"""
        # La división siempre es (tabla × num) ÷ tabla = num
        # Esto ya está manejado en generar_ejercicios()
        # Este método no debería ser llamado directamente para división
        a = tabla * num
        return {
            "texto": f"{a} ÷ {tabla} =",
            "respuesta": num
        }

    def _generar_potencia(self, tabla, num):
        """Genera un ejercicio de potenciación"""
        # La base es el número de la tabla (siempre el primer dígito)
        base = tabla
        # El exponente es el número proporcionado (0 a 12)
        exp = num

        return {
            "texto": f"{base}^{exp} =",
            "respuesta": base ** exp
        }

    def _generar_raiz(self, tabla, num):
        """Genera un ejercicio de radicación"""
        # El índice de la raíz es el número de la tabla actual
        indice_raiz = tabla
        # El resultado será num (de 0 a 12)
        # Por lo tanto, el radicando es num^indice_raiz

        radicando = num ** indice_raiz
        respuesta = num

        # Mostrar según el índice de la raíz
        if indice_raiz == 2:
            texto = f"√{radicando} ="  # Raíz cuadrada (común)
        elif indice_raiz == 3:
            texto = f"∛{radicando} ="  # Raíz cúbica
        else:
            # Para índices mayores, usar notación con superíndice
            texto = f"ⁿ√{radicando} =".replace("ⁿ", str(indice_raiz))  # Raíz n-ésima

        return {
            "texto": texto,
            "respuesta": respuesta
        }

    # ==================== CONTROL DE TIEMPO ====================

    def iniciar_cronometro(self):
        """Inicia el cronómetro y habilita los campos de respuesta"""
        if self.finalizado:
            messagebox.showinfo(
                "⚠️ Ya finalizado",
                "Esta operación ya fue finalizada. No puede volver a iniciar."
            )
            return

        if not self.corriendo:
            # Ajustar tiempo_inicio para que el tiempo continúe desde donde se quedó
            self.tiempo_inicio = datetime.now() - timedelta(seconds=self.tiempo_total)
            self.corriendo = True

            for entry in self.entries.values():
                entry.configure(state="normal")

            # Bloquear el botón INICIAR después de presionarlo
            if self.boton_iniciar:
                self.boton_iniciar.configure(
                    state="disabled",
                    fg_color="#CCCCCC",
                    text_color="#666666"
                )

            # Habilitar el botón FINALIZAR con estilo activo
            if self.boton_finalizar:
                self.boton_finalizar.configure(
                    state="normal",
                    fg_color=Config.COLOR_PRIMARY,
                    hover_color=self._oscurecer_color(Config.COLOR_PRIMARY),
                    text_color="white"
                )

            self.actualizar_cronometro()

    def detener_cronometro(self):
        """Detiene el cronómetro y guarda el tiempo acumulado"""
        if self.corriendo:
            self.tiempo_total = (datetime.now() - self.tiempo_inicio).total_seconds()
            self.corriendo = False

    def actualizar_cronometro(self):
        """Actualiza el cronómetro cada segundo"""
        if not self.corriendo:
            return

        elapsed = (datetime.now() - self.tiempo_inicio).total_seconds()
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
        self.label_tiempo.configure(
            text=f"{mins:02d}:{secs:02d}",
            text_color=Config.COLOR_TIMER_NORMAL
        )

    def _mostrar_tiempo_con_penalizacion(self, mins, secs):
        """Muestra el tiempo cuando hay penalización"""
        self.label_tiempo.configure(
            text=f"{mins:02d}:{secs:02d}",
            text_color=Config.COLOR_TIMER_WARNING
        )
        self.root.after(1000, self.actualizar_cronometro)

    def _manejar_tiempo_agotado(self, mins, secs):
        """Maneja el caso cuando se agota el tiempo máximo"""
        self.label_tiempo.configure(
            text=f"{mins:02d}:{secs:02d}",
            text_color=Config.COLOR_TIMER_DANGER
        )
        self.detener_cronometro()

        messagebox.showwarning(
            "⏰ Tiempo agotado",
            f"Has excedido el tiempo máximo de {int(self.tiempo_maximo//60)} minutos.\n"
            "La operación se finalizará automáticamente."
        )
        self.finalizar_operacion()

    # ==================== FINALIZACIÓN Y NAVEGACIÓN ====================

    def finalizar_operacion(self):
        """Finaliza la operación actual y calcula los resultados"""
        if self.finalizado:
            messagebox.showinfo("⚠️ Ya finalizado", "Esta operación ya fue finalizada.")
            return

        if self.tiempo_total == 0 and not self.corriendo:
            messagebox.showwarning("⚠️ Error", "Primero debe presionar INICIAR")
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
            entry.configure(state="disabled")

        if self.boton_finalizar:
            self.boton_finalizar.configure(state="disabled")

        if self.boton_iniciar:
            self.boton_iniciar.configure(state="disabled")

    def _guardar_resultado(self, correctas, incorrectas):
        """Guarda el resultado de la operación actual"""
        clave = f"{self.operacion_actual}_tabla{self.tabla_actual}"
        total_ejercicios = len(self.ejercicios)  # Usar el total real de ejercicios generados
        self.resultados_operacion[clave] = {
            "operacion": self.operacion_actual,
            "tabla": self.tabla_actual,
            "correctas": correctas,
            "incorrectas": incorrectas,
            "total": total_ejercicios,
            "tiempo": self.tiempo_total
        }

        # Guardar los ejercicios con las respuestas del usuario
        for ej in self.ejercicios:
            respuesta_usuario = self.entries[ej["id"]].get().strip()
            self.historial_ejercicios.append({
                "operacion": self.operacion_actual,
                "tabla": self.tabla_actual,
                "ejercicio": ej["texto"],
                "respuesta_correcta": ej["respuesta"],
                "respuesta_usuario": respuesta_usuario,
                "correcto": respuesta_usuario == str(ej["respuesta"])
            })

    def _mostrar_mensaje_finalizacion(self, correctas):
        """Muestra mensaje informativo al finalizar una operación"""
        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)
        total_ejercicios = len(self.ejercicios)

        # Emoji según el desempeño
        porcentaje = (correctas / total_ejercicios) * 100
        emoji = "🌟" if porcentaje >= 90 else "👍" if porcentaje >= 70 else "💪"

        messagebox.showinfo(
            f"{emoji} ¡Operación Completada!",
            f"{nombre_op} - TABLA DEL {self.tabla_actual}\n\n"
            f"Aciertos: {correctas}/{total_ejercicios}\n"
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

        # Si no se ha guardado, guardar los resultados actuales antes de avanzar
        if clave_actual not in self.resultados_operacion:
            if not messagebox.askyesno(
                "⚠️ Advertencia",
                "¿Pasar a la siguiente tabla sin guardar esta?"
            ):
                return

            # Detener el cronómetro si está corriendo
            if self.corriendo:
                self.detener_cronometro()

            # Guardar resultados de la tabla actual (aunque esté sin finalizar)
            correctas, incorrectas = self._evaluar_respuestas()
            self._guardar_resultado(correctas, incorrectas)
            self.finalizado = True

        if self.tabla_actual < self.tabla_max:
            self.tabla_actual += 1
            self.mostrar_pantalla_ejercicios()
        else:
            self.mostrar_resumen_operacion_completa()

    def mostrar_resumen_operacion_completa(self):
        """Muestra el resumen de todas las tablas de la operación actual"""
        correctas_total, tiempo_total_op, total_preguntas = self._calcular_totales_operacion()

        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)
        emoji_op = self.obtener_emoji_operacion(self.operacion_actual)

        mensaje = f"{emoji_op} RESUMEN DE {nombre_op.upper()}\n\n"
        mensaje += f"Total de aciertos: {correctas_total}/{total_preguntas}\n"
        mensaje += f"Tiempo total: {int(tiempo_total_op//60):02d}:{int(tiempo_total_op%60):02d}\n\n"

        idx_actual = self.operaciones_nivel.index(self.operacion_actual)

        if idx_actual + 1 < len(self.operaciones_nivel):
            siguiente_op = self.operaciones_nivel[idx_actual + 1]
            nombre_siguiente = self.obtener_nombre_operacion(siguiente_op)
            mensaje += f"Presione ACEPTAR para continuar con {nombre_siguiente}"

            messagebox.showinfo("✅ Operación Completada", mensaje)

            self.operacion_actual = siguiente_op
            # Usar la tabla mínima de la nueva operación
            self.tabla_actual = self.obtener_tabla_minima(siguiente_op)
            self.solicitar_limite_tabla_operacion()
        else:
            mensaje += "¡Ha completado todas las operaciones!"
            messagebox.showinfo("🎉 Test Completado", mensaje)
            self.mostrar_resultados_finales()

    def _calcular_totales_operacion(self):
        """Calcula los totales de la operación actual"""
        correctas_total = 0
        tiempo_total_op = 0
        total_preguntas = 0

        for clave, r in self.resultados_operacion.items():
            if r["operacion"] == self.operacion_actual:
                correctas_total += r["correctas"]
                tiempo_total_op += r["tiempo"]
                total_preguntas += r["total"]

        return correctas_total, tiempo_total_op, total_preguntas

    # ==================== RESULTADOS ====================

    def mostrar_resultados_operacion(self):
        """Muestra los resultados parciales hasta el momento"""
        if not self.resultados_operacion:
            messagebox.showinfo("📊 Sin datos", "Aún no has completado operaciones.")
            return

        texto = "📊 RESULTADOS HASTA AHORA\n\n"
        total_ac = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_pr = sum(r["total"] for r in self.resultados_operacion.values())

        for clave, r in sorted(self.resultados_operacion.items()):
            op = r["operacion"]
            emoji = self.obtener_emoji_operacion(op)
            tabla = r["tabla"]
            mins = int(r["tiempo"] // 60)
            secs = int(r["tiempo"] % 60)
            texto += f"{emoji} {op.upper()} - Tabla {tabla}: {r['correctas']}/{r['total']}  |  {mins:02d}:{secs:02d}\n"

        texto += f"\nTOTAL: {total_ac}/{total_pr}"
        messagebox.showinfo("📊 Resultados Parciales", texto)

    def calcular_nota_final(self):
        """Calcula la nota final con penalización por tiempo"""
        total_aciertos = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_preguntas = sum(r["total"] for r in self.resultados_operacion.values())

        nota = (total_aciertos / total_preguntas) * 100 if total_preguntas > 0 else 0

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

    # ==================== VER RESPUESTAS ====================

    def mostrar_ventana_respuestas(self):
        """Muestra una ventana con todos los ejercicios y respuestas del usuario"""
        if not self.historial_ejercicios:
            messagebox.showinfo("📝 Sin datos", "No hay ejercicios realizados.")
            return

        # Crear ventana emergente
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Ejercicios Realizados")
        ventana.geometry("1100x750")

        # Centrar ventana
        ventana.update_idletasks()
        width = ventana.winfo_width()
        height = ventana.winfo_height()
        x = (ventana.winfo_screenwidth() // 2) - (width // 2)
        y = (ventana.winfo_screenheight() // 2) - (height // 2)
        ventana.geometry(f"{width}x{height}+{x}+{y}")

        # Frame principal con scrollbar
        main_frame = ctk.CTkScrollableFrame(
            ventana,
            fg_color="white"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Encabezado
        ctk.CTkLabel(
            main_frame,
            text="📝 EJERCICIOS REALIZADOS",
            font=("Arial", 28, "bold"),
            text_color=Config.COLOR_PRIMARY
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            main_frame,
            text=f"{self.nombre} - {self.curso}",
            font=("Arial", 16),
            text_color="#666666"
        ).pack()

        ctk.CTkLabel(
            main_frame,
            text=f"📅 {self.fecha}",
            font=("Arial", 14),
            text_color="#888888"
        ).pack(pady=(0, 20))

        # Separador
        ctk.CTkFrame(
            main_frame,
            height=3,
            fg_color=Config.COLOR_PRIMARY
        ).pack(fill="x", pady=15, padx=50)

        # Agrupar ejercicios por operación
        ejercicios_por_operacion = {}
        orden_operaciones = []

        for ej in self.historial_ejercicios:
            clave = f"{ej['operacion']}_tabla{ej['tabla']}"
            if clave not in ejercicios_por_operacion:
                ejercicios_por_operacion[clave] = {
                    "operacion": ej["operacion"],
                    "tabla": ej["tabla"],
                    "ejercicios": []
                }
                orden_operaciones.append(clave)
            ejercicios_por_operacion[clave]["ejercicios"].append(ej)

        # Mostrar ejercicios
        for clave in orden_operaciones:
            grupo = ejercicios_por_operacion[clave]
            nombre_op = self.obtener_nombre_operacion(grupo["operacion"])
            emoji_op = self.obtener_emoji_operacion(grupo["operacion"])

            # Encabezado de sección
            header_frame = ctk.CTkFrame(
                main_frame,
                fg_color="#E8F5E9",
                corner_radius=10
            )
            header_frame.pack(fill="x", pady=(15, 10))

            ctk.CTkLabel(
                header_frame,
                text=f"{emoji_op} {nombre_op} - Tabla {grupo['tabla']}",
                font=("Arial", 18, "bold"),
                text_color="#333333"
            ).pack(pady=12, padx=15, anchor="w")

            # Tabla de ejercicios
            self._crear_tabla_ejercicios_ventana(main_frame, grupo["ejercicios"])

        # Separador final
        ctk.CTkFrame(
            main_frame,
            height=3,
            fg_color=Config.COLOR_PRIMARY
        ).pack(fill="x", pady=20, padx=50)

        # Botones
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(pady=20)

        ctk.CTkButton(
            botones_frame,
            text="🖨️ IMPRIMIR",
            font=("Arial", 16, "bold"),
            width=180,
            height=50,
            corner_radius=15,
            fg_color=Config.COLOR_PRIMARY,
            hover_color=self._oscurecer_color(Config.COLOR_PRIMARY),
            command=self.imprimir_ejercicios
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            botones_frame,
            text="✗ CERRAR",
            font=("Arial", 16, "bold"),
            width=180,
            height=50,
            corner_radius=15,
            fg_color=Config.COLOR_DANGER,
            hover_color=self._oscurecer_color(Config.COLOR_DANGER),
            command=ventana.destroy
        ).pack(side="left", padx=10)

    def _crear_tabla_ejercicios_ventana(self, parent, ejercicios):
        """Crea una tabla de ejercicios en la ventana de respuestas"""
        from tkinter import Frame, Label

        table_frame = Frame(parent, bg="white")
        table_frame.pack(fill="x", padx=20, pady=5)

        # Encabezados
        headers = ["#", "Ejercicio", "Tu respuesta", "Correcta", "Estado"]
        col_widths = [40, 200, 120, 120, 120]

        for col, (header, width) in enumerate(zip(headers, col_widths)):
            Label(
                table_frame,
                text=header,
                font=("Arial", 11, "bold"),
                bg=Config.COLOR_PRIMARY,
                fg="white",
                width=width//8,
                relief="solid",
                bd=1,
                padx=8,
                pady=6
            ).grid(row=0, column=col, sticky="ew")

        # Filas de ejercicios
        for idx, ejercicio in enumerate(ejercicios, 1):
            bg_color = "#F8F9FA" if idx % 2 == 0 else "white"

            # Determinar estado
            if ejercicio["correcto"]:
                estado = "✓ Correcto"
                color_estado = Config.COLOR_SUCCESS
            else:
                estado = "✗ Incorrecto"
                color_estado = Config.COLOR_DANGER

            # Preparar respuesta usuario
            resp_usuario = ejercicio["respuesta_usuario"] if ejercicio["respuesta_usuario"] else "(vacío)"

            datos = [
                str(idx),
                ejercicio["ejercicio"],
                resp_usuario,
                str(ejercicio["respuesta_correcta"]),
                estado
            ]

            for col, (valor, width) in enumerate(zip(datos, col_widths)):
                fg_color = color_estado if col == 4 else "#333"
                font_weight = "bold" if col == 4 else "normal"

                Label(
                    table_frame,
                    text=valor,
                    font=("Arial", 10, font_weight),
                    bg=bg_color,
                    fg=fg_color,
                    width=width//8,
                    relief="solid",
                    bd=1,
                    padx=8,
                    pady=5
                ).grid(row=idx, column=col, sticky="ew")

    # ==================== IMPRESIÓN ====================

    def imprimir_ejercicios(self):
        """Genera e imprime un reporte HTML con todos los ejercicios realizados"""
        if not self.historial_ejercicios:
            messagebox.showinfo("📝 Sin datos", "No hay ejercicios realizados.")
            return

        html_content = self._generar_html_ejercicios()

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.html',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(html_content)
            temp_file = f.name

        self._abrir_archivo_en_navegador(temp_file)

    def _generar_html_ejercicios(self):
        """Genera el contenido HTML para los ejercicios realizados"""
        # Agrupar ejercicios por operación manteniendo el orden cronológico
        ejercicios_por_operacion = {}
        orden_operaciones = []

        for ej in self.historial_ejercicios:
            clave = f"{ej['operacion']}_tabla{ej['tabla']}"
            if clave not in ejercicios_por_operacion:
                ejercicios_por_operacion[clave] = {
                    "operacion": ej["operacion"],
                    "tabla": ej["tabla"],
                    "ejercicios": []
                }
                orden_operaciones.append(clave)
            ejercicios_por_operacion[clave]["ejercicios"].append(ej)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ejercicios Realizados - Agilidad Mental</title>
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
        .seccion {{
            margin-top: 30px;
            page-break-inside: avoid;
        }}
        .seccion-header {{
            background-color: #e8f5e9;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
            border: 1px solid #ddd;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th {{
            background-color: {Config.COLOR_PRIMARY};
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: bold;
            font-size: 12px;
        }}
        td {{
            padding: 8px;
            border: 1px solid #ddd;
            font-size: 12px;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .correcto {{
            color: {Config.COLOR_SUCCESS};
            font-weight: bold;
        }}
        .incorrecto {{
            color: {Config.COLOR_DANGER};
            font-weight: bold;
        }}
        hr {{
            border: none;
            border-top: 2px solid {Config.COLOR_PRIMARY};
            margin: 30px 0;
        }}
        @media print {{
            body {{ margin: 20px; }}
            .seccion {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <h1>EJERCICIOS REALIZADOS - TEST DE AGILIDAD MENTAL</h1>
    <div class="info">
        <p><strong>Estudiante:</strong> {self.nombre}</p>
        <p><strong>Curso:</strong> {self.curso}</p>
        <p><strong>Fecha:</strong> {self.fecha}</p>
    </div>
    <hr>
"""

        # Generar secciones en orden cronológico
        for clave in orden_operaciones:
            grupo = ejercicios_por_operacion[clave]
            nombre_op = self.obtener_nombre_operacion(grupo["operacion"])

            html += f"""
    <div class="seccion">
        <div class="seccion-header">{nombre_op} - Tabla {grupo['tabla']}</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 30%;">Ejercicio</th>
                    <th style="width: 20%;">Tu respuesta</th>
                    <th style="width: 25%;">Respuesta correcta</th>
                    <th style="width: 20%;">Estado</th>
                </tr>
            </thead>
            <tbody>
"""

            for idx, ejercicio in enumerate(grupo["ejercicios"], 1):
                estado_class = "correcto" if ejercicio["correcto"] else "incorrecto"
                estado_text = "Correcto" if ejercicio["correcto"] else "Incorrecto"
                resp_usuario = ejercicio["respuesta_usuario"] if ejercicio["respuesta_usuario"] else "(sin respuesta)"

                html += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{ejercicio['ejercicio']}</td>
                    <td>{resp_usuario}</td>
                    <td>{ejercicio['respuesta_correcta']}</td>
                    <td class="{estado_class}">{estado_text}</td>
                </tr>
"""

            html += """
            </tbody>
        </table>
    </div>
"""

        html += """
</body>
</html>"""

        return html

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
                "🖨️ Imprimir",
                "Se abrió el reporte en su navegador.\nUse Ctrl+P para imprimir."
            )
        except Exception as e:
            messagebox.showerror(
                "❌ Error",
                f"No se pudo abrir el archivo para imprimir: {e}"
            )


# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    root = ctk.CTk()
    app = AgilidadMentalApp(root)
    root.mainloop()
