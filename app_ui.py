"""Tkinter interface for Sip Time Cafe."""

from __future__ import annotations

import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional, Tuple

from cooling_model import CoolingModel, PredictionResult
from drink_data import (
    COLORS,
    CUP_PROFILES,
    DEFAULT_COLD_LIMIT,
    DEFAULT_CUP,
    DEFAULT_DRINK,
    DEFAULT_GOOD_HIGH,
    DEFAULT_GOOD_LOW,
    DEFAULT_HOT_LIMIT,
    DEFAULT_ROOM_TEMP,
    DRINK_PROFILES,
    FONT_FAMILY,
    POPULAR_DRINKS,
    SIMULATION_MINUTES,
)
from settings_store import load_settings, save_settings


class TemperaturePredictorApp:
    """Tkinter interface for the hot drink cooling predictor."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sip Time Cafe")
        self.root.geometry("1180x790")
        self.root.minsize(1040, 700)

        self.result: Optional[PredictionResult] = None
        self.model: Optional[CoolingModel] = None
        self.drink_cards: Dict[str, tk.Frame] = {}
        self.metric_labels: Dict[str, tk.Label] = {}

        self.drink_type = tk.StringVar(value=DEFAULT_DRINK)
        self.initial_temp = tk.StringVar(
            value=f"{DRINK_PROFILES[DEFAULT_DRINK].suggested_temp:.0f}"
        )
        self.room_temp = tk.StringVar(value=f"{DEFAULT_ROOM_TEMP:.0f}")
        self.cup_type = tk.StringVar(value=DEFAULT_CUP)
        self.hot_limit = tk.DoubleVar(value=DEFAULT_HOT_LIMIT)
        self.good_high = tk.DoubleVar(value=DEFAULT_GOOD_HIGH)
        self.good_low = tk.DoubleVar(value=DEFAULT_GOOD_LOW)
        self.cold_limit = tk.DoubleVar(value=DEFAULT_COLD_LIMIT)
        self.inspect_minute = tk.DoubleVar(value=0)
        self.loaded_saved_settings = self.load_saved_settings()

        self._configure_style()
        self._build_layout()
        self.calculate()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["background"])
        style.configure("TLabel", background=COLORS["background"], foreground=COLORS["ink"])
        style.configure("TEntry", padding=5, fieldbackground="#ffffff")
        style.configure("TCombobox", padding=5, fieldbackground="#ffffff")
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#ffffff")],
            foreground=[("readonly", COLORS["ink"])],
        )
        style.configure(
            "Treeview",
            background=COLORS["panel"],
            fieldbackground=COLORS["panel"],
            foreground=COLORS["ink"],
            rowheight=22,
            font=(FONT_FAMILY, 9),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["slate"],
            foreground="#ffffff",
            font=(FONT_FAMILY, 9, "bold"),
            relief="flat",
        )

    def _build_layout(self) -> None:
        self.root.configure(bg=COLORS["background"])
        main = tk.Frame(self.root, bg=COLORS["background"], padx=26, pady=20)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0, minsize=275)
        main.rowconfigure(0, weight=1)

        workspace = tk.Frame(main, bg=COLORS["background"])
        workspace.grid(row=0, column=0, sticky="nsew", padx=(0, 24))
        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(2, weight=1, minsize=245)

        self._build_header(workspace)
        self._build_overview_panel(workspace)
        self._build_chart_panel(workspace)
        self._build_bottom_panels(workspace)
        self._build_actions_panel(self._create_scrollable_actions(main))

    def _create_scrollable_actions(self, parent: tk.Frame) -> tk.Frame:
        shell = self._panel(parent)
        shell.grid(row=0, column=1, sticky="ns")
        shell.grid_propagate(False)
        shell.configure(width=290)
        shell.rowconfigure(0, weight=1)
        shell.columnconfigure(0, weight=1)

        canvas = tk.Canvas(
            shell,
            bg=COLORS["panel"],
            highlightthickness=0,
            width=286,
        )
        scrollbar = ttk.Scrollbar(shell, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        inner = tk.Frame(canvas, bg=COLORS["panel"], padx=20, pady=4)
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def update_scroll_region(_event: object = None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_inner_width(event: tk.Event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def on_mousewheel(event: tk.Event) -> None:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        inner.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", fit_inner_width)
        canvas.bind("<Enter>", lambda _event: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _event: canvas.unbind_all("<MouseWheel>"))
        self.actions_canvas = canvas
        return inner

    def _build_header(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent, bg=COLORS["background"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        tk.Label(
            header,
            text="Sip Time Cafe",
            bg=COLORS["background"],
            fg=COLORS["ink"],
            font=(FONT_FAMILY, 26, "bold"),
        ).pack(anchor="w")

        self.header_status = tk.Label(
            header,
            text="",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 11),
        )
        self.header_status.pack(anchor="w", pady=(3, 0))

    def _build_overview_panel(self, parent: tk.Frame) -> None:
        overview = tk.Frame(parent, bg=COLORS["background"])
        overview.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        overview.columnconfigure(0, weight=2)
        overview.columnconfigure(1, weight=1)
        overview.columnconfigure(2, weight=1)
        overview.columnconfigure(3, weight=1)

        hero = self._panel(overview, padx=22, pady=16)
        hero.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        tk.Label(
            hero,
            text="BEST SIP TIME",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 9, "bold"),
        ).pack(anchor="w")
        mascot_row = tk.Frame(hero, bg=COLORS["panel"])
        mascot_row.pack(fill="x")
        self.best_value_label = tk.Label(
            mascot_row,
            text="--",
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=(FONT_FAMILY, 36, "bold"),
        )
        self.best_value_label.pack(side="left", anchor="w", pady=(4, 0))
        mascot = tk.Canvas(
            mascot_row,
            width=62,
            height=54,
            bg=COLORS["panel"],
            highlightthickness=0,
        )
        mascot.pack(side="right", padx=(8, 0))
        self._draw_mug_mascot(mascot)
        self.best_meta_label = tk.Label(
            hero,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            font=(FONT_FAMILY, 10),
            justify="left",
        )
        self.best_meta_label.pack(anchor="w", pady=(2, 0))

        for index, (key, title, color) in enumerate(
            [
                ("safe", "Safe From", COLORS["red"]),
                ("ready", "Ready Window", COLORS["green_dark"]),
                ("cool", "Cool At", COLORS["blue"]),
            ],
            start=1,
        ):
            card = self._panel(overview, padx=14, pady=13)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 1 else 10, 0))
            tk.Frame(card, bg=color, height=4).pack(fill="x", pady=(0, 10))
            tk.Label(
                card,
                text=title,
                bg=COLORS["panel"],
                fg=COLORS["muted"],
                font=(FONT_FAMILY, 9, "bold"),
            ).pack(anchor="w")
            value = tk.Label(
                card,
                text="--",
                bg=COLORS["panel"],
                fg=COLORS["ink"],
                font=(FONT_FAMILY, 18, "bold"),
            )
            value.pack(anchor="w", pady=(5, 0))
            self.metric_labels[key] = value

    def _bind_card_click(self, widget: tk.Widget, drink_name: str) -> None:
        widget.bind("<Button-1>", lambda _event: self._select_drink(drink_name))
        for child in widget.winfo_children():
            self._bind_card_click(child, drink_name)

    def _build_chart_panel(self, parent: tk.Frame) -> None:
        panel = self._panel(parent)
        panel.grid(row=2, column=0, sticky="nsew", pady=(0, 16))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        header = tk.Frame(panel, bg=COLORS["slate"], height=34)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(
            header,
            text="Cooling Curve",
            bg=COLORS["slate"],
            fg="#ffffff",
            font=(FONT_FAMILY, 11),
            padx=16,
            pady=7,
        ).pack(anchor="w")

        self.canvas = tk.Canvas(panel, bg=COLORS["panel"], highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=12, pady=10)
        self.canvas.bind("<Configure>", lambda _event: self.draw_graph())

    def _build_bottom_panels(self, parent: tk.Frame) -> None:
        bottom = tk.Frame(parent, bg=COLORS["background"])
        bottom.grid(row=3, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)

        timeline_panel = self._panel(bottom)
        timeline_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self._panel_header(timeline_panel, "Prediction Summary")
        self.timeline = ttk.Treeview(
            timeline_panel,
            columns=("time", "temp", "state"),
            show="headings",
            height=5,
        )
        self.timeline.heading("time", text="Time")
        self.timeline.heading("temp", text="Temperature")
        self.timeline.heading("state", text="Status")
        self.timeline.column("time", width=90, anchor="center")
        self.timeline.column("temp", width=110, anchor="center")
        self.timeline.column("state", width=180, anchor="w")
        self.timeline.pack(fill="both", expand=True, padx=14, pady=12)

        notes_panel = self._panel(bottom)
        notes_panel.grid(row=0, column=1, sticky="nsew")
        self._panel_header(notes_panel, "Model Notes")
        self.explanation_text = tk.Text(
            notes_panel,
            height=6,
            wrap="word",
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            relief="flat",
            font=(FONT_FAMILY, 10),
        )
        self.explanation_text.pack(fill="both", expand=True, padx=16, pady=12)
        self.explanation_text.configure(state="disabled")

    def _build_actions_panel(self, parent: tk.Frame) -> None:
        tk.Label(
            parent,
            text="Actions",
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            font=(FONT_FAMILY, 13),
        ).pack(anchor="w", pady=(0, 6))

        row = tk.Frame(parent, bg=COLORS["panel"])
        row.pack(fill="x", pady=(0, 0))
        self._button(
            row,
            "Predict",
            COLORS["accent"],
            COLORS["accent_dark"],
            self.calculate,
            side="left",
            expand=True,
            padx=(0, 3),
        )
        self._button(
            row,
            "Save",
            COLORS["green"],
            COLORS["green_dark"],
            self.save_current_settings,
            side="left",
            expand=True,
            padx=3,
        )
        self._button(
            row,
            "Export",
            COLORS["blue"],
            COLORS["blue_dark"],
            self.export_csv,
            side="left",
            expand=True,
            padx=3,
        )
        self._button(
            row,
            "Reset",
            COLORS["red"],
            COLORS["red_dark"],
            self.reset_defaults,
            side="left",
            expand=True,
            padx=(3, 0),
        )

        self._section_label(parent, "Quick Drinks", top=14)
        quick_grid = tk.Frame(parent, bg=COLORS["panel"])
        quick_grid.pack(fill="x")
        for index, (drink_name, display_name, color) in enumerate(POPULAR_DRINKS):
            quick_grid.columnconfigure(index % 2, weight=1)
            chip = tk.Frame(
                quick_grid,
                bg=COLORS["panel_alt"],
                highlightthickness=1,
                highlightbackground=COLORS["line"],
                padx=7,
                pady=6,
                cursor="hand2",
            )
            chip.grid(
                row=index // 2,
                column=index % 2,
                sticky="ew",
                padx=(0 if index % 2 == 0 else 6, 0),
                pady=(0, 6),
            )
            self.drink_cards[drink_name] = chip
            dot = tk.Canvas(
                chip,
                width=18,
                height=18,
                bg=COLORS["panel_alt"],
                highlightthickness=0,
            )
            dot.pack(side="left", padx=(0, 6))
            dot.create_oval(3, 3, 15, 15, fill=color, outline="")
            tk.Label(
                chip,
                text=display_name,
                bg=COLORS["panel_alt"],
                fg=COLORS["ink"],
                font=(FONT_FAMILY, 9),
            ).pack(side="left")
            self._bind_card_click(chip, drink_name)

        self._section_label(parent, "Drink Setup", top=12)
        drink_box = ttk.Combobox(
            parent,
            textvariable=self.drink_type,
            values=list(DRINK_PROFILES.keys()),
            state="readonly",
        )
        self._field(parent, "Drink type", drink_box)
        drink_box.bind("<<ComboboxSelected>>", self._on_drink_changed)

        cup_box = ttk.Combobox(
            parent,
            textvariable=self.cup_type,
            values=list(CUP_PROFILES.keys()),
            state="readonly",
        )
        self._field(parent, "Cup type", cup_box)
        cup_box.bind("<<ComboboxSelected>>", self._on_cup_changed)

        temp_row = tk.Frame(parent, bg=COLORS["panel"])
        temp_row.pack(fill="x", pady=(5, 0))
        temp_row.columnconfigure(0, weight=1)
        temp_row.columnconfigure(1, weight=1)
        tk.Label(temp_row, text="Start °C", bg=COLORS["panel"], fg=COLORS["muted"]).grid(
            row=0, column=0, sticky="w", padx=(0, 6)
        )
        tk.Label(temp_row, text="Room °C", bg=COLORS["panel"], fg=COLORS["muted"]).grid(
            row=0, column=1, sticky="w", padx=(6, 0)
        )
        initial_entry = ttk.Entry(temp_row, textvariable=self.initial_temp)
        room_entry = ttk.Entry(temp_row, textvariable=self.room_temp)
        initial_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(3, 0))
        room_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(3, 0))
        self._bind_prediction_entry(initial_entry)
        self._bind_prediction_entry(room_entry)

        self.setup_note = self._note_label(parent)

        self._section_label(parent, "Comfort Range", top=12)
        self._slider(parent, "Too hot above", self.hot_limit, 55, 80)
        self._slider(parent, "Ready upper", self.good_high, 45, 70)
        self._slider(parent, "Ready lower", self.good_low, 35, 65)
        self._slider(parent, "Cool below", self.cold_limit, 25, 55)

        self._section_label(parent, "Inspect", top=9)
        minute_slider = ttk.Scale(
            parent,
            from_=0,
            to=SIMULATION_MINUTES,
            variable=self.inspect_minute,
            command=lambda _value: self.update_inspector(),
        )
        minute_slider.pack(fill="x", pady=(2, 4))
        self.inspector_label = tk.Label(
            parent,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            font=(FONT_FAMILY, 9),
            anchor="w",
            justify="left",
        )
        self.inspector_label.pack(fill="x")

        self._update_drink_note()
        self._update_cup_note()

    def _panel(self, parent: tk.Widget, padx: int = 0, pady: int = 0) -> tk.Frame:
        return tk.Frame(
            parent,
            bg=COLORS["panel"],
            padx=padx,
            pady=pady,
            highlightthickness=1,
            highlightbackground=COLORS["line"],
            relief="flat",
        )

    def _panel_header(self, parent: tk.Frame, text: str) -> None:
        header = tk.Frame(parent, bg=COLORS["slate"])
        header.pack(fill="x")
        tk.Label(
            header,
            text=text,
            bg=COLORS["slate"],
            fg="#ffffff",
            font=(FONT_FAMILY, 10),
            padx=14,
            pady=7,
        ).pack(anchor="w")

    def _button(
        self,
        parent: tk.Widget,
        text: str,
        bg: str,
        active_bg: str,
        command,
        side: str = "top",
        expand: bool = False,
        padx: Tuple[int, int] = (0, 0),
    ) -> None:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg="#ffffff",
            activebackground=active_bg,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            font=(FONT_FAMILY, 9),
            cursor="hand2",
            pady=6,
        )
        button.pack(side=side, fill="x", expand=expand, padx=padx, pady=(0, 0))

    def _section_label(self, parent: tk.Widget, text: str, top: int = 0) -> None:
        tk.Label(
            parent,
            text=text,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 10),
        ).pack(anchor="w", pady=(top, 5))

    def _field(self, parent: tk.Widget, label: str, widget: ttk.Widget) -> None:
        tk.Label(
            parent,
            text=label,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 9),
        ).pack(anchor="w")
        widget.pack(fill="x", pady=(2, 6))

    def _note_label(self, parent: tk.Widget) -> tk.Label:
        label = tk.Label(
            parent,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 9),
            wraplength=220,
            justify="left",
            anchor="w",
        )
        label.pack(fill="x", pady=(6, 0))
        return label

    def _bind_prediction_entry(self, widget: ttk.Entry) -> None:
        widget.bind("<Return>", lambda _event: self.calculate())
        widget.bind("<FocusOut>", lambda _event: self.calculate(silent=True))

    def _slider(
        self,
        parent: tk.Widget,
        label: str,
        variable: tk.DoubleVar,
        minimum: float,
        maximum: float,
    ) -> None:
        row = tk.Frame(parent, bg=COLORS["panel"])
        row.pack(fill="x", pady=(1, 0))
        tk.Label(
            row,
            text=label,
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            font=(FONT_FAMILY, 9),
        ).pack(side="left")

        value_text = tk.StringVar(value=f"{variable.get():.0f}°C")
        tk.Label(
            row,
            textvariable=value_text,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            width=5,
            anchor="e",
            font=(FONT_FAMILY, 9),
        ).pack(side="right")

        def update_value_label(*_args: object) -> None:
            value_text.set(f"{variable.get():.0f}°C")

        variable.trace_add("write", update_value_label)

        def on_change(raw_value: str) -> None:
            rounded = round(float(raw_value))
            if abs(variable.get() - rounded) > 0.001:
                variable.set(rounded)
            self.calculate(silent=True)

        scale = tk.Scale(
            parent,
            from_=minimum,
            to=maximum,
            orient="horizontal",
            resolution=1,
            variable=variable,
            command=on_change,
            showvalue=False,
            bg=COLORS["panel"],
            highlightthickness=0,
            troughcolor="#d9e5ee",
            activebackground=COLORS["accent"],
            sliderrelief="flat",
        )
        scale.pack(fill="x", pady=(0, 2))

    def _draw_drink_icon(self, canvas: tk.Canvas, drink_name: str, color: str) -> None:
        canvas.delete("all")
        if "tea" in drink_name.lower() or "water" in drink_name.lower():
            canvas.create_oval(10, 16, 48, 48, outline=color, width=3)
            canvas.create_arc(42, 24, 62, 42, start=-75, extent=150, outline=color, width=3)
            canvas.create_line(18, 26, 42, 26, fill=color, width=3)
            canvas.create_oval(28, 5, 48, 24, outline=color, width=3)
            canvas.create_line(32, 20, 44, 8, fill=color, width=2)
        else:
            canvas.create_arc(17, 0, 41, 26, start=80, extent=80, outline=color, width=2)
            canvas.create_arc(28, 0, 52, 26, start=80, extent=80, outline=color, width=2)
            canvas.create_oval(12, 18, 48, 52, outline=color, width=3)
            canvas.create_rectangle(12, 30, 48, 44, outline="", fill=COLORS["panel"])
            canvas.create_arc(42, 25, 63, 45, start=-70, extent=140, outline=color, width=3)
            canvas.create_line(15, 50, 45, 50, fill=color, width=3)
            canvas.create_oval(21, 24, 39, 39, fill=color, outline="")

    def _draw_mug_mascot(self, canvas: tk.Canvas) -> None:
        canvas.create_arc(12, 0, 30, 24, start=70, extent=90, outline=COLORS["accent"], width=2)
        canvas.create_arc(30, 0, 48, 24, start=70, extent=90, outline=COLORS["blue"], width=2)
        canvas.create_oval(8, 16, 48, 50, fill="#f7f2ff", outline=COLORS["accent"], width=2)
        canvas.create_arc(42, 24, 64, 44, start=-70, extent=140, outline=COLORS["accent"], width=2)
        canvas.create_oval(21, 30, 25, 34, fill=COLORS["ink"], outline="")
        canvas.create_oval(33, 30, 37, 34, fill=COLORS["ink"], outline="")
        canvas.create_arc(24, 32, 36, 43, start=200, extent=140, outline=COLORS["accent_dark"], width=2)
        canvas.create_oval(13, 36, 20, 42, fill="#d8f5ff", outline="")
        canvas.create_oval(38, 36, 45, 42, fill="#d8f5ff", outline="")

    def _select_drink(self, drink_name: str) -> None:
        drink = DRINK_PROFILES[drink_name]
        self.drink_type.set(drink_name)
        self.initial_temp.set(f"{drink.suggested_temp:.0f}")
        self._update_drink_note()
        self.calculate(silent=True)

    def _refresh_drink_cards(self) -> None:
        selected = self.drink_type.get()
        for drink_name, card in self.drink_cards.items():
            active = drink_name == selected
            bg = COLORS["panel"] if active else COLORS["panel_alt"]
            card.configure(
                bg=bg,
                highlightbackground=COLORS["accent"] if active else COLORS["line"],
                highlightthickness=2 if active else 1,
            )
            for child in card.winfo_children():
                try:
                    child.configure(bg=bg)
                except tk.TclError:
                    pass

    def _update_cup_note(self) -> None:
        self._update_setup_note()

    def _update_drink_note(self) -> None:
        self._update_setup_note()

    def _update_setup_note(self) -> None:
        drink = DRINK_PROFILES[self.drink_type.get()]
        cup = CUP_PROFILES[self.cup_type.get()]
        self.setup_note.configure(
            text=(
                f"Suggested start {drink.suggested_temp:.0f}°C · "
                f"cup k {cup.cooling_rate:.3f}/min"
            )
        )

    def _on_drink_changed(self, _event: object = None) -> None:
        drink = DRINK_PROFILES[self.drink_type.get()]
        self.initial_temp.set(f"{drink.suggested_temp:.0f}")
        self._update_drink_note()
        self.calculate(silent=True)

    def _on_cup_changed(self, _event: object = None) -> None:
        self._update_cup_note()
        self.calculate(silent=True)

    def get_current_settings(self) -> Dict[str, object]:
        return {
            "drink_type": self.drink_type.get(),
            "cup_type": self.cup_type.get(),
            "initial_temp": self.initial_temp.get(),
            "room_temp": self.room_temp.get(),
            "hot_limit": self.hot_limit.get(),
            "good_high": self.good_high.get(),
            "good_low": self.good_low.get(),
            "cold_limit": self.cold_limit.get(),
            "inspect_minute": self.inspect_minute.get(),
        }

    def load_saved_settings(self) -> bool:
        settings = load_settings()
        if not settings:
            return False

        drink_type = settings.get("drink_type")
        cup_type = settings.get("cup_type")
        if isinstance(drink_type, str) and drink_type in DRINK_PROFILES:
            self.drink_type.set(drink_type)
        if isinstance(cup_type, str) and cup_type in CUP_PROFILES:
            self.cup_type.set(cup_type)

        self._set_string_setting(settings, "initial_temp", self.initial_temp)
        self._set_string_setting(settings, "room_temp", self.room_temp)
        self._set_float_setting(settings, "hot_limit", self.hot_limit)
        self._set_float_setting(settings, "good_high", self.good_high)
        self._set_float_setting(settings, "good_low", self.good_low)
        self._set_float_setting(settings, "cold_limit", self.cold_limit)
        self._set_float_setting(settings, "inspect_minute", self.inspect_minute)
        return True

    def save_current_settings(self) -> None:
        if not self.calculate(silent=False):
            return

        try:
            save_settings(self.get_current_settings())
        except OSError as error:
            messagebox.showerror("Save failed", f"Could not save settings:\n{error}")
            return

        self.header_status.configure(
            text="Saved setup. It will be restored next time you open Sip Time Cafe.",
            fg=COLORS["green_dark"],
        )

    @staticmethod
    def _set_string_setting(
        settings: Dict[str, object],
        key: str,
        variable: tk.StringVar,
    ) -> None:
        value = settings.get(key)
        if isinstance(value, (str, int, float)):
            variable.set(str(value))

    @staticmethod
    def _set_float_setting(
        settings: Dict[str, object],
        key: str,
        variable: tk.DoubleVar,
    ) -> None:
        value = settings.get(key)
        try:
            variable.set(float(value))
        except (TypeError, ValueError):
            pass

    def reset_defaults(self) -> None:
        self.drink_type.set(DEFAULT_DRINK)
        self.cup_type.set(DEFAULT_CUP)
        self.initial_temp.set(f"{DRINK_PROFILES[DEFAULT_DRINK].suggested_temp:.0f}")
        self.room_temp.set(f"{DEFAULT_ROOM_TEMP:.0f}")
        self.hot_limit.set(DEFAULT_HOT_LIMIT)
        self.good_high.set(DEFAULT_GOOD_HIGH)
        self.good_low.set(DEFAULT_GOOD_LOW)
        self.cold_limit.set(DEFAULT_COLD_LIMIT)
        self.inspect_minute.set(0)
        self._update_drink_note()
        self._update_cup_note()
        self.calculate(silent=True)

    def calculate(self, silent: bool = False) -> bool:
        try:
            initial = float(self.initial_temp.get())
            room = float(self.room_temp.get())
            self._validate_inputs(initial, room)
            hot_limit = self.hot_limit.get()
            good_high = self.good_high.get()
            good_low = self.good_low.get()
            cold_limit = self.cold_limit.get()
            self._validate_thresholds(hot_limit, good_high, good_low, cold_limit)
        except ValueError as error:
            self.show_error(str(error), silent=silent)
            return False

        cup = CUP_PROFILES[self.cup_type.get()]
        self.model = CoolingModel(initial, room, cup)
        self.result = self.model.predict(hot_limit, good_high, good_low, cold_limit)

        self._refresh_drink_cards()
        self._update_cup_note()
        self.update_header()
        if self.loaded_saved_settings:
            self.header_status.configure(
                text=f"Loaded saved setup: {self.drink_type.get()} in a {self.cup_type.get()}",
                fg=COLORS["green_dark"],
            )
            self.loaded_saved_settings = False
        self.update_timeline()
        self.update_explanation()
        self.update_inspector()
        self.draw_graph()
        return True

    def _validate_inputs(self, initial: float, room: float) -> None:
        if initial <= room:
            raise ValueError("Starting temperature must be higher than room temperature.")
        if not 0 <= room <= 45:
            raise ValueError("Room temperature should be between 0 and 45°C.")
        if not 30 <= initial <= 100:
            raise ValueError("Starting drink temperature should be between 30 and 100°C.")

    def _validate_thresholds(
        self, hot_limit: float, good_high: float, good_low: float, cold_limit: float
    ) -> None:
        if not hot_limit > good_high > good_low > cold_limit:
            raise ValueError(
                "Temperature thresholds must follow: too hot > ready upper > "
                "ready lower > cool."
            )

    def show_error(self, message: str, silent: bool = False) -> None:
        self.header_status.configure(text=message, fg=COLORS["red"])
        self.inspector_label.configure(text=message)
        if not silent:
            messagebox.showwarning("Prediction unavailable", message)

    def update_header(self) -> None:
        if not self.result:
            return
        if self.result.drinkable_from is None:
            ready_window = "not reached"
        elif self.result.drinkable_until is None:
            ready_window = f"after {self.format_time(self.result.drinkable_from)}"
        else:
            ready_window = (
                f"{self.format_time(self.result.drinkable_from)} - "
                f"{self.format_time(self.result.drinkable_until)}"
            )
        best_time = self.format_time(self.result.peak_recommendation)
        safe_time = self.format_time(self.result.too_hot_until)
        cool_time = self.format_time(self.result.cold_from)

        self.header_status.configure(
            text=(
                f"{self.drink_type.get()} in a {self.cup_type.get()}   |   "
                f"Best sip: {best_time}   |   "
                f"Ready window: {ready_window}"
            ),
            fg=COLORS["muted"],
        )
        self.best_value_label.configure(text=best_time)
        self.best_meta_label.configure(
            text=(
                f"{self.drink_type.get()} starts at {float(self.initial_temp.get()):.0f}°C. "
                f"The comfortable range is {self.good_low.get():.0f}-{self.good_high.get():.0f}°C."
            )
        )
        self.metric_labels["safe"].configure(text=safe_time)
        self.metric_labels["ready"].configure(text=ready_window)
        self.metric_labels["cool"].configure(text=cool_time)

    def update_timeline(self) -> None:
        if not self.result or not self.model:
            return

        self.timeline.delete(*self.timeline.get_children())
        rows: List[Tuple[str, float]] = [("Now", 0.0)]
        for label, minute in [
            ("No longer too hot", self.result.too_hot_until),
            ("Drinkable starts", self.result.drinkable_from),
            ("Best sip", self.result.peak_recommendation),
            ("Drinkable ends", self.result.drinkable_until),
            ("Turns cool", self.result.cold_from),
        ]:
            if minute is not None:
                rows.append((label, minute))

        seen: set[int] = set()
        for label, minute in rows:
            rounded_minute = max(0, min(SIMULATION_MINUTES, int(round(minute))))
            if rounded_minute in seen:
                continue
            seen.add(rounded_minute)
            temperature = self.model.temperature_at(minute)
            self.timeline.insert(
                "",
                "end",
                values=(self.format_time(minute), f"{temperature:.1f}°C", label),
            )

    def update_explanation(self) -> None:
        if not self.model:
            return

        formula = (
            "Formula: T(t) = room + (initial - room) * e^(-k*t)\n\n"
            f"Drink: {self.drink_type.get()}\n"
            f"Cup: {self.cup_type.get()}\n"
            f"Starting temperature: {self.model.initial_temp:.1f}°C\n"
            f"Room temperature: {self.model.room_temp:.1f}°C\n"
            f"Cup cooling coefficient k: {self.model.cup.cooling_rate:.3f} per minute\n\n"
            "Drink type suggests the starting temperature. Cooling speed is based on "
            "the selected cup type."
        )
        self.explanation_text.configure(state="normal")
        self.explanation_text.delete("1.0", "end")
        self.explanation_text.insert("1.0", formula)
        self.explanation_text.configure(state="disabled")

    def update_inspector(self) -> None:
        if not self.model:
            return

        minute = round(self.inspect_minute.get())
        temperature = self.model.temperature_at(minute)
        state = self.model.classify(
            temperature,
            self.hot_limit.get(),
            self.good_high.get(),
            self.good_low.get(),
            self.cold_limit.get(),
        )
        self.inspector_label.configure(
            text=f"Minute {minute}: {temperature:.1f}°C, {state}"
        )

    def draw_graph(self) -> None:
        if not self.result or not self.model:
            return

        canvas = self.canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 600)
        height = max(canvas.winfo_height(), 260)
        pad_left, pad_right, pad_top, pad_bottom = 58, 24, 26, 45
        plot_w = width - pad_left - pad_right
        plot_h = height - pad_top - pad_bottom

        min_temp = min(
            self.cold_limit.get(),
            self.model.room_temp,
            min(point.temperature for point in self.result.points),
        ) - 5
        max_temp = max(
            self.hot_limit.get(),
            self.good_high.get(),
            max(point.temperature for point in self.result.points),
        ) + 5
        temp_range = max_temp - min_temp

        def x_for(minute: float) -> float:
            return pad_left + (minute / SIMULATION_MINUTES) * plot_w

        def y_for(temp: float) -> float:
            return pad_top + (max_temp - temp) / temp_range * plot_h

        good_top = y_for(self.good_high.get())
        good_bottom = y_for(self.good_low.get())
        canvas.create_rectangle(
            pad_left,
            good_top,
            width - pad_right,
            good_bottom,
            fill=COLORS["ready"],
            outline="",
        )
        canvas.create_text(
            width - pad_right - 8,
            (good_top + good_bottom) / 2,
            text="Ready to drink",
            anchor="e",
            fill=COLORS["green_dark"],
            font=(FONT_FAMILY, 10, "bold"),
        )

        for ratio in [0, 0.25, 0.5, 0.75, 1.0]:
            y = pad_top + ratio * plot_h
            temp = max_temp - ratio * temp_range
            canvas.create_line(pad_left, y, width - pad_right, y, fill="#e5edf3")
            canvas.create_text(
                pad_left - 10,
                y,
                text=f"{temp:.0f}",
                anchor="e",
                fill=COLORS["muted"],
                font=(FONT_FAMILY, 9),
            )

        for minute in [0, 30, 60, 90, 120, 150, 180]:
            x = x_for(minute)
            canvas.create_line(x, pad_top, x, height - pad_bottom, fill="#f3f7fa")
            canvas.create_text(
                x,
                height - pad_bottom + 16,
                text=str(minute),
                anchor="n",
                fill=COLORS["muted"],
                font=(FONT_FAMILY, 9),
            )

        canvas.create_line(
            pad_left,
            height - pad_bottom,
            width - pad_right,
            height - pad_bottom,
            fill=COLORS["slate"],
            width=2,
        )
        canvas.create_line(
            pad_left,
            pad_top,
            pad_left,
            height - pad_bottom,
            fill=COLORS["slate"],
            width=2,
        )
        canvas.create_text(
            width / 2,
            height - 8,
            text="Waiting time (minutes)",
            fill=COLORS["muted"],
            font=(FONT_FAMILY, 10),
        )
        canvas.create_text(
            18,
            height / 2,
            text="Temperature °C",
            angle=90,
            fill=COLORS["muted"],
            font=(FONT_FAMILY, 10),
        )

        curve: List[float] = []
        for point in self.result.points:
            curve.extend([x_for(point.minute), y_for(point.temperature)])
        if len(curve) >= 4:
            canvas.create_line(*curve, fill=COLORS["accent"], width=3, smooth=True)

        for milestone, label, color in [
            (self.result.too_hot_until, "Safe", COLORS["red"]),
            (self.result.peak_recommendation, "Best", COLORS["green_dark"]),
            (self.result.cold_from, "Cool", COLORS["blue"]),
        ]:
            if milestone is not None and 0 <= milestone <= SIMULATION_MINUTES:
                x = x_for(milestone)
                y = y_for(self.model.temperature_at(milestone))
                canvas.create_line(
                    x,
                    pad_top,
                    x,
                    height - pad_bottom,
                    fill=color,
                    dash=(4, 4),
                )
                canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline="")
                canvas.create_text(
                    x + 8,
                    y - 10,
                    text=label,
                    anchor="w",
                    fill=color,
                    font=(FONT_FAMILY, 9, "bold"),
                )

    def export_csv(self) -> None:
        if not self.result:
            messagebox.showinfo("No prediction", "Please run a prediction first.")
            return

        path = filedialog.asksaveasfilename(
            title="Export prediction data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="hot_drink_prediction.csv",
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["minute", "temperature_c", "state"])
            for point in self.result.points:
                writer.writerow([point.minute, f"{point.temperature:.2f}", point.state])

        messagebox.showinfo(
            "Export complete", f"Prediction data has been saved to:\n{path}"
        )

    @staticmethod
    def format_time(minute: Optional[float]) -> str:
        if minute is None:
            return "Not reached"
        if minute < 1:
            return "Now"
        rounded = int(round(minute))
        hours = rounded // 60
        mins = rounded % 60
        if hours and mins:
            return f"{hours}h {mins}m"
        if hours:
            return f"{hours}h"
        return f"{mins}m"
