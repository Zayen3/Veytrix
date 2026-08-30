import customtkinter as ctk
from tkinter import filedialog, Canvas
from pathlib import Path

from PIL import Image

from metadata import extract_metadata
from analyzer import analyze_privacy
from sanitizer import (
    sanitize_image,
    verify_sanitization,
    remove_gps_data,
    remove_device_data,
    remove_timestamp_data,
    remove_software_data,
)


# =========================================================
# VEYTRIX — IMAGE METADATA PRIVACY STUDIO
# =========================================================

BACKGROUND = "#0B0D12"
SURFACE = "#131722"
SURFACE_ALT = "#1B2130"
SURFACE_SELECTED = "#293145"

BORDER = "#30394B"
BORDER_SOFT = "#293245"

TEXT_PRIMARY = "#F3EFE7"
TEXT_SECONDARY = "#B8BECA"
TEXT_MUTED = "#737B8C"

SKY = "#8DCEF0"
LAVENDER = "#B7A0FF"
PEACH = "#FFB783"
MINT = "#91D6B5"
DANGER = "#F08089"

SERIF_FONT = "Georgia"
UI_FONT = "Segoe UI"
MONO_FONT = "Consolas"


# =========================================================
# APPLICATION
# =========================================================

class VeytrixApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Veytrix | Image Metadata Privacy")
        self.geometry("1280x860")
        self.minsize(980, 700)

        ctk.set_appearance_mode("dark")
        self.configure(fg_color=BACKGROUND)

        # Application state
        self.selected_file = None
        self.metadata = {}
        self.analysis = {}
        self.preview_image = None
        self.cleaned_output = None

        # Sanitization selections
        self.gps_var = ctk.BooleanVar(value=False)
        self.device_var = ctk.BooleanVar(value=False)
        self.time_var = ctk.BooleanVar(value=False)
        self.software_var = ctk.BooleanVar(value=False)
        self.full_clean_var = ctk.BooleanVar(value=False)

        self.option_tiles = {}

        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=BACKGROUND,
            corner_radius=0,
            scrollbar_button_color="#2A3140",
            scrollbar_button_hover_color=LAVENDER,
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Build UI
        self.create_hero()
        self.create_image_section()
        self.create_analysis_section()
        self.create_sanitize_section()

        self.update_sanitization_availability()

    # =====================================================
    # GENERAL HELPERS
    # =====================================================

    @staticmethod
    def clear_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def create_section(self):
        return ctk.CTkFrame(
            self.main_frame,
            fg_color=SURFACE,
            corner_radius=28,
            border_width=1,
            border_color=BORDER,
        )

    def create_section_header(self, parent, number, title, subtitle):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=44, pady=(32, 20))

        ctk.CTkLabel(
            header,
            text=f"{number}  /  VEYTRIX PRIVACY STUDIO",
            font=(MONO_FONT, 10, "bold"),
            text_color=LAVENDER,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text=title,
            font=(SERIF_FONT, 30, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(7, 5))

        ctk.CTkLabel(
            header,
            text=subtitle,
            font=(UI_FONT, 14),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=900,
        ).pack(anchor="w")

    @staticmethod
    def create_status_pill(parent, text, color):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=(MONO_FONT, 8, "bold"),
            text_color=color,
            fg_color="#222938",
            corner_radius=9,
            padx=10,
            pady=4,
        )

    # =====================================================
    # HERO
    # =====================================================

    def create_hero(self):
        hero = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )
        hero.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=42,
            pady=(28, 20),
        )

        hero.grid_columnconfigure(0, weight=5)
        hero.grid_columnconfigure(1, weight=5)

        # ---------------- LEFT SIDE ----------------

        left = ctk.CTkFrame(
            hero,
            fg_color="transparent",
        )
        left.grid(
            row=0,
            column=0,
            sticky="nw",
            padx=(8, 25),
            pady=(10, 10),
        )

        ctk.CTkLabel(
            left,
            text="VEYTRIX",
            font=("Arial", 60, "bold"),
            text_color=SKY,
        ).pack(anchor="w")

        tagline = ctk.CTkFrame(
            left,
            fg_color="transparent",
        )
        tagline.pack(anchor="w", pady=(3, 0))

        ctk.CTkFrame(
            tagline,
            width=3,
            height=20,
            fg_color=LAVENDER,
            corner_radius=2,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            tagline,
            text="IMAGE PRIVACY, WITHOUT THE PARANOIA.",
            font=(MONO_FONT, 10, "bold"),
            text_color="#A9A3C7",
        ).pack(side="left")

        ctk.CTkLabel(
            left,
            text="Your photos have\nanother layer.",
            font=(SERIF_FONT, 44, "bold"),
            text_color=TEXT_PRIMARY,
            justify="left",
        ).pack(anchor="w", pady=(18, 12))

        ctk.CTkLabel(
            left,
            text=(
                "Pixels are what you see. Metadata is what travels with your image.\n"
                "Veytrix reveals the information behind the picture—so you decide\n"
                "what stays."
            ),
            font=(UI_FONT, 15),
            text_color=TEXT_SECONDARY,
            justify="left",
        ).pack(anchor="w")

        journey = ctk.CTkFrame(
            left,
            fg_color="transparent",
        )
        journey.pack(anchor="w", pady=(28, 0))

        for text, color in (
            ("01  REVEAL", SKY),
            ("→", TEXT_MUTED),
            ("02  CHOOSE", LAVENDER),
            ("→", TEXT_MUTED),
            ("03  CLEAN", MINT),
        ):
            ctk.CTkLabel(
                journey,
                text=text,
                font=(MONO_FONT, 10, "bold"),
                text_color=color,
            ).pack(side="left", padx=(0, 14))

        # ---------------- RIGHT VISUAL ----------------

        visual_box = ctk.CTkFrame(
            hero,
            fg_color=SURFACE_ALT,
            corner_radius=28,
            border_width=1,
            border_color=BORDER,
            height=280,
        )
        visual_box.grid(
            row=0,
            column=1,
            sticky="nsew",
            pady=(0, 5),
        )
        visual_box.grid_propagate(False)

        canvas = Canvas(
            visual_box,
            width=620,
            height=340,
            bg=SURFACE_ALT,
            highlightthickness=0,
        )
        canvas.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        # Metadata lines
        items = (
            ("LOCATION", SKY, 100),
            ("DEVICE", LAVENDER, 140),
            ("TIME", MINT, 180),
            ("SOFTWARE", PEACH, 220),
        )

        for label, color, y in items:
            canvas.create_oval(
                55, y - 4, 63, y + 4,
                fill=color,
                outline="",
            )
            canvas.create_text(
                75,
                y,
                text=label,
                fill=color,
                anchor="w",
                font=(MONO_FONT, 8, "bold"),
            )
            canvas.create_line(
                145,
                y,
                250,
                y,
                fill=color,
                width=1,
                dash=(2, 3),
            )

        # Image frame
        x1, y1, x2, y2 = 265, 55, 485, 245

        canvas.create_rectangle(
            x1 - 7,
            y1 - 7,
            x2 + 7,
            y2 + 7,
            outline="#586277",
            width=1,
        )

        canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill="#182331",
            outline="#A6B2C6",
            width=1,
        )

        # Sky
        canvas.create_rectangle(
            x1 + 2,
            y1 + 2,
            x2 - 2,
            y1 + 70,
            fill="#697796",
            outline="",
        )

        # Mountains
        canvas.create_polygon(
            268, 180,
            325, 95,
            380, 160,
            430, 90,
            483, 180,
            fill="#263548",
            outline="",
        )

        canvas.create_polygon(
            268, 180,
            345, 120,
            400, 170,
            455, 105,
            483, 180,
            fill="#1A2738",
            outline="",
        )

        # Sun
        canvas.create_oval(
            350,
            75,
            425,
            150,
            fill="#E895A0",
            outline="",
        )

        # Lake
        canvas.create_rectangle(
            x1 + 2,
            180,
            x2 - 2,
            y2 - 2,
            fill="#142331",
            outline="",
        )

        # Foreground
        canvas.create_oval(
            280,
            215,
            335,
            247,
            fill="#0E151D",
            outline="",
        )
        canvas.create_oval(
            425,
            210,
            480,
            247,
            fill="#101720",
            outline="",
        )

        # Peeled corner
        canvas.create_polygon(
            435,
            58,
            480,
            58,
            480,
            103,
            fill=LAVENDER,
            outline="",
        )
        canvas.create_polygon(
            435,
            58,
            480,
            103,
            450,
            92,
            fill="#9A86DD",
            outline="",
        )

        # Right labels
        for label, color, y in (
            ("REVEAL", SKY, 105),
            ("INSPECT", LAVENDER, 145),
            ("CLEAN", MINT, 185),
        ):
            canvas.create_line(
                500,
                y,
                535,
                y,
                fill=color,
                width=1,
                dash=(2, 3),
            )
            canvas.create_text(
                540,
                y,
                text=label,
                fill=color,
                anchor="w",
                font=(MONO_FONT, 8, "bold"),
            )

        # Increased size as requested
        canvas.create_text(
            375,
            295,
            text="WHAT TRAVELS WITH THE IMAGE?",
            fill=TEXT_SECONDARY,
            font=(MONO_FONT, 10, "bold"),
        )

    # =====================================================
    # SECTION 01 — IMAGE SELECTION
    # =====================================================

    def create_image_section(self):
        self.image_section = self.create_section()
        self.image_section.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=38,
            pady=8,
        )

        self.create_section_header(
            self.image_section,
            "01",
            "Bring the image into focus.",
            "Choose an image. Veytrix will inspect the information travelling behind the pixels.",
        )

        content = ctk.CTkFrame(
            self.image_section,
            fg_color="transparent",
        )
        content.pack(
            fill="x",
            padx=44,
            pady=(0, 38),
        )

        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)

        # Preview card
        preview = ctk.CTkFrame(
            content,
            fg_color=SURFACE_ALT,
            corner_radius=24,
            height=245,
            border_width=1,
            border_color="#252E40",
        )
        preview.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 24),
        )
        preview.grid_propagate(False)

        self.preview_label = ctk.CTkLabel(
            preview,
            text="YOUR IMAGE\nWILL APPEAR HERE",
            font=(MONO_FONT, 10, "bold"),
            text_color=TEXT_MUTED,
            justify="center",
        )
        self.preview_label.place(
            relx=0.28,
            rely=0.5,
            anchor="center",
        )

        ctk.CTkFrame(
            preview,
            width=1,
            height=175,
            fg_color=BORDER,
        ).place(
            relx=0.54,
            rely=0.5,
            anchor="center",
        )

        info = ctk.CTkFrame(
            preview,
            fg_color="transparent",
        )
        info.place(
            relx=0.58,
            rely=0.5,
            anchor="w",
        )

        self.file_name_label = ctk.CTkLabel(
            info,
            text="No image selected",
            font=(UI_FONT, 16, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        self.file_name_label.pack(anchor="w")

        self.file_details_label = ctk.CTkLabel(
            info,
            text="Choose a JPG or JPEG image to begin.",
            font=(UI_FONT, 12),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=250,
        )
        self.file_details_label.pack(
            anchor="w",
            pady=(8, 12),
        )

        ctk.CTkLabel(
            info,
            text="✓  Original stays untouched",
            font=(MONO_FONT, 9, "bold"),
            text_color=MINT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text="•  Clean copy created separately",
            font=(UI_FONT, 11),
            text_color=TEXT_SECONDARY,
        ).pack(
            anchor="w",
            pady=(7, 0),
        )

        # Image selection area
        right = ctk.CTkFrame(
            content,
            fg_color="transparent",
        )
        right.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        ctk.CTkLabel(
            right,
            text="START WITH THE ORIGINAL.",
            font=(MONO_FONT, 10, "bold"),
            text_color=SKY,
        ).pack(anchor="w")

        dropzone = ctk.CTkFrame(
            right,
            fg_color=SURFACE_ALT,
            corner_radius=22,
            border_width=1,
            border_color="#586277",
        )
        dropzone.pack(
            fill="both",
            expand=True,
            pady=(12, 0),
        )

        ctk.CTkLabel(
            dropzone,
            text="▱  +",
            font=(UI_FONT, 34, "bold"),
            text_color=LAVENDER,
        ).pack(pady=(24, 7))

        ctk.CTkButton(
            dropzone,
            text="Choose an image  →",
            command=self.select_image,
            height=58,
            width=280,
            corner_radius=17,
            font=(UI_FONT, 16, "bold"),
            fg_color=SKY,
            hover_color="#6AB6DB",
            text_color="#101722",
        ).pack(pady=(0, 9))

        ctk.CTkLabel(
            dropzone,
            text="JPG, JPEG SUPPORTED",
            font=(MONO_FONT, 9),
            text_color=TEXT_MUTED,
        ).pack(pady=(0, 20))

    # =====================================================
    # SECTION 02 — ANALYSIS
    # =====================================================

    def create_analysis_section(self):
        self.analysis_section = self.create_section()
        self.analysis_section.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=38,
            pady=12,
        )

        self.create_section_header(
            self.analysis_section,
            "02",
            "Let's look beneath the pixels.",
            "The findings below reflect metadata actually detected in your selected image.",
        )

        self.analysis_content = ctk.CTkFrame(
            self.analysis_section,
            fg_color="transparent",
        )
        self.analysis_content.pack(
            fill="both",
            expand=True,
            padx=44,
            pady=(0, 38),
        )

        self.show_analysis_placeholder()

    def show_analysis_placeholder(self):
        self.clear_frame(self.analysis_content)

        placeholder = ctk.CTkFrame(
            self.analysis_content,
            fg_color=SURFACE_ALT,
            corner_radius=22,
        )
        placeholder.pack(fill="x")

        ctk.CTkLabel(
            placeholder,
            text="Nothing to inspect yet.",
            font=(SERIF_FONT, 23, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(
            anchor="w",
            padx=28,
            pady=(25, 5),
        )

        ctk.CTkLabel(
            placeholder,
            text=(
                "Choose an image above and Veytrix will check what "
                "information is travelling with it."
            ),
            font=(UI_FONT, 13),
            text_color=TEXT_SECONDARY,
            wraplength=700,
            justify="left",
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 25),
        )

    def get_detected_categories(self):
        return {
            "location": bool(
                self.analysis.get("gps_section_detected")
                or self.analysis.get("gps_coordinates")
            ),
            "device": bool(
                self.metadata.get("make")
                or self.metadata.get("model")
            ),
            "time": bool(
                self.analysis.get("timestamp_detected")
            ),
            "software": bool(
                self.metadata.get("software")
            ),
        }

    def create_analysis_panel(
        self,
        parent,
        title,
        found_text,
        clear_text,
        detected,
        accent,
        value,
        relevance,
    ):
        panel = ctk.CTkFrame(
            parent,
            fg_color=SURFACE_ALT,
            corner_radius=20,
            border_width=1,
            border_color=accent if detected else BORDER_SOFT,
        )

        header = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )
        header.pack(
            fill="x",
            padx=22,
            pady=(18, 8),
        )

        ctk.CTkLabel(
            header,
            text=title,
            font=(UI_FONT, 16, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        self.create_status_pill(
            header,
            "FOUND" if detected else "NOT DETECTED",
            accent if detected else MINT,
        ).pack(side="right")

        if detected and value:
            ctk.CTkLabel(
                panel,
                text=value,
                font=(MONO_FONT, 9),
                text_color=accent,
                justify="left",
                wraplength=360,
            ).pack(
                anchor="w",
                padx=22,
                pady=(2, 8),
            )

        ctk.CTkLabel(
            panel,
            text=found_text if detected else clear_text,
            font=(UI_FONT, 12),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=380,
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 6 if detected else 20),
        )

        if detected:
            ctk.CTkLabel(
                panel,
                text=relevance,
                font=(UI_FONT, 10),
                text_color=TEXT_MUTED,
                justify="left",
                wraplength=380,
            ).pack(
                anchor="w",
                padx=22,
                pady=(0, 18),
            )

        return panel

    def display_analysis(self):
        self.clear_frame(self.analysis_content)

        detected = self.get_detected_categories()
        detected_count = sum(detected.values())

        overall_risk = self.analysis.get(
            "overall_risk",
            "LOW",
        )

        risk_color = {
            "HIGH": DANGER,
            "MEDIUM": PEACH,
            "LOW": MINT,
        }.get(
            overall_risk,
            TEXT_SECONDARY,
        )

        # Summary
        summary = ctk.CTkFrame(
            self.analysis_content,
            fg_color=SURFACE_ALT,
            corner_radius=22,
            border_width=1,
            border_color=BORDER_SOFT,
        )
        summary.pack(
            fill="x",
            pady=(0, 18),
        )

        ctk.CTkLabel(
            summary,
            text="OVERALL PRIVACY SIGNAL",
            font=(MONO_FONT, 9, "bold"),
            text_color=TEXT_MUTED,
        ).pack(
            anchor="w",
            padx=28,
            pady=(18, 2),
        )

        ctk.CTkLabel(
            summary,
            text=overall_risk,
            font=(SERIF_FONT, 30, "bold"),
            text_color=risk_color,
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 3),
        )

        summary_text = (
            f"{detected_count} privacy-related metadata layer(s) were detected."
            if detected_count
            else "No common privacy-related metadata categories were detected."
        )

        ctk.CTkLabel(
            summary,
            text=summary_text,
            font=(UI_FONT, 13),
            text_color=TEXT_SECONDARY,
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 18),
        )

        # Values for analysis cards
        gps = self.analysis.get("gps_coordinates")

        if gps:
            location_value = (
                f"{gps.get('latitude', 0):.6f}°, "
                f"{gps.get('longitude', 0):.6f}°"
            )
        elif self.analysis.get("gps_section_detected"):
            location_value = "GPS metadata present"
        else:
            location_value = ""

        make = self.metadata.get("make")
        model = self.metadata.get("model")

        device_value = " • ".join(
            str(value)
            for value in (make, model)
            if value
        )

        time_value = (
            self.metadata.get("original_date")
            or self.metadata.get("capture_date")
            or self.metadata.get("digitized_date")
            or ""
        )

        software_value = (
            str(self.metadata.get("software"))
            if self.metadata.get("software")
            else ""
        )

        signals = (
            (
                "Location",
                "GPS or location metadata is embedded in this image.",
                "No GPS location data was detected.",
                detected["location"],
                SKY,
                location_value,
                "Privacy relevance: high when precise location could reveal where an image was taken.",
            ),
            (
                "Device identity",
                "Camera manufacturer or model information is embedded.",
                "No common camera or device identity was detected.",
                detected["device"],
                LAVENDER,
                device_value,
                "Privacy relevance: contextual. Device details can sometimes help link images to a device.",
            ),
            (
                "Time trace",
                "Date or timestamp information is embedded in this image.",
                "No common timestamp metadata was detected.",
                detected["time"],
                MINT,
                str(time_value),
                "Privacy relevance: contextual. Timing information can reveal when an image was taken or processed.",
            ),
            (
                "Software trace",
                "Software or processing information is embedded.",
                "No software trace was detected.",
                detected["software"],
                PEACH,
                software_value,
                "Privacy relevance: generally informational and not automatically a serious privacy risk.",
            ),
        )

        grid = ctk.CTkFrame(
            self.analysis_content,
            fg_color="transparent",
        )
        grid.pack(fill="x")

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        for index, signal in enumerate(signals):
            panel = self.create_analysis_panel(
                grid,
                *signal,
            )
            panel.grid(
                row=index // 2,
                column=index % 2,
                sticky="nsew",
                padx=5,
                pady=5,
            )

    # =====================================================
    # SECTION 03 — SANITIZATION
    # =====================================================

    def create_sanitize_section(self):
        self.sanitize_section = self.create_section()
        self.sanitize_section.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=38,
            pady=(10, 38),
        )

        self.create_section_header(
            self.sanitize_section,
            "03",
            "You're in control. Remove what you don't want.",
            (
                "Choose the metadata layers you want to remove. "
                "Veytrix creates a separate copy and never overwrites your original."
            ),
        )

        content = ctk.CTkFrame(
            self.sanitize_section,
            fg_color="transparent",
        )
        content.pack(
            fill="x",
            padx=44,
            pady=(0, 38),
        )

        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)

        # Options
        options = ctk.CTkFrame(
            content,
            fg_color="transparent",
        )
        options.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 24),
        )

        options.grid_columnconfigure(0, weight=1)
        options.grid_columnconfigure(1, weight=1)

        option_data = (
            (
                "location",
                "Location",
                "Remove embedded GPS coordinates.",
                self.gps_var,
                SKY,
                0,
                0,
                1,
                False,
            ),
            (
                "device",
                "Device",
                "Remove camera manufacturer and model.",
                self.device_var,
                LAVENDER,
                0,
                1,
                1,
                False,
            ),
            (
                "time",
                "Time",
                "Remove common EXIF timestamps.",
                self.time_var,
                MINT,
                1,
                0,
                1,
                False,
            ),
            (
                "software",
                "Software",
                "Remove application information.",
                self.software_var,
                PEACH,
                1,
                1,
                1,
                False,
            ),
            (
                "full",
                "Full EXIF Clean",
                "Remove all available EXIF metadata in one pass.",
                self.full_clean_var,
                LAVENDER,
                2,
                0,
                2,
                True,
            ),
        )

        for data in option_data:
            self.create_option_tile(
                options,
                *data,
            )

        self.create_action_card(content)

    def create_option_tile(
        self,
        parent,
        key,
        title,
        description,
        variable,
        accent,
        row,
        column,
        columnspan=1,
        full_clean=False,
    ):
        tile = ctk.CTkFrame(
            parent,
            fg_color=SURFACE_ALT,
            corner_radius=18,
            border_width=1,
            border_color=BORDER,
        )
        tile.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            sticky="ew",
            padx=5,
            pady=6,
        )

        checkbox = ctk.CTkCheckBox(
            tile,
            text="",
            variable=variable,
            command=self.on_option_changed,
            width=30,
            checkbox_width=25,
            checkbox_height=25,
            corner_radius=7,
            border_width=2,
            border_color="#687286",
            fg_color=accent,
            hover_color=accent,
        )
        checkbox.pack(
            side="left",
            padx=(20, 13),
            pady=19,
        )

        text_holder = ctk.CTkFrame(
            tile,
            fg_color="transparent",
        )
        text_holder.pack(
            side="left",
            fill="x",
            expand=True,
            pady=14,
        )

        ctk.CTkLabel(
            text_holder,
            text=title,
            font=(UI_FONT, 15, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_holder,
            text=description,
            font=(UI_FONT, 11),
            text_color=TEXT_SECONDARY,
            wraplength=260,
            justify="left",
        ).pack(
            anchor="w",
            pady=(3, 0),
        )

        status = self.create_status_pill(
            tile,
            "AVAILABLE" if full_clean else "NOT DETECTED",
            MINT if full_clean else TEXT_MUTED,
        )
        status.pack(
            side="right",
            padx=18,
        )

        self.option_tiles[key] = {
            "frame": tile,
            "checkbox": checkbox,
            "status": status,
            "variable": variable,
            "accent": accent,
            "full_clean": full_clean,
        }

    # =====================================================
    # ACTION CARD
    # =====================================================

    def create_action_card(self, parent):
        self.action_card = ctk.CTkFrame(
            parent,
            fg_color=SURFACE_ALT,
            corner_radius=24,
            border_width=1,
            border_color="#293247",
        )
        self.action_card.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.action_state_label = ctk.CTkLabel(
            self.action_card,
            text="READY WHEN YOU ARE",
            font=(MONO_FONT, 10, "bold"),
            text_color=MINT,
        )
        self.action_state_label.pack(
            anchor="w",
            padx=30,
            pady=(28, 12),
        )

        ctk.CTkLabel(
            self.action_card,
            text="The original\nnever changes.",
            font=(SERIF_FONT, 27, "bold"),
            text_color=TEXT_PRIMARY,
            justify="left",
        ).pack(
            anchor="w",
            padx=30,
        )

        ctk.CTkLabel(
            self.action_card,
            text=(
                "Remove only what matters to you, or choose a broader "
                "reset when you want one."
            ),
            font=(UI_FONT, 13),
            text_color=TEXT_SECONDARY,
            wraplength=310,
            justify="left",
        ).pack(
            anchor="w",
            padx=30,
            pady=(10, 18),
        )

        self.sanitize_button = ctk.CTkButton(
            self.action_card,
            text="Create clean copy  →",
            command=self.sanitize_selected_image,
            height=56,
            corner_radius=17,
            fg_color=LAVENDER,
            hover_color="#9984DF",
            text_color="#181523",
            font=(UI_FONT, 15, "bold"),
        )
        self.sanitize_button.pack(
            anchor="w",
            padx=30,
            pady=(0, 16),
        )

        # -------------------------------------------------
        # RESULT AREA
        #
        # IMPORTANT:
        # wraplength=0 disables automatic word wrapping.
        # The success message below uses explicit line breaks.
        # This prevents "created" becoming "cr / eated" and
        # prevents ".jpeg" being pushed to another line.
        # -------------------------------------------------

        self.result_message = ctk.CTkLabel(
            self.action_card,
            text="Choose an image and select what you want to remove.",
            font=(UI_FONT, 11),
            text_color=TEXT_MUTED,
            justify="left",
            anchor="w",
            wraplength=0,
        )
        self.result_message.pack(
            anchor="w",
            fill="x",
            padx=30,
            pady=(0, 9),
        )

        self.result_removed = ctk.CTkLabel(
            self.action_card,
            text="",
            font=(MONO_FONT, 9),
            text_color=MINT,
            justify="left",
            anchor="w",
            wraplength=0,
        )
        self.result_removed.pack(
            anchor="w",
            fill="x",
            padx=30,
            pady=(0, 7),
        )

        self.result_output = ctk.CTkLabel(
            self.action_card,
            text="",
            font=(MONO_FONT, 9),
            text_color=MINT,
            justify="left",
            anchor="w",
            wraplength=0,
        )
        self.result_output.pack(
            anchor="w",
            fill="x",
            padx=30,
            pady=(0, 10),
        )

        self.result_original = ctk.CTkLabel(
            self.action_card,
            text="",
            font=(MONO_FONT, 9, "bold"),
            text_color=MINT,
            justify="left",
            anchor="w",
            wraplength=0,
        )
        self.result_original.pack(
            anchor="w",
            fill="x",
            padx=30,
            pady=(0, 26),
        )

    # =====================================================
    # OPTION AVAILABILITY AND STATE
    # =====================================================

    def update_sanitization_availability(self):
        detected = self.get_detected_categories()
        image_selected = self.selected_file is not None

        for key, item in self.option_tiles.items():
            if item["full_clean"]:
                available = image_selected
            else:
                available = (
                    image_selected
                    and detected.get(key, False)
                )

            if not available:
                item["variable"].set(False)

            item["checkbox"].configure(
                state="normal" if available else "disabled"
            )

            if item["full_clean"]:
                text = (
                    "AVAILABLE"
                    if available
                    else "SELECT IMAGE"
                )
                color = (
                    MINT
                    if available
                    else TEXT_MUTED
                )
            else:
                text = (
                    "DETECTED"
                    if available
                    else "NOT DETECTED"
                )
                color = (
                    item["accent"]
                    if available
                    else TEXT_MUTED
                )

            item["status"].configure(
                text=text,
                text_color=color,
            )

        self.update_option_visuals()

    def on_option_changed(self):
        # Full clean is exclusive
        if self.full_clean_var.get():
            for variable in (
                self.gps_var,
                self.device_var,
                self.time_var,
                self.software_var,
            ):
                variable.set(False)

        # Individual options disable full clean
        elif any(
            variable.get()
            for variable in (
                self.gps_var,
                self.device_var,
                self.time_var,
                self.software_var,
            )
        ):
            self.full_clean_var.set(False)

        self.cleaned_output = None
        self.update_option_visuals()

        self.set_result_state(
            "READY TO CREATE A CLEAN COPY",
            "Your original image will remain unchanged.",
            MINT,
        )

        self.sanitize_button.configure(
            text="Create clean copy  →"
        )

    def update_option_visuals(self):
        for item in self.option_tiles.values():
            selected = item["variable"].get()

            item["frame"].configure(
                fg_color=(
                    SURFACE_SELECTED
                    if selected
                    else SURFACE_ALT
                ),
                border_color=(
                    item["accent"]
                    if selected
                    else BORDER
                ),
            )

    def reset_options(self):
        for variable in (
            self.gps_var,
            self.device_var,
            self.time_var,
            self.software_var,
            self.full_clean_var,
        ):
            variable.set(False)

        self.cleaned_output = None
        self.update_sanitization_availability()

    # =====================================================
    # FILE SELECTION
    # =====================================================

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Choose an image to inspect",
            filetypes=[
                ("JPEG Images", "*.jpg *.jpeg"),
                ("All Files", "*.*"),
            ],
        )

        if not file_path:
            return

        path = Path(file_path)

        if path.suffix.lower() not in {".jpg", ".jpeg"}:
            self.file_name_label.configure(
                text="Unsupported file",
                text_color=PEACH,
            )
            self.file_details_label.configure(
                text="Please select a JPG or JPEG image.",
                text_color=PEACH,
            )
            return

        try:
            self.selected_file = path

            self.metadata = extract_metadata(path)
            self.analysis = analyze_privacy(
                self.metadata
            )

            self.update_file_information()
            self.update_preview()
            self.display_analysis()
            self.reset_options()

            self.set_result_state(
                "INSPECTION COMPLETE",
                (
                    "Review the detected categories and choose "
                    "what you want to remove."
                ),
                MINT,
            )

        except Exception as error:
            self.selected_file = None
            self.metadata = {}
            self.analysis = {}

            self.file_name_label.configure(
                text="Could not analyze this image",
                text_color=DANGER,
            )

            self.file_details_label.configure(
                text=str(error),
                text_color=DANGER,
            )

            self.preview_label.configure(
                image=None,
                text="PREVIEW\nUNAVAILABLE",
                text_color=PEACH,
            )

            self.show_analysis_placeholder()
            self.update_sanitization_availability()

    def update_file_information(self):
        self.file_name_label.configure(
            text=self.selected_file.name,
            text_color=TEXT_PRIMARY,
        )

        image_format = self.metadata.get(
            "format",
            "JPEG",
        )
        width = self.metadata.get("width")
        height = self.metadata.get("height")
        count = self.metadata.get(
            "metadata_count",
            0,
        )

        if width and height:
            detail = (
                f"{image_format}  •  "
                f"{width} × {height} px  •  "
                f"{count} EXIF field(s)"
            )
        else:
            detail = "Image selected successfully."

        self.file_details_label.configure(
            text=detail,
            text_color=TEXT_SECONDARY,
        )

    def update_preview(self):
        try:
            with Image.open(
                self.selected_file
            ) as image:

                preview = image.convert("RGB")
                preview.thumbnail((230, 190))

                self.preview_image = ctk.CTkImage(
                    light_image=preview,
                    dark_image=preview,
                    size=preview.size,
                )

            self.preview_label.configure(
                image=self.preview_image,
                text="",
            )

        except Exception:
            self.preview_label.configure(
                image=None,
                text="PREVIEW\nUNAVAILABLE",
                text_color=PEACH,
            )

    # =====================================================
    # RESULT FORMATTING
    # =====================================================

    @staticmethod
    def get_display_filename(filename, max_length=42):
        """
        Keep the extension on the same line.

        Only shorten genuinely long filenames. The extension is
        always preserved, so '.jpeg' will never be displayed alone.
        """

        if len(filename) <= max_length:
            return filename

        path = Path(filename)
        suffix = path.suffix
        stem = path.stem

        available = max_length - len(suffix) - 1

        if available < 10:
            return filename

        return f"{stem[:available]}…{suffix}"

    # =====================================================
    # SANITIZATION
    # =====================================================

    def sanitize_selected_image(self):
        if not self.selected_file:
            self.set_result_state(
                "NO IMAGE SELECTED",
                "Choose an image before creating a clean copy.",
                PEACH,
            )
            return

        try:
            selected_options = []

            # ---------------- FULL CLEAN ----------------

            if self.full_clean_var.get():
                output_path = sanitize_image(
                    self.selected_file
                )

                selected_options = [
                    "All EXIF metadata"
                ]

                verified = verify_sanitization(
                    output_path
                )

                status = (
                    "CLEAN COPY VERIFIED"
                    if verified
                    else "CLEAN COPY CREATED"
                )

                detail = (
                    "The output was checked and no EXIF metadata "
                    "remains according to Veytrix verification."
                    if verified
                    else (
                        "The copy was created, but EXIF verification "
                        "could not confirm complete removal."
                    )
                )

            # ------------- SELECTIVE CLEANING -------------

            else:
                working_path = self.selected_file

                operations = (
                    (
                        self.gps_var,
                        remove_gps_data,
                        "Location",
                    ),
                    (
                        self.device_var,
                        remove_device_data,
                        "Device",
                    ),
                    (
                        self.time_var,
                        remove_timestamp_data,
                        "Time",
                    ),
                    (
                        self.software_var,
                        remove_software_data,
                        "Software",
                    ),
                )

                for variable, operation, name in operations:
                    if variable.get():
                        working_path = operation(
                            working_path
                        )
                        selected_options.append(
                            name
                        )

                if not selected_options:
                    self.set_result_state(
                        "NOTHING SELECTED",
                        (
                            "Choose at least one detected metadata "
                            "category or select Full EXIF Clean."
                        ),
                        PEACH,
                    )
                    return

                output_path = working_path
                status = "CLEAN COPY CREATED"

                detail = (
                    "Your selected metadata categories were removed "
                    "from a newly created copy."
                )

            # ---------------- SUCCESS STATE ----------------

            self.cleaned_output = Path(
                output_path
            )

            # Reset the general state first
            self.set_result_state(
                status,
                "",
                MINT,
            )

            # Explicit line break prevents awkward automatic wrapping
            if self.full_clean_var.get():
                success_message = (
                    "A newly created copy was cleaned.\n"
                    "Your original image remains untouched."
                )
            else:
                success_message = (
                    "Your selected metadata categories were removed from\n"
                    "a newly created copy."
                )

            removed = "  •  ".join(
                selected_options
            )

            display_name = self.get_display_filename(
                self.cleaned_output.name
            )

            self.result_message.configure(
                text=success_message,
                text_color=MINT,
            )

            self.result_removed.configure(
                text=f"REMOVED  •  {removed}"
            )

            self.result_output.configure(
                text=f"OUTPUT  •  {display_name}"
            )

            self.result_original.configure(
                text="✓  YOUR ORIGINAL IMAGE REMAINS UNCHANGED."
            )

            self.sanitize_button.configure(
                text="Create another clean copy  →"
            )

        except Exception as error:
            self.set_result_state(
                "SANITIZATION INTERRUPTED",
                str(error),
                DANGER,
            )

    # =====================================================
    # RESULT STATE
    # =====================================================

    def set_result_state(
        self,
        title,
        message,
        color,
    ):
        self.action_state_label.configure(
            text=title,
            text_color=color,
        )

        self.result_message.configure(
            text=message,
            text_color=color,
        )

        self.result_removed.configure(
            text=""
        )

        self.result_output.configure(
            text=""
        )

        self.result_original.configure(
            text=""
        )


# =========================================================
# APPLICATION STARTUP
# =========================================================

def launch_app():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = VeytrixApp()
    app.mainloop()


if __name__ == "__main__":
    launch_app()