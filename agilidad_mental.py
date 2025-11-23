import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
import random
import os
import sys
import tempfile
import subprocess
import platform

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from tkcalendar import DateEntry, Calendar
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False


# ==================== FUNCIÓN PARA RUTAS DE RECURSOS ====================
def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, funciona para dev y para PyInstaller"""
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ==================== CONFIGURACIÓN Y CONSTANTES ====================
class Config:
    """Configuración y constantes del programa - Diseño para niños"""

    # Dimensiones
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700

    # Paleta de colores vibrantes para niños
    COLOR_BG_GRADIENT_1 = "#E3F2FD"  # Azul muy claro
    COLOR_BG_GRADIENT_2 = "#F3E5F5"  # Púrpura muy claro

    # Colores principales brillantes
    COLOR_VERDE_BRILLANTE = "#4CAF50"
    COLOR_AZUL_BRILLANTE = "#2196F3"
    COLOR_NARANJA_BRILLANTE = "#FF9800"
    COLOR_ROSA_BRILLANTE = "#E91E63"
    COLOR_MORADO_BRILLANTE = "#9C27B0"
    COLOR_AMARILLO_BRILLANTE = "#FFC107"
    COLOR_ROJO_BRILLANTE = "#F44336"
    COLOR_CYAN_BRILLANTE = "#00BCD4"

    # Colores específicos por nivel
    COLOR_NIVEL_1 = "#4CAF50"  # Verde
    COLOR_NIVEL_2 = "#FF9800"  # Naranja
    COLOR_NIVEL_3 = "#E91E63"  # Rosa

    # Colores suaves para cada operación (independientes del nivel)
    COLOR_SUMA = "#87CEEB"  # Azul suave (Sky Blue)
    COLOR_RESTA = "#90EE90"  # Verde suave (Light Green)
    COLOR_MULTIPLICACION = "#DDA0DD"  # Púrpura suave (Plum)
    COLOR_DIVISION = "#FFB6C1"  # Rosa suave (Light Pink)
    COLOR_POTENCIA = "#B0C4DE"  # Azul grisáceo suave (Light Steel Blue)
    COLOR_RAIZ = "#FF8355"  # Amarillo suave (Khaki)

    COLOR_SUCCESS = "#4CAF50"
    COLOR_DANGER = "#F44336"
    COLOR_INFO = "#2196F3"

    # Fuentes grandes y claras para niños
    FONT_TITLE = ("Comic Sans MS", 36, "bold")
    FONT_SUBTITLE = ("Comic Sans MS", 24, "bold")
    FONT_NORMAL = ("Comic Sans MS", 18)
    FONT_BUTTON = ("Comic Sans MS", 20, "bold")
    FONT_SMALL = ("Comic Sans MS", 14)

    # Tiempos por nivel
    NIVEL_1_TIEMPO_PRINCIPAL = 12 * 60
    NIVEL_1_TIEMPO_MAXIMO = 15 * 60
    NIVEL_2_TIEMPO_PRINCIPAL = 10 * 60
    NIVEL_2_TIEMPO_MAXIMO = 12 * 60
    NIVEL_3_TIEMPO_PRINCIPAL = 10 * 60
    NIVEL_3_TIEMPO_MAXIMO = 12 * 60

    # Tiempos especiales para potenciación y radicación
    POTENCIA_RAIZ_TIEMPO_PRINCIPAL = 3 * 60
    POTENCIA_RAIZ_TIEMPO_MAXIMO = 5 * 60

    # Ejercicios y penalización
    EJERCICIOS_POR_TABLA = 13
    MAX_INTENTOS_GENERACION = 1000
    PENALIZACION_POR_MINUTO = 1  # 1 punto por cada minuto extra
    PENALIZACION_MAXIMA = 3  # Máximo 3 puntos (3 minutos extra)

    # Operaciones
    NOMBRES_OPERACIONES = {
        "suma": "Suma",
        "resta": "Resta",
        "multiplicación": "Multiplicación",
        "división": "División",
        "potencia": "Potenciación",
        "raiz": "Radicación"
    }

    EMOJIS_OPERACIONES = {
        "suma": "➕",
        "resta": "➖",
        "multiplicación": "✖️",
        "división": "➗",
        "potencia": "🔼",
        "raiz": "✔️"
    }

    # Cursos
    CURSOS = [
        "Segundo", "Tercero", "Cuarto", "Quinto",
        "Sexto", "Séptimo", "Octavo", "Noveno",
        "Décimo", "Primero BGU", "Segundo BGU", "Tercero BGU"
    ]


# ==================== APLICACIÓN PRINCIPAL ====================
class AgilidadMentalApp:
  

    def __init__(self, root):
        self.root = root
        self._configurar_ventana()
        self._inicializar_variables()
        self.mostrar_pantalla_inicio()

    def _configurar_ventana(self):
        """Configura la ventana principal"""
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root.title("Agilidad RMmath")

        # Obtener dimensiones de pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calcular tamaño de ventana (80% de la pantalla, pero no más que los valores configurados)
        window_width = min(Config.WINDOW_WIDTH, int(screen_width * 0.8))
        window_height = min(Config.WINDOW_HEIGHT, int(screen_height * 0.85))

        # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg="#E3F2FD")

        # Configurar tamaño mínimo
        self.root.minsize(900, 600)

        # Asegurar que la ventana sea redimensionable y tenga botones de control
        self.root.resizable(True, True)
        self.root.attributes('-topmost', False)

    def _inicializar_variables(self):
        """Inicializa variables del programa"""
        self.nivel = None
        self.nombre = ""
        self.curso = ""
        self.fecha = datetime.now().strftime("%d/%m/%Y")
        self.tabla_max = 10
        self.tabla_actual = 1
        self.limites_tablas = {}
        self.tiempo_inicio = None
        self.tiempo_operacion_actual = 0  # Tiempo de la operación actual
        self.tiempo_principal_operacion = 0  # Tiempo principal por operación (12 o 10 min)
        self.tiempo_maximo_operacion = 0  # Tiempo máximo por operación (15 o 12 min)
        self.corriendo = False
        self.finalizado = False
        self.test_finalizado_automaticamente = False  # Nuevo: para saber si finalizó por tiempo
        self.resultados_operacion = {}
        self.operaciones_nivel = []
        self.operacion_actual = ""
        self.ejercicios = []
        self.historial_ejercicios = []
        self.entries = {}
        self.boton_finalizar = None
        self.boton_iniciar = None
        self.label_tiempo = None
        self.cronometro_frame = None  # Nuevo: para cambiar el color del cronómetro
        self.en_tiempo_extra = False  # Nuevo: para saber si está en tiempo extra

    def validar_numero(self, valor):
        """Valida entrada numérica"""
        if valor == "" or valor == "-":
            return True
        try:
            int(valor)
            return True
        except ValueError:
            return False

    def validar_nombre(self, valor):
        """Valida que el nombre no exceda 50 caracteres y no contenga números"""
        if len(valor) > 50:
            return False
        # Permitir vacío, espacios y letras, pero no números
        if valor == "":
            return True
        # Rechazar si contiene dígitos
        if any(char.isdigit() for char in valor):
            return False
        return True

    def _crear_imagen_circular(self, image, size):
        """Convierte una imagen en circular"""
        # Redimensionar la imagen
        image = image.resize((size, size), Image.Resampling.LANCZOS)

        # Crear una máscara circular
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)

        # Convertir imagen a RGBA si no lo está
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Aplicar la máscara circular
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(image, (0, 0))
        output.putalpha(mask)

        return output

    def limpiar_pantalla(self):
        """Limpia todos los widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def obtener_nombre_operacion(self, operacion):
        """Retorna nombre de operación"""
        return Config.NOMBRES_OPERACIONES.get(operacion, operacion.upper())

    def obtener_emoji_operacion(self, operacion):
        """Retorna emoji de operación"""
        return Config.EMOJIS_OPERACIONES.get(operacion, "📝")

    def obtener_tabla_minima(self, operacion):
        """Retorna tabla mínima por operación"""
        return 2 if operacion in ["multiplicación", "división", "potencia", "raiz"] else 1

    def obtener_color_nivel(self, nivel):
        """Retorna color por nivel"""
        colores = {1: Config.COLOR_NIVEL_1, 2: Config.COLOR_NIVEL_2, 3: Config.COLOR_NIVEL_3}
        return colores.get(nivel, Config.COLOR_VERDE_BRILLANTE)

    def obtener_color_operacion(self, operacion):
        """Retorna color suave por operación"""
        colores = {
            "suma": Config.COLOR_SUMA,
            "resta": Config.COLOR_RESTA,
            "multiplicación": Config.COLOR_MULTIPLICACION,
            "división": Config.COLOR_DIVISION,
            "potencia": Config.COLOR_POTENCIA,
            "raiz": Config.COLOR_RAIZ
        }
        return colores.get(operacion, Config.COLOR_AZUL_BRILLANTE)

    # ==================== PANTALLA DE INICIO ====================
    def mostrar_pantalla_inicio(self):
        """Pantalla inicial super colorida y divertida"""
        self.limpiar_pantalla()

        # Contenedor principal con gradiente
        main_container = ctk.CTkFrame(self.root, fg_color="#E3F2FD", corner_radius=0)
        main_container.pack(fill="both", expand=True)

        # ENCABEZADO GRANDE Y COLORIDO
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20, 5))

        # Logo circular en la parte superior
        try:
            logo_path = resource_path("logo.jpg")
            if os.path.exists(logo_path) and PIL_AVAILABLE:
                logo_img = Image.open(logo_path)
                # Convertir el logo en circular
                logo_circular = self._crear_imagen_circular(logo_img, 120)
                # Usar CTkImage para evitar warnings y tener mejor escalado en HighDPI
                ctk_logo = ctk.CTkImage(light_image=logo_circular, dark_image=logo_circular, size=(120, 120))

                logo_label = ctk.CTkLabel(header_frame, image=ctk_logo, text="")
                logo_label.pack(pady=(0, 10))
        except Exception as e:
            print(f"No se pudo cargar el logo en pantalla de inicio: {e}")

        # Título principal con estilo infantil
        title_label = ctk.CTkLabel(
            header_frame,
            text="🌟 Agilidad RMmath! 🌟",
            font=("Comic Sans MS", 40, "bold"),
            text_color=Config.COLOR_AZUL_BRILLANTE
        )
        title_label.pack(pady=(0, 10))

        # Mensaje motivador
        mensaje_label = ctk.CTkLabel(
            header_frame,
            text="¡Elige tu nivel y demuestra lo que sabes! 💪🧠",
            font=("Comic Sans MS", 14, "bold"),
            text_color=Config.COLOR_MORADO_BRILLANTE
        )
        mensaje_label.pack(pady=(5, 0))

        # CONTENEDOR DE BOTONES DE NIVEL
        niveles_container = ctk.CTkFrame(main_container, fg_color="transparent")
        niveles_container.pack(expand=True, fill="both", pady=10, padx=20)

        # Configurar grid para distribución equitativa
        niveles_container.grid_rowconfigure(0, weight=1)
        niveles_container.grid_rowconfigure(1, weight=1)
        niveles_container.grid_rowconfigure(2, weight=1)
        niveles_container.grid_columnconfigure(0, weight=1)

        # NIVEL 1 - VERDE
        self._crear_boton_nivel_grande(
            niveles_container,
            row=0,
            nivel=1,
            titulo="🌟 NIVEL 1 🌟",
            descripcion="Suma y Resta",
            detalle="¡Perfecto para empezar!",
            color=Config.COLOR_VERDE_BRILLANTE,
            emoji="🟢"
        )

        # NIVEL 2 - NARANJA
        self._crear_boton_nivel_grande(
            niveles_container,
            row=1,
            nivel=2,
            titulo="⭐ NIVEL 2 ⭐",
            descripcion="Suma, Resta, Multiplicación y División",
            detalle="¡Un reto intermedio!",
            color=Config.COLOR_NARANJA_BRILLANTE,
            emoji="🟠"
        )

        # NIVEL 3 - ROSA
        self._crear_boton_nivel_grande(
            niveles_container,
            row=2,
            nivel=3,
            titulo="✨ NIVEL 3 ✨",
            descripcion="Todas las operaciones + Potencia y Raíz",
            detalle="¡Para verdaderos campeones!",
            color=Config.COLOR_ROSA_BRILLANTE,
            emoji="🔴"
        )

        # Footer decorativo
        footer_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom", pady=10)

        footer_label = ctk.CTkLabel(
            footer_frame,
            text="🎯 ¡Diviértete mientras aprendes! 🎯",
            font=("Comic Sans MS", 14, "bold"),
            text_color=Config.COLOR_CYAN_BRILLANTE
        )
        footer_label.pack()

    def _crear_boton_nivel_grande(self, parent, row, nivel, titulo, descripcion, detalle, color, emoji):
        """Crea un botón de nivel super grande y atractivo"""
        # Frame principal del botón - sin shadow frame pixeleado
        nivel_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=15,
            border_width=4,
            border_color=color
        )
        nivel_frame.grid(row=row, column=0, pady=8, padx=20, sticky="nsew")

        # Contenedor interno
        inner_frame = ctk.CTkFrame(nivel_frame, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Configurar grid con pesos para responsividad
        inner_frame.grid_columnconfigure(0, weight=0, minsize=70)   # Emoji
        inner_frame.grid_columnconfigure(1, weight=1, minsize=250)  # Texto
        inner_frame.grid_columnconfigure(2, weight=0, minsize=120)  # Botón
        inner_frame.grid_rowconfigure(0, weight=1)
        inner_frame.grid_rowconfigure(1, weight=1)

        # Emoji grande a la izquierda
        emoji_label = ctk.CTkLabel(
            inner_frame,
            text=emoji,
            font=("Segoe UI Emoji", 50),
        )
        emoji_label.grid(row=0, column=0, rowspan=2, padx=(5, 15), sticky="")

        # Título
        titulo_label = ctk.CTkLabel(
            inner_frame,
            text=titulo,
            font=("Comic Sans MS", 22, "bold"),
            text_color=color,
            anchor="w"
        )
        titulo_label.grid(row=0, column=1, sticky="w", pady=(2, 0))

        # Descripción
        desc_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        desc_frame.grid(row=1, column=1, sticky="w")

        desc_label = ctk.CTkLabel(
            desc_frame,
            text=descripcion,
            font=("Comic Sans MS", 13),
            text_color="#555555",
            anchor="w"
        )
        desc_label.pack(anchor="w")

        detalle_label = ctk.CTkLabel(
            desc_frame,
            text=detalle,
            font=("Comic Sans MS", 11, "italic"),
            text_color=color,
            anchor="w"
        )
        detalle_label.pack(anchor="w")

        # Botón grande de selección
        boton = ctk.CTkButton(
            inner_frame,
            text="¡JUGAR!\n🚀",
            font=("Comic Sans MS", 18, "bold"),
            width=120,
            height=70,
            corner_radius=15,
            fg_color=color,
            hover_color=self._aclarar_color(color),
            text_color="white",
            command=lambda: self.seleccionar_nivel(nivel)
        )
        boton.grid(row=0, column=2, rowspan=2, padx=(10, 5), pady=5)

    def _oscurecer_color(self, color_hex):
        """Oscurece un color"""
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * 0.7), int(g * 0.7), int(b * 0.7)
        return f'#{r:02x}{g:02x}{b:02x}'

    def _aclarar_color(self, color_hex):
        """Aclara un color"""
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        # Mezcla con blanco para aclarar
        r = int(r + (255 - r) * 0.5)
        g = int(g + (255 - g) * 0.5)
        b = int(b + (255 - b) * 0.5)
        return f'#{r:02x}{g:02x}{b:02x}'

    def abrir_calendario(self):
        """Abre ventana con calendario para seleccionar fecha"""
        if not TKCALENDAR_AVAILABLE:
            messagebox.showinfo("📅", "Para usar el calendario instala: pip install tkcalendar")
            return

        # Crear ventana de calendario
        cal_window = ctk.CTkToplevel(self.root)
        cal_window.title("📅 Seleccionar Fecha")
        try:
            cal_window.iconbitmap(resource_path("logo.ico"))
        except:
            pass
        cal_window.transient(self.root)
        cal_window.grab_set()

        # Tamaño de la ventana
        width, height = 350, 400
        cal_window.geometry(f"{width}x{height}")

        # Centrar ventana
        cal_window.update_idletasks()
        x = (cal_window.winfo_screenwidth() - width) // 2
        y = (cal_window.winfo_screenheight() - height) // 2
        cal_window.geometry(f"{width}x{height}+{x}+{y}")
        cal_window.resizable(False, False)

        # Frame principal
        main_frame = ctk.CTkFrame(cal_window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Título
        ctk.CTkLabel(
            main_frame,
            text="📅 Selecciona una Fecha",
            font=("Comic Sans MS", 18, "bold"),
            text_color=Config.COLOR_AZUL_BRILLANTE
        ).pack(pady=(10, 15))

        # Calendario
        cal = Calendar(
            main_frame,
            selectmode='day',
            date_pattern='dd/mm/yyyy',
            locale='es_ES',
            showweeknumbers=False,
            background=Config.COLOR_AZUL_BRILLANTE,
            foreground='white',
            selectbackground=Config.COLOR_VERDE_BRILLANTE,
            selectforeground='white',
            normalbackground='white',
            normalforeground='black',
            weekendbackground='#F0F0F0',
            weekendforeground='black',
            headersbackground=Config.COLOR_AZUL_BRILLANTE,
            headersforeground='white',
            borderwidth=2
        )

        # Obtener fecha actual del entry si es válida
        try:
            fecha_actual = self.entry_fecha.get()
            if fecha_actual:
                cal.selection_set(datetime.strptime(fecha_actual, "%d/%m/%Y"))
        except:
            cal.selection_set(datetime.now())

        cal.pack(pady=10, padx=10)

        # Frame para botones
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=15)

        def seleccionar_fecha():
            """Actualiza el campo de fecha con la fecha seleccionada"""
            fecha_seleccionada = cal.get_date()
            self.entry_fecha.delete(0, 'end')
            self.entry_fecha.insert(0, fecha_seleccionada)
            cal_window.destroy()

        def cancelar():
            """Cierra el calendario sin cambios"""
            cal_window.destroy()

        # Botón Aceptar
        ctk.CTkButton(
            buttons_frame,
            text="✅ Aceptar",
            font=("Comic Sans MS", 14, "bold"),
            width=120,
            height=35,
            corner_radius=15,
            fg_color=Config.COLOR_VERDE_BRILLANTE,
            hover_color=self._aclarar_color(Config.COLOR_VERDE_BRILLANTE),
            text_color="white",
            command=seleccionar_fecha
        ).pack(side="left", padx=5)

        # Botón Cancelar
        ctk.CTkButton(
            buttons_frame,
            text="❌ Cancelar",
            font=("Comic Sans MS", 14, "bold"),
            width=120,
            height=35,
            corner_radius=15,
            fg_color=Config.COLOR_ROJO_BRILLANTE,
            hover_color=self._aclarar_color(Config.COLOR_ROJO_BRILLANTE),
            text_color="white",
            command=cancelar
        ).pack(side="left", padx=5)

        # Atajos de teclado
        cal_window.bind('<Return>', lambda e: seleccionar_fecha())
        cal_window.bind('<Escape>', lambda e: cancelar())

        # Llevar ventana al frente
        cal_window.lift()
        cal_window.attributes('-topmost', True)
        cal_window.after(100, lambda: cal_window.attributes('-topmost', False))

    # ==================== PANTALLA DE DATOS ====================
    def mostrar_pantalla_datos(self):
        """Formulario de datos super amigable"""
        self.limpiar_pantalla()

        main_frame = ctk.CTkFrame(self.root, fg_color="#E3F2FD")
        main_frame.pack(fill="both", expand=True)

        # Contenedor central sin scroll - tamaño fijo
        center_frame = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=20,
            border_width=4,
            border_color=self.obtener_color_nivel(self.nivel)
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        content_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        content_frame.pack(padx=50, pady=35)

        # Título con emoji del nivel
        color_nivel = self.obtener_color_nivel(self.nivel)
        emojis_nivel = {1: "🟢", 2: "🟠", 3: "🔴"}

        titulo_label = ctk.CTkLabel(
            content_frame,
            text=f"{emojis_nivel.get(self.nivel, '⭐')} NIVEL {self.nivel} {emojis_nivel.get(self.nivel, '⭐')}",
            font=("Comic Sans MS", 28, "bold"),
            text_color=color_nivel
        )
        titulo_label.pack(pady=(0, 5))

        subtitulo_label = ctk.CTkLabel(
            content_frame,
            text="¡Cuéntanos sobre ti! 😊",
            font=("Comic Sans MS", 16),
            text_color="#666666"
        )
        subtitulo_label.pack(pady=(0, 20))

        # Campo Nombre con diseño infantil
        nombre_container = self._crear_campo_infantil(
            content_frame,
            "👤 ¿Cómo te llamas?",
            "Escribe tu nombre completo aquí",
            color_nivel
        )
        self.entry_nombre = nombre_container

        # Campo Curso
        curso_label = ctk.CTkLabel(
            content_frame,
            text="📚 ¿En qué curso estás?",
            font=("Comic Sans MS", 16, "bold"),
            text_color=color_nivel,
            anchor="w"
        )
        curso_label.pack(fill="x", pady=(10, 6))

        self.combo_curso = ctk.CTkComboBox(
            content_frame,
            values=Config.CURSOS,
            font=("Comic Sans MS", 15),
            width=420,
            height=40,
            corner_radius=12,
            button_color=color_nivel,
            button_hover_color=self._oscurecer_color(color_nivel),
            dropdown_fg_color="white",
            dropdown_hover_color="#F0F0F0",
            border_color=color_nivel,
            border_width=2,
            state="readonly"
        )
        self.combo_curso.set("👉 Selecciona tu curso")
        self.combo_curso.pack(pady=(0, 10))

        # Campo Fecha
        fecha_label = ctk.CTkLabel(
            content_frame,
            text="📅 Fecha de hoy:",
            font=("Comic Sans MS", 16, "bold"),
            text_color=color_nivel,
            anchor="w"
        )
        fecha_label.pack(fill="x", pady=(10, 6))

        # Frame para fecha + botón calendario
        fecha_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        fecha_frame.pack(pady=(0, 20))

        self.entry_fecha = ctk.CTkEntry(
            fecha_frame,
            font=("Comic Sans MS", 15),
            width=340,
            height=40,
            corner_radius=12,
            border_color=color_nivel,
            border_width=2
        )
        self.entry_fecha.insert(0, self.fecha)
        self.entry_fecha.pack(side="left", padx=(0, 10))

        # Botón calendario
        btn_calendario = ctk.CTkButton(
            fecha_frame,
            text="📅",
            font=("Segoe UI Emoji", 20),
            width=60,
            height=40,
            corner_radius=12,
            fg_color=color_nivel,
            hover_color=self._aclarar_color(color_nivel),
            command=self.abrir_calendario
        )
        btn_calendario.pack(side="left")

        # Botón comenzar
        btn_comenzar = ctk.CTkButton(
            content_frame,
            text="🚀 ¡COMENZAR! 🚀",
            font=("Comic Sans MS", 20, "bold"),
            width=300,
            height=60,
            corner_radius=30,
            fg_color=color_nivel,
            hover_color=self._aclarar_color(color_nivel),
            text_color="white",
            command=self.validar_datos
        )
        btn_comenzar.pack(pady=(5, 0))

        # Botón volver decorativo - Se crea al final para que esté encima
        volver_btn = ctk.CTkButton(
            main_frame,
            text="⬅️ Volver",
            font=("Comic Sans MS", 14, "bold"),
            width=120,
            height=40,
            corner_radius=20,
            fg_color=Config.COLOR_AZUL_BRILLANTE,
            hover_color=self._aclarar_color(Config.COLOR_AZUL_BRILLANTE),
            text_color="white",
            command=self.mostrar_pantalla_inicio
        )
        volver_btn.place(x=20, y=20)

    def _crear_campo_infantil(self, parent, label_text, placeholder, color):
        """Crea un campo de entrada con diseño infantil"""
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Comic Sans MS", 16, "bold"),
            text_color=color,
            anchor="w"
        )
        label.pack(fill="x", pady=(0, 6))

        # Validación para limitar a 40 caracteres
        vcmd_nombre = (self.root.register(self.validar_nombre), '%P')

        entry = ctk.CTkEntry(
            parent,
            font=("Comic Sans MS", 15),
            width=420,
            height=40,
            corner_radius=12,
            placeholder_text=placeholder,
            border_color=color,
            border_width=2,
            validate="key",
            validatecommand=vcmd_nombre
        )
        entry.pack(pady=(0, 10))
        return entry

    # ==================== PANTALLA DE PREPARACIÓN ====================
    def mostrar_pantalla_preparacion(self):
        """Pantalla de preparación antes de mostrar ejercicios"""
        self.limpiar_pantalla()

        color_operacion = self.obtener_color_operacion(self.operacion_actual)
        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)
        emoji_op = self.obtener_emoji_operacion(self.operacion_actual)

        # Calcular número real de ejercicios
        num_ejercicios = self._calcular_num_ejercicios(self.operacion_actual, self.tabla_actual)

        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color="#E3F2FD")
        main_frame.pack(fill="both", expand=True)

        # Contenedor central - MÁS COMPACTO
        center_frame = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=25,
            border_width=4,
            border_color=color_operacion
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        content_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        content_frame.pack(padx=40, pady=35)

        # Emoji más pequeño
        ctk.CTkLabel(
            content_frame,
            text=emoji_op,
            font=("Segoe UI Emoji", 60)
        ).pack(pady=(0, 10))

        # Título más pequeño
        ctk.CTkLabel(
            content_frame,
            text="¡PREPÁRATE!",
            font=("Comic Sans MS", 32, "bold"),
            text_color=color_operacion
        ).pack(pady=(0, 8))

        # Información más compacta
        ctk.CTkLabel(
            content_frame,
            text=f"{nombre_op} - Tabla del {self.tabla_actual}",
            font=("Comic Sans MS", 22, "bold"),
            text_color="#333333"
        ).pack(pady=(0, 15))

        # Instrucciones más compactas
        instrucciones_frame = ctk.CTkFrame(
            content_frame,
            fg_color=self._aclarar_color(color_operacion),
            corner_radius=15
        )
        instrucciones_frame.pack(fill="x", pady=(0, 18), padx=15)

        ctk.CTkLabel(
            instrucciones_frame,
            text=f"📝 {num_ejercicios} ejercicios",
            font=("Comic Sans MS", 16),
            text_color="#333333"
        ).pack(pady=6)

        ctk.CTkLabel(
            instrucciones_frame,
            text="⏱️ El cronómetro iniciará automáticamente",
            font=("Comic Sans MS", 16),
            text_color="#333333"
        ).pack(pady=6)

        ctk.CTkLabel(
            instrucciones_frame,
            text="✍️ Completa todos los ejercicios",
            font=("Comic Sans MS", 16),
            text_color="#333333"
        ).pack(pady=6)

        # Mensaje motivador más pequeño
        ctk.CTkLabel(
            content_frame,
            text="¡Confía en ti! ¡Tú puedes! 💪",
            font=("Comic Sans MS", 15, "bold", "italic"),
            text_color=color_operacion
        ).pack(pady=(8, 18))

        # Botón más compacto
        ctk.CTkButton(
            content_frame,
            text="▶️ ¡COMENZAR AHORA!",
            font=("Comic Sans MS", 22, "bold"),
            width=300,
            height=65,
            corner_radius=20,
            fg_color=Config.COLOR_VERDE_BRILLANTE,
            hover_color=self._aclarar_color(Config.COLOR_VERDE_BRILLANTE),
            text_color="white",
            command=self.iniciar_ejercicios_directo
        ).pack()

    def _calcular_num_ejercicios(self, operacion, tabla):
        """Calcula el número real de ejercicios según la operación y tabla"""
        if operacion == "resta":
            # En resta solo se generan ejercicios desde 0 hasta la tabla
            return tabla + 1  # +1 porque incluye el 0
        else:
            # Para las demás operaciones son 13 ejercicios (0 a 12)
            return 13

    def iniciar_ejercicios_directo(self):
        """Muestra ejercicios e inicia cronómetro automáticamente"""
        # Solo reiniciar variables de tiempo si es la primera tabla de la operación
        tabla_minima = self.obtener_tabla_minima(self.operacion_actual)
        if self.tabla_actual == tabla_minima:
            # Primera tabla de esta operación, reiniciar tiempo
            self.tiempo_operacion_actual = 0
            self.en_tiempo_extra = False
        # Si no es la primera tabla, mantener tiempo_operacion_actual sin cambios

        self.corriendo = False
        self.finalizado = False

        # Establecer tiempos según la operación
        if self.operacion_actual in ["potencia", "raiz"]:
            # Tiempos especiales para potenciación y radicación
            self.tiempo_principal_operacion = Config.POTENCIA_RAIZ_TIEMPO_PRINCIPAL
            self.tiempo_maximo_operacion = Config.POTENCIA_RAIZ_TIEMPO_MAXIMO
        elif self.nivel == 1:
            self.tiempo_principal_operacion = Config.NIVEL_1_TIEMPO_PRINCIPAL
            self.tiempo_maximo_operacion = Config.NIVEL_1_TIEMPO_MAXIMO
        else:  # Nivel 2 y 3
            self.tiempo_principal_operacion = Config.NIVEL_2_TIEMPO_PRINCIPAL
            self.tiempo_maximo_operacion = Config.NIVEL_2_TIEMPO_MAXIMO

        self._mostrar_ejercicios_y_cronometro()
        # Iniciar cronómetro automáticamente después de un breve delay
        self.root.after(100, self.iniciar_cronometro)

    def mostrar_pantalla_ejercicios(self):
        """Método legacy que ahora muestra la pantalla de preparación"""
        # NO reiniciar corriendo ni finalizado aquí para preservar el cronómetro
        self.finalizado = False

        if self.tabla_actual > self.tabla_max:
            idx = self.operaciones_nivel.index(self.operacion_actual) + 1
            if idx >= len(self.operaciones_nivel):
                self.mostrar_resultados_finales()
                return
            self.operacion_actual = self.operaciones_nivel[idx]
            self.tabla_actual = self.obtener_tabla_minima(self.operacion_actual)

        self.ejercicios = self.generar_ejercicios(self.operacion_actual)
        self.mostrar_pantalla_preparacion()

    # ==================== PANTALLA DE EJERCICIOS ====================
    def _mostrar_ejercicios_y_cronometro(self):
        """Pantalla de ejercicios colorida y divertida"""
        self.limpiar_pantalla()
        self.corriendo = False
        self.finalizado = False

        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color="#E3F2FD")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Panel de ejercicios (izquierda)
        self._crear_panel_ejercicios_colorido(main_frame)

        # Panel de controles (derecha)
        self._crear_panel_controles_divertido(main_frame)

    def _crear_panel_ejercicios_colorido(self, parent):
        """Panel de ejercicios con diseño basado en operación"""
        # Color principal según operación
        color_operacion = self.obtener_color_operacion(self.operacion_actual)
        color_operacion_claro = self._aclarar_color(color_operacion)

        ejercicios_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=25,
            border_width=5,
            border_color=color_operacion
        )
        ejercicios_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        # Encabezado con color de la operación
        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)
        emoji_op = self.obtener_emoji_operacion(self.operacion_actual)

        header = ctk.CTkFrame(
            ejercicios_frame,
            fg_color=color_operacion,
            corner_radius=20,
            height=100
        )
        header.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            header,
            text=f"{emoji_op} {nombre_op} - Tabla del {self.tabla_actual} {emoji_op}",
            font=("Comic Sans MS", 32, "bold"),
            text_color="white"
        ).pack(pady=20)

        # Scrollable frame para ejercicios
        scroll_frame = ctk.CTkScrollableFrame(
            ejercicios_frame,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Crear ejercicios con dos colores alternados de la operación
        self.entries = {}
        colores_alternados = [color_operacion, color_operacion_claro]

        for i, ej in enumerate(self.ejercicios):
            color_ej = colores_alternados[i % 2]
            self._crear_ejercicio_colorido(scroll_frame, ej, i, color_ej)

    def _crear_ejercicio_colorido(self, parent, ejercicio, index, color):
        """Crea un ejercicio individual colorido"""
        # Frame del ejercicio
        ej_frame = ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=15,
            height=70
        )
        ej_frame.pack(fill="x", pady=8, padx=10)

        content_frame = ctk.CTkFrame(ej_frame, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Ejercicio
        if "^" in ejercicio["texto"]:
            self._crear_ejercicio_potencia_colorido(content_frame, ejercicio)
        else:
            ctk.CTkLabel(
                content_frame,
                text=ejercicio["texto"],
                font=("Comic Sans MS", 24, "bold"),
                text_color="black",
                width=250,
                anchor="e"
            ).pack(side="left", padx=(0, 20))

        # Entry con diseño grande
        vcmd = (self.root.register(self.validar_numero), '%P')
        entry = ctk.CTkEntry(
            content_frame,
            font=("Comic Sans MS", 24, "bold"),
            width=150,
            height=50,
            justify="center",
            corner_radius=12,
            state="disabled",
            border_color="white",
            border_width=3,
            fg_color=color,
            text_color="black",
            validate="key",
            validatecommand=vcmd
        )
        entry.pack(side="left")
        self.entries[ejercicio["id"]] = entry

    def _crear_ejercicio_potencia_colorido(self, parent, ejercicio):
        """Crea ejercicio de potencia con diseño especial"""
        from tkinter import Label, Frame

        bg_color = parent.cget("fg_color")
        if isinstance(bg_color, tuple):
            bg_color = bg_color[1]

        # Si bg_color es "transparent" o None, usar el color del padre
        if bg_color in ("transparent", None, ""):
            # Obtener el color del frame padre (ej_frame)
            parent_of_parent = parent.master
            bg_color = parent_of_parent.cget("fg_color")
            if isinstance(bg_color, tuple):
                bg_color = bg_color[1]

        op_frame = Frame(parent, bg=bg_color)
        op_frame.pack(side="left", padx=(0, 20))

        parts = ejercicio["texto"].split("^")
        base = parts[0].strip()
        exp_part = parts[1].replace("=", "").strip()

        Label(op_frame, text=base, font=("Comic Sans MS", 24, "bold"),
              bg=bg_color, fg="black").pack(side="left")
        Label(op_frame, text=exp_part, font=("Comic Sans MS", 14, "bold"),
              bg=bg_color, fg="black").pack(side="left", anchor="n")
        Label(op_frame, text=" =", font=("Comic Sans MS", 24, "bold"),
              bg=bg_color, fg="black").pack(side="left")

    def _crear_panel_controles_divertido(self, parent):
        """Panel de controles con diseño basado en operación"""
        # Colores según operación
        color_operacion = self.obtener_color_operacion(self.operacion_actual)
        color_operacion_oscuro = self._oscurecer_color(color_operacion)

        controles_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controles_frame.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        # Cronómetro con color de la operación
        self.cronometro_frame = ctk.CTkFrame(
            controles_frame,
            fg_color=color_operacion,
            corner_radius=20,
            border_width=5,
            border_color=color_operacion_oscuro
        )
        self.cronometro_frame.pack(fill="x", pady=(0, 20))

        self.label_tiempo_titulo = ctk.CTkLabel(
            self.cronometro_frame,
            text="⏱️ TIEMPO ⏱️",
            font=("Comic Sans MS", 20, "bold"),
            text_color="white"
        )
        self.label_tiempo_titulo.pack(pady=(20, 10))

        mins = int(self.tiempo_operacion_actual // 60)
        secs = int(self.tiempo_operacion_actual % 60)

        self.label_tiempo = ctk.CTkLabel(
            self.cronometro_frame,
            text=f"{mins:02d}:{secs:02d}",
            font=("Comic Sans MS", 56, "bold"),
            text_color="white"
        )
        self.label_tiempo.pack(pady=(0, 20))

        # Info estudiante con color de la operación (aclarado)
        color_operacion_claro = self._aclarar_color(color_operacion)
        info_frame = ctk.CTkFrame(
            controles_frame,
            fg_color=color_operacion_claro,
            corner_radius=20
        )
        info_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            info_frame,
            text="👤",
            font=("Segoe UI Emoji", 40)
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            info_frame,
            text=self.nombre,
            font=("Comic Sans MS", 18, "bold"),
            text_color="white"
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            info_frame,
            text=self.curso,
            font=("Comic Sans MS", 16),
            text_color="white"
        ).pack(pady=(0, 15))

        # Botón Finalizar
        self.boton_finalizar = ctk.CTkButton(
            controles_frame,
            text="⏹️ FINALIZAR",
            font=("Comic Sans MS", 22, "bold"),
            width=220,
            height=70,
            corner_radius=20,
            fg_color=Config.COLOR_ROJO_BRILLANTE,
            hover_color=self._aclarar_color(Config.COLOR_ROJO_BRILLANTE),
            text_color="white",
            command=self.finalizar_operacion
        )
        self.boton_finalizar.pack(pady=(0, 15))

        # Botón Ver Resultados - con mejor tamaño y espaciado
        ctk.CTkButton(
            controles_frame,
            text="📊 VER RESULTADOS",
            font=("Comic Sans MS", 16, "bold"),
            width=220,
            height=65,
            corner_radius=20,
            fg_color=color_operacion,
            hover_color=self._aclarar_color(color_operacion),
            text_color="white",
            command=self.mostrar_resultados_operacion
        ).pack(pady=(0, 15))

        if self._debe_mostrar_boton_siguiente():
            texto = "➡️ SIGUIENTE TABLA" if self.tabla_actual < self.tabla_max else "➡️ SIGUIENTE OPERACIÓN"
            ctk.CTkButton(
                controles_frame,
                text=texto,
                font=("Comic Sans MS", 15, "bold"),
                width=220,
                height=65,
                corner_radius=20,
                fg_color=color_operacion_oscuro,
                hover_color=self._aclarar_color(color_operacion_oscuro),
                text_color="white",
                command=self.siguiente_operacion
            ).pack(pady=(0, 15))

        # Guardamos la referencia del botón iniciar como None ya que no existe
        self.boton_iniciar = None

    def _debe_mostrar_boton_siguiente(self):
        """Verifica si mostrar botón siguiente"""
        idx_actual = self.operaciones_nivel.index(self.operacion_actual)
        es_ultima_operacion = (idx_actual == len(self.operaciones_nivel) - 1)
        es_ultima_tabla = (self.tabla_actual == self.tabla_max)
        return not (es_ultima_tabla and es_ultima_operacion)

    # ==================== SELECTOR DE TABLAS ====================
    def solicitar_limite_tabla_operacion(self):
        """Selector de tabla con diseño tipo juego"""
        if not self.operacion_actual:
            self.operacion_actual = self.operaciones_nivel[0]

        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)
        emoji_op = self.obtener_emoji_operacion(self.operacion_actual)
        tabla_minima = self.obtener_tabla_minima(self.operacion_actual)
        color_operacion = self.obtener_color_operacion(self.operacion_actual)

        # Dialog moderno con tamaño fijo
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"{nombre_op}")
        try:
            dialog.iconbitmap(resource_path("logo.ico"))
        except:
            pass
        dialog.transient(self.root)
        dialog.grab_set()

        # Establecer tamaño fijo de la ventana - MÁS PEQUEÑA
        dialog_width = 450
        dialog_height = 500

        # Frame principal
        main_frame = ctk.CTkFrame(
            dialog,
            fg_color="white",
            corner_radius=25,
            border_width=5,
            border_color=color_operacion,
            width=dialog_width,
            height=dialog_height
        )
        main_frame.pack(padx=20, pady=20)

        # Emoji más pequeño
        ctk.CTkLabel(
            main_frame,
            text=emoji_op,
            font=("Segoe UI Emoji", 50)
        ).pack(pady=(20, 5))

        # Título más pequeño
        ctk.CTkLabel(
            main_frame,
            text=nombre_op.upper(),
            font=("Comic Sans MS", 24, "bold"),
            text_color=color_operacion
        ).pack()

        # Pregunta más compacta
        pregunta_text = "¿Hasta qué tabla quieres practicar? 🎯"
        if self.operacion_actual in ["potencia", "raiz"]:
            pregunta_text += "\n(Tablas disponibles: 2 y 3)"
        elif tabla_minima == 2:
            pregunta_text += "\n(Comienza desde la tabla 2)"

        ctk.CTkLabel(
            main_frame,
            text=pregunta_text,
            font=("Comic Sans MS", 14),
            text_color="#666666",
            justify="center"
        ).pack(pady=(10, 15))

        # Frame del valor más pequeño
        valor_frame = ctk.CTkFrame(
            main_frame,
            fg_color=color_operacion,
            corner_radius=20,
            height=100
        )
        valor_frame.pack(fill="x", padx=30, pady=15)

        valor_label = ctk.CTkLabel(
            valor_frame,
            text=f"TABLA {tabla_minima}",
            font=("Comic Sans MS", 36, "bold"),
            text_color="white"
        )
        valor_label.pack(pady=20)

        # Slider más pequeño
        def actualizar_valor(value):
            valor_label.configure(text=f"TABLA {int(value)}")

        # Limitar tablas para potenciación y radicación
        if self.operacion_actual in ["potencia", "raiz"]:
            tabla_maxima = 3
        else:
            tabla_maxima = 12

        slider = ctk.CTkSlider(
            main_frame,
            from_=tabla_minima,
            to=tabla_maxima,
            number_of_steps=tabla_maxima-tabla_minima,
            width=320,
            height=25,
            button_color=color_operacion,
            button_hover_color=self._oscurecer_color(color_operacion),
            progress_color=color_operacion,
            command=actualizar_valor
        )
        slider.set(tabla_minima)
        slider.pack(pady=(10, 20), padx=30)

        resultado = {"confirmado": False}

        def confirmar():
            resultado["confirmado"] = True
            resultado["valor"] = int(slider.get())
            dialog.destroy()

        def cancelar():
            resultado["confirmado"] = False
            dialog.destroy()

        # Botones más pequeños
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(10, 20))

        ctk.CTkButton(
            buttons_frame,
            text="✅ ¡LISTO!",
            font=("Comic Sans MS", 16, "bold"),
            width=140,
            height=50,
            corner_radius=15,
            fg_color=Config.COLOR_VERDE_BRILLANTE,
            hover_color=self._aclarar_color(Config.COLOR_VERDE_BRILLANTE),
            text_color="white",
            command=confirmar
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            buttons_frame,
            text="❌ CANCELAR",
            font=("Comic Sans MS", 16, "bold"),
            width=140,
            height=50,
            corner_radius=15,
            fg_color=Config.COLOR_ROJO_BRILLANTE,
            hover_color=self._aclarar_color(Config.COLOR_ROJO_BRILLANTE),
            text_color="white",
            command=cancelar
        ).pack(side="left", padx=10)

        dialog.bind('<Return>', lambda e: confirmar())
        dialog.bind('<Escape>', lambda e: cancelar())

        # Centrar con el tamaño definido
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog_width // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.resizable(False, False)

        self.root.wait_window(dialog)

        if resultado["confirmado"]:
            self.limites_tablas[self.operacion_actual] = resultado["valor"]
            self.tabla_max = resultado["valor"]
            self.tabla_actual = tabla_minima
            self.mostrar_pantalla_ejercicios()
        else:
            self.mostrar_pantalla_datos()

    # ==================== RESULTADOS FINALES ====================
    def mostrar_resultados_finales(self):
        """Pantalla de resultados estilo celebración"""
        self.limpiar_pantalla()

        nota, tiempo, pen = self.calcular_nota_final()

        main_frame = ctk.CTkFrame(self.root, fg_color="#E3F2FD")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Encabezado con emojis según nota
        if nota >= 90:
            emoji = "🎉🏆"
            mensaje = "¡EXCELENTE!"
            color_nota = Config.COLOR_VERDE_BRILLANTE
        elif nota >= 70:
            emoji = "😊👍"
            mensaje = "¡MUY BIEN!"
            color_nota = Config.COLOR_AZUL_BRILLANTE
        else:
            emoji = "💪📚"
            mensaje = "¡SIGUE PRACTICANDO!"
            color_nota = Config.COLOR_NARANJA_BRILLANTE

        # Frame con scroll para el contenido
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=20
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Contenedor para todo el contenido
        content_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header compacto
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(15, 5))

        ctk.CTkLabel(
            header_frame,
            text=f"{emoji} {mensaje}",
            font=("Comic Sans MS", 28, "bold"),
            text_color=color_nota
        ).pack()

        ctk.CTkLabel(
            header_frame,
            text=f"{self.nombre} • {self.curso} • {self.fecha}",
            font=("Comic Sans MS", 13),
            text_color="#666666"
        ).pack(pady=(2, 0))

        # NOTA FINAL - Diseño sutil y agradable
        nota_frame = ctk.CTkFrame(
            content_frame,
            fg_color=self._aclarar_color(color_nota),
            corner_radius=12,
            border_width=2,
            border_color=color_nota
        )
        nota_frame.pack(pady=(10, 8), padx=60)

        nota_content = ctk.CTkFrame(nota_frame, fg_color="transparent")
        nota_content.pack(padx=25, pady=12)

        ctk.CTkLabel(
            nota_content,
            text=f"Calificación Final: {nota}/100",
            font=("Comic Sans MS", 16, "bold"),
            text_color=color_nota
        ).pack()

        # Mostrar información de penalización si existe
        if pen > 0:
            # Mostrar penalización detallada
            pen_frame = ctk.CTkFrame(
                content_frame,
                fg_color=self._aclarar_color(Config.COLOR_ROJO_BRILLANTE),
                corner_radius=12
            )
            pen_frame.pack(pady=(5, 8), padx=40, fill="x")

            ctk.CTkLabel(
                pen_frame,
                text=f"⚠️ Penalización por Tiempo Extra",
                font=("Comic Sans MS", 14, "bold"),
                text_color=Config.COLOR_ROJO_BRILLANTE
            ).pack(pady=(8, 2))

            ctk.CTkLabel(
                pen_frame,
                text=f"Penalización total aplicada: -{pen} punto(s)",
                font=("Comic Sans MS", 13),
                text_color=Config.COLOR_ROJO_BRILLANTE
            ).pack(pady=(0, 8))

        # Título detalle compacto
        ctk.CTkLabel(
            content_frame,
            text="📊 DETALLE DE RESPUESTAS",
            font=("Comic Sans MS", 18, "bold"),
            text_color=Config.COLOR_MORADO_BRILLANTE
        ).pack(pady=(8, 5))

        # Tabla simple de resultados
        self._crear_tabla_resultados_simple(content_frame)

        # Botones finales compactos
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(pady=(10, 15))

        botones = [
            ("📝 VER\nRESPUESTAS", Config.COLOR_AZUL_BRILLANTE, self.mostrar_ventana_respuestas),
            ("🖨️ IMPRIMIR", Config.COLOR_MORADO_BRILLANTE, self.imprimir_resultados),
            ("🔄 OTRO\nTEST", Config.COLOR_VERDE_BRILLANTE, self.reiniciar_aplicativo),
            ("❌ SALIR", Config.COLOR_ROJO_BRILLANTE, self.root.quit)
        ]

        for texto, color, comando in botones:
            ctk.CTkButton(
                buttons_frame,
                text=texto,
                font=("Comic Sans MS", 14, "bold"),
                width=140,
                height=60,
                corner_radius=15,
                fg_color=color,
                hover_color=self._aclarar_color(color),
                text_color="white",
                command=comando
            ).pack(side="left", padx=8)

    def _crear_tabla_resultados_simple(self, parent):
        """Tabla de resultados simplificada y colorida"""
        resultados_por_operacion = self._agrupar_resultados_por_operacion()

        table_container = ctk.CTkFrame(parent, fg_color="transparent")
        table_container.pack(padx=30)

        # Encabezado
        header_frame = ctk.CTkFrame(
            table_container,
            fg_color=Config.COLOR_MORADO_BRILLANTE,
            corner_radius=10
        )
        header_frame.pack(fill="x", pady=(0, 4))

        headers = ["Operación", "Tabla", "✅", "❌"]
        for header in headers:
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Comic Sans MS", 13, "bold"),
                text_color="white",
                width=120
            ).pack(side="left", padx=8, pady=6, expand=True)

        # Filas
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

                color_fila = self.obtener_color_operacion(operacion)

                row_frame = ctk.CTkFrame(
                    table_container,
                    fg_color=color_fila,
                    corner_radius=10
                )
                row_frame.pack(fill="x", pady=2)

                datos = [f"{emoji_op} {nombre_op}", str(tabla_max), str(correctas), str(incorrectas)]
                for dato in datos:
                    ctk.CTkLabel(
                        row_frame,
                        text=dato,
                        font=("Comic Sans MS", 12, "bold"),
                        text_color="white",
                        width=120
                    ).pack(side="left", padx=8, pady=6, expand=True)

        # Total
        total_frame = ctk.CTkFrame(
            table_container,
            fg_color=Config.COLOR_AMARILLO_BRILLANTE,
            corner_radius=10
        )
        total_frame.pack(fill="x", pady=(8, 0))

        totales = ["🏆 TOTAL", "", str(total_correctas), str(total_incorrectas)]
        for total in totales:
            ctk.CTkLabel(
                total_frame,
                text=total,
                font=("Comic Sans MS", 13, "bold"),
                text_color="#333333",
                width=120
            ).pack(side="left", padx=8, pady=8, expand=True)

    # ==================== VENTANA DE RESPUESTAS ====================
    def mostrar_ventana_respuestas(self):
        """Ventana con todas las respuestas"""
        if not self.historial_ejercicios:
            messagebox.showinfo("📝", "No hay ejercicios realizados.")
            return

        ventana = ctk.CTkToplevel(self.root)
        ventana.title("📝 Mis Respuestas")
        try:
            ventana.iconbitmap(resource_path("logo.ico"))
        except:
            pass

        # Ventana más pequeña
        width, height = 900, 650

        # Centrar
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() - width) // 2
        y = (ventana.winfo_screenheight() - height) // 2
        ventana.geometry(f"{width}x{height}+{x}+{y}")

        # IMPORTANTE: Hacer que la ventana aparezca por delante
        ventana.lift()
        ventana.attributes('-topmost', True)
        ventana.after(100, lambda: ventana.attributes('-topmost', False))

        # Contenido
        main_frame = ctk.CTkFrame(ventana, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        ctk.CTkLabel(
            main_frame,
            text="📝 TODAS MIS RESPUESTAS 📝",
            font=("Comic Sans MS", 28, "bold"),
            text_color=Config.COLOR_MORADO_BRILLANTE
        ).pack(pady=(15, 8))

        ctk.CTkLabel(
            main_frame,
            text=f"{self.nombre} • {self.curso} • {self.fecha}",
            font=("Comic Sans MS", 14),
            text_color="#666666"
        ).pack(pady=(0, 15))

        # Scroll con ejercicios
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Agrupar por operación
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

        # Mostrar cada grupo
        for clave in orden_operaciones:
            grupo = ejercicios_por_operacion[clave]
            nombre_op = self.obtener_nombre_operacion(grupo["operacion"])
            emoji_op = self.obtener_emoji_operacion(grupo["operacion"])
            color = self.obtener_color_operacion(grupo["operacion"])

            # Header del grupo
            header = ctk.CTkFrame(scroll_frame, fg_color=color, corner_radius=15)
            header.pack(fill="x", pady=(15, 10))

            ctk.CTkLabel(
                header,
                text=f"{emoji_op} {nombre_op} - Tabla {grupo['tabla']}",
                font=("Comic Sans MS", 24, "bold"),
                text_color="white"
            ).pack(pady=15)

            # Ejercicios del grupo
            for i, ejercicio in enumerate(grupo["ejercicios"], 1):
                self._crear_fila_respuesta(scroll_frame, i, ejercicio, color)

        # Botones
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=20)

        ctk.CTkButton(
            buttons_frame,
            text="🖨️ IMPRIMIR",
            font=("Comic Sans MS", 20, "bold"),
            width=200,
            height=60,
            corner_radius=20,
            fg_color=Config.COLOR_AZUL_BRILLANTE,
            hover_color=self._aclarar_color(Config.COLOR_AZUL_BRILLANTE),
            text_color="white",
            command=self.imprimir_ejercicios
        ).pack(side="left", padx=15)

        ctk.CTkButton(
            buttons_frame,
            text="❌ CERRAR",
            font=("Comic Sans MS", 20, "bold"),
            width=200,
            height=60,
            corner_radius=20,
            fg_color=Config.COLOR_ROJO_BRILLANTE,
            hover_color=self._aclarar_color(Config.COLOR_ROJO_BRILLANTE),
            text_color="white",
            command=ventana.destroy
        ).pack(side="left", padx=15)

    def _crear_fila_respuesta(self, parent, numero, ejercicio, color_base):
        """Crea una fila de respuesta individual"""
        bg = "#F0F0F0" if numero % 2 == 0 else "white"

        fila = ctk.CTkFrame(parent, fg_color=bg, corner_radius=10)
        fila.pack(fill="x", pady=3, padx=20)

        content = ctk.CTkFrame(fila, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)

        # Ejercicio
        ctk.CTkLabel(
            content,
            text=ejercicio["ejercicio"],
            font=("Comic Sans MS", 16),
            text_color="#333333",
            width=150,
            anchor="w"
        ).pack(side="left", padx=5)

        # Tu respuesta
        resp_usuario = ejercicio["respuesta_usuario"] if ejercicio["respuesta_usuario"] else "(vacío)"
        ctk.CTkLabel(
            content,
            text=f"Tu respuesta: {resp_usuario}",
            font=("Comic Sans MS", 14),
            text_color="#666666",
            width=140
        ).pack(side="left", padx=5)

        # Respuesta correcta
        ctk.CTkLabel(
            content,
            text=f"Correcta: {ejercicio['respuesta_correcta']}",
            font=("Comic Sans MS", 14),
            text_color="#666666",
            width=120
        ).pack(side="left", padx=5)

        # Estado - Ahora más compacto y mejor distribuido
        if ejercicio["correcto"]:
            estado_text = "✅ BIEN"
            estado_color = Config.COLOR_VERDE_BRILLANTE
        else:
            estado_text = "❌ MAL"
            estado_color = Config.COLOR_ROJO_BRILLANTE

        estado_label = ctk.CTkLabel(
            content,
            text=estado_text,
            font=("Comic Sans MS", 14, "bold"),
            text_color=estado_color,
            width=80
        )
        estado_label.pack(side="left", padx=5)

    # ==================== FUNCIONES DE LÓGICA ====================

    def seleccionar_nivel(self, nivel):
        """Selecciona nivel y configura operaciones"""
        self.nivel = nivel
        if nivel == 1:
            self.operaciones_nivel = ["suma", "resta"]
        elif nivel == 2:
            self.operaciones_nivel = ["suma", "resta", "multiplicación", "división"]
        else:
            self.operaciones_nivel = ["suma", "resta", "multiplicación", "división", "potencia", "raiz"]
        self.mostrar_pantalla_datos()

    def validar_datos(self):
        """Valida datos del estudiante"""
        nombre = self.entry_nombre.get().strip()
        curso = self.combo_curso.get()

        if not nombre or curso == "👉 Selecciona tu curso":
            messagebox.showwarning("⚠️", "Por favor completa todos los datos")
            return

        self.nombre = nombre
        self.curso = curso
        self.fecha = self.entry_fecha.get()

        self.resultados_operacion = {}
        self.operacion_actual = ""
        self.tabla_actual = 1
        self.limites_tablas = {}
        self.solicitar_limite_tabla_operacion()

    def generar_ejercicios(self, operacion):
        """Genera ejercicios según operación"""
        ejercicios = []
        tabla = self.tabla_actual
        numeros = list(range(0, 13))

        if operacion == "resta":
            numeros_validos = list(range(0, tabla + 1))
            for num in numeros_validos:
                ejercicios.append({"texto": f"{tabla} - {num} =", "respuesta": tabla - num})
        elif operacion == "división":
            for num in numeros:
                dividendo = tabla * num
                ejercicios.append({"texto": f"{dividendo} ÷ {tabla} =", "respuesta": num})
        else:
            for num in numeros:
                ej = self._generar_ejercicio_por_tipo(operacion, tabla, num)
                if ej:
                    ejercicios.append(ej)

        random.shuffle(ejercicios)
        for idx, ej in enumerate(ejercicios):
            ej["id"] = idx
        return ejercicios

    def _generar_ejercicio_por_tipo(self, operacion, tabla, num):
        """Genera ejercicio individual"""
        if operacion == "suma":
            return {"texto": f"{tabla} + {num} =", "respuesta": tabla + num}
        elif operacion == "multiplicación":
            return {"texto": f"{tabla} × {num} =", "respuesta": tabla * num}
        elif operacion == "potencia":
            return {"texto": f"{num}^{tabla} =", "respuesta": num ** tabla}
        elif operacion == "raiz":
            radicando = num ** tabla
            if tabla == 2:
                texto = f"√{radicando} ="
            elif tabla == 3:
                texto = f"∛{radicando} ="
            else:
                texto = f"ⁿ√{radicando} =".replace("ⁿ", str(tabla))
            return {"texto": texto, "respuesta": num}
        return None

    def _focus_next_entry(self, event, next_entry):
        """Mueve el foco al siguiente entry cuando se presiona Tab"""
        next_entry.focus_set()
        # Seleccionar todo el texto si el entry tiene contenido
        if next_entry.get():
            next_entry.select_range(0, "end")
        return "break"  # Previene el comportamiento por defecto de Tab

    def iniciar_cronometro(self):
        """Inicia cronómetro"""
        if self.finalizado:
            messagebox.showinfo("⚠️", "Esta operación ya fue finalizada")
            return

        if not self.corriendo:
            self.tiempo_inicio = datetime.now() - timedelta(seconds=self.tiempo_operacion_actual)
            self.corriendo = True

            # Habilitar entries para escribir y configurar navegación con Tab
            entry_list = list(self.entries.values())
            for i, entry in enumerate(entry_list):
                entry.configure(state="normal")
                # Configurar navegación con Tab
                if i < len(entry_list) - 1:
                    next_entry = entry_list[i + 1]
                    entry.bind("<Tab>", lambda e, next_e=next_entry: self._focus_next_entry(e, next_e))
                else:
                    # En el último entry, Tab va al primero
                    entry.bind("<Tab>", lambda e, next_e=entry_list[0]: self._focus_next_entry(e, next_e))

            # El botón finalizar ya está habilitado desde el inicio
            # No necesitamos cambiar su estado

            self.actualizar_cronometro()

    def detener_cronometro(self):
        """Detiene cronómetro"""
        if self.corriendo:
            self.tiempo_operacion_actual = (datetime.now() - self.tiempo_inicio).total_seconds()
            self.corriendo = False

    def actualizar_cronometro(self):
        """Actualiza cronómetro cada segundo"""
        if not self.corriendo:
            return

        elapsed = (datetime.now() - self.tiempo_inicio).total_seconds()
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)

        # Actualizar texto del cronómetro
        self.label_tiempo.configure(text=f"{mins:02d}:{secs:02d}")

        # REGLA: Si pasa del tiempo principal, cambiar a tiempo extra
        if elapsed > self.tiempo_principal_operacion and not self.en_tiempo_extra:
            self.en_tiempo_extra = True
            # Cambiar el color del cronómetro a rojo/naranja brillante
            if self.cronometro_frame:
                self.cronometro_frame.configure(
                    fg_color=Config.COLOR_ROJO_BRILLANTE,
                    border_color=self._oscurecer_color(Config.COLOR_ROJO_BRILLANTE)
                )
            if self.label_tiempo_titulo:
                self.label_tiempo_titulo.configure(text="⚠️ TIEMPO EXTRA ⚠️")

        # REGLA: Si llega al tiempo máximo, finalizar automáticamente esta operación
        if elapsed >= self.tiempo_maximo_operacion:
            self.detener_cronometro()
            self.test_finalizado_automaticamente = True

            # Determinar qué sigue después
            idx_actual = self.operaciones_nivel.index(self.operacion_actual)
            es_ultima_operacion = (idx_actual == len(self.operaciones_nivel) - 1)

            # Mensaje personalizado según lo que sigue
            if es_ultima_operacion:
                mensaje_siguiente = "Al presionar Aceptar verás el resumen final de tus resultados."
            else:
                siguiente_op = self.operaciones_nivel[idx_actual + 1]
                nombre_siguiente = self.obtener_nombre_operacion(siguiente_op)
                mensaje_siguiente = f"Al presionar Aceptar continuarás con la siguiente operación: {nombre_siguiente}."

            messagebox.showwarning(
                "⏰ Tiempo Agotado",
                f"¡Se acabó el tiempo para esta operación!\n\n"
                f"Has llegado al límite de {int(self.tiempo_maximo_operacion//60)} minutos.\n\n"
                f"{mensaje_siguiente}"
            )
            self.finalizar_operacion_automatica()
        else:
            self.root.after(1000, self.actualizar_cronometro)

    def finalizar_operacion_automatica(self):
        """Finaliza la operación actual automáticamente cuando se acaba el tiempo"""
        # Detener cronómetro si está corriendo
        if self.corriendo:
            self.detener_cronometro()

        # Evaluar y guardar la operación actual
        if self.ejercicios and not self.finalizado:
            correctas, incorrectas = self._evaluar_respuestas()
            # Deshabilitar entries
            for entry in self.entries.values():
                entry.configure(state="disabled")
            # Deshabilitar botón finalizar
            if self.boton_finalizar:
                self.boton_finalizar.configure(state="disabled", fg_color="#CCCCCC", text_color="#666666")
            self.finalizado = True
            self._guardar_resultado(correctas, incorrectas)

        # Verificar si hay más operaciones pendientes
        idx_actual = self.operaciones_nivel.index(self.operacion_actual)
        es_ultima_operacion = (idx_actual == len(self.operaciones_nivel) - 1)

        if es_ultima_operacion:
            # Era la última operación, mostrar resultados finales
            self.mostrar_resultados_finales()
        else:
            # Terminar con esta operación completa y continuar con la siguiente
            self.mostrar_resumen_operacion_completa()

    def finalizar_operacion(self):
        """Finaliza operación actual"""
        if self.finalizado:
            messagebox.showinfo("⚠️", "Ya finalizado")
            return

        if self.tiempo_operacion_actual == 0 and not self.corriendo:
            messagebox.showwarning("⚠️", "El cronómetro aún no ha iniciado")
            return

        self.detener_cronometro()
        correctas, incorrectas = self._evaluar_respuestas()

        # Deshabilitar entries
        for entry in self.entries.values():
            entry.configure(state="disabled")

        # Deshabilitar botón finalizar
        if self.boton_finalizar:
            self.boton_finalizar.configure(state="disabled", fg_color="#CCCCCC", text_color="#666666")

        self.finalizado = True
        self._guardar_resultado(correctas, incorrectas)

        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)
        total = len(self.ejercicios)
        porcentaje = (correctas / total) * 100
        emoji = "🌟" if porcentaje >= 90 else "👍" if porcentaje >= 70 else "💪"

        messagebox.showinfo(
            f"{emoji} ¡Completado!",
            f"{nombre_op} - Tabla {self.tabla_actual}\n\n"
            f"Aciertos: {correctas}/{total}\n"
            f"Tiempo: {int(self.tiempo_operacion_actual//60):02d}:{int(self.tiempo_operacion_actual%60):02d}"
        )

        idx_actual = self.operaciones_nivel.index(self.operacion_actual)
        es_ultima_operacion = (idx_actual == len(self.operaciones_nivel) - 1)
        es_ultima_tabla = (self.tabla_actual == self.tabla_max)

        if es_ultima_tabla and es_ultima_operacion:
            self.mostrar_resultados_finales()
        elif es_ultima_tabla:
            self.mostrar_resumen_operacion_completa()

    def _evaluar_respuestas(self):
        """Evalúa respuestas"""
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

    def _guardar_resultado(self, correctas, incorrectas):
        """Guarda resultado"""
        clave = f"{self.operacion_actual}_tabla{self.tabla_actual}"
        self.resultados_operacion[clave] = {
            "operacion": self.operacion_actual,
            "tabla": self.tabla_actual,
            "correctas": correctas,
            "incorrectas": incorrectas,
            "total": len(self.ejercicios),
            "tiempo": self.tiempo_operacion_actual
        }

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

    def siguiente_operacion(self):
        """Avanza a siguiente tabla/operación"""
        clave_actual = f"{self.operacion_actual}_tabla{self.tabla_actual}"

        if clave_actual not in self.resultados_operacion:
            if not messagebox.askyesno("⚠️", "¿Pasar sin a la siguiente tabla?"):
                return
            if self.corriendo:
                self.detener_cronometro()
            correctas, incorrectas = self._evaluar_respuestas()
            self._guardar_resultado(correctas, incorrectas)
            self.finalizado = True

        # Detener cronómetro sin reiniciar
        if self.corriendo:
            self.detener_cronometro()

        if self.tabla_actual < self.tabla_max:
            self.tabla_actual += 1
            self.mostrar_pantalla_ejercicios()
        else:
            self.mostrar_resumen_operacion_completa()

    def mostrar_resumen_operacion_completa(self):
        """Muestra resumen de operación con pantalla visual"""
        self.limpiar_pantalla()

        # Calcular estadísticas de esta operación
        correctas_total = 0
        incorrectas_total = 0
        total_preguntas = 0

        for clave, r in self.resultados_operacion.items():
            if r["operacion"] == self.operacion_actual:
                correctas_total += r["correctas"]
                incorrectas_total += r["incorrectas"]
                total_preguntas += r["total"]

        # Usar el tiempo acumulado del cronómetro (ya incluye todas las tablas)
        tiempo_total_op = self.tiempo_operacion_actual

        nombre_op = self.obtener_nombre_operacion(self.operacion_actual)
        emoji_op = self.obtener_emoji_operacion(self.operacion_actual)
        color_operacion = self.obtener_color_operacion(self.operacion_actual)

        # Calcular nota parcial de esta operación
        nota_operacion = round((correctas_total / total_preguntas) * 100) if total_preguntas > 0 else 0

        # Determinar mensaje según nota
        if nota_operacion >= 90:
            mensaje = "¡EXCELENTE!"
            color_nota = Config.COLOR_VERDE_BRILLANTE
        elif nota_operacion >= 70:
            mensaje = "¡MUY BIEN!"
            color_nota = Config.COLOR_AZUL_BRILLANTE
        else:
            mensaje = "¡SIGUE PRACTICANDO!"
            color_nota = Config.COLOR_NARANJA_BRILLANTE

        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color="#E3F2FD")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Contenedor central
        center_frame = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=20,
            border_width=4,
            border_color=color_operacion
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        content_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        content_frame.pack(padx=50, pady=40)

        # Emoji de la operación
        ctk.CTkLabel(
            content_frame,
            text=emoji_op,
            font=("Segoe UI Emoji", 60)
        ).pack(pady=(0, 10))

        # Mensaje motivador
        ctk.CTkLabel(
            content_frame,
            text=mensaje,
            font=("Comic Sans MS", 32, "bold"),
            text_color=color_nota
        ).pack(pady=(0, 5))

        # Nombre de la operación
        ctk.CTkLabel(
            content_frame,
            text=f"{nombre_op} Completada",
            font=("Comic Sans MS", 20, "bold"),
            text_color=color_operacion
        ).pack(pady=(0, 20))

        # Tabla de resultados
        tabla_frame = ctk.CTkFrame(
            content_frame,
            fg_color=self._aclarar_color(color_operacion),
            corner_radius=15
        )
        tabla_frame.pack(fill="x", pady=(0, 20), padx=20)

        # Encabezado
        header_frame = ctk.CTkFrame(tabla_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            header_frame,
            text="Correctas ✅",
            font=("Comic Sans MS", 16, "bold"),
            text_color="white",
            width=150
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header_frame,
            text="Incorrectas ❌",
            font=("Comic Sans MS", 16, "bold"),
            text_color="white",
            width=150
        ).pack(side="left", padx=10)

        # Valores
        valores_frame = ctk.CTkFrame(tabla_frame, fg_color="transparent")
        valores_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            valores_frame,
            text=str(correctas_total),
            font=("Comic Sans MS", 36, "bold"),
            text_color="white",
            width=150
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            valores_frame,
            text=str(incorrectas_total),
            font=("Comic Sans MS", 36, "bold"),
            text_color="white",
            width=150
        ).pack(side="left", padx=10)

        # Tiempo
        ctk.CTkLabel(
            content_frame,
            text=f"⏱️ Tiempo: {int(tiempo_total_op//60):02d}:{int(tiempo_total_op%60):02d}",
            font=("Comic Sans MS", 18),
            text_color="#666666"
        ).pack(pady=(0, 25))

        # Determinar siguiente paso
        idx_actual = self.operaciones_nivel.index(self.operacion_actual)

        if idx_actual + 1 < len(self.operaciones_nivel):
            siguiente_op = self.operaciones_nivel[idx_actual + 1]
            nombre_siguiente = self.obtener_nombre_operacion(siguiente_op)

            ctk.CTkButton(
                content_frame,
                text=f"➡️ Continuar con {nombre_siguiente}",
                font=("Comic Sans MS", 20, "bold"),
                width=350,
                height=65,
                corner_radius=20,
                fg_color=Config.COLOR_VERDE_BRILLANTE,
                hover_color=self._aclarar_color(Config.COLOR_VERDE_BRILLANTE),
                text_color="white",
                command=lambda: self._continuar_siguiente_operacion(siguiente_op)
            ).pack()
        else:
            ctk.CTkButton(
                content_frame,
                text="🎉 Ver Resultados Finales",
                font=("Comic Sans MS", 20, "bold"),
                width=350,
                height=65,
                corner_radius=20,
                fg_color=Config.COLOR_VERDE_BRILLANTE,
                hover_color=self._aclarar_color(Config.COLOR_VERDE_BRILLANTE),
                text_color="white",
                command=self.mostrar_resultados_finales
            ).pack()

    def _continuar_siguiente_operacion(self, siguiente_op):
        """Continúa con la siguiente operación"""
        self.operacion_actual = siguiente_op
        self.tabla_actual = self.obtener_tabla_minima(siguiente_op)
        # Reiniciar tiempo para la nueva operación
        self.tiempo_operacion_actual = 0
        self.en_tiempo_extra = False
        self.solicitar_limite_tabla_operacion()

    def mostrar_resultados_operacion(self):
        """Muestra resultados parciales"""
        if not self.resultados_operacion:
            messagebox.showinfo("📊", "Aún no has completado operaciones")
            return

        texto = "📊 RESULTADOS PARCIALES\n\n"
        total_ac = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_pr = sum(r["total"] for r in self.resultados_operacion.values())

        for clave, r in sorted(self.resultados_operacion.items()):
            op = r["operacion"]
            emoji = self.obtener_emoji_operacion(op)
            tabla = r["tabla"]
            mins = int(r["tiempo"] // 60)
            secs = int(r["tiempo"] % 60)
            texto += f"{emoji} {op.upper()} T{tabla}: {r['correctas']}/{r['total']} | {mins:02d}:{secs:02d}\n"

        texto += f"\nTOTAL: {total_ac}/{total_pr}"
        messagebox.showinfo("📊 Resultados", texto)

    def calcular_nota_final(self):
        """Calcula nota final con penalización por tiempo extra en cada operación"""
        total_aciertos = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_preguntas = sum(r["total"] for r in self.resultados_operacion.values())
        nota_base = (total_aciertos / total_preguntas) * 100 if total_preguntas > 0 else 0

        # Calcular penalización por cada operación que haya excedido el tiempo principal
        penalizacion_total = 0

        # Calcular penalización por cada operación/tabla
        for r in self.resultados_operacion.values():
            tiempo_operacion = r["tiempo"]
            operacion = r["operacion"]

            # Determinar tiempo principal según la operación
            if operacion in ["potencia", "raiz"]:
                tiempo_principal = Config.POTENCIA_RAIZ_TIEMPO_PRINCIPAL
                penalizacion_maxima = 2  # Máximo 2 puntos para potenciación/radicación (2 minutos extra)
            elif self.nivel == 1:
                tiempo_principal = Config.NIVEL_1_TIEMPO_PRINCIPAL
                penalizacion_maxima = Config.PENALIZACION_MAXIMA
            else:  # Nivel 2 y 3
                tiempo_principal = Config.NIVEL_2_TIEMPO_PRINCIPAL
                penalizacion_maxima = Config.PENALIZACION_MAXIMA

            if tiempo_operacion > tiempo_principal:
                # Tiempo extra en segundos
                tiempo_extra = tiempo_operacion - tiempo_principal
                # Convertir a minutos (redondeando hacia arriba)
                minutos_extra = int(tiempo_extra / 60)
                if tiempo_extra % 60 > 0:
                    minutos_extra += 1

                # Penalización: 1 punto por minuto extra, con máximo según la operación
                penalizacion_operacion = min(minutos_extra * Config.PENALIZACION_POR_MINUTO, penalizacion_maxima)
                penalizacion_total += penalizacion_operacion

        tiempo_total = sum(r["tiempo"] for r in self.resultados_operacion.values())
        nota_final = max(round(nota_base - penalizacion_total, 1), 0)
        return nota_final, tiempo_total, round(penalizacion_total, 1)

    def _agrupar_resultados_por_operacion(self):
        """Agrupa resultados"""
        resultados_agrupados = {}
        for clave, r in self.resultados_operacion.items():
            op = r["operacion"]
            if op not in resultados_agrupados:
                resultados_agrupados[op] = []
            resultados_agrupados[op].append(r)
        return resultados_agrupados

    def reiniciar_aplicativo(self):
        """Reinicia aplicación"""
        self._inicializar_variables()
        self.mostrar_pantalla_inicio()

    # ==================== IMPRESIÓN (mantiene funcionalidad original) ====================

    def imprimir_ejercicios(self):
        """Imprime ejercicios en HTML"""
        if not self.historial_ejercicios:
            messagebox.showinfo("📝", "No hay ejercicios")
            return
        html = self._generar_html_ejercicios()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html)
            temp_file = f.name
        self._abrir_archivo_en_navegador(temp_file)

    def imprimir_resultados(self):
        """Imprime resultados en HTML"""
        nota, tiempo, pen = self.calcular_nota_final()
        html = self._generar_html_reporte(nota, pen)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html)
            temp_file = f.name
        self._abrir_archivo_en_navegador(temp_file)

    def _generar_html_ejercicios(self):
        """Genera HTML ejercicios"""
        ejercicios_por_operacion = {}
        orden_operaciones = []
        for ej in self.historial_ejercicios:
            clave = f"{ej['operacion']}_tabla{ej['tabla']}"
            if clave not in ejercicios_por_operacion:
                ejercicios_por_operacion[clave] = {
                    "operacion": ej["operacion"], "tabla": ej["tabla"], "ejercicios": []}
                orden_operaciones.append(clave)
            ejercicios_por_operacion[clave]["ejercicios"].append(ej)

        html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
        <title>Ejercicios</title><style>
        body {{font-family: Arial; margin: 40px;}}
        h1 {{color: {Config.COLOR_MORADO_BRILLANTE}; text-align: center;}}
        table {{width: 100%; border-collapse: collapse; margin: 20px 0;}}
        th {{background-color: {Config.COLOR_MORADO_BRILLANTE}; color: white; padding: 10px;}}
        td {{padding: 8px; border: 1px solid #ddd;}}
        .correcto {{color: {Config.COLOR_VERDE_BRILLANTE}; font-weight: bold;}}
        .incorrecto {{color: {Config.COLOR_ROJO_BRILLANTE}; font-weight: bold;}}
        </style></head><body>
        <h1>EJERCICIOS REALIZADOS</h1>
        <p style="text-align:center;"><strong>Estudiante:</strong> {self.nombre} |
        <strong>Curso:</strong> {self.curso} | <strong>Fecha:</strong> {self.fecha}</p><hr>"""

        for clave in orden_operaciones:
            grupo = ejercicios_por_operacion[clave]
            nombre_op = self.obtener_nombre_operacion(grupo["operacion"])
            html += f"""<h2>{nombre_op} - Tabla {grupo['tabla']}</h2>
            <table><thead><tr><th>Ejercicio</th><th>Tu respuesta</th>
            <th>Correcta</th><th>Estado</th></tr></thead><tbody>"""
            for ej in grupo["ejercicios"]:
                clase = "correcto" if ej["correcto"] else "incorrecto"
                estado = "Correcto" if ej["correcto"] else "Incorrecto"
                resp = ej["respuesta_usuario"] if ej["respuesta_usuario"] else "(vacío)"
                html += f"""<tr><td>{ej['ejercicio']}</td><td>{resp}</td>
                <td>{ej['respuesta_correcta']}</td><td class="{clase}">{estado}</td></tr>"""
            html += "</tbody></table>"
        html += "</body></html>"
        return html

    def _generar_html_reporte(self, nota, pen):
        """Genera HTML reporte"""
        color_nota = Config.COLOR_VERDE_BRILLANTE if nota >= 70 else Config.COLOR_ROJO_BRILLANTE
        html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
        <title>Resultados</title><style>
        body {{font-family: Arial; margin: 40px;}}
        h1 {{color: {Config.COLOR_MORADO_BRILLANTE}; text-align: center;}}
        .nota {{text-align: center; font-size: 36px; font-weight: bold; color: {color_nota};}}
        table {{width: 100%; border-collapse: collapse; margin: 20px 0;}}
        th {{background-color: {Config.COLOR_MORADO_BRILLANTE}; color: white; padding: 12px;}}
        td {{padding: 10px; border: 1px solid #ddd;}}
        </style></head><body>
        <h1>RESULTADOS - TEST DE AGILIDAD MENTAL</h1>
        <p style="text-align:center;"><strong>Estudiante:</strong> {self.nombre} |
        <strong>Curso:</strong> {self.curso} | <strong>Fecha:</strong> {self.fecha}</p>
        <div class="nota">NOTA FINAL: {nota}/100</div>"""

        if pen > 0:
            html += f'<p style="text-align:center;color:{Config.COLOR_ROJO_BRILLANTE};"><strong>Penalización: -{pen} pts</strong></p>'

        html += f"""<hr><h2>DETALLE DE RESULTADOS</h2>
        <table><thead><tr><th>Operación</th><th>Hasta Tabla</th>
        <th>Correctas</th><th>Incorrectas</th></tr></thead><tbody>
        {self._generar_filas_tabla_html()}</tbody></table></body></html>"""
        return html

    def _generar_filas_tabla_html(self):
        """Genera filas HTML"""
        resultados_por_operacion = self._agrupar_resultados_por_operacion()
        filas = ""
        for operacion in self.operaciones_nivel:
            if operacion in resultados_por_operacion:
                nombre_op = self.obtener_nombre_operacion(operacion)
                tablas = resultados_por_operacion[operacion]
                total_c = sum(t["correctas"] for t in tablas)
                total_i = sum(t["incorrectas"] for t in tablas)
                tabla_max = max(t["tabla"] for t in tablas)
                filas += f"<tr><td><strong>{nombre_op}</strong></td><td><strong>{tabla_max}</strong></td>"
                filas += f"<td><strong>{total_c}</strong></td><td><strong>{total_i}</strong></td></tr>"

        total_c = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_i = sum(r["incorrectas"] for r in self.resultados_operacion.values())
        filas += f"""<tr style="background-color:#c8e6c9;"><td colspan="2"><strong>TOTAL</strong></td>
        <td><strong>{total_c}</strong></td><td><strong>{total_i}</strong></td></tr>"""
        return filas

    def _abrir_archivo_en_navegador(self, archivo):
        """Abre archivo en navegador"""
        try:
            sistema = platform.system()
            if sistema == 'Windows':
                os.startfile(archivo)
            elif sistema == 'Darwin':
                subprocess.run(['open', archivo])
            else:
                subprocess.run(['xdg-open', archivo])
            messagebox.showinfo("🖨️", "Archivo abierto. Usa Ctrl+P para imprimir")
        except Exception as e:
            messagebox.showerror("❌", f"Error al abrir: {e}")


# ==================== INICIO ====================
if __name__ == "__main__":
    root = ctk.CTk()
    root.iconbitmap(resource_path("logo.ico"))
    app = AgilidadMentalApp(root)
    root.mainloop()
