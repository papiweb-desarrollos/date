# Papiweb desarrollos informaticos
# Papitime
import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog, ttk
import calendar
import json
import os
import vlc
from datetime import datetime
import pytz
from PIL import Image, ImageTk, ImageDraw

# Configuración de Idioma
calendar.setfirstweekday(calendar.SUNDAY)
MESES_ES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIAS_ES = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]

COLORS = {
    'bg_dark': '#020617', 'bg_card': '#0f172a', 'win_header': '#1e3a8a',
    'primary': '#1e40af', 'gold': '#93c5fd', 'taskbar': '#000000',
    'start_btn': '#2563eb', 'today': '#fbbf24', 'text': '#f8fafc'
}

class PapiwebProOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Papiweb Sapphire OS 2026 - Ultra Edition")
        self.root.geometry("1600x900")
        
        self.data = self.load_data()
        self.tz = pytz.timezone('America/Argentina/Buenos_Aires')
        self.windows = {}
        self.pen_color = "#00d4ff"
        self.pen_size = 2

        self.setup_desktop()
        self.setup_taskbar()
        self.init_start_menu()

    def setup_desktop(self):
        self.desktop = tk.Canvas(self.root, highlightthickness=0)
        self.desktop.place(x=0, y=0, relwidth=1, relheight=0.95)

        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Cargar fondo.png adaptado a la resolución de la pantalla
        try:
            img = Image.open("fondo.png")
            # Redimensionar la imagen al tamaño de la pantalla
            img = img.resize((screen_width, int(screen_height * 0.95)), Image.Resampling.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(img)
            self.desktop.create_image(0, 0, image=self.bg_img, anchor="nw")
        except:
            self.desktop.configure(bg=COLORS['bg_dark'])

    def setup_taskbar(self):
        self.taskbar = tk.Frame(self.root, bg=COLORS['taskbar'], height=45)
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.btn_container = tk.Frame(self.taskbar, bg=COLORS['taskbar'])
        self.btn_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def init_start_menu(self):
        self.mb = tk.Menubutton(self.taskbar, text="💎 PAPIWEB", bg=COLORS['start_btn'], 
                               fg="white", font=("Arial", 10, "bold"), relief="flat", padx=20)
        self.menu = tk.Menu(self.mb, tearoff=0, bg=COLORS['bg_card'], fg="white", activebackground=COLORS['primary'])
        apps = [("📅 Agenda", self.open_calendar), ("🎨 Paint Pro", self.open_paint),
                ("🔢 Calculadora", self.open_calc), ("📝 Notas", self.open_notes),
                ("🎬 Media Player", self.open_media), ("💾 Exportar JSON", self.export_full_json),
                ("❓ Ayuda", self.show_help), ("🚪 Salir", self.exit_app)]
        for label, cmd in apps: self.menu.add_command(label=label, command=cmd)
        self.mb.config(menu=self.menu)
        self.mb.pack(side=tk.LEFT, fill=tk.Y)

    # --- MOTOR DE VENTANAS ---
    def create_win(self, wid, title, w, h, content_func):
        if wid in self.windows: return self.windows[wid]['f'].lift()

        # Asegurar que las dimensiones no excedan la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Limitar dimensiones al 90% de la pantalla
        max_width = int(screen_width * 0.9)
        max_height = int(screen_height * 0.8)

        adjusted_w = min(w, max_width)
        adjusted_h = min(h, max_height)

        f = tk.Frame(self.desktop, bg=COLORS['bg_card'], highlightthickness=1, highlightbackground=COLORS['gold'])
        f.place(x=100, y=50, width=adjusted_w, height=adjusted_h)

        bar = tk.Frame(f, bg=COLORS['win_header'], height=32, cursor="fleur")
        bar.pack(side=tk.TOP, fill=tk.X)
        tk.Label(bar, text=title, bg=COLORS['win_header'], fg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=10)

        # Botones de control
        tk.Button(bar, text="✕", command=lambda: self.close_win(wid), bg="#7f1d1d", fg="white", bd=0, width=3).pack(side=tk.RIGHT)
        tk.Button(bar, text="▢", command=lambda: self.toggle_fs(wid), bg="#334155", fg="white", bd=0, width=3).pack(side=tk.RIGHT)

        def move(e): f.place(x=f.winfo_x()+(e.x-f._x), y=f.winfo_y()+(e.y-f._y))
        bar.bind("<Button-1>", lambda e: (setattr(f, '_x', e.x), setattr(f, '_y', e.y), f.lift()))
        bar.bind("<B1-Motion>", move)

        self.windows[wid] = {'f': f, 'orig': (100, 50, adjusted_w, adjusted_h), 'fs': False}
        content = tk.Frame(f, bg=COLORS['bg_card'])
        content.pack(fill=tk.BOTH, expand=True)
        content_func(content)

    def toggle_fs(self, wid):
        w_data = self.windows[wid]
        if not w_data['fs']:
            w_data['f'].place(x=0, y=0, relwidth=1, relheight=1)
            w_data['fs'] = True
        else:
            x, y, w, h = w_data['orig']
            w_data['f'].place(x=x, y=y, width=w, height=h, relwidth=0, relheight=0)
            w_data['fs'] = False

    def close_win(self, wid):
        self.windows[wid]['f'].destroy()
        del self.windows[wid]

    # --- APP: AGENDA ESPAÑOL ---
    def open_calendar(self):
        self.create_win("cal", "AGENDA MASTER 2026", 1100, 750, self.setup_cal_ui)

    def setup_cal_ui(self, p):
        import math

        # Marco principal para contener el calendario y el reloj
        main_container = tk.Frame(p, bg=COLORS['bg_card'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Marco para el calendario (parte izquierda)
        calendar_container = tk.Frame(main_container, bg=COLORS['bg_card'])
        calendar_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        now = datetime.now()

        for m in range(1, 13):
            f = tk.Frame(calendar_container, bg=COLORS['bg_card'], bd=1, relief="flat", highlightthickness=1, highlightbackground="#1e293b")
            f.grid(row=(m-1)//4, column=(m-1)%4, sticky="nsew", padx=3, pady=3)
            tk.Label(f, text=MESES_ES[m-1].upper(), fg=COLORS['gold'], bg=COLORS['bg_card'], font=("Arial", 9, "bold")).pack()

            d_frame = tk.Frame(f, bg=COLORS['bg_card'])
            d_frame.pack()

            for i, d in enumerate(DIAS_ES):
                tk.Label(d_frame, text=d, fg="#475569", bg=COLORS['bg_card'], font=("Arial", 6)).grid(row=0, column=i)

            cal = calendar.monthcalendar(2026, m)
            for r, week in enumerate(cal):
                for c, day in enumerate(week):
                    if day == 0: continue
                    is_today = (day == now.day and m == now.month)
                    btn = tk.Button(d_frame, text=str(day), width=2, relief="flat",
                                   bg=COLORS['today'] if is_today else COLORS['bg_card'],
                                   fg="black" if is_today else "white", font=("Arial", 7),
                                   command=lambda d=day, m=m: self.edit_event(d, m))
                    btn.grid(row=r+1, column=c)

        for i in range(4): calendar_container.grid_columnconfigure(i, weight=1)
        for i in range(3): calendar_container.grid_rowconfigure(i, weight=1)

        # Marco para el reloj analógico (parte derecha)
        clock_frame = tk.Frame(main_container, bg=COLORS['bg_card'], width=200)
        clock_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        clock_frame.pack_propagate(False)  # Mantener el ancho fijo

        # Título del reloj
        tk.Label(clock_frame, text="RELOJ", fg=COLORS['gold'], bg=COLORS['bg_card'], font=("Arial", 10, "bold")).pack(pady=5)

        # Canvas para el reloj analógico
        self.clock_canvas = tk.Canvas(clock_frame, width=180, height=180, bg=COLORS['bg_card'], highlightthickness=0)
        self.clock_canvas.pack(pady=10)

        # Fecha debajo del reloj
        self.date_label = tk.Label(clock_frame, text="", fg=COLORS['gold'], bg=COLORS['bg_card'], font=("Arial", 10, "bold"))
        self.date_label.pack(pady=5)

        # Iniciar la actualización del reloj
        self.update_analog_clock()

    def edit_event(self, day, month):
        """Editar evento para un día específico"""
        # Esta función abre una ventana para editar eventos del calendario
        event_window = tk.Toplevel(self.root)
        event_window.title(f"Editar evento - {day}/{month}")
        event_window.geometry("400x300")
        event_window.configure(bg=COLORS['bg_card'])

        # Campo para ingresar el evento
        tk.Label(event_window, text=f"Evento para {day}/{month}:", bg=COLORS['bg_card'], fg=COLORS['text']).pack(pady=10)

        event_text = tk.Text(event_window, height=10, width=40, bg=COLORS['bg_dark'], fg=COLORS['text'])
        event_text.pack(pady=10, padx=20)

        # Cargar evento existente si hay alguno
        date_str = f"{datetime.now().year}-{month:02d}-{day:02d}"
        if date_str in self.data.get('events', {}):
            event_text.insert("1.0", self.data['events'][date_str])

        def save_event():
            # Guardar el evento
            event_content = event_text.get("1.0", tk.END).strip()
            if 'events' not in self.data:
                self.data['events'] = {}
            self.data['events'][date_str] = event_content
            event_window.destroy()

        # Botón para guardar
        tk.Button(event_window, text="Guardar", command=save_event,
                 bg=COLORS['primary'], fg=COLORS['text']).pack(pady=10)

    # --- APP: PAINT PRO CON FONDO ---
    def open_paint(self):
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calcular dimensiones para la ventana de paint (proporcional a la pantalla)
        window_width = min(800, int(screen_width * 0.8))
        window_height = min(600, int(screen_height * 0.7))

        self.create_win("paint", "PAINT PRO", window_width, window_height, self.setup_paint_ui)

    def setup_paint_ui(self, p):
        tools = tk.Frame(p, bg="#0f172a", height=40)
        tools.pack(side=tk.TOP, fill=tk.X)

        icons = [("🎨", self.pick_color), ("✏️", lambda: self.set_tool(2)),
                 ("🖌️", lambda: self.set_tool(5)), ("🧽", self.enable_eraser),
                 ("🔍", self.toggle_magnifier), ("✍️", self.enable_text_mode)]
        for icon, cmd in icons:
            tk.Button(tools, text=icon, command=cmd, bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2, pady=2)

        # Botón para limpiar todo el lienzo
        tk.Button(tools, text="🗑️", command=self.clear_canvas, bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2)

        # Botón para pantalla completa
        tk.Button(tools, text="⛶", command=self.toggle_fullscreen, bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2)

        # Botón para exportar
        tk.Button(tools, text="📤", command=self.export_canvas, bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2)

        # Botones para controlar zoom de la lupa
        zoom_frame = tk.Frame(tools, bg="#0f172a")
        zoom_frame.pack(side=tk.LEFT, padx=5)

        tk.Button(zoom_frame, text="-", command=self.decrease_magnification, bg="#1e293b", fg="white", width=2).pack(side=tk.LEFT)
        tk.Label(zoom_frame, text="Zoom", bg="#0f172a", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(zoom_frame, text="+", command=self.increase_magnification, bg="#1e293b", fg="white", width=2).pack(side=tk.LEFT)

        # Botón para colocar texto en coordenadas específicas
        tk.Button(tools, text="🎯", command=self.place_text_at_coordinates, bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2)

        # Botones para deshacer y rehacer
        tk.Button(tools, text="↩️", command=self.undo_action, bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(tools, text="↪️", command=self.redo_action, bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2)

        # Botones para cambiar rápidamente la fuente
        font_frame = tk.Frame(tools, bg="#0f172a")
        font_frame.pack(side=tk.LEFT, padx=2)

        tk.Button(font_frame, text="◀", command=self.prev_font, bg="#1e293b", fg="white", width=2).pack(side=tk.LEFT)
        tk.Label(font_frame, text="Font", bg="#0f172a", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=1)
        tk.Button(font_frame, text="▶", command=self.next_font, bg="#1e293b", fg="white", width=2).pack(side=tk.LEFT)

        # Barra de estado para mostrar información
        self.status_bar = tk.Label(p, text="Modo: Dibujo | Herramienta: Lápiz", bg="#1e293b", fg="white", anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.cv = tk.Canvas(p, bg="black", highlightthickness=0)
        self.cv.pack(fill=tk.BOTH, expand=True, pady=(0, 2))  # Pequeño padding arriba de la barra de estado

        # Intentar cargar imagen de fondo
        self.paint_bg_path = "paint.png"
        self.p_bg = None
        self.load_paint_background()

        # Vincular evento de cambio de tamaño para actualizar el fondo
        self.cv.bind("<Configure>", self.on_paint_resize)

        # Vincular eventos para la lupa
        self.magnifier_active = False
        self.text_mode_active = False
        self.magnification_level = 5  # Nivel inicial de magnificación
        self.drawing_history = []  # Registrar las operaciones de dibujo para la lupa
        self.history_index = -1  # Índice actual en el historial
        self.history_limit = 50  # Límite de operaciones en el historial
        self.available_fonts = ["Arial", "Times", "Courier", "Helvetica", "Comic Sans MS", "Verdana", "Georgia", "Palatino", "Garamond", "Trebuchet MS", "Arial Black", "Impact"]
        self.current_font_index = 0  # Índice de la fuente actual
        def set_initial_coords(e):
            # Si hay un trazo en curso, guardarlo en el historial
            if hasattr(self, 'current_stroke') and self.current_stroke is not None:
                self.add_to_history(self.current_stroke)
                self.current_stroke = None
            self.lx = e.x
            self.ly = e.y

        self.cv.bind("<B1-Motion>", self.draw_paint)
        self.cv.bind("<Button-1>", set_initial_coords)
        self.cv.bind("<ButtonRelease-1>", self.finish_stroke)
        self.cv.bind("<Motion>", self.on_mouse_move)
        self.cv.bind("<MouseWheel>", self.on_mousewheel)  # Para Windows
        self.cv.bind("<Button-4>", self.on_mousewheel_up)  # Para Linux
        self.cv.bind("<Button-5>", self.on_mousewheel_down)  # Para Linux
        self.cv.focus_set()  # Asegurar que el canvas pueda recibir eventos de teclado
        self.cv.bind("<Key>", self.on_key_press)

        # Vincular eventos de mousewheel a la ventana principal también
        p.bind("<MouseWheel>", self.on_mousewheel)  # Para Windows
        p.bind("<Button-4>", self.on_mousewheel_up)  # Para Linux
        p.bind("<Button-5>", self.on_mousewheel_down)  # Para Linux
        p.bind("<Key>", self.on_key_press)

        # Vincular evento de movimiento del mouse a la ventana principal para actualizar la lupa
        p.bind("<Motion>", self.on_main_window_mouse_move, add="+")

    def toggle_magnifier(self):
        """Activa/desactiva la herramienta de lupa"""
        self.magnifier_active = not self.magnifier_active
        self.text_mode_active = False  # Desactivar modo texto cuando se activa la lupa

        if self.magnifier_active:
            # Activar lupa
            mode = "Lupa"
            tool = "Lupa"
            self.status_bar.config(text=f"Modo: {mode} | Herramienta: {tool} | Zoom: {self.magnification_level}x")

            # Crear ventana de lupa si no existe
            if not hasattr(self, 'magnifier_window') or not self.magnifier_window.winfo_exists():
                self.create_magnifier_window()
            else:
                self.magnifier_window.deiconify()  # Mostrar ventana si estaba oculta
        else:
            # Desactivar lupa
            mode = "Dibujo"
            tool = "Lápiz"
            self.status_bar.config(text=f"Modo: {mode} | Herramienta: {tool}")

            # Ocultar ventana de lupa
            if hasattr(self, 'magnifier_window') and self.magnifier_window.winfo_exists():
                self.magnifier_window.withdraw()

    def increase_magnification(self):
        """Aumenta el nivel de magnificación"""
        if self.magnifier_active:
            self.magnification_level = min(self.magnification_level + 1, 10)  # Máximo 10x
            self.status_bar.config(text=f"Modo: Lupa | Herramienta: Lupa | Zoom: {self.magnification_level}x")

    def decrease_magnification(self):
        """Disminuye el nivel de magnificación"""
        if self.magnifier_active:
            self.magnification_level = max(self.magnification_level - 1, 1)  # Mínimo 1x
            self.status_bar.config(text=f"Modo: Lupa | Herramienta: Lupa | Zoom: {self.magnification_level}x")

    def create_magnifier_window(self):
        """Crea la ventana de la lupa"""
        self.magnifier_window = tk.Toplevel(self.root)
        self.magnifier_window.title("Lupa")
        self.magnifier_window.geometry("300x300")
        self.magnifier_window.overrideredirect(True)  # Ventana sin bordes
        self.magnifier_window.attributes('-topmost', True)  # Siempre visible

        # Canvas para mostrar la imagen ampliada
        self.magnifier_canvas = tk.Canvas(self.magnifier_window, width=300, height=300, bg='white')
        self.magnifier_canvas.pack(fill=tk.BOTH, expand=True)

        # Ocultar la ventana inicialmente
        self.magnifier_window.withdraw()

    def enable_text_mode(self):
        """Activa el modo de escritura de texto"""
        self.text_mode_active = True
        self.magnifier_active = False  # Desactivar lupa cuando se activa el modo texto
        self.status_bar.config(text="Modo: Texto | Haz clic donde quieras escribir")

        # Ocultar ventana de lupa si está activa
        if hasattr(self, 'magnifier_window') and self.magnifier_window.winfo_exists():
            self.magnifier_window.withdraw()

        # Cambiar cursor para indicar modo texto
        self.cv.config(cursor="cross")

        # Vincular evento de clic para insertar texto
        self.cv.bind("<Button-1>", self.start_text_input)

    def start_text_input(self, event):
        """Inicia la entrada de texto en la posición del clic"""
        # Pedir texto al usuario
        from tkinter.simpledialog import askstring
        text = askstring("Texto", "Introduce el texto:")

        if text:
            # Crear ventana de diálogo para elegir fuente
            font_window = tk.Toplevel(self.root)
            font_window.title("Fuente del Texto")
            font_window.geometry("300x200")
            font_window.configure(bg=COLORS['bg_card'])

            # Variables para la fuente
            current_font = self.available_fonts[self.current_font_index] if self.available_fonts else "Arial"
            font_family_var = tk.StringVar(value=current_font)
            font_size_var = tk.StringVar(value="12")

            # Etiquetas y campos de entrada
            tk.Label(font_window, text="Tipo de Letra:", bg=COLORS['bg_card'], fg=COLORS['text']).pack(pady=5)
            font_family_entry = tk.Entry(font_window, textvariable=font_family_var)
            font_family_entry.pack(pady=5)

            tk.Label(font_window, text="Tamaño:", bg=COLORS['bg_card'], fg=COLORS['text']).pack(pady=5)
            font_size_entry = tk.Entry(font_window, textvariable=font_size_var)
            font_size_entry.pack(pady=5)

            def confirm_and_create_text():
                try:
                    font_family = font_family_var.get() or "Arial"
                    font_size = int(font_size_var.get()) or 12
                    font = (font_family, font_size)

                    # Registrar la operación de texto en el historial
                    operation = {
                        'type': 'text',
                        'x': event.x,
                        'y': event.y,
                        'text': text,
                        'fill': self.pen_color,
                        'font': font
                    }

                    self.add_to_history(operation)

                    # Dibujar el texto en la posición del clic
                    canvas_text_id = self.cv.create_text(event.x, event.y, text=text, fill=self.pen_color, font=font)

                    # Actualizar el ID del canvas en el historial
                    self.drawing_history[self.history_index]['canvas_id'] = canvas_text_id

                    # Permitir edición del texto recién creado
                    self.selected_text_id = self.history_index
                    self.enable_text_editing(canvas_text_id, event.x, event.y)

                    font_window.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Por favor ingrese un tamaño de fuente válido (número entero)")

            tk.Button(font_window, text="Crear Texto", command=confirm_and_create_text,
                      bg=COLORS['primary'], fg=COLORS['text']).pack(pady=10)

            tk.Button(font_window, text="Cancelar", command=font_window.destroy,
                      bg="#7f1d1d", fg=COLORS['text']).pack(pady=5)

        else:
            # Si se cancela la entrada de texto, volver al modo normal
            self.text_mode_active = False
            self.cv.config(cursor="")
            self.cv.bind("<B1-Motion>", self.draw_paint)
            def set_initial_coords(e):
                # Si hay un trazo en curso, guardarlo en el historial
                if hasattr(self, 'current_stroke') and self.current_stroke is not None:
                    self.add_to_history(self.current_stroke)
                    self.current_stroke = None
                self.lx = e.x
                self.ly = e.y

            self.cv.bind("<Button-1>", set_initial_coords)
            self.cv.bind("<ButtonRelease-1>", self.finish_stroke)
            self.status_bar.config(text="Modo: Dibujo | Herramienta: Lápiz")

    def enable_text_editing(self, canvas_text_id, x, y):
        """Habilita la edición del texto recién creado"""
        # Cambiar cursor para indicar que el texto es editable
        self.cv.config(cursor="plus")

        # Vincular eventos para mover el texto
        def start_move(event):
            # Detener temporalmente el dibujo del lápiz
            self.cv.unbind("<B1-Motion>")
            self.cv.unbind("<Button-1>")
            self.drag_data = {"x": event.x, "y": event.y, "item": canvas_text_id}

        def move_text(event):
            if hasattr(self, 'drag_data'):
                dx = event.x - self.drag_data["x"]
                dy = event.y - self.drag_data["y"]

                # Mover el texto en el canvas
                self.cv.move(self.drag_data["item"], dx, dy)

                # Actualizar la posición en el historial
                for item in self.drawing_history:
                    if item.get('canvas_id') == self.drag_data["item"]:
                        item['x'] += dx
                        item['y'] += dy
                        break

                # Actualizar drag_data para el próximo movimiento
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y

        def end_move(event):
            if hasattr(self, 'drag_data'):
                # Restaurar eventos de dibujo del lápiz
                self.cv.bind("<B1-Motion>", self.draw_paint)
                def set_initial_coords(e):
                    # Si hay un trazo en curso, guardarlo en el historial
                    if hasattr(self, 'current_stroke') and self.current_stroke is not None:
                        self.add_to_history(self.current_stroke)
                        self.current_stroke = None
                    self.lx = e.x
                    self.ly = e.y

                self.cv.bind("<Button-1>", set_initial_coords)
                self.cv.bind("<ButtonRelease-1>", self.finish_stroke)
                delattr(self, 'drag_data')

        # Vincular eventos de arrastre
        self.cv.tag_bind(canvas_text_id, "<Button-1>", start_move)
        self.cv.tag_bind(canvas_text_id, "<B1-Motion>", move_text)
        self.cv.tag_bind(canvas_text_id, "<ButtonRelease-1>", end_move)

        # Permitir edición del contenido del texto con doble clic
        def edit_text_content(event):
            from tkinter.simpledialog import askstring
            current_text = self.cv.itemcget(canvas_text_id, 'text')
            new_text = askstring("Editar Texto", "Modificar texto:", initialvalue=current_text)

            if new_text is not None:
                # Actualizar el texto en el canvas
                self.cv.itemconfig(canvas_text_id, text=new_text)

                # Actualizar el texto en el historial
                for item in self.drawing_history:
                    if item.get('canvas_id') == canvas_text_id:
                        # Guardar el texto anterior para posibilidad de deshacer
                        old_text = item['text']
                        item['text'] = new_text
                        break

        self.cv.tag_bind(canvas_text_id, "<Double-Button-1>", edit_text_content)

        # Permitir edición de fuente con clic derecho
        def edit_text_font(event):
            # Crear ventana de diálogo para editar fuente
            font_window = tk.Toplevel(self.root)
            font_window.title("Editar Fuente")
            font_window.geometry("300x200")
            font_window.configure(bg=COLORS['bg_card'])

            # Obtener fuente actual
            current_font = self.cv.itemcget(canvas_text_id, 'font')
            if isinstance(current_font, str):
                font_parts = current_font.split()
                if len(font_parts) >= 2:
                    current_family = font_parts[0]
                    current_size = int(font_parts[1])
                else:
                    current_family = "Arial"
                    current_size = 12
            else:
                current_family = current_font[0] if len(current_font) > 0 else "Arial"
                current_size = current_font[1] if len(current_font) > 1 else 12

            # Etiquetas y campos de entrada
            tk.Label(font_window, text="Tipo de Letra:", bg=COLORS['bg_card'], fg=COLORS['text']).pack(pady=5)
            font_family_var = tk.StringVar(value=current_family)
            font_family_entry = tk.Entry(font_window, textvariable=font_family_var)
            font_family_entry.pack(pady=5)

            tk.Label(font_window, text="Tamaño:", bg=COLORS['bg_card'], fg=COLORS['text']).pack(pady=5)
            font_size_var = tk.StringVar(value=str(current_size))
            font_size_entry = tk.Entry(font_window, textvariable=font_size_var)
            font_size_entry.pack(pady=5)

            def confirm_font_change():
                try:
                    new_family = font_family_var.get() or "Arial"
                    new_size = int(font_size_var.get()) or 12
                    new_font = (new_family, new_size)

                    # Actualizar la fuente en el canvas
                    self.cv.itemconfig(canvas_text_id, font=new_font)

                    # Actualizar la fuente en el historial
                    for item in self.drawing_history:
                        if item.get('canvas_id') == canvas_text_id:
                            item['font'] = new_font
                            break

                    font_window.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Por favor ingrese un tamaño de fuente válido (número entero)")

            tk.Button(font_window, text="Aplicar", command=confirm_font_change,
                      bg=COLORS['primary'], fg=COLORS['text']).pack(pady=10)

            tk.Button(font_window, text="Cancelar", command=font_window.destroy,
                      bg="#7f1d1d", fg=COLORS['text']).pack(pady=5)

        self.cv.tag_bind(canvas_text_id, "<Button-3>", edit_text_font)  # Clic derecho para editar fuente

    def enable_eraser(self):
        """Activa la herramienta de borrado"""
        # Cambiar el cursor para indicar que es una goma de borrar
        self.cv.config(cursor="dot")

        # Cambiar temporalmente la función de dibujo para que borre elementos
        self.original_draw_paint = self.draw_paint
        self.cv.bind("<B1-Motion>", self.erase_item)

        # Crear una función específica para el evento de Button-1 en modo borrador
        def eraser_click_handler(e):
            self.lx = e.x
            self.ly = e.y
            self.erase_single_item(e)

        self.cv.bind("<Button-1>", eraser_click_handler)

        # Desvincular TODOS los eventos que permiten arrastrar texto u otros elementos
        try:
            self.cv.unbind("<Button-3>")  # Desvincular clic derecho para edición de texto
        except:
            pass  # Si no hay evento vinculado, ignorar
        try:
            self.cv.unbind("<Double-Button-1>")  # Desvincular doble clic para edición de texto
        except:
            pass  # Si no hay evento vinculado, ignorar
        # Desvincular eventos de arrastre específicos de los elementos de texto existentes
        # Esto es crítico para evitar que la goma se convierta en herramienta de arrastre
        try:
            # Obtener todos los elementos en el canvas
            all_items = self.cv.find_all()
            for item in all_items:
                # Verificar si el elemento es de tipo texto
                if self.cv.type(item) == "text":
                    # Desvincular eventos específicos de arrastre para cada elemento de texto
                    try:
                        self.cv.tag_unbind(item, "<Button-1>")
                        self.cv.tag_unbind(item, "<B1-Motion>")
                        self.cv.tag_unbind(item, "<ButtonRelease-1>")
                        self.cv.tag_unbind(item, "<Double-Button-1>")
                    except:
                        pass  # Si no se pueden desvincular eventos específicos, ignorar
        except:
            pass  # Si no se pueden obtener los elementos, ignorar

        # También desvincular cualquier evento de arrastre general que pueda haber sido establecido
        try:
            self.cv.unbind("<Button-1>")
            self.cv.unbind("<B1-Motion>")
            self.cv.unbind("<ButtonRelease-1>")
        except:
            pass  # Si no hay eventos generales vinculados, ignorar

        # Volver a vincular los eventos específicos de borrado
        self.cv.bind("<Button-1>", eraser_click_handler)

        # Actualizar la barra de estado
        self.status_bar.config(text="Modo: Borrador | Haz clic o arrastra para borrar elementos")

    def erase_item(self, e):
        """Borra elementos en la posición del mouse"""
        # Obtener los elementos en la posición del mouse
        x, y = e.x, e.y
        items = self.cv.find_overlapping(x-5, y-5, x+5, y+5)  # Área de borrado más pequeña (10x10 píxeles)

        # Obtener todos los IDs de canvas de nuestro historial
        history_canvas_ids = set()
        for operation in self.drawing_history:
            if operation.get('type') == 'stroke':
                # Para trazos, agregar todos los IDs de canvas
                for canvas_id in operation.get('canvas_ids', []):
                    history_canvas_ids.add(canvas_id)
            elif 'canvas_id' in operation:
                # Para otros tipos, agregar el ID directamente
                history_canvas_ids.add(operation['canvas_id'])

        for item in items:
            # Verificar si el item pertenece a nuestro historial (no es el fondo u otros elementos)
            if item in history_canvas_ids:
                # Eliminar el elemento del canvas sin importar su tipo
                self.cv.delete(item)

                # Buscar en el historial el elemento correspondiente para marcarlo como eliminado
                for i, operation in enumerate(self.drawing_history):
                    if operation.get('type') == 'stroke':
                        # Para trazos, verificar si el ID está en los canvas_ids
                        if item in operation.get('canvas_ids', []):
                            if item in operation['canvas_ids']:  # Asegurarse de que el item esté en la lista antes de remover
                                operation['canvas_ids'].remove(item)
                                # Si el trazo ya no tiene elementos, marcarlo como eliminado
                                if len(operation['canvas_ids']) == 0:
                                    operation['deleted'] = True
                            break
                    elif operation.get('canvas_id') == item:
                        # Para otros tipos, marcar directamente como eliminado
                        operation['deleted'] = True
                        break

    def erase_single_item(self, e):
        """Borra un solo elemento en la posición del click"""
        x, y = e.x, e.y
        items = self.cv.find_overlapping(x-5, y-5, x+5, y+5)  # Área de borrado más pequeña (10x10 píxeles)

        # Obtener todos los IDs de canvas de nuestro historial
        history_canvas_ids = set()
        for operation in self.drawing_history:
            if operation.get('type') == 'stroke':
                # Para trazos, agregar todos los IDs de canvas
                for canvas_id in operation.get('canvas_ids', []):
                    history_canvas_ids.add(canvas_id)
            elif 'canvas_id' in operation:
                # Para otros tipos, agregar el ID directamente
                history_canvas_ids.add(operation['canvas_id'])

        if items:
            # Buscar el primer elemento del historial en los items encontrados
            for item in reversed(items):  # Revertir para tomar el elemento superior primero
                if item in history_canvas_ids:
                    # Verificar si es un texto o una línea para manejarlo adecuadamente
                    item_type = self.cv.type(item)

                    if item_type == "text":
                        # Para texto, permitir borrar solo si está dentro del área de borrado
                        # Obtener las coordenadas del texto
                        text_x, text_y = self.cv.coords(item)[0], self.cv.coords(item)[1]

                        # Calcular distancia entre el cursor y el texto
                        distance = ((x - text_x) ** 2 + (y - text_y) ** 2) ** 0.5

                        # Si el cursor está cerca del texto (dentro del área de borrado), borrarlo
                        if distance <= 10:  # Radio de 10 píxeles
                            # Eliminar el elemento del canvas
                            self.cv.delete(item)

                            # Buscar en el historial el elemento correspondiente para marcarlo como eliminado
                            for i, operation in enumerate(self.drawing_history):
                                if operation.get('type') == 'stroke':
                                    # Para trazos, verificar si el ID está en los canvas_ids
                                    if item in operation.get('canvas_ids', []):
                                        operation['canvas_ids'].remove(item)
                                        # Si el trazo ya no tiene elementos, marcarlo como eliminado
                                        if len(operation['canvas_ids']) == 0:
                                            operation['deleted'] = True
                                        break
                                elif operation.get('canvas_id') == item:
                                    # Para otros tipos, marcar directamente como eliminado
                                    operation['deleted'] = True
                                    break
                    elif item_type == "line":
                        # Para líneas, borrar solo si están dentro del área de borrado
                        coords = self.cv.coords(item)
                        if len(coords) >= 4:
                            x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]

                            # Calcular distancia del punto al segmento de línea
                            line_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                            if line_length > 0:
                                distance_to_line = abs((x2 - x1) * (y1 - y) - (x1 - x) * (y2 - y1)) / line_length

                                # Si la distancia es menor al radio de borrado y el punto está cerca del segmento
                                if distance_to_line <= 5:  # Radio de 5 píxeles
                                    # Verificar si el punto está dentro del segmento de línea
                                    dot_product = ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (line_length ** 2)

                                    # Clamping para asegurar que el punto esté dentro del segmento
                                    closest_point_x = x1 + dot_product * (x2 - x1)
                                    closest_point_y = y1 + dot_product * (y2 - y1)

                                    # Distancia al punto más cercano en el segmento
                                    distance_to_closest = ((x - closest_point_x) ** 2 + (y - closest_point_y) ** 2) ** 0.5

                                    if distance_to_closest <= 5:  # Radio de 5 píxeles
                                        # Eliminar el elemento del canvas
                                        self.cv.delete(item)

                                        # Buscar en el historial el elemento correspondiente para marcarlo como eliminado
                                        for i, operation in enumerate(self.drawing_history):
                                            if operation.get('type') == 'stroke':
                                                # Para trazos, verificar si el ID está en los canvas_ids
                                                if item in operation.get('canvas_ids', []):
                                                    operation['canvas_ids'].remove(item)
                                                    # Si el trazo ya no tiene elementos, marcarlo como eliminado
                                                    if len(operation['canvas_ids']) == 0:
                                                        operation['deleted'] = True
                                                    break
                                            elif operation.get('canvas_id') == item:
                                                # Para otros tipos, marcar directamente como eliminado
                                                operation['deleted'] = True
                                                break
                    break  # Romper después de borrar un elemento

    def clear_canvas(self):
        """Limpia todo el lienzo excepto el fondo"""
        # Eliminar todos los elementos dibujados del canvas
        for item in self.cv.find_all():
            # No eliminar el fondo (primer elemento)
            if item != self.cv.find_all()[0]:
                self.cv.delete(item)

        # Limpiar el historial
        self.drawing_history = []
        self.history_index = -1

        # Recargar el fondo
        self.load_paint_background()

        # Actualizar la barra de estado
        self.status_bar.config(text="Lienzo limpio")

    def toggle_fullscreen(self):
        """Alternar entre pantalla completa y ventana normal"""
        # Obtener la ventana principal del paint
        paint_window = self.cv.winfo_toplevel()

        # Alternar el estado de pantalla completa
        current_state = paint_window.attributes('-fullscreen')
        paint_window.attributes('-fullscreen', not current_state)

        # Actualizar la barra de estado
        if not current_state:
            self.status_bar.config(text="Modo: Pantalla Completa")
        else:
            self.status_bar.config(text="Modo: Ventana Normal")

    def export_canvas(self):
        """Exportar el lienzo como imagen"""
        from tkinter import filedialog
        from PIL import Image, ImageDraw

        # Obtener dimensiones del canvas
        width = self.cv.winfo_width()
        height = self.cv.winfo_height()

        if width <= 1 or height <= 1:
            # Si no se pueden obtener dimensiones reales, usar valores por defecto
            width = 800
            height = 600

        # Crear una imagen PIL para dibujar
        img = Image.new("RGB", (width, height), "black")

        # Intentar incluir el fondo del lienzo de pintura
        if hasattr(self, 'p_bg'):
            # Si hay un fondo de lienzo, usarlo como base
            try:
                # Obtener la imagen original
                original_image = self.load_original_background()
                if original_image:
                    # Redimensionar la imagen original al tamaño del canvas
                    bg_img = original_image.resize((width, height), Image.Resampling.LANCZOS)
                    img = bg_img.convert("RGB")
            except:
                # Si no se puede cargar el fondo, continuar con imagen negra
                img = Image.new("RGB", (width, height), "black")

        draw = ImageDraw.Draw(img)

        # Obtener todos los elementos del canvas
        items = self.cv.find_all()

        for item in items:
            # Obtener tipo de elemento
            item_type = self.cv.type(item)
            bbox = self.cv.bbox(item)

            if bbox:  # Asegurarse de que el elemento tenga una caja delimitadora
                coords = self.cv.coords(item)

                if item_type == "line":
                    # Obtener color del elemento
                    color = self.cv.itemcget(item, "fill")
                    width_line = float(self.cv.itemcget(item, "width"))

                    if len(coords) >= 4:
                        # Dibujar línea en la imagen
                        draw.line([(coords[0], coords[1]), (coords[2], coords[3])],
                                 fill=color, width=int(width_line))

                elif item_type == "text":
                    # Obtener texto, posición, color y fuente
                    text = self.cv.itemcget(item, "text")
                    x, y = coords[0], coords[1]
                    color = self.cv.itemcget(item, "fill")
                    text_font = self.cv.itemcget(item, "font")  # Renombrar variable para evitar conflicto

                    # Importar ImageFont si no está importado
                    try:
                        from PIL import ImageFont
                    except ImportError:
                        # Si no se puede importar ImageFont, dibujar sin fuente específica
                        draw.text((x, y), text, fill=color)
                        continue

                    # Procesar la información de la fuente para obtener tamaño y tipo
                    font_name = "arial"  # Valor por defecto
                    font_size = 12       # Valor por defecto

                    try:
                        # La fuente puede venir en formato "nombre tamaño" o como tupla
                        if isinstance(text_font, str):
                            parts = text_font.split()
                            if len(parts) >= 2:
                                font_name = parts[0]
                                font_size = int(parts[1])
                            elif len(parts) == 1:
                                font_name = parts[0]
                        elif isinstance(text_font, tuple):
                            # Si es una tupla, el primer elemento es el nombre y el segundo el tamaño
                            if len(text_font) >= 2:
                                font_name = text_font[0]
                                font_size = int(text_font[1])
                            elif len(text_font) >= 1:
                                font_name = text_font[0]
                        else:
                            # Si es un objeto Font, obtener nombre y tamaño
                            try:
                                font_name = text_font.actual()["family"]
                                font_size = text_font.actual()["size"]
                            except:
                                pass
                    except:
                        # Si hay un error al procesar la fuente, usar valores por defecto
                        font_name = "arial"
                        font_size = 12

                    # Intentar crear la fuente con el tamaño correcto
                    pil_font = None
                    try:
                        # Intentar cargar una fuente TrueType con el tamaño especificado
                        pil_font = ImageFont.truetype(f"{font_name}.ttf", font_size)
                    except:
                        try:
                            # Intentar con variantes del nombre de la fuente
                            font_variants = [
                                f"{font_name}.ttf",
                                f"{font_name.lower()}.ttf",
                                f"{font_name.upper()}.ttf",
                                f"/usr/share/fonts/truetype/dejavu/{font_name}.ttf",
                                f"C:/Windows/Fonts/{font_name}.ttf",
                                f"/System/Library/Fonts/{font_name}.ttf",  # Para macOS
                                f"/usr/share/fonts/TTF/{font_name}.ttf"   # Otra ubicación común en Linux
                            ]
                            for variant in font_variants:
                                try:
                                    if variant.startswith('/') or variant.startswith('C:'):
                                        # Ruta completa
                                        pil_font = ImageFont.truetype(variant, font_size)
                                    else:
                                        # Nombre de fuente
                                        pil_font = ImageFont.truetype(variant, font_size)
                                    break
                                except:
                                    continue
                        except:
                            pass

                        # Si no se puede cargar ninguna fuente específica, usar una fuente por defecto
                        if pil_font is None:
                            try:
                                # Crear una fuente con tamaño aproximado usando la fuente por defecto
                                # ImageFont no permite cambiar el tamaño de la fuente por defecto directamente
                                # pero podemos usar ImageFont.load_default() y escalar el resultado
                                pil_font = ImageFont.load_default()
                            except:
                                pil_font = ImageFont.load_default()

                    # Dibujar texto en la imagen con la fuente y tamaño correctos
                    try:
                        if pil_font:
                            draw.text((x, y), text, fill=color, font=pil_font)
                        else:
                            draw.text((x, y), text, fill=color)
                    except:
                        # Si hay un error al dibujar con la fuente, dibujar sin especificar fuente
                        draw.text((x, y), text, fill=color)

        # Abrir diálogo para guardar archivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ],
            title="Guardar lienzo como"
        )

        if file_path:
            # Determinar formato según extensión
            if file_path.lower().endswith('.pdf'):
                # Para exportar a PDF, necesitamos un módulo adicional
                try:
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter, A4
                    from io import BytesIO

                    # Obtener dimensiones para el PDF
                    if width > height:
                        pagesize = (width, height)
                    else:
                        pagesize = (height, width)

                    pdf_canvas = canvas.Canvas(file_path, pagesize=pagesize)

                    # Guardar imagen temporalmente
                    temp_img_path = file_path.rsplit('.', 1)[0] + "_temp.png"
                    img.save(temp_img_path)

                    # Dibujar imagen en el PDF
                    pdf_canvas.drawImage(temp_img_path, 0, 0, width, height)
                    pdf_canvas.save()

                    # Eliminar imagen temporal
                    import os
                    os.remove(temp_img_path)

                    self.status_bar.config(text=f"Lienzo exportado como PDF: {file_path}")
                except ImportError:
                    # Si no está disponible reportlab, guardar como PNG
                    img.save(file_path.replace('.pdf', '.png'))
                    self.status_bar.config(text=f"Lienzo exportado como PNG: {file_path.replace('.pdf', '.png')}")
            else:
                # Guardar como imagen
                img.save(file_path)
                self.status_bar.config(text=f"Lienzo exportado como: {file_path}")

    def add_to_history(self, operation):
        """Agrega una operación al historial"""
        # Si hay operaciones después del índice actual, eliminarlas (para mantener la línea temporal)
        if self.history_index < len(self.drawing_history) - 1:
            self.drawing_history = self.drawing_history[:self.history_index + 1]

        # Agregar la nueva operación
        self.drawing_history.append(operation)

        # Actualizar el índice
        self.history_index = len(self.drawing_history) - 1

        # Limitar el tamaño del historial
        if len(self.drawing_history) > self.history_limit:
            self.drawing_history.pop(0)
            self.history_index = len(self.drawing_history) - 1  # Ajustar el índice después de eliminar

    def undo_action(self):
        """Deshace la última acción"""
        if self.history_index >= 0 and self.history_index < len(self.drawing_history):
            # Obtener la última operación del historial
            last_operation = self.drawing_history[self.history_index]

            # Eliminar los elementos del canvas según el tipo de operación
            if last_operation['type'] == 'stroke':
                # Si es un trazo, eliminar todos los segmentos
                for canvas_id in last_operation.get('canvas_ids', []):
                    try:
                        self.cv.delete(canvas_id)
                    except:
                        pass  # El elemento ya pudo haber sido eliminado
            elif 'canvas_id' in last_operation:
                # Si es otro tipo de operación con un solo canvas_id
                try:
                    self.cv.delete(last_operation['canvas_id'])
                except:
                    pass  # El elemento ya pudo haber sido eliminado

            # Decrementar el índice
            self.history_index -= 1

            # Actualizar la barra de estado
            remaining = self.history_index + 1
            self.status_bar.config(text=f"Operación deshecha. Operaciones restantes: {remaining}")

            # Actualizar la lupa si está activa
            if self.magnifier_active:
                self.update_magnifier_smooth(*self.get_current_cursor_position())

    def redo_action(self):
        """Rehace la última acción deshecha"""
        if self.history_index < len(self.drawing_history) - 1:
            # Incrementar el índice
            self.history_index += 1

            # Obtener la operación a rehacer
            next_operation = self.drawing_history[self.history_index]

            # Volver a crear el elemento en el canvas
            if next_operation['type'] == 'stroke':
                # Si es un trazo, recrear todos los segmentos
                canvas_ids = []
                for point in next_operation['points']:
                    x1, y1, x2, y2 = point
                    canvas_id = self.cv.create_line(
                        x1, y1, x2, y2,
                        fill=next_operation['fill'],
                        width=next_operation['width'],
                        capstyle="round",
                        smooth=True
                    )
                    canvas_ids.append(canvas_id)
                next_operation['canvas_ids'] = canvas_ids
            elif next_operation['type'] == 'text':
                canvas_id = self.cv.create_text(
                    next_operation['x'], next_operation['y'],
                    text=next_operation['text'], fill=next_operation['fill'],
                    font=next_operation['font']
                )
                next_operation['canvas_id'] = canvas_id

            # Actualizar la barra de estado
            remaining = len(self.drawing_history) - self.history_index - 1
            self.status_bar.config(text=f"Operación rehecha. Operaciones pendientes: {remaining}")

            # Actualizar la lupa si está activa
            if self.magnifier_active:
                self.update_magnifier_smooth(*self.get_current_cursor_position())

    def get_current_cursor_position(self):
        """Obtiene la posición actual del cursor"""
        # Obtener la posición actual del mouse relativa al canvas
        try:
            x = self.cv.winfo_pointerx() - self.cv.winfo_rootx()
            y = self.cv.winfo_pointery() - self.cv.winfo_rooty()
            return (x, y)
        except:
            # Si no se puede obtener la posición, devolver una posición por defecto
            return (100, 100)

    def prev_font(self):
        """Selecciona la fuente anterior en la lista"""
        if len(self.available_fonts) > 0:
            self.current_font_index = (self.current_font_index - 1) % len(self.available_fonts)
            current_font = self.available_fonts[self.current_font_index]
            self.status_bar.config(text=f"Fuente actual: {current_font}")

    def next_font(self):
        """Selecciona la siguiente fuente en la lista"""
        if len(self.available_fonts) > 0:
            self.current_font_index = (self.current_font_index + 1) % len(self.available_fonts)
            current_font = self.available_fonts[self.current_font_index]
            self.status_bar.config(text=f"Fuente actual: {current_font}")

    def place_text_at_coordinates(self):
        """Coloca texto en coordenadas específicas"""
        # Crear ventana de diálogo para ingresar coordenadas
        coord_window = tk.Toplevel(self.root)
        coord_window.title("Colocar texto en coordenadas")
        coord_window.geometry("300x250")
        coord_window.configure(bg=COLORS['bg_card'])

        # Etiquetas y campos de entrada
        tk.Label(coord_window, text="Coordenada X:", bg=COLORS['bg_card'], fg=COLORS['text']).pack(pady=5)
        x_entry = tk.Entry(coord_window)
        x_entry.pack(pady=5)

        tk.Label(coord_window, text="Coordenada Y:", bg=COLORS['bg_card'], fg=COLORS['text']).pack(pady=5)
        y_entry = tk.Entry(coord_window)
        y_entry.pack(pady=5)

        tk.Label(coord_window, text="Texto:", bg=COLORS['bg_card'], fg=COLORS['text']).pack(pady=5)
        text_entry = tk.Entry(coord_window)
        text_entry.pack(pady=5)

        tk.Label(coord_window, text="Tipo de Letra:", bg=COLORS['bg_card'], fg=COLORS['text']).pack(pady=5)
        current_font = self.available_fonts[self.current_font_index] if self.available_fonts else "Arial"
        font_family_entry = tk.Entry(coord_window)
        font_family_entry.insert(0, current_font)  # Usar la fuente actual
        font_family_entry.pack(pady=5)

        tk.Label(coord_window, text="Tamaño:", bg=COLORS['bg_card'], fg=COLORS['text']).pack(pady=5)
        font_size_entry = tk.Entry(coord_window)
        font_size_entry.insert(0, "12")  # Valor por defecto
        font_size_entry.pack(pady=5)

        def confirm_placement():
            try:
                x = int(x_entry.get())
                y = int(y_entry.get())
                text = text_entry.get()
                font_family = font_family_entry.get() or self.available_fonts[self.current_font_index] if self.available_fonts else "Arial"
                font_size = int(font_size_entry.get()) or 12

                if text:
                    # Registrar la operación de texto en el historial
                    operation = {
                        'type': 'text',
                        'x': x,
                        'y': y,
                        'text': text,
                        'fill': self.pen_color,
                        'font': font
                    }

                    self.add_to_history(operation)

                    # Dibujar el texto en la posición especificada
                    canvas_text_id = self.cv.create_text(x, y, text=text, fill=self.pen_color, font=font)

                    # Actualizar el ID del canvas en el historial
                    self.drawing_history[self.history_index]['canvas_id'] = canvas_text_id

                    # Permitir edición del texto recién creado
                    self.selected_text_id = self.history_index
                    self.enable_text_editing(canvas_text_id, x, y)

                coord_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese coordenadas y tamaño de fuente válidos (números enteros)")

        tk.Button(coord_window, text="Colocar Texto", command=confirm_placement,
                  bg=COLORS['primary'], fg=COLORS['text']).pack(pady=10)

        tk.Button(coord_window, text="Cancelar", command=coord_window.destroy,
                  bg="#7f1d1d", fg=COLORS['text']).pack(pady=5)

    def on_mouse_move(self, event):
        """Maneja el movimiento del mouse para la lupa"""
        if self.magnifier_active:
            # Mostrar coordenadas en la barra de estado
            self.status_bar.config(text=f"Modo: Lupa | Posición: ({event.x}, {event.y})")

            # Actualizar la imagen en la ventana de lupa
            self.update_magnifier(event.x, event.y)

    def update_magnifier(self, x, y):
        """Actualiza la imagen mostrada en la ventana de lupa"""
        if not self.magnifier_active or not hasattr(self, 'magnifier_window') or not self.magnifier_window.winfo_exists():
            return

        try:
            # Obtener dimensiones del canvas
            canvas_width = self.cv.winfo_width()
            canvas_height = self.cv.winfo_height()

            if canvas_width <= 1 or canvas_height <= 1:
                return

            # Definir región a ampliar basada en el nivel de magnificación
            # A mayor nivel de zoom, menor región del lienzo se toma
            base_region_size = 60
            region_size = max(5, int(base_region_size / self.magnification_level))

            # Calcular límites de la región a capturar
            x1 = max(0, int(x - region_size//2))
            y1 = max(0, int(y - region_size//2))
            x2 = min(canvas_width, int(x + region_size//2))
            y2 = min(canvas_height, int(y + region_size//2))

            # Actualizar posición de la ventana de lupa cerca del cursor
            self.magnifier_window.geometry(f"+{x+20}+{y+20}")

            # Limpiar el canvas de la lupa
            self.magnifier_canvas.delete("all")

            # Intentar obtener la imagen de fondo para mostrarla en la lupa
            if hasattr(self, 'p_bg') and self.p_bg:
                try:
                    # Obtener la imagen original
                    original_image = self.load_original_background()

                    if original_image:
                        # Calcular la proporción entre el canvas y la imagen original
                        img_width, img_height = original_image.size

                        # Calcular la región correspondiente en la imagen original
                        canvas_to_img_x_ratio = img_width / canvas_width
                        canvas_to_img_y_ratio = img_height / canvas_height

                        bg_x1 = int(x1 * canvas_to_img_x_ratio)
                        bg_y1 = int(y1 * canvas_to_img_y_ratio)
                        bg_x2 = int(x2 * canvas_to_img_x_ratio)
                        bg_y2 = int(y2 * canvas_to_img_y_ratio)

                        # Asegurarse de que las coordenadas estén dentro de los límites
                        bg_x1 = max(0, min(bg_x1, img_width))
                        bg_y1 = max(0, min(bg_y1, img_height))
                        bg_x2 = max(0, min(bg_x2, img_width))
                        bg_y2 = max(0, min(bg_y2, img_height))

                        # Recortar la región de la imagen original
                        cropped_img = original_image.crop((bg_x1, bg_y1, bg_x2, bg_y2))

                        # Ampliar la imagen recortada al tamaño de la lupa
                        magnified_img = cropped_img.resize((300, 300), Image.Resampling.LANCZOS)

                        # Convertir a PhotoImage
                        photo = ImageTk.PhotoImage(magnified_img)

                        # Mostrar la imagen en la lupa
                        self.magnifier_canvas.create_image(150, 150, image=photo, anchor="center")
                        # Guardar referencia para evitar que sea eliminada por el recolector de basura
                        self.magnifier_canvas.image = photo
                    else:
                        # Si no se puede obtener la imagen original, dibujar rectángulo base
                        self.magnifier_canvas.create_rectangle(0, 0, 300, 300, fill='#0f172a', outline='white')
                except:
                    # Si hay algún error al procesar la imagen, dibujar rectángulo base
                    self.magnifier_canvas.create_rectangle(0, 0, 300, 300, fill='#0f172a', outline='white')
            else:
                # Si no hay imagen de fondo, dibujar rectángulo base
                self.magnifier_canvas.create_rectangle(0, 0, 300, 300, fill='#0f172a', outline='white')

            # Calcular dimensiones de la región a ampliar
            region_width = x2 - x1
            region_height = y2 - y1

            if region_width > 0 and region_height > 0:
                # Factor de escala para ampliar la región al tamaño del canvas de la lupa
                scale_x = 300 / region_width
                scale_y = 300 / region_height
                # Mantener proporción
                scale = min(scale_x, scale_y)

                # Calcular dimensiones finales después de aplicar la escala
                scaled_width = int(region_width * scale)
                scaled_height = int(region_height * scale)

                # Calcular posición centrada en el canvas de la lupa
                offset_x = (300 - scaled_width) // 2
                offset_y = (300 - scaled_height) // 2

                # Reproducir las operaciones de dibujo en la región de la lupa
                for operation in self.drawing_history:
                    if operation['type'] == 'line':
                        # Verificar si la línea intersecta con la región de interés
                        x1_line, y1_line = operation['x1'], operation['y1']
                        x2_line, y2_line = operation['x2'], operation['y2']

                        # Solo dibujar si la línea está dentro de la región de interés
                        if (x1 <= x1_line <= x2 and y1 <= y1_line <= y2) or \
                           (x1 <= x2_line <= x2 and y1 <= y2_line <= y2) or \
                           (x1_line <= x1 <= x2_line and y1_line <= y1 <= y2_line) or \
                           (x1_line <= x2 <= x2_line and y1_line <= y2 <= y2_line):

                            # Transformar coordenadas al espacio de la lupa
                            new_x1 = (x1_line - x1) * scale + offset_x
                            new_y1 = (y1_line - y1) * scale + offset_y
                            new_x2 = (x2_line - x1) * scale + offset_x
                            new_y2 = (y2_line - y1) * scale + offset_y

                            # Ajustar grosor de línea proporcionalmente
                            new_width = max(1, operation['width'] * scale)

                            # Dibujar la línea en la lupa
                            self.magnifier_canvas.create_line(
                                new_x1, new_y1, new_x2, new_y2,
                                fill=operation['fill'], width=new_width, capstyle="round", smooth=True
                            )
                    elif operation['type'] == 'text':
                        # Verificar si el texto está dentro de la región de interés
                        text_x, text_y = operation['x'], operation['y']

                        if x1 <= text_x <= x2 and y1 <= text_y <= y2:
                            # Transformar coordenadas al espacio de la lupa
                            new_x = (text_x - x1) * scale + offset_x
                            new_y = (text_y - y1) * scale + offset_y

                            # Ajustar tamaño de fuente proporcionalmente
                            original_font_size = operation['font'][1]
                            new_font_size = max(6, int(original_font_size * scale))  # Tamaño mínimo de 6
                            new_font = (operation['font'][0], new_font_size)

                            # Dibujar el texto en la lupa
                            self.magnifier_canvas.create_text(
                                new_x, new_y,
                                text=operation['text'], fill=operation['fill'], font=new_font
                            )

                # Dibujar十字线 para indicar el centro exacto
                center_x = (x - x1) * scale + offset_x
                center_y = (y - y1) * scale + offset_y
                self.magnifier_canvas.create_line(center_x - 20, center_y, center_x + 20, center_y, fill='red', width=2)
                self.magnifier_canvas.create_line(center_x, center_y - 20, center_x, center_y + 20, fill='red', width=2)

            # Mostrar coordenadas y nivel de zoom en la lupa
            self.magnifier_canvas.create_text(150, 15, text=f"({x},{y}) - {self.magnification_level}x", fill='white', font=("Arial", 10), tag="zoom_info")

        except Exception as e:
            print(f"Error actualizando la lupa: {e}")
            # En caso de error, asegurarse de tener un fondo
            self.magnifier_canvas.create_rectangle(0, 0, 300, 300, fill='#0f172a', outline='white')

    def load_original_background(self):
        """Carga la imagen original de fondo"""
        try:
            if hasattr(self, 'paint_bg_path') and self.paint_bg_path:
                return Image.open(self.paint_bg_path)
        except:
            pass
        return None

    def on_mousewheel(self, event):
        """Maneja el evento de la rueda del ratón para Windows"""
        if self.magnifier_active:
            if event.delta > 0:
                self.increase_magnification()
            else:
                self.decrease_magnification()

    def on_mousewheel_up(self, event):
        """Maneja el evento de la rueda del ratón hacia arriba para Linux"""
        if self.magnifier_active:
            self.increase_magnification()

    def on_mousewheel_down(self, event):
        """Maneja el evento de la rueda del ratón hacia abajo para Linux"""
        if self.magnifier_active:
            self.decrease_magnification()

    def on_key_press(self, event):
        """Maneja eventos de teclado"""
        if event.keysym == 'Escape':
            if self.magnifier_active:
                self.toggle_magnifier()  # Desactivar modo lupa

    def on_main_window_mouse_move(self, event):
        """Maneja el movimiento del mouse en la ventana principal para actualizar la lupa"""
        # Convertir coordenadas de la ventana principal al canvas
        if self.magnifier_active and hasattr(self, 'cv'):
            # Obtener la posición relativa al canvas
            cv_x = event.x - self.cv.winfo_x()
            cv_y = event.y - self.cv.winfo_y()

            # Solo actualizar si las coordenadas están dentro del canvas
            if 0 <= cv_x <= self.cv.winfo_width() and 0 <= cv_y <= self.cv.winfo_height():
                # Actualizar la posición de la lupa con movimiento más suave
                self.update_magnifier_smooth(cv_x, cv_y)

    def on_mouse_move(self, event):
        """Maneja el movimiento del mouse para la lupa"""
        if self.magnifier_active:
            # Mostrar coordenadas en la barra de estado
            self.status_bar.config(text=f"Modo: Lupa | Posición: ({event.x}, {event.y}) | Zoom: {self.magnification_level}x")
            # Actualizar la lupa
            self.update_magnifier_smooth(event.x, event.y)
        else:
            # Mostrar coordenadas en la barra de estado para otros modos
            self.status_bar.config(text=f"Modo: Dibujo | Herramienta: Lápiz | Posición: ({event.x}, {event.y})")

    def update_magnifier_smooth(self, x, y):
        """Actualiza la imagen mostrada en la ventana de lupa con movimiento más suave"""
        if not self.magnifier_active or not hasattr(self, 'magnifier_window') or not self.magnifier_window.winfo_exists():
            return

        try:
            # Obtener dimensiones del canvas
            canvas_width = self.cv.winfo_width()
            canvas_height = self.cv.winfo_height()

            if canvas_width <= 1 or canvas_height <= 1:
                return

            # Definir región a ampliar basada en el nivel de magnificación
            # A mayor nivel de zoom, menor región del lienzo se toma
            base_region_size = 60
            region_size = max(5, int(base_region_size / self.magnification_level))

            # Calcular límites de la región a capturar
            x1 = max(0, int(x - region_size//2))
            y1 = max(0, int(y - region_size//2))
            x2 = min(canvas_width, int(x + region_size//2))
            y2 = min(canvas_height, int(y + region_size//2))

            # Actualizar posición de la ventana de lupa cerca del cursor con movimiento más suave
            # Colocar la ventana de la lupa ligeramente desplazada del cursor para evitar interferencia
            offset_x = 20
            offset_y = 20

            # Evitar que la ventana de la lupa salga de los límites de la pantalla
            screen_width = self.magnifier_window.winfo_screenwidth()
            screen_height = self.magnifier_window.winfo_screenheight()

            # Calcular posición objetivo
            target_x = x + offset_x
            target_y = y + offset_y

            # Ajustar si la ventana se sale de la pantalla
            if target_x + 300 > screen_width:
                target_x = x - 320  # Colocar a la izquierda del cursor
            if target_y + 300 > screen_height:
                target_y = y - 320  # Colocar arriba del cursor

            # Actualizar posición con suavizado
            self.magnifier_window.geometry(f"+{target_x}+{target_y}")

            # Limpiar el canvas de la lupa
            self.magnifier_canvas.delete("all")

            # Intentar obtener la imagen de fondo para mostrarla en la lupa
            if hasattr(self, 'p_bg') and self.p_bg:
                try:
                    # Obtener la imagen original
                    original_image = self.load_original_background()

                    if original_image:
                        # Calcular la proporción entre el canvas y la imagen original
                        img_width, img_height = original_image.size

                        # Calcular la región correspondiente en la imagen original
                        canvas_to_img_x_ratio = img_width / canvas_width
                        canvas_to_img_y_ratio = img_height / canvas_height

                        bg_x1 = int(x1 * canvas_to_img_x_ratio)
                        bg_y1 = int(y1 * canvas_to_img_y_ratio)
                        bg_x2 = int(x2 * canvas_to_img_x_ratio)
                        bg_y2 = int(y2 * canvas_to_img_y_ratio)

                        # Asegurarse de que las coordenadas estén dentro de los límites
                        bg_x1 = max(0, min(bg_x1, img_width))
                        bg_y1 = max(0, min(bg_y1, img_height))
                        bg_x2 = max(0, min(bg_x2, img_width))
                        bg_y2 = max(0, min(bg_y2, img_height))

                        # Recortar la región de la imagen original
                        cropped_img = original_image.crop((bg_x1, bg_y1, bg_x2, bg_y2))

                        # Ampliar la imagen recortada al tamaño de la lupa
                        magnified_img = cropped_img.resize((300, 300), Image.Resampling.LANCZOS)

                        # Convertir a PhotoImage
                        photo = ImageTk.PhotoImage(magnified_img)

                        # Mostrar la imagen en la lupa
                        self.magnifier_canvas.create_image(150, 150, image=photo, anchor="center")
                        # Guardar referencia para evitar que sea eliminada por el recolector de basura
                        self.magnifier_canvas.image = photo
                    else:
                        # Si no se puede obtener la imagen original, dibujar rectángulo base
                        self.magnifier_canvas.create_rectangle(0, 0, 300, 300, fill='#0f172a', outline='white')
                except:
                    # Si hay algún error al procesar la imagen, dibujar rectángulo base
                    self.magnifier_canvas.create_rectangle(0, 0, 300, 300, fill='#0f172a', outline='white')
            else:
                # Si no hay imagen de fondo, dibujar rectángulo base
                self.magnifier_canvas.create_rectangle(0, 0, 300, 300, fill='#0f172a', outline='white')

            # Calcular dimensiones de la región a ampliar
            region_width = x2 - x1
            region_height = y2 - y1

            if region_width > 0 and region_height > 0:
                # Factor de escala para ampliar la región al tamaño del canvas de la lupa
                scale_x = 300 / region_width
                scale_y = 300 / region_height
                # Mantener proporción
                scale = min(scale_x, scale_y)

                # Calcular dimensiones finales después de aplicar la escala
                scaled_width = int(region_width * scale)
                scaled_height = int(region_height * scale)

                # Calcular posición centrada en el canvas de la lupa
                offset_x = (300 - scaled_width) // 2
                offset_y = (300 - scaled_height) // 2

                # Reproducir las operaciones de dibujo en la región de la lupa
                for operation in self.drawing_history:
                    if operation['type'] == 'line':
                        # Verificar si la línea intersecta con la región de interés
                        x1_line, y1_line = operation['x1'], operation['y1']
                        x2_line, y2_line = operation['x2'], operation['y2']

                        # Solo dibujar si la línea está dentro de la región de interés
                        if (x1 <= x1_line <= x2 and y1 <= y1_line <= y2) or \
                           (x1 <= x2_line <= x2 and y1 <= y2_line <= y2) or \
                           (x1_line <= x1 <= x2_line and y1_line <= y1 <= y2_line) or \
                           (x1_line <= x2 <= x2_line and y1_line <= y2 <= y2_line):

                            # Transformar coordenadas al espacio de la lupa
                            new_x1 = (x1_line - x1) * scale + offset_x
                            new_y1 = (y1_line - y1) * scale + offset_y
                            new_x2 = (x2_line - x1) * scale + offset_x
                            new_y2 = (y2_line - y1) * scale + offset_y

                            # Ajustar grosor de línea proporcionalmente
                            new_width = max(1, operation['width'] * scale)

                            # Dibujar la línea en la lupa
                            self.magnifier_canvas.create_line(
                                new_x1, new_y1, new_x2, new_y2,
                                fill=operation['fill'], width=new_width, capstyle="round", smooth=True
                            )
                    elif operation['type'] == 'text':
                        # Verificar si el texto está dentro de la región de interés
                        text_x, text_y = operation['x'], operation['y']

                        if x1 <= text_x <= x2 and y1 <= text_y <= y2:
                            # Transformar coordenadas al espacio de la lupa
                            new_x = (text_x - x1) * scale + offset_x
                            new_y = (text_y - y1) * scale + offset_y

                            # Ajustar tamaño de fuente proporcionalmente
                            original_font_size = operation['font'][1]
                            new_font_size = max(6, int(original_font_size * scale))  # Tamaño mínimo de 6
                            new_font = (operation['font'][0], new_font_size)

                            # Dibujar el texto en la lupa
                            self.magnifier_canvas.create_text(
                                new_x, new_y,
                                text=operation['text'], fill=operation['fill'], font=new_font
                            )

                # Dibujar十字线 para indicar el centro exacto
                center_x = (x - x1) * scale + offset_x
                center_y = (y - y1) * scale + offset_y
                self.magnifier_canvas.create_line(center_x - 20, center_y, center_x + 20, center_y, fill='red', width=2)
                self.magnifier_canvas.create_line(center_x, center_y - 20, center_y, center_y + 20, fill='red', width=2)

            # Mostrar coordenadas y nivel de zoom en la lupa
            self.magnifier_canvas.create_text(150, 15, text=f"({x},{y}) - {self.magnification_level}x", fill='white', font=("Arial", 10), tag="zoom_info")

        except Exception as e:
            print(f"Error actualizando la lupa: {e}")
            # En caso de error, asegurarse de tener un fondo
            self.magnifier_canvas.create_rectangle(0, 0, 300, 300, fill='#0f172a', outline='white')

    def load_paint_background(self):
        """Carga la imagen de fondo para el lienzo de pintura"""
        try:
            if hasattr(self, 'cv'):
                # Obtener dimensiones reales del canvas
                width = self.cv.winfo_width()
                height = self.cv.winfo_height()

                # Si no se pueden obtener las dimensiones, usar valores por defecto
                if width <= 1 or height <= 1:
                    width = 800
                    height = 600

                p_img = Image.open(self.paint_bg_path).resize((width, height), Image.Resampling.LANCZOS)
                self.p_bg = ImageTk.PhotoImage(p_img)

                # Eliminar imagen anterior si existe
                items = self.cv.find_withtag("background")
                if items:
                    self.cv.delete(items[0])

                # Crear nueva imagen de fondo
                self.cv.create_image(0, 0, image=self.p_bg, anchor="nw", tags="background")
        except:
            pass

    def on_paint_resize(self, event):
        """Maneja el evento de cambio de tamaño del lienzo"""
        # Solo redimensionar si el tamaño ha cambiado
        if event.width > 1 and event.height > 1:
            self.load_paint_background()

    def draw_paint(self, e):
        # Si es el primer punto del trazo, iniciar un nuevo trazo
        if not hasattr(self, 'current_stroke') or self.current_stroke is None:
            # Iniciar un nuevo trazo
            self.current_stroke = {
                'type': 'stroke',
                'points': [(self.lx, self.ly, e.x, e.y)],  # Lista de puntos (x1, y1, x2, y2)
                'fill': self.pen_color,
                'width': self.pen_size,
                'canvas_ids': []  # IDs de los elementos en el canvas
            }
        else:
            # Agregar punto al trazo existente
            self.current_stroke['points'].append((self.lx, self.ly, e.x, e.y))

        # Crear la línea en el canvas
        canvas_id = self.cv.create_line(self.lx, self.ly, e.x, e.y, fill=self.pen_color, width=self.pen_size, capstyle="round", smooth=True)

        # Agregar el ID del canvas al trazo
        self.current_stroke['canvas_ids'].append(canvas_id)

        self.lx, self.ly = e.x, e.y

    def finish_stroke(self, e):
        """Finaliza el trazo actual y lo guarda en el historial"""
        if hasattr(self, 'current_stroke') and self.current_stroke is not None:
            # Solo guardar en historial si hay elementos en el trazo
            if len(self.current_stroke['canvas_ids']) > 0:
                self.add_to_history(self.current_stroke)
            self.current_stroke = None

    def start_new_stroke(self, e):
        """Inicia un nuevo trazo"""
        # Si hay un trazo en curso, guardarlo en el historial
        if hasattr(self, 'current_stroke') and self.current_stroke is not None:
            self.add_to_history(self.current_stroke)
            self.current_stroke = None

    # --- APP: CALCULADORA COMPLETA ---
    def open_calc(self):
        self.create_win("calc", "CALCULADORA", 350, 480, self.setup_calc_ui)

    def setup_calc_ui(self, p):
        disp = tk.Entry(p, font=("Arial", 24), justify="right", bg="#020617", fg="white", bd=10, relief="flat")
        disp.pack(fill=tk.X, padx=10, pady=10)
        
        grid = tk.Frame(p, bg=COLORS['bg_card'])
        grid.pack(fill=tk.BOTH, expand=True)
        
        btns = [('sin', 'cos', 'tan', 'log'), ('7', '8', '9', '/'), ('4', '5', '6', '*'), 
                ('1', '2', '3', '-'), ('0', '.', '=', '+'), ('C', '(', ')', 'sqrt')]
        
        for r, row in enumerate(btns):
            for c, txt in enumerate(row):
                tk.Button(grid, text=txt, bg="#1e293b", fg=COLORS['gold'], font=("Arial", 10, "bold"),
                          command=lambda t=txt: self.calc_logic(disp, t)).grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
        for i in range(4): grid.grid_columnconfigure(i, weight=1)
        for i in range(6): grid.grid_rowconfigure(i, weight=1)

    def calc_logic(self, disp, char):
        if char == '=':
            try:
                res = eval(disp.get().replace('sqrt', 'math.sqrt').replace('sin', 'math.sin'))
                disp.delete(0, tk.END); disp.insert(tk.END, str(res))
            except: disp.delete(0, tk.END); disp.insert(tk.END, "Error")
        elif char == 'C': disp.delete(0, tk.END)
        else: disp.insert(tk.END, char)

    # --- APP: BLOC DE NOTAS ---
    def open_notes(self):
        self.create_win("notes", "NOTAS", 500, 500, self.setup_notes_ui)

    def setup_notes_ui(self, p):
        bar = tk.Frame(p, bg="#1e293b")
        bar.pack(fill=tk.X)
        tk.Button(bar, text="💾", command=self.save_data_json, bg="#1e293b", fg="white").pack(side=tk.LEFT)
        
        self.txt = tk.Text(p, bg="#0f172a", fg="white", font=("Consolas", 12), padx=10, pady=10)
        self.txt.pack(fill=tk.BOTH, expand=True)
        self.txt.insert("1.0", self.data.get('notes', ''))

    # --- FUNCIONES DE SISTEMA ---
    def pick_color(self): self.pen_color = colorchooser.askcolor()[1]
    def set_tool(self, size, color=None):
        self.pen_size = size
        if color: self.pen_color = color

        # Si estábamos en modo borrador, restaurar la función de dibujo original
        if hasattr(self, 'original_draw_paint'):
            self.cv.bind("<B1-Motion>", self.original_draw_paint)
            # Restaurar la función original de inicialización de coordenadas
            def set_initial_coords(e):
                # Si hay un trazo en curso, guardarlo en el historial
                if hasattr(self, 'current_stroke') and self.current_stroke is not None:
                    self.add_to_history(self.current_stroke)
                    self.current_stroke = None
                self.lx = e.x
                self.ly = e.y

            # Volver a vincular el evento de Button-1 para establecer coordenadas iniciales
            self.cv.bind("<Button-1>", set_initial_coords)
            self.cv.bind("<ButtonRelease-1>", self.finish_stroke)
            self.cv.config(cursor="")
            # Restaurar eventos de texto si es necesario
            try:
                self.cv.bind("<Button-3>", self.edit_text_font)  # Clic derecho para editar fuente
            except AttributeError:
                pass  # Si la función no existe, ignorar
            try:
                self.cv.bind("<Double-Button-1>", self.enable_text_editing)  # Doble clic para editar texto
            except AttributeError:
                pass  # Si la función no existe, ignorar
            # Restaurar eventos de arrastre de texto para elementos existentes
            try:
                # Obtener todos los elementos de texto en el canvas y restaurar eventos de arrastre
                all_items = self.cv.find_all()
                for item in all_items:
                    if self.cv.type(item) == "text":
                        # Restaurar eventos de arrastre para cada elemento de texto
                        def start_drag(event, item_id=item):
                            # Detener temporalmente el dibujo del lápiz
                            self.cv.unbind("<B1-Motion>")
                            self.cv.unbind("<Button-1>")
                            self.drag_data = {"x": event.x, "y": event.y, "item": item_id}

                        def move_text(event):
                            if hasattr(self, 'drag_data'):
                                dx = event.x - self.drag_data["x"]
                                dy = event.y - self.drag_data["y"]

                                # Mover el texto en el canvas
                                self.cv.move(self.drag_data["item"], dx, dy)

                                # Actualizar la posición en el historial
                                for item in self.drawing_history:
                                    if item.get('canvas_id') == self.drag_data["item"]:
                                        item['x'] += dx
                                        item['y'] += dy
                                        break

                                # Actualizar drag_data para el próximo movimiento
                                self.drag_data["x"] = event.x
                                self.drag_data["y"] = event.y

                        def end_drag(event):
                            if hasattr(self, 'drag_data'):
                                # Restaurar eventos de dibujo del lápiz
                                self.cv.bind("<B1-Motion>", self.draw_paint)
                                def set_initial_coords(e):
                                    # Si hay un trazo en curso, guardarlo en el historial
                                    if hasattr(self, 'current_stroke') and self.current_stroke is not None:
                                        self.add_to_history(self.current_stroke)
                                        self.current_stroke = None
                                    self.lx = e.x
                                    self.ly = e.y

                                self.cv.bind("<Button-1>", set_initial_coords)
                                self.cv.bind("<ButtonRelease-1>", self.finish_stroke)
                                delattr(self, 'drag_data')

                        # Vincular eventos de arrastre al elemento de texto
                        self.cv.tag_bind(item, "<Button-1>", start_drag)
                        self.cv.tag_bind(item, "<B1-Motion>", move_text)
                        self.cv.tag_bind(item, "<ButtonRelease-1>", end_drag)
            except:
                pass  # Si no se pueden obtener los elementos, ignorar
            delattr(self, 'original_draw_paint')

    def export_full_json(self):
        filename = f"Papiweb_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(self.data, f, indent=4)
        messagebox.showinfo("Exportar", f"Sistema exportado a {filename}")

    def show_help(self):
        """Mostrar ventana de ayuda con manual de uso"""
        # Crear ventana de ayuda
        help_window = tk.Toplevel(self.root)
        help_window.title("Ayuda - Manual de Uso")
        help_window.geometry("800x600")
        help_window.configure(bg=COLORS['bg_card'])

        # Título
        title_label = tk.Label(help_window, text="PAPIWEB DESARROLLOS INFORMÁTICOS",
                              bg=COLORS['bg_card'], fg=COLORS['gold'],
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Subtítulo
        subtitle_label = tk.Label(help_window, text="Manual de Usuario",
                                 bg=COLORS['bg_card'], fg=COLORS['text'],
                                 font=("Arial", 12))
        subtitle_label.pack(pady=5)

        # Crear un canvas con scrollbar para el contenido
        canvas_frame = tk.Frame(help_window, bg=COLORS['bg_card'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(canvas_frame, bg=COLORS['bg_card'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_card'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Contenido de ayuda
        help_content = """
MANUAL DE USO - PAPIWEB DESARROLLOS INFORMÁTICOS

APLICACIONES DISPONIBLES:

1. AGENDA (📅)
   - Vista mensual con calendario
   - Seleccione un día para editar eventos
   - Soporta eventos diarios

2. PAINT PRO (🎨)
   - Herramientas de dibujo: Lápiz, pincel, goma de borrar
   - Selector de colores y tamaños
   - Modo texto para agregar texto
   - Lupa para ver detalles
   - Controles de zoom (+/-)
   - Deshacer/Rehacer (Ctrl+Z / Ctrl+Y)
   - Exportar lienzo como imagen

3. CALCULADORA (🔢)
   - Operaciones matemáticas básicas
   - Funciones científicas (seno, coseno, tangente, logaritmos, etc.)
   - Constantes matemáticas

4. NOTAS (📝)
   - Editor de texto básico
   - Guardado automático
   - Exportación a JSON

5. REPRODUCTOR MULTIMEDIA (🎬)
   - Reproducción de archivos de video y audio
   - Controles de reproducción: Play/Pausa, Stop
   - Control de volumen
   - Barra de progreso
   - Pantalla completa
   - Controles de zoom para video
   - Atajos de teclado

ATAJOS DE TECLADO - REPRODUCTOR MULTIMEDIA:

   ESPACIO o ENTER: Reproducir/Pausar
   FLECHA IZQUIERDA (←): Retroceder 10 segundos
   FLECHA DERECHA (→): Avanzar 10 segundos
   FLECHA ARRIBA (↑): Aumentar volumen
   FLECHA ABAJO (↓): Disminuir volumen
   TECLA 'F': Pantalla completa
   TECLA 'ESC': Salir de pantalla completa
   TECLA 'M': Silenciar/Desilenciar
   TECLA '+': Acercar video (zoom in)
   TECLA '-': Alejar video (zoom out)
   TECLA '0': Restablecer zoom

ATAJOS DE TECLADO - PAINT PRO:

   FLECHA IZQUIERDA (←): Mover lienzo a la izquierda
   FLECHA DERECHA (→): Mover lienzo a la derecha
   FLECHA ARRIBA (↑): Mover lienzo hacia arriba
   FLECHA ABAJO (↓): Mover lienzo hacia abajo
   TECLA '+' o '=': Aumentar tamaño del pincel
   TECLA '-': Disminuir tamaño del pincel
   TECLA 'Z': Deshacer (con Ctrl+Z)
   TECLA 'Y': Rehacer (con Ctrl+Y)
   TECLA 'C': Cambiar color
   TECLA 'T': Modo texto
   TECLA 'M': Activar lupa
   TECLA 'F': Pantalla completa

FUNCIONES ADICIONALES:

   - El lienzo del Paint se adapta a la resolución de la pantalla
   - El reproductor multimedia detecta y se adapta a la resolución del video
   - Soporte para archivos multimedia: MP4, AVI, MKV, MP3, WAV, etc.
   - Exportación de proyectos a formato JSON
   - Sistema de ventanas con arrastre
   - Barra de tareas con botón de inicio

PAPIWEB DESARROLLOS INFORMÁTICOS
Versión 2026 - Ultra Edition
        """.strip()

        # Crear etiqueta con el contenido
        content_label = tk.Label(scrollable_frame, text=help_content,
                                bg=COLORS['bg_card'], fg=COLORS['text'],
                                font=("Consolas", 10), justify=tk.LEFT, anchor="nw")
        content_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botón de cierre
        close_button = tk.Button(help_window, text="Cerrar", command=help_window.destroy,
                                bg=COLORS['primary'], fg=COLORS['text'])
        close_button.pack(pady=10)

    def exit_app(self):
        """Salir de la aplicación"""
        # Preguntar confirmación antes de salir
        if messagebox.askyesno("Salir", "¿Estás seguro de que quieres salir de PAPIWEB?"):
            self.root.quit()

    def load_data(self):
        if os.path.exists("db_sapphire.json"):
            with open("db_sapphire.json", "r") as f: return json.load(f)
        return {"events": {}, "notes": "", "drawings": []}

    def save_data_json(self):
        self.data['notes'] = self.txt.get("1.0", tk.END)
        with open("db_sapphire.json", "w") as f: json.dump(self.data, f)

    def open_media(self):
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calcular dimensiones proporcionales para la ventana (máximo 80% de la pantalla)
        window_width = min(800, int(screen_width * 0.8))
        window_height = min(600, int(screen_height * 0.8))

        self.create_win("media", "MEDIA PLAYER", window_width, window_height, self.setup_media_player)

    def setup_media_player(self, p):
        # Obtener dimensiones de la pantalla
        screen_width = p.winfo_screenwidth()
        screen_height = p.winfo_screenheight()

        # Calcular dimensiones proporcionales para la ventana (máximo 80% de la pantalla)
        window_width = min(800, int(screen_width * 0.8))
        window_height = min(600, int(screen_height * 0.8))

        # Dimensiones para el contenedor de video (70% de la altura de la ventana)
        video_height = int(window_height * 0.7)
        controls_height = window_height - video_height

        # Intentar cargar fondo.png para el reproductor
        try:
            img = Image.open("reproductor.png")
            # Redimensionar la imagen al tamaño de la ventana
            img = img.resize((window_width, window_height), Image.Resampling.LANCZOS)
            self.media_bg_img = ImageTk.PhotoImage(img)

            # Crear un label con la imagen de fondo
            bg_label = tk.Label(p, image=self.media_bg_img)
            bg_label.image = self.media_bg_img  # Mantener una referencia
            bg_label.place(x=0, y=0, width=window_width, height=window_height)

        except:
            # Si no se encuentra la imagen, crear un frame negro
            bg_frame = tk.Frame(p, bg="black")
            bg_frame.place(x=0, y=0, width=window_width, height=window_height)

        # Crear frame para el contenedor de video
        self.video_container = tk.Frame(p, bg="black")
        self.video_container.place(x=0, y=0, width=window_width, height=video_height)  # Parte superior para video

        # Crear frame para controles debajo del video
        self.controls_frame = tk.Frame(p, bg="black")
        self.controls_frame.place(x=0, y=video_height, width=window_width, height=controls_height)  # Parte inferior para controles

        # Controles del reproductor
        tk.Label(self.controls_frame, text="VLC PLAYER ACTIVO", bg="black", fg="white").pack(pady=5)

        # Botones de control básicos
        button_frame = tk.Frame(self.controls_frame, bg="black")
        button_frame.pack(pady=5)

        # Crear el reproductor VLC en el contexto de esta ventana
        try:
            import vlc
            # Crear instancia de VLC con opciones para adaptarse a la resolución del equipo
            self.vlc_instance = vlc.Instance()
            self.vlc_player = self.vlc_instance.media_player_new()

            # IMPORTANTE: Vincular el video al contenedor en la aplicación
            if hasattr(self.vlc_player, 'set_hwnd'):  # Windows
                self.vlc_player.set_hwnd(self.video_container.winfo_id())
            elif hasattr(self.vlc_player, 'set_xwindow'):  # Linux
                self.vlc_player.set_xwindow(self.video_container.winfo_id())
            elif hasattr(self.vlc_player, 'set_nsobject'):  # macOS
                self.vlc_player.set_nsobject(self.video_container.winfo_id())
        except ImportError:
            self.vlc_player = None
            tk.Label(self.controls_frame, text="VLC no disponible", bg="black", fg="red").pack(pady=5)
        except Exception as e:
            self.vlc_player = None
            tk.Label(self.controls_frame, text=f"Error VLC: {str(e)}", bg="black", fg="red").pack(pady=5)

        # Marco para controles de reproducción
        controls_row1 = tk.Frame(button_frame, bg="black")
        controls_row1.pack(side=tk.LEFT, padx=2)

        # Asociar funciones con el reproductor VLC local
        tk.Button(controls_row1, text="📁", command=lambda: self.load_media_file(), bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2)
        self.play_button = tk.Button(controls_row1, text="▶️", command=lambda: self.play_media(), bg="#1e293b", fg="white", width=3)
        self.play_button.pack(side=tk.LEFT, padx=2)
        tk.Button(controls_row1, text="⏸️", command=lambda: self.pause_media(), bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(controls_row1, text="⏹️", command=lambda: self.stop_media(), bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2)

        # Botón para pantalla completa
        tk.Button(controls_row1, text="⛶", command=lambda: self.toggle_fullscreen_media(), bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT, padx=2)

        # Botones para ajustar el tamaño del video
        zoom_frame = tk.Frame(controls_row1, bg="black")
        zoom_frame.pack(side=tk.LEFT, padx=2)

        tk.Button(zoom_frame, text="-fit", command=self.fit_video_to_container, bg="#1e293b", fg="white", width=3).pack(side=tk.LEFT)
        tk.Button(zoom_frame, text="+", command=self.zoom_in_video, bg="#1e293b", fg="white", width=2).pack(side=tk.LEFT, padx=1)
        tk.Button(zoom_frame, text="-", command=self.zoom_out_video, bg="#1e293b", fg="white", width=2).pack(side=tk.LEFT, padx=1)

        # Control de volumen
        volume_frame = tk.Frame(button_frame, bg="black")
        volume_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(volume_frame, text="🔊", bg="black", fg="white").pack(side=tk.LEFT)
        self.volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     length=100, bg="black", fg="white", highlightthickness=0,
                                     command=self.set_volume, relief=tk.FLAT)
        self.volume_scale.set(80)  # Volumen inicial al 80%
        self.volume_scale.pack(side=tk.LEFT)

        # Barra de progreso
        progress_frame = tk.Frame(self.controls_frame, bg="black")
        progress_frame.pack(fill=tk.X, padx=5, pady=2)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = tk.Scale(progress_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     variable=self.progress_var, bg="black", fg="white",
                                     highlightthickness=0, relief=tk.FLAT,
                                     command=self.seek_video)
        self.progress_bar.pack(fill=tk.X)

        # Iniciar actualización del progreso
        self.update_progress()

        # Bandera para controlar la visibilidad de los controles
        self.controls_visible = True
        self.controls_hide_timer = None

        # Vincular eventos de teclado para controlar el reproductor
        self.video_container.bind("<Key>", self.handle_keyboard_controls)
        self.video_container.focus_set()  # Asegurar que el contenedor pueda recibir eventos de teclado
        self.video_container.focus_force()  # Forzar el foco en el contenedor de video

        # Vincular eventos de mouse para permitir mover la imagen/video dentro del contenedor
        self.video_container.bind("<ButtonPress-1>", self.start_pan_video)
        self.video_container.bind("<B1-Motion>", self.pan_video)
        self.video_container.bind("<ButtonRelease-1>", self.end_pan_video)

        # Almacenar dimensiones para uso posterior
        self.window_width = window_width
        self.window_height = window_height
        self.video_height = video_height
        self.controls_height = controls_height

        # Variables para el desplazamiento de video
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.video_offset_x = 0
        self.video_offset_y = 0
        self.is_panning = False

        # Variables para el zoom del video
        self.video_scale = 1.0  # Escala actual del video

    def start_pan_video(self, event):
        """Iniciar el desplazamiento del video"""
        # Solo permitir desplazamiento si no se está arrastrando controles
        if not self.controls_visible or event.y > self.video_container.winfo_height() - self.controls_frame.winfo_height():
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.is_panning = True

    def pan_video(self, event):
        """Desplazar el video mientras se mueve el mouse"""
        if self.is_panning and self.vlc_player:
            # Calcular desplazamiento
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y

            # Para VLC, el desplazamiento real del video es complejo
            # Vamos a usar la funcionalidad de video para ajustar la vista
            try:
                # Obtener dimensiones actuales del video
                video_width = self.vlc_player.video_get_width()
                video_height = self.vlc_player.video_get_height()

                if video_width > 0 and video_height > 0:
                    # Obtener dimensiones del contenedor
                    container_width = self.video_container.winfo_width()
                    container_height = self.video_container.winfo_height()

                    # Calcular proporciones
                    video_aspect = video_width / video_height
                    container_aspect = container_width / container_height

                    # Ajustar la posición de visualización si es posible
                    # Nota: Esta funcionalidad depende del backend de video y puede no funcionar en todos los casos
                    # Solo se intenta si el video es más grande que el contenedor
                    if video_width > container_width or video_height > container_height:
                        # Intentar usar la funcionalidad de ajuste de video de VLC
                        # Esto puede no estar disponible en todos los backends
                        pass  # La funcionalidad de desplazamiento real requiere técnicas específicas de video que no están disponibles en todos los backends de VLC
            except:
                pass  # Si no se pueden obtener dimensiones, continuar sin desplazamiento

            # Actualizar posición inicial para el próximo movimiento
            self.pan_start_x = event.x
            self.pan_start_y = event.y

    def end_pan_video(self, event):
        """Finalizar el desplazamiento del video"""
        self.is_panning = False

    def fit_video_to_container(self):
        """Ajustar el video al tamaño del contenedor"""
        if self.vlc_player:
            try:
                # Intentar ajustar el video para que se vea completo en el contenedor
                # Esto se hace obteniendo las dimensiones del video y ajustando la escala
                video_width = self.vlc_player.video_get_width()
                video_height = self.vlc_player.video_get_height()

                if video_width > 0 and video_height > 0:
                    # Obtener dimensiones del contenedor
                    container_width = self.video_container.winfo_width()
                    container_height = self.video_container.winfo_height()

                    if container_width > 1 and container_height > 1:
                        # Calcular proporciones
                        video_ratio = video_width / video_height
                        container_ratio = container_width / container_height

                        # Ajustar la escala para que el video se vea completo
                        if video_ratio > container_ratio:
                            # Video más ancho que el contenedor - ajustar ancho
                            scale_factor = container_width / video_width
                        else:
                            # Video más alto que el contenedor - ajustar alto
                            scale_factor = container_height / video_height

                        # Aplicar la escala
                        self.vlc_player.video_set_scale(scale_factor)
                        self.video_scale = scale_factor

                        # Actualizar la barra de estado si existe
                        if hasattr(self, 'status_bar'):
                            try:
                                self.status_bar.config(text=f"Video ajustado. Escala: {scale_factor:.2f}")
                            except:
                                pass  # Ignorar si el widget ya no existe
                    else:
                        # Si no se pueden obtener dimensiones del contenedor, usar ajuste predeterminado
                        self.vlc_player.video_set_scale(0)  # Ajuste automático
                        self.video_scale = 0
                        if hasattr(self, 'status_bar'):
                            try:
                                self.status_bar.config(text="Video ajustado al contenedor")
                            except:
                                pass  # Ignorar si el widget ya no existe
                else:
                    # Si no se pueden obtener dimensiones del video, usar ajuste predeterminado
                    self.vlc_player.video_set_scale(0)  # Ajuste automático
                    self.video_scale = 0
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text="Video ajustado al contenedor")
                        except:
                            pass  # Ignorar si el widget ya no existe
            except Exception as e:
                # Si no se puede ajustar, usar ajuste predeterminado
                try:
                    self.vlc_player.video_set_scale(0)  # Ajuste automático
                    self.video_scale = 0
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text="Video ajustado (automático)")
                        except:
                            pass  # Ignorar si el widget ya no existe
                except:
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text="No se pudo ajustar el video")
                        except:
                            pass  # Ignorar si el widget ya no existe

    def zoom_in_video(self):
        """Acercar el video"""
        if self.vlc_player:
            try:
                # Obtener la escala actual
                current_scale = self.vlc_player.video_get_scale()
                if current_scale == 0:  # Si es 0, significa que está usando ajuste automático
                    current_scale = self.video_scale if self.video_scale != 0 else 1.0

                # Aumentar la escala en un 25%
                new_scale = current_scale * 1.25
                self.vlc_player.video_set_scale(new_scale)
                self.video_scale = new_scale

                if hasattr(self, 'status_bar'):
                    try:
                        self.status_bar.config(text=f"Zoom: {new_scale:.2f}x")
                    except:
                        pass  # Ignorar si el widget ya no existe
            except:
                # Si no se puede obtener la escala actual, usar un valor predeterminado
                try:
                    new_scale = self.video_scale * 1.25 if self.video_scale != 0 else 1.25
                    self.vlc_player.video_set_scale(new_scale)
                    self.video_scale = new_scale
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text=f"Zoom: {new_scale:.2f}x")
                        except:
                            pass  # Ignorar si el widget ya no existe
                except:
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text="No se pudo aplicar zoom")
                        except:
                            pass  # Ignorar si el widget ya no existe

    def zoom_out_video(self):
        """Alejar el video"""
        if self.vlc_player:
            try:
                # Obtener la escala actual
                current_scale = self.vlc_player.video_get_scale()
                if current_scale == 0:  # Si es 0, significa que está usando ajuste automático
                    current_scale = self.video_scale if self.video_scale != 0 else 1.0

                # Disminuir la escala en un 25%
                new_scale = max(current_scale / 1.25, 0.1)  # Mínimo 0.1 para no hacerlo invisible
                self.vlc_player.video_set_scale(new_scale)
                self.video_scale = new_scale

                if hasattr(self, 'status_bar'):
                    try:
                        self.status_bar.config(text=f"Zoom: {new_scale:.2f}x")
                    except:
                        pass  # Ignorar si el widget ya no existe
            except:
                # Si no se puede obtener la escala actual, usar un valor predeterminado
                try:
                    new_scale = max(self.video_scale / 1.25, 0.1) if self.video_scale != 0 else 0.8
                    self.vlc_player.video_set_scale(new_scale)
                    self.video_scale = new_scale
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text=f"Zoom: {new_scale:.2f}x")
                        except:
                            pass  # Ignorar si el widget ya no existe
                except:
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text="No se pudo aplicar zoom")
                        except:
                            pass  # Ignorar si el widget ya no existe")

    def handle_keyboard_controls(self, event):
        """Manejar controles del reproductor mediante teclado"""
        key = event.keysym.lower()
        key_char = event.char  # Obtener el carácter presionado

        if key == 'space' or key == 'return' or key == 'enter':
            # Espacio o Enter para reproducir/pausar
            if self.vlc_player:
                if self.vlc_player.is_playing():
                    self.vlc_player.pause()
                    # Cambiar el texto del botón de pausa a play
                    if hasattr(self, 'play_button'):
                        try:
                            self.play_button.config(text="▶️")
                        except:
                            pass  # Ignorar si el widget ya no existe
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text="Pausado")
                        except:
                            pass  # Ignorar si el widget ya no existe
                else:
                    self.vlc_player.play()
                    # Cambiar el texto del botón de play a pausa
                    if hasattr(self, 'play_button'):
                        try:
                            self.play_button.config(text="⏸️")
                        except:
                            pass  # Ignorar si el widget ya no existe
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text="Reproduciendo...")
                        except:
                            pass  # Ignorar si el widget ya no existe
        elif key == 'left':
            # Flecha izquierda para retroceder 10 segundos
            self.seek_backward()
        elif key == 'right':
            # Flecha derecha para avanzar 10 segundos
            self.seek_forward()
        elif key == 'up':
            # Flecha arriba para aumentar volumen
            self.increase_volume()
        elif key == 'down':
            # Flecha abajo para disminuir volumen
            self.decrease_volume()
        elif key == 'f':
            # Tecla 'f' para pantalla completa
            self.toggle_fullscreen_media()
        elif key == 'escape':
            # Tecla Escape para salir de pantalla completa
            if hasattr(self, 'video_container'):
                media_window = self.video_container.winfo_toplevel()
                current_state = media_window.attributes('-fullscreen')
                if current_state:
                    media_window.attributes('-fullscreen', False)
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text="Modo: Ventana Normal")
                        except:
                            pass  # Ignorar si el widget ya no existe
        elif key == 'm':
            # Tecla 'm' para silenciar/desilenciar
            self.toggle_mute()
        elif key_char == '+':
            # Tecla '+' para acercar el video (zoom in)
            self.zoom_in_video()
        elif key_char == '-':
            # Tecla '-' para alejar el video (zoom out)
            self.zoom_out_video()
        elif key == '0':
            # Tecla '0' para restablecer el zoom
            if self.vlc_player:
                self.vlc_player.video_set_scale(1.0)  # Restablecer a tamaño original
                if hasattr(self, 'status_bar'):
                    try:
                        self.status_bar.config(text="Zoom restablecido")
                    except:
                        pass  # Ignorar si el widget ya no existe

    def seek_backward(self):
        """Retroceder 10 segundos en la reproducción"""
        if self.vlc_player:
            try:
                # Obtener tiempo actual
                current_time = self.vlc_player.get_time()
                # Retroceder 10 segundos (10000 ms)
                new_time = max(0, current_time - 10000)
                self.vlc_player.set_time(new_time)
            except:
                pass  # Ignorar si no se puede obtener el tiempo

    def seek_forward(self):
        """Avanzar 10 segundos en la reproducción"""
        if self.vlc_player:
            try:
                # Obtener tiempo actual
                current_time = self.vlc_player.get_time()
                # Avanzar 10 segundos (10000 ms)
                new_time = current_time + 10000
                self.vlc_player.set_time(new_time)
            except:
                pass  # Ignorar si no se puede obtener el tiempo

    def increase_volume(self):
        """Aumentar volumen"""
        if self.vlc_player:
            try:
                current_volume = self.vlc_player.audio_get_volume()
                new_volume = min(100, current_volume + 10)  # Aumentar 10%, máximo 100%
                self.vlc_player.audio_set_volume(new_volume)

                # Actualizar el slider de volumen si existe
                if hasattr(self, 'volume_scale'):
                    try:
                        self.volume_scale.set(new_volume)
                    except:
                        pass  # Ignorar si el widget ya no existe

                if hasattr(self, 'status_bar'):
                    try:
                        self.status_bar.config(text=f"Volumen: {new_volume}%")
                    except:
                        pass  # Ignorar si el widget ya no existe
            except:
                pass  # Ignorar si no se puede obtener/establecer el volumen

    def decrease_volume(self):
        """Disminuir volumen"""
        if self.vlc_player:
            try:
                current_volume = self.vlc_player.audio_get_volume()
                new_volume = max(0, current_volume - 10)  # Disminuir 10%, mínimo 0%
                self.vlc_player.audio_set_volume(new_volume)

                # Actualizar el slider de volumen si existe
                if hasattr(self, 'volume_scale'):
                    try:
                        self.volume_scale.set(new_volume)
                    except:
                        pass  # Ignorar si el widget ya no existe

                if hasattr(self, 'status_bar'):
                    try:
                        self.status_bar.config(text=f"Volumen: {new_volume}%")
                    except:
                        pass  # Ignorar si el widget ya no existe
            except:
                pass  # Ignorar si no se puede obtener/establecer el volumen

    def toggle_mute(self):
        """Silenciar/desilenciar el audio"""
        if self.vlc_player:
            try:
                is_muted = self.vlc_player.audio_get_mute()
                self.vlc_player.audio_set_mute(not is_muted)

                if hasattr(self, 'status_bar'):
                    try:
                        if not is_muted:
                            self.status_bar.config(text="Audio silenciado")
                        else:
                            self.status_bar.config(text="Audio activado")
                    except:
                        pass  # Ignorar si el widget ya no existe
            except:
                pass  # Ignorar si no se puede obtener/establecer el estado de silencio

    def load_media_file(self):
        """Cargar archivo de media real y vincularlo al reproductor"""
        from tkinter import filedialog
        import os
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Media", "*.mp4 *.mp3 *.avi *.mkv *.wav *.flv *.webm *.m4a *.ogg *.flac")]
        )
        if file_path:
            try:
                # 1. Crear el objeto Media
                self.media = self.vlc_instance.media_new(file_path)
                # 2. Asignar el media al reproductor
                self.vlc_player.set_media(self.media)

                # 3. VINCULACIÓN VISUAL (Crítico para ver el video)
                # Esto le dice a VLC que dibuje dentro de tu recuadro negro
                if hasattr(self.vlc_player, 'set_hwnd'):  # Windows
                    self.vlc_player.set_hwnd(self.video_container.winfo_id())
                elif hasattr(self.vlc_player, 'set_xwindow'):  # Linux
                    self.vlc_player.set_xwindow(self.video_container.winfo_id())
                elif hasattr(self.vlc_player, 'set_nsobject'):  # macOS
                    self.vlc_player.set_nsobject(self.video_container.winfo_id())

                # Obtener información del archivo de video para adaptar la reproducción
                self.media.parse()

                # Esperar un poco para que se parsee el archivo
                import time
                time.sleep(0.1)

                # Obtener dimensiones del video si es posible
                try:
                    # Obtener estadísticas del media
                    if self.media.get_duration() > 0:  # Verificar que se haya cargado correctamente
                        # Actualizar el status bar de la ventana principal si existe
                        if hasattr(self, 'status_bar'):
                            try:
                                self.status_bar.config(text=f"Cargado: {os.path.basename(file_path)}")
                            except:
                                pass  # Ignorar si el widget ya no existe
                        # También intentar actualizar el status_bar si está en otro contexto
                        elif hasattr(self, 'status_bar'):
                            try:
                                self.status_bar.config(text=f"Cargado: {os.path.basename(file_path)}")
                            except:
                                pass  # Ignorar si el widget ya no existe
                        # Si no hay status_bar, usar una alternativa
                        else:
                            # Actualizar la barra de estado del contenedor de video si existe
                            try:
                                # Buscar un widget de estado en el contexto actual
                                parent_window = self.video_container.winfo_toplevel()
                                # No actualizar status_bar directamente, solo registrar que se cargó
                                print(f"Archivo cargado: {os.path.basename(file_path)}")  # Registro temporal
                            except:
                                pass  # Ignorar si no se puede acceder al widget
                except:
                    # Si no se pueden obtener dimensiones, continuar de todas formas
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text=f"Cargado: {os.path.basename(file_path)}")
                        except:
                            pass  # Ignorar si el widget ya no existe
                    # También intentar actualizar el status_bar si está en otro contexto
                    elif hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text=f"Cargado: {os.path.basename(file_path)}")
                        except:
                            pass  # Ignorar si el widget ya no existe
                    # Si no hay status_bar, usar una alternativa
                    else:
                        # Actualizar la barra de estado del contenedor de video si existe
                        try:
                            # Buscar un widget de estado en el contexto actual
                            parent_window = self.video_container.winfo_toplevel()
                            # No actualizar status_bar directamente, solo registrar que se cargó
                            print(f"Archivo cargado: {os.path.basename(file_path)}")  # Registro temporal
                        except:
                            pass  # Ignorar si no se puede acceder al widget
            except Exception as e:
                # Actualizar el status bar de la ventana principal si existe
                if hasattr(self, 'status_bar'):
                    try:
                        self.status_bar.config(text=f"Error al cargar: {str(e)}")
                    except:
                        pass  # Ignorar si el widget ya no existe
                # También intentar actualizar el status_bar si está en otro contexto
                elif hasattr(self, 'status_bar'):
                    try:
                        self.status_bar.config(text=f"Error al cargar: {str(e)}")
                    except:
                        pass  # Ignorar si el widget ya no existe
                # Si no hay status_bar, usar una alternativa
                else:
                    # Actualizar la barra de estado del contenedor de video si existe
                    try:
                        # Buscar un widget de estado en el contexto actual
                        parent_window = self.video_container.winfo_toplevel()
                        # No actualizar status_bar directamente, solo registrar el error
                        print(f"Error al cargar: {str(e)}")  # Registro temporal
                    except:
                        pass  # Ignorar si no se puede acceder al widget

    def show_controls(self, event=None):
        """Mostrar la barra de controles"""
        if not self.controls_visible:
            try:
                # Restaurar la posición original de la barra de controles
                video_height = self.video_container.winfo_height()
                window_width = self.video_container.winfo_width()
                controls_height = self.controls_frame.winfo_reqheight()

                # Mostrar la barra de controles en la posición correcta
                self.controls_frame.place(x=0, y=video_height-controls_height, width=window_width, height=controls_height)
                self.controls_visible = True
            except:
                # Si no se pueden obtener las dimensiones, usar valores por defecto
                self.controls_frame.place(x=0, y=270, width=600, height=100)
                self.controls_visible = True

        # Reiniciar el temporizador para ocultar los controles
        if self.controls_hide_timer:
            try:
                self.controls_hide_timer.cancel()
            except:
                pass

        # Programar la ocultación de los controles después de 3 segundos de inactividad
        import threading
        self.controls_hide_timer = threading.Timer(3.0, self.auto_hide_controls)
        self.controls_hide_timer.start()

    def auto_hide_controls(self):
        """Ocultar la barra de controles automáticamente"""
        # Ejecutar en el hilo principal de GUI
        def hide():
            try:
                if self.controls_visible and self.vlc_player and self.vlc_player.is_playing():
                    # Ocultar la barra de controles
                    self.controls_frame.place_forget()
                    self.controls_visible = False
            except:
                # Si el widget ya no existe, ignorar el error
                pass

        # Usar after para ejecutar en el hilo de la GUI
        try:
            self.video_container.after(0, hide)
        except:
            # Si el contenedor ya no existe, ignorar el error
            pass

    def hide_controls(self):
        """Ocultar la barra de controles"""
        # Ejecutar en el hilo principal de GUI
        def hide():
            try:
                if self.controls_visible and self.vlc_player and self.vlc_player.is_playing():
                    self.controls_frame.place_forget()
                    self.controls_visible = False
            except:
                # Si el widget ya no existe, ignorar el error
                pass

        # Usar after para ejecutar en el hilo de la GUI
        try:
            self.video_container.after(0, hide)
        except:
            # Si el contenedor ya no existe, ignorar el error
            pass

    def handle_click_on_video(self, event):
        """Manejar clic en el video para mostrar controles"""
        # Mostrar controles al hacer clic
        self.show_controls()

        # Si se está reproduciendo, pausar; si está pausado, reproducir
        if self.vlc_player:
            if self.vlc_player.is_playing():
                self.vlc_player.pause()
                # Cambiar el texto del botón de play a pausa
                if hasattr(self, 'play_button'):
                    self.play_button.config(text="▶️")
            else:
                self.vlc_player.play()
                # Cambiar el texto del botón de pausa a play
                if hasattr(self, 'play_button'):
                    self.play_button.config(text="⏸️")

    def set_volume(self, val):
        """Establecer volumen del reproductor"""
        if self.vlc_player:
            volume = int(val)
            self.vlc_player.audio_set_volume(volume)

    def update_progress(self):
        """Actualizar la barra de progreso periódicamente"""
        if self.vlc_player and self.vlc_player.is_playing():
            try:
                # Obtener tiempo actual y duración total
                current_time = self.vlc_player.get_time()
                total_time = self.vlc_player.get_length()

                if total_time > 0:
                    # Calcular porcentaje de progreso
                    progress = (current_time / total_time) * 100
                    self.progress_var.set(progress)
            except:
                pass

        # Actualizar cada 500ms
        self.video_container.after(500, self.update_progress)

    def seek_video(self, val):
        """Buscar posición específica en el video"""
        if self.vlc_player:
            try:
                # Obtener duración total
                total_time = self.vlc_player.get_length()
                if total_time > 0:
                    # Calcular tiempo objetivo
                    target_time = (float(val) / 100) * total_time
                    self.vlc_player.set_time(int(target_time))
            except:
                pass

    def load_media_file(self):
        """Cargar archivo de media real y vincularlo al reproductor"""
        from tkinter import filedialog
        import os
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Media", "*.mp4 *.mp3 *.avi *.mkv *.wav *.flv *.webm *.m4a *.ogg *.flac")]
        )
        if file_path:
            try:
                # 1. Crear el objeto Media
                self.media = self.vlc_instance.media_new(file_path)
                # 2. Asignar el media al reproductor
                self.vlc_player.set_media(self.media)

                # 3. VINCULACIÓN VISUAL (Crítico para ver el video)
                # Esto le dice a VLC que dibuje dentro de tu recuadro negro
                if hasattr(self.vlc_player, 'set_hwnd'):  # Windows
                    self.vlc_player.set_hwnd(self.video_container.winfo_id())
                elif hasattr(self.vlc_player, 'set_xwindow'):  # Linux
                    self.vlc_player.set_xwindow(self.video_container.winfo_id())
                elif hasattr(self.vlc_player, 'set_nsobject'):  # macOS
                    self.vlc_player.set_nsobject(self.video_container.winfo_id())

                # Obtener información del archivo de video para adaptar la reproducción
                self.media.parse()

                # Intentar obtener las dimensiones del video para ajustar la reproducción
                # Esperar un poco para que la información esté disponible
                import time
                time.sleep(0.1)  # Breve espera para que se parsee el archivo

                # Obtener dimensiones del video si es posible
                try:
                    # Obtener estadísticas del media
                    if self.media.get_duration() > 0:  # Verificar que se haya cargado correctamente
                        # Actualizar el status bar de la ventana principal
                        if hasattr(self, 'status_bar'):
                            try:
                                self.status_bar.config(text=f"Cargado: {os.path.basename(file_path)}")
                            except:
                                pass  # Ignorar si el widget ya no existe
                except:
                    # Si no se pueden obtener dimensiones, continuar de todas formas
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text=f"Cargado: {os.path.basename(file_path)}")
                        except:
                            pass  # Ignorar si el widget ya no existe
            except Exception as e:
                # Actualizar el status bar de la ventana principal
                if hasattr(self, 'status_bar'):
                    try:
                        self.status_bar.config(text=f"Error al cargar: {str(e)}")
                    except:
                        pass  # Ignorar si el widget ya no existe
        from tkinter import filedialog
        import os
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Media", "*.mp4 *.mp3 *.avi *.mkv *.wav *.flv *.webm *.m4a *.ogg *.flac")]
        )
        if file_path:
            try:
                # 1. Crear el objeto Media
                self.media = self.vlc_instance.media_new(file_path)
                # 2. Asignar el media al reproductor
                self.vlc_player.set_media(self.media)

                # 3. VINCULACIÓN VISUAL (Crítico para ver el video)
                # Esto le dice a VLC que dibuje dentro de tu recuadro negro
                if hasattr(self.vlc_player, 'set_hwnd'):  # Windows
                    self.vlc_player.set_hwnd(self.video_container.winfo_id())
                elif hasattr(self.vlc_player, 'set_xwindow'):  # Linux
                    self.vlc_player.set_xwindow(self.video_container.winfo_id())
                elif hasattr(self.vlc_player, 'set_nsobject'):  # macOS
                    self.vlc_player.set_nsobject(self.video_container.winfo_id())

                # Obtener información del archivo de video para adaptar la reproducción
                self.media.parse()

                # Actualizar el status bar de la ventana principal
                if hasattr(self, 'status_bar'):
                    self.status_bar.config(text=f"Cargado: {os.path.basename(file_path)}")
            except Exception as e:
                # Actualizar el status bar de la ventana principal
                if hasattr(self, 'status_bar'):
                    self.status_bar.config(text=f"Error al cargar: {str(e)}")

    def play_media(self):
        """Reproducir media y ocultar controles automáticamente"""
        if self.vlc_player:
            # Antes de reproducir, intentar obtener las dimensiones del video
            # para ajustar la reproducción a la resolución del equipo
            try:
                # Iniciar la reproducción
                self.vlc_player.play()

                # Intentar obtener las dimensiones del video después de un breve momento
                import time
                time.sleep(0.5)  # Esperar a que el video comience

                # Obtener dimensiones del video si es posible
                video_width = self.vlc_player.video_get_width()
                video_height = self.vlc_player.video_get_height()

                if video_width > 0 and video_height > 0:
                    # Obtener dimensiones del contenedor de video
                    container_width = self.video_container.winfo_width()
                    container_height = self.video_container.winfo_height()

                    # Si las dimensiones son válidas, ajustar si es necesario
                    if container_width > 1 and container_height > 1:
                        # Calcular la proporción del video
                        video_ratio = video_width / video_height
                        container_ratio = container_width / container_height

                        # Ajustar la visualización según la proporción
                        if video_ratio > container_ratio:
                            # Video más ancho que el contenedor - ajustar ancho
                            self.vlc_player.video_set_scale(container_width / video_width)
                        else:
                            # Video más alto que el contenedor - ajustar alto
                            self.vlc_player.video_set_scale(container_height / video_height)

            except Exception as e:
                # Si no se pueden obtener dimensiones, reproducir normalmente
                pass

            # Cambiar el texto del botón de play a pausa
            if hasattr(self, 'play_button'):
                self.play_button.config(text="⏸️")

            # Ocultar la barra de controles después de comenzar la reproducción
            self.hide_controls_after_play()

            # Actualizar la barra de estado si existe
            if hasattr(self, 'status_bar'):
                try:
                    self.status_bar.config(text="Reproduciendo...")
                except:
                    pass  # Ignorar si el widget ya no existe

    def hide_controls_after_play(self):
        """Ocultar la barra de controles después de comenzar la reproducción"""
        # Ocultar controles después de un breve periodo
        def delayed_hide():
            try:
                if self.vlc_player and self.vlc_player.is_playing():
                    self.controls_frame.lower()  # Enviar al fondo para que no interfiera
                    self.controls_frame.place_forget()  # Ocultar la barra de controles
                    self.controls_visible = False
            except:
                # Si el widget ya no existe, ignorar el error
                pass

        # Ejecutar después de 2 segundos para dar tiempo a la reproducción a comenzar
        try:
            self.video_container.after(2000, delayed_hide)
        except:
            # Si el contenedor ya no existe, ignorar el error
            pass

    def pause_media(self):
        if self.vlc_player:
            self.vlc_player.pause()
            # Cambiar el texto del botón de pausa a play
            if hasattr(self, 'play_button'):
                try:
                    self.play_button.config(text="▶️")
                except:
                    pass  # Ignorar si el widget ya no existe
            if hasattr(self, 'status_bar'):
                try:
                    self.status_bar.config(text="Pausado")
                except:
                    pass  # Ignorar si el widget ya no existe

    def stop_media(self):
        """Detener media"""
        if self.vlc_player:
            self.vlc_player.stop()

        # Actualizar la barra de estado si existe
        if hasattr(self, 'status_bar'):
            try:
                self.status_bar.config(text="Detenido")
            except:
                pass  # Ignorar si el widget ya no existe


    def load_media_file(self):
        """Cargar archivo de media real y vincularlo al reproductor"""
        from tkinter import filedialog
        import os
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Media", "*.mp4 *.mp3 *.avi *.mkv *.wav *.flv *.webm *.m4a *.ogg *.flac")]
        )
        if file_path:
            try:
                # 1. Crear el objeto Media
                self.media = self.vlc_instance.media_new(file_path)
                # 2. Asignar el media al reproductor
                self.vlc_player.set_media(self.media)

                # 3. VINCULACIÓN VISUAL (Crítico para ver el video)
                # Esto le dice a VLC que dibuje dentro de tu recuadro negro
                if hasattr(self.vlc_player, 'set_hwnd'):  # Windows
                    self.vlc_player.set_hwnd(self.video_container.winfo_id())
                elif hasattr(self.vlc_player, 'set_xwindow'):  # Linux
                    self.vlc_player.set_xwindow(self.video_container.winfo_id())
                elif hasattr(self.vlc_player, 'set_nsobject'):  # macOS
                    self.vlc_player.set_nsobject(self.video_container.winfo_id())

                # Obtener información del archivo de video para adaptar la reproducción
                self.media.parse()

                # Intentar obtener las dimensiones del video para ajustar la reproducción
                # Esperar un poco para que la información esté disponible
                import time
                time.sleep(0.1)  # Breve espera para que se parsee el archivo

                # Obtener dimensiones del video si es posible
                try:
                    # Obtener estadísticas del media
                    if self.media.get_duration() > 0:  # Verificar que se haya cargado correctamente
                        # Actualizar el status bar de la ventana principal
                        if hasattr(self, 'status_bar'):
                            try:
                                self.status_bar.config(text=f"Cargado: {os.path.basename(file_path)}")
                            except:
                                pass  # Ignorar si el widget ya no existe
                except:
                    # Si no se pueden obtener dimensiones, continuar de todas formas
                    if hasattr(self, 'status_bar'):
                        try:
                            self.status_bar.config(text=f"Cargado: {os.path.basename(file_path)}")
                        except:
                            pass  # Ignorar si el widget ya no existe
            except Exception as e:
                # Actualizar el status bar de la ventana principal
                if hasattr(self, 'status_bar'):
                    try:
                        self.status_bar.config(text=f"Error al cargar: {str(e)}")
                    except:
                        pass  # Ignorar si el widget ya no existe
        from tkinter import filedialog
        import os
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Media", "*.mp4 *.mp3 *.avi *.mkv *.wav *.flv *.webm *.m4a *.ogg *.flac")]
        )
        if file_path:
            try:
                # 1. Crear el objeto Media
                self.media = self.vlc_instance.media_new(file_path)
                # 2. Asignar el media al reproductor
                self.vlc_player.set_media(self.media)

                # 3. VINCULACIÓN VISUAL (Crítico para ver el video)
                # Esto le dice a VLC que dibuje dentro de tu recuadro negro
                if hasattr(self.vlc_player, 'set_hwnd'):  # Windows
                    self.vlc_player.set_hwnd(self.video_container.winfo_id())
                elif hasattr(self.vlc_player, 'set_xwindow'):  # Linux
                    self.vlc_player.set_xwindow(self.video_container.winfo_id())
                elif hasattr(self.vlc_player, 'set_nsobject'):  # macOS
                    self.vlc_player.set_nsobject(self.video_container.winfo_id())

                if hasattr(self, 'status_bar'):
                    self.status_bar.config(text=f"Cargado: {os.path.basename(file_path)}")
            except Exception as e:
                if hasattr(self, 'status_bar'):
                    self.status_bar.config(text=f"Error al cargar: {str(e)}")

    def play_media(self):
        """Activar la reproducción de video y sonido"""
        if self.vlc_player:
            self.vlc_player.play() # Esta es la orden que inicia todo

            # Actualizar la barra de estado si existe
            if hasattr(self, 'status_bar'):
                try:
                    self.status_bar.config(text="Reproduciendo...")
                except:
                    pass  # Ignorar si el widget ya no existe
            # También intentar actualizar el status_bar si está en otro contexto
            elif hasattr(self, 'status_bar'):
                try:
                    self.status_bar.config(text="Reproduciendo...")
                except:
                    pass  # Ignorar si el widget ya no existe

    def pause_media(self):
        if self.vlc_player:
            self.vlc_player.pause()
            # Cambiar el texto del botón de pausa a play
            if hasattr(self, 'play_button'):
                try:
                    self.play_button.config(text="▶️")
                except:
                    pass  # Ignorar si el widget ya no existe
            if hasattr(self, 'status_bar'):
                try:
                    self.status_bar.config(text="Pausado")
                except:
                    pass  # Ignorar si el widget ya no existe

    def toggle_fullscreen_media(self):
        """Alternar entre pantalla completa y ventana normal para el reproductor"""
        # Obtener la ventana principal del reproductor
        media_window = self.video_container.winfo_toplevel()

        # Alternar el estado de pantalla completa
        current_state = media_window.attributes('-fullscreen')
        new_state = not current_state
        media_window.attributes('-fullscreen', new_state)

        # Ajustar el tamaño del contenedor de video según el estado
        if new_state:  # Entrando en pantalla completa
            # Expandir el contenedor de video para ocupar toda la ventana
            self.video_container.place(x=0, y=0, relwidth=1, relheight=1)
            # Mostrar la barra de controles al entrar en pantalla completa
            self.controls_frame.lift()
            # Obtener dimensiones de la pantalla completa
            screen_width = media_window.winfo_screenwidth()
            screen_height = media_window.winfo_screenheight()
            self.controls_frame.place(x=0, y=screen_height-self.controls_frame.winfo_reqheight(),
                                     width=screen_width, height=self.controls_frame.winfo_reqheight())
            self.controls_visible = True
        else:  # Saliendo de pantalla completa
            # Restaurar el tamaño original del contenedor de video
            self.video_container.place(x=0, y=0, width=self.window_width, height=self.video_height)
            # Restaurar la barra de controles en su posición original
            self.controls_frame.lift()
            self.controls_frame.place(x=0, y=self.video_height, width=self.window_width, height=self.controls_height)
            self.controls_visible = True

        # Actualizar la barra de estado si existe
        if hasattr(self, 'status_bar'):
            try:
                if new_state:
                    self.status_bar.config(text="Modo: Pantalla Completa")
                else:
                    self.status_bar.config(text="Modo: Ventana Normal")
            except:
                pass  # Ignorar si el widget ya no existe

        # Reiniciar el temporizador para ocultar los controles
        if self.controls_hide_timer:
            try:
                self.controls_hide_timer.cancel()
            except:
                pass

        # Programar la ocultación de los controles después de 3 segundos de inactividad
        import threading
        self.controls_hide_timer = threading.Timer(3.0, self.auto_hide_controls)
        self.controls_hide_timer.start()


    def update_analog_clock(self):
        """Actualizar el reloj analógico con la hora de Buenos Aires"""
        import math

        # Obtener la hora actual en Buenos Aires
        tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')
        now = datetime.now(tz_buenos_aires)

        # Actualizar la fecha
        if hasattr(self, 'date_label'):
            self.date_label.config(text=now.strftime("%d/%m/%Y"))

        # Limpiar el canvas si existe
        if hasattr(self, 'clock_canvas'):
            self.clock_canvas.delete("all")

            # Dimensiones del reloj
            width = 180
            height = 180
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 2 - 10

            # Dibujar el borde del reloj con incrustaciones de diamantes azules (lujo)
            for i in range(12):
                angle = math.radians(i * 30)
                x = center_x + (radius - 5) * math.sin(angle)
                y = center_y - (radius - 5) * math.cos(angle)

                # Dibujar diamantes azules de lujo en posiciones de horas
                self.clock_canvas.create_oval(x-4, y-4, x+4, y+4, fill="#00d4ff", outline="white", width=1)

            # Dibujar el centro del reloj
            self.clock_canvas.create_oval(center_x-8, center_y-8, center_x+8, center_y+8, fill="black", outline=COLORS['gold'], width=2)

            # Calcular ángulos para las manecillas
            hour_angle = math.radians((now.hour % 12) * 30 + now.minute * 0.5)
            minute_angle = math.radians(now.minute * 6 + now.second * 0.1)
            second_angle = math.radians(now.second * 6)

            # Dibujar manecilla de horas
            hour_length = radius * 0.5
            hour_x = center_x + hour_length * math.sin(hour_angle)
            hour_y = center_y - hour_length * math.cos(hour_angle)
            self.clock_canvas.create_line(center_x, center_y, hour_x, hour_y, width=6, fill=COLORS['gold'])

            # Dibujar manecilla de minutos
            minute_length = radius * 0.7
            minute_x = center_x + minute_length * math.sin(minute_angle)
            minute_y = center_y - minute_length * math.cos(minute_angle)
            self.clock_canvas.create_line(center_x, center_y, minute_x, minute_y, width=4, fill=COLORS['gold'])

            # Dibujar manecilla de segundos (más delgada y larga)
            second_length = radius * 0.8
            second_x = center_x + second_length * math.sin(second_angle)
            second_y = center_y - second_length * math.cos(second_angle)
            self.clock_canvas.create_line(center_x, center_y, second_x, second_y, width=2, fill="#00d4ff")  # Azul brillante para segundos

            # Actualizar el reloj cada 1000ms (1 segundo)
            self.clock_canvas.after(1000, self.update_analog_clock)


if __name__ == "__main__":
    root = tk.Tk()
    app = PapiwebProOS(root)
    root.mainloop()