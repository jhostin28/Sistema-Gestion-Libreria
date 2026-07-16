import customtkinter as ctk

from src.data.database_mgr import create_tables
from src.gui.login import LoginWindow


def main() -> None:
    create_tables()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = LoginWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
