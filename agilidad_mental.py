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
        self.tabla_max = 10
        self.tiempo_inicio = None
        self.tiempo_total = 0
        self.corriendo = False

        # Resultados
        self.resultados_operacion = {}
        self.operaciones_nivel = []
        self.operacion_actual = ""
        self.ejercicios = []
        self.entries = {}

        self.mostrar_pantalla_inicio()

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_pantalla_inicio(self):
        self.limpiar_pantalla()

        # Logo (izquierda)
        frame_izq = tk.Frame(self.root, bg="#f0f0f0")
        frame_izq.pack(side="left", padx=60, pady=120, anchor="n")

        if PIL_AVAILABLE and os.path.exists("logo.png"):
            img = Image.open("logo.png")
            img = img.resize((280, 280), Image.Resampling.LANCZOS)
            logo = ImageTk.PhotoImage(img)
            label_logo = tk.Label(frame_izq, image=logo, bg="#f0f0f0")
            label_logo.image = logo
            label_logo.pack()
        else:
            tk.Label(frame_izq, text="LOGO\nINSTITUCIÓN", font=("Arial", 26, "bold"), bg="#f0f0f0", fg="#333",
                     justify="center").pack(pady=120)

        # Botones niveles (derecha)
        frame_der = tk.Frame(self.root, bg="#f0f0f0")
        frame_der.pack(side="right", padx=120, expand=True)

        tk.Label(frame_der, text="Seleccione el Nivel", font=("Arial", 22, "bold"), bg="#f0f0f0", fg="#003366").pack(pady=80)

        for nivel in [1, 2, 3]:
            btn = tk.Button(frame_der, text=f"Nivel {nivel}", font=("Arial", 20, "bold"), width=12, height=3,
                            bg="#4CAF50", fg="white", relief="raised",
                            command=lambda n=nivel: self.seleccionar_nivel(n))
            btn.pack(pady=25)

    def seleccionar_nivel(self, nivel):
        self.nivel = nivel
        if nivel == 1:
            self.operaciones_nivel = ["suma", "resta"]
            self.tiempo_principal = 12 * 60
            self.tiempo_maximo = 15 * 60
        elif nivel == 2:
            self.operaciones_nivel = ["suma", "resta", "multiplicación", "división"]
            self.tiempo_principal = 10 * 60
            self.tiempo_maximo = 12 * 60
        else:
            self.operaciones_nivel = ["suma", "resta", "multiplicación", "división", "potencia", "raíz"]
            self.tiempo_principal = 10 * 60
            self.tiempo_maximo = 12 * 60

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

        tk.Label(frame, text="Hasta qué tabla (suma):", font=("Arial", 16), bg="#f0f0f0").grid(row=4, column=0, sticky="w", pady=12)
        self.spin_tabla = tk.Spinbox(frame, from_=2, to=12, font=("Arial", 16), width=10)
        self.spin_tabla.grid(row=4, column=1, sticky="w", pady=12)

        tk.Button(frame, text="COMENZAR TEST", font=("Arial", 18, "bold"), width=25, height=2,
                  bg="#2196F3", fg="white", command=self.validar_datos).grid(row=5, column=0, columnspan=2, pady=50)

    def validar_datos(self):
        nombre = self.entry_nombre.get().strip()
        curso = self.combo_curso.get()
        if not nombre or not curso:
            messagebox.showwarning("Faltan datos", "Complete nombre y curso.")
            return
        self.nombre = nombre
        self.curso = curso
        self.fecha = self.entry_fecha.get()
        self.tabla_max = int(self.spin_tabla.get())
        self.resultados_operacion = {}
        self.operacion_actual = ""
        self.mostrar_pantalla_ejercicios()

    def generar_ejercicios(self, operacion):
        ejercicios = []
        for i in range(12):
            if operacion == "suma":
                a = random.randint(1, self.tabla_max * 10)
                b = random.randint(1, self.tabla_max * 10)
                resp = a + b
                texto = f"{a} + {b} ="
            elif operacion == "resta":
                a = random.randint(20, 300)
                b = random.randint(1, a-10)
                resp = a - b
                texto = f"{a} - {b} ="
            elif operacion == "multiplicación":
                a = random.randint(2, self.tabla_max)
                b = random.randint(2, 12)
                resp = a * b
                texto = f"{a} × {b} ="
            elif operacion == "división":
                b = random.randint(2, 12)
                resp = random.randint(2, 12)
                a = b * resp
                texto = f"{a} ÷ {b} ="
            elif operacion == "potencia":
                base = random.randint(2, 10)
                exp = random.randint(2, 4)
                resp = base ** exp
                texto = f"{base}^{exp} ="
            elif operacion == "raíz":
                cuadrados = [16,25,36,49,64,81,100,121,144,169,196,225,256,289,324,361,400]
                num = random.choice(cuadrados)
                resp = int(math.sqrt(num))
                texto = f"√{num} ="
            else:
                continue
            ejercicios.append({"texto": texto, "respuesta": resp, "id": i})
        return ejercicios

    def iniciar_cronometro(self):
        if not self.corriendo:
            self.tiempo_inicio = datetime.now()
            self.corriendo = True
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
            self.label_tiempo.config(text=f"Tiempo: {mins:02d}:{secs:02d}")
            self.root.after(1000, self.actualizar_cronometro)

    def mostrar_pantalla_ejercicios(self):
        self.limpiar_pantalla()
        self.corriendo = False
        self.tiempo_total = 0

        # Determinar operación actual
        if not self.operacion_actual or self.operacion_actual in self.resultados_operacion:
            idx = 0 if not self.operacion_actual else self.operaciones_nivel.index(self.operacion_actual) + 1
            if idx >= len(self.operaciones_nivel):
                self.mostrar_resultados_finales()
                return
            self.operacion_actual = self.operaciones_nivel[idx]

        self.ejercicios = self.generar_ejercicios(self.operacion_actual)

        # Frame principal con grid
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=40, pady=30)
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)

        # IZQUIERDA: Operaciones (sin fondo, sin bordes)
        left_frame = tk.Frame(main_frame, bg="#f0f0f0")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 40))

        tk.Label(left_frame, text=f"{self.operacion_actual.upper()}", font=("Arial", 26, "bold"),
                 bg="#f0f0f0", fg="#003366").pack(anchor="center", pady=(0, 20))

        self.label_tiempo = tk.Label(left_frame, text="Tiempo: 00:00", font=("Arial", 22, "bold"),
                                     bg="#f0f0f0", fg="red")
        self.label_tiempo.pack(pady=(0, 30))

        # Mostrar las 12 operaciones directamente
        self.entries = {}
        for i, ej in enumerate(self.ejercicios):
            row_frame = tk.Frame(left_frame, bg="#f0f0f0")
            row_frame.pack(pady=12, anchor="w", padx=100)

            tk.Label(row_frame, text=ej["texto"], font=("Arial", 20, "bold"), bg="#f0f0f0", width=14, anchor="e").pack(side="left")
            entry = tk.Entry(row_frame, font=("Arial", 20), width=10, justify="center", bd=3, relief="solid")
            entry.pack(side="left", padx=15)
            self.entries[ej["id"]] = entry

        # DERECHA: Botones verticales
        right_frame = tk.Frame(main_frame, bg="#f0f0f0")
        right_frame.grid(row=0, column=1, sticky="n")

        btn_style = {"font": ("Arial", 16, "bold"), "width": 22, "height": 3, "bd": 3, "relief": "raised"}

        tk.Button(right_frame, text="INICIAR", bg="#4CAF50", fg="white",
                  command=self.iniciar_cronometro, **btn_style).pack(pady=20)
        tk.Button(right_frame, text="FINALIZAR", bg="#FF9800", fg="white",
                  command=self.finalizar_operacion, **btn_style).pack(pady=20)
        tk.Button(right_frame, text="RESULTADOS", bg="#2196F3", fg="white",
                  command=self.mostrar_resultados_operacion, **btn_style).pack(pady=20)
        tk.Button(right_frame, text="SIGUIENTE →", bg="#9C27B0", fg="white",
                  command=self.siguiente_operacion, **btn_style).pack(pady=20)

    def finalizar_operacion(self):
        if self.tiempo_total == 0 and not self.corriendo:
            messagebox.showwarning("Error", "Primero debe presionar INICIAR")
            return
        self.detener_cronometro()

        correctas = 0
        for ej in self.ejercicios:
            val = self.entries[ej["id"]].get().strip()
            if val.isdigit() and int(val) == ej["respuesta"]:
                correctas += 1

        self.resultados_operacion[self.operacion_actual] = {
            "correctas": correctas, "total": 12, "tiempo": self.tiempo_total
        }

        messagebox.showinfo("¡Operación Completada!",
                            f"{self.operacion_actual.upper()}\n\nAciertos: {correctas}/12\nTiempo usado: {int(self.tiempo_total//60):02d}:{int(self.tiempo_total%60):02d}")

    def siguiente_operacion(self):
        if self.operacion_actual not in self.resultados_operacion:
            if not messagebox.askyesno("Advertencia", "¿Pasar sin guardar esta operación?"):
                return
        self.tiempo_total = 0
        self.mostrar_pantalla_ejercicios()

    def mostrar_resultados_operacion(self):
        if not self.resultados_operacion:
            messagebox.showinfo("Sin datos", "Aún no has completado operaciones.")
            return
        texto = "RESULTADOS HASTA AHORA\n\n"
        total_ac = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_pr = len(self.resultados_operacion) * 12
        for op, r in self.resultados_operacion.items():
            texto += f"{op.upper()}: {r['correctas']}/12  |  {int(r['tiempo']//60):02d}:{int(r['tiempo']%60):02d}\n"
        texto += f"\nTOTAL: {total_ac}/{total_pr}"
        messagebox.showinfo("Resultados Parciales", texto)

    def calcular_nota_final(self):
        total_aciertos = sum(r["correctas"] for r in self.resultados_operacion.values())
        total_preguntas = len(self.operaciones_nivel) * 12
        tiempo_total = sum(r["tiempo"] for r in self.resultados_operacion.values())

        nota = (total_aciertos / total_preguntas) * 100
        penalizacion = 0
        if tiempo_total > self.tiempo_principal:
            exceso = tiempo_total - self.tiempo_principal
            penalizacion = min((exceso / 60) * 2, 35)
        nota_final = max(round(nota - penalizacion, 1), 0)
        return nota_final, tiempo_total, penalizacion

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
