from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import requests
import api


class Dashboard(Frame):
    def submit(self):
        try:
            self.set_loading(True)
            city = self.user_input.get().strip()

            if not city:
                messagebox.showwarning("Warning", "Location field cannot be empty.")
                return
            validity = api.is_valid(city)
            if validity == "network_error":
                messagebox.showerror(
                    "Error", "Network error. Please check your internet connection."
                )
                return
            elif not validity:
                messagebox.showerror(
                    "Error", "Invalid location. Please check your entry."
                )
                return

            result = api.get_weather_data(city)

            # Check if we got valid data
            if result is None:
                messagebox.showerror("Error", "Failed to fetch weather data.")
                return

            current_weather, hourly_forecast, daily_forecast = result

            if (
                not current_weather
                or not isinstance(current_weather, dict)
                or "location" not in current_weather
            ):
                messagebox.showerror("Error", "Failed to fetch weather data.")
            else:
                self.controller.show_frame("Weather")
                weather_frame = self.controller.frames["Weather"]
                weather_frame.update_weather("daily")

        except Exception as e:
            messagebox.showerror("Error", f"{str(e)}")
            return
        finally:
            self.set_loading(False)

    def auto_locate_and_submit(self):
        try:
            self.set_loading(True)
            city = self.detect_city_from_ip()
            if not city:
                messagebox.showerror(
                    "Error", "Could not detect location automatically."
                )
                return
            self.user_input.delete(0, END)
            self.user_input.insert(0, city)
            self.submit()
        except Exception as e:
            messagebox.showerror("Error", f"Auto locate failed: {str(e)}")
        finally:
            self.set_loading(False)

    def detect_city_from_ip(self):
        try:
            r = requests.get("https://ipinfo.io/json", timeout=5)
            if r.ok:
                j = r.json()
                city = (j.get("city") or "").strip()
                if city:
                    return city
                region = (j.get("region") or "").strip()
                if region:
                    return region
        except Exception:
            pass

        try:
            r = requests.get("https://ipapi.co/json/", timeout=5)
            if r.ok:
                j = r.json()
                city = (j.get("city") or "").strip()
                if city:
                    return city
                region = (j.get("region") or "").strip()
                if region:
                    return region
        except Exception:
            pass

        return ""

    def set_loading(self, is_loading):
        if is_loading:
            self.status_label.config(text="Loading...", fg="yellow")
            self.update_idletasks()
            self.submit_btn.config(state="disabled")
            self.auto_locate_btn.config(state="disabled")
        else:
            self.status_label.config(text="")
            self.submit_btn.config(state="normal")
            self.auto_locate_btn.config(state="normal")

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0C101C")
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)

        heading = Label(
            self,
            text="Know Your Weather",
            font=("Segoe UI", 24, "bold"),
            bg="#0C101C",
            fg="#607D8B",
        )
        heading.grid(row=0, column=0, sticky="ew")

        entry_frame = Frame(self, bg="#607D8B")
        entry_frame.grid(row=1, column=0, sticky="nsew")

        sub_heading = Label(
            entry_frame,
            text="Enter your location.",
            font=("Segoe UI", 14, "bold"),
            bg="#607D8B",
            fg="#0C101C",
        )
        sub_heading.pack(pady=(50, 0))

        self.user_input = ttk.Entry(entry_frame, width=30)
        self.user_input.pack(
            pady=20,
        )

        self.user_input.focus_set()  # Set focus when dashboard loads
        self.user_input.bind("<Return>", lambda event: self.submit())

        self.submit_btn = Button(
            entry_frame,
            text="Get Weather",
            font=("Segoe UI", 12, "bold"),
            bg="#000814",
            fg="#607D8B",
            bd=0,
            pady=5,
            command=self.submit,
        )
        self.submit_btn.pack()

        Label(
            entry_frame,
            text="Or",
            font=("Segoe UI", 14, "bold"),
            bg="#607D8B",
            fg="#0C101C",
        ).pack()

        self.auto_locate_btn = Button(
            entry_frame,
            text="Auto Locate",
            font=("Segoe UI", 12, "bold"),
            bg="#000814",
            fg="#607D8B",
            bd=0,
            pady=5,
            command=self.auto_locate_and_submit,
        )
        self.auto_locate_btn.pack()

        self.status_label = Label(
            entry_frame,
            text="",
            font=("Segoe UI", 12, "italic"),
            bg="#607D8B",
            fg="yellow",
        )
        self.status_label.pack(pady=10)
