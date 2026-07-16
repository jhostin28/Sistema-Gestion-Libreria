from tkinter import ttk


BG = "#111827"
PANEL = "#1f2937"
PANEL_ALT = "#273449"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
ACCENT = "#2563eb"
SUCCESS = "#15803d"
DANGER = "#b91c1c"
WARNING = "#b45309"


def configure_treeview_style() -> None:
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "Library.Treeview",
        background=PANEL,
        foreground=TEXT,
        fieldbackground=PANEL,
        rowheight=30,
        borderwidth=0,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Library.Treeview.Heading",
        background=PANEL_ALT,
        foreground=TEXT,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "Library.Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "white")],
    )
    style.map(
        "Library.Treeview.Heading",
        background=[("active", "#334155")],
    )
