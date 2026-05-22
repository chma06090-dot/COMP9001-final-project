"""Entry point for Sip Time Cafe."""

from app_ui import TemperaturePredictorApp


def main() -> None:
    import tkinter as tk

    root = tk.Tk()
    TemperaturePredictorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
