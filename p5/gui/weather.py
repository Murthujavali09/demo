from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import Label
from datetime import datetime
from PIL import Image, ImageTk
import os
import api


class Weather(Frame):

    def update_weather(self, to_show):
        try:
            self.animation_frames.clear()
            self.animated_widgets.clear()

            current_weather, hourly_forecast, daily_forecast = api.get_data()
            if not current_weather or "location" not in current_weather:
                return

            self.city_label.config(text=current_weather["location"])

            temp_val = current_weather["temperature_c"]
            wind_val = current_weather["windspeed_kph"]
            vis_val = current_weather["visibility_km"]
            is_metric = self.unit_var.get() == "Metric"

            if is_metric:
                temp_disp = f"{temp_val}°C"
                wind_disp = f"{wind_val} km/h"
                vis_disp = f"{vis_val:.1f} km"
            else:
                temp_disp = f"{self.c_to_f(temp_val)}°F"
                wind_disp = f"{self.kmh_to_mph(wind_val)} mph"
                vis_disp = f"{vis_val * 0.621371:.1f} mi"

            self.curr_temp.config(text=f"{temp_disp}")

            code = current_weather["weather_code"]
            icon_path = api.get_icon(code)
            if os.path.exists(icon_path):
                img = Image.open(icon_path).resize((64, 64))
                self.weather_icon = ImageTk.PhotoImage(img)
                self.curr_icon.config(image=self.weather_icon)
            else:
                print(f"Icon not found for code {code}: {icon_path}")

            self.description.config(text=current_weather["condition"])
            self.visibility.config(text=f"Visibility: {vis_disp} ")
            self.humidity.config(
                text=f"Humidity: {current_weather['humidity_percent']}%"
            )
            self.feels_like.config(text=f"Feels like: {temp_disp}")
            self.wind_speed.config(text=f"Wind: {wind_disp}")
            self.sunrise.config(text=f"Sunrise: {current_weather['sunrise']}")
            self.sunset.config(text=f"Sunset: {current_weather['sunset']}")

            for widget in self.frame2.winfo_children():
                widget.destroy()  # Clear old forecast

            options_frame = Frame(self.frame2, bg="#1F2C3C")
            options_frame.grid(row=0, column=0, columnspan=5,
                               sticky="ew", pady=(7, 0))
            options_frame.grid_rowconfigure(0, weight=1)

            daily = Button(
                options_frame,
                text="Weekly",
                font=("Segoe UI", 14),
                bd=0,
                bg="#1F2C3C",
                fg="grey",
                command=self.show_daily,
            )
            daily.grid(row=0, column=0, sticky="w", padx=20)

            hourly = Button(
                options_frame,
                text="Hourly",
                font=("Segoe UI", 14),
                bd=0,
                bg="#1F2C3C",
                fg="grey",
                command=self.show_hourly,
            )
            hourly.grid(row=0, column=1, sticky="w", padx=20)

            if to_show == "daily":
                daily.config(fg="white")
                headers = ["Day", "Weather",
                           "Condition", "Min Temp", "Max Temp"]
                for col, txt in enumerate(headers):
                    Label(
                        self.frame2,
                        text=txt,
                        font=("Segoe UI", 11, "bold"),
                        bg="#1F2C3C",
                        fg="white",
                        anchor="w",
                    ).grid(row=1, column=col, sticky="w", padx=40)
                for i, day in enumerate(daily_forecast):
                    code = day.get("weather_code", 0)
                    icon_path = api.get_icon(code)
                    min_temp = day["min_temp_c"]
                    max_temp = day["max_temp_c"]
                    min_temp_disp = (
                        f"{min_temp}°C" if is_metric else f"{self.c_to_f(min_temp)}°F"
                    )
                    max_temp_disp = (
                        f"{max_temp}°C" if is_metric else f"{self.c_to_f(max_temp)}°F"
                    )
                    self.add_week(
                        day["date"],
                        day["day_name"],
                        icon_path,
                        day["condition"],
                        min_temp_disp,
                        max_temp_disp,
                        i + 2,
                    )
            else:
                hourly.config(fg="white")
                headers = ["Time", "Temp", "Condition", "Wind", "Humidity"]
                for col, txt in enumerate(headers):
                    Label(
                        self.frame2,
                        text=txt,
                        font=("Segoe UI", 11, "bold"),
                        bg="#1F2C3C",
                        fg="white",
                        anchor="w",
                    ).grid(row=1, column=col, sticky="w", padx=40)
                for i, hour in enumerate(hourly_forecast):
                    temp = hour["temp_c"] if is_metric else self.c_to_f(
                        hour["temp_c"])
                    wind = (
                        hour["windspeed_kph"]
                        if is_metric
                        else self.kmh_to_mph(hour["windspeed_kph"])
                    )
                    temp_display = f"{temp}°{'C' if is_metric else 'F'}"
                    wind_display = f"{wind} {'km/h' if is_metric else 'mph'}"
                    self.add_hour(
                        hour["time"],
                        temp_display,
                        hour["condition"],
                        wind_display,
                        hour["humidity_percent"],
                        i + 2,
                    )
        except Exception as e:
            messagebox.showerror("Error", f"{str(e)}")

    def add_hour(self, time, temp, condition, windspeed, humidity, row):

        Label(
            self.frame2, text=time, font=("Segoe UI", 10), bg="#1F2C3C", fg="white"
        ).grid(row=row, column=0, sticky="w", padx=40, pady=2)
        Label(
            self.frame2, text=f"{temp}", font=("Segoe UI", 10), bg="#1F2C3C", fg="white"
        ).grid(row=row, column=1, sticky="w", padx=40, pady=2)
        Label(
            self.frame2, text=condition, font=("Segoe UI", 10), bg="#1F2C3C", fg="white"
        ).grid(row=row, column=2, sticky="w", padx=40, pady=2)
        Label(
            self.frame2,
            text=f"{windspeed}",
            font=("Segoe UI", 10),
            bg="#1F2C3C",
            fg="white",
        ).grid(row=row, column=3, sticky="w", padx=40, pady=2)
        Label(
            self.frame2,
            text=f"{humidity}%",
            font=("Segoe UI", 10),
            bg="#1F2C3C",
            fg="white",
        ).grid(row=row, column=4, sticky="w", padx=40, pady=2)

    def add_week(self,date,day_name,icon_path,condition,min_temp_disp,max_temp_disp,row,size=(50, 50),):
        today_str = datetime.today().strftime("%Y-%m-%d")

        Label(
            self.frame2,
            text=day_name if date != today_str else "Today",
            font=("Segoe UI", 10),
            bg="#1F2C3C",
            fg="white",
        ).grid(row=row, column=0, sticky="w", padx=40)

        frame_key = f"day_{row}"

        try:
            if icon_path in self.icon_cache:
                frames, delay = self.icon_cache[icon_path]
            else:
                pil_img = Image.open(icon_path)
                frame_count = getattr(pil_img, "n_frames", 1)
                delay = pil_img.info.get("duration", 100)
                frames = []
                for i in range(frame_count):
                    pil_img.seek(i)
                    frame_resized = pil_img.resize(
                        size, Image.Resampling.LANCZOS)
                    frames.append(ImageTk.PhotoImage(frame_resized))
                pil_img.close()
                self.icon_cache[icon_path] = (frames, delay)

            self.animation_frames[frame_key] = frames

        except Exception as e:
            print(f"Error loading {icon_path}: {e}")
            frames = []
            delay = 100

        icon_label = Label(self.frame2, bg="#1F2C3C")
        icon_label.grid(row=row, column=1, sticky="w", padx=40)
        self.animated_widgets.append(icon_label)

        def animate(idx=0):
            if frames and icon_label.winfo_exists():
                try:
                    icon_label.config(image=frames[idx])
                    icon_label.image = frames[idx]
                    self.frame2.after(delay, animate, (idx + 1) % len(frames))
                except:
                    pass

        if frames:
            self.frame2.after(200, animate)

        Label(
            self.frame2, text=condition, font=("Segoe UI", 10), bg="#1F2C3C", fg="white"
        ).grid(row=row, column=2, sticky="w", padx=40)
        Label(
            self.frame2,
            text=min_temp_disp,
            font=("Segoe UI", 10),
            bg="#1F2C3C",
            fg="white",
        ).grid(row=row, column=3, sticky="w", padx=40)
        Label(
            self.frame2,
            text=max_temp_disp,
            font=("Segoe UI", 10),
            bg="#1F2C3C",
            fg="white",
        ).grid(row=row, column=4, sticky="w", padx=40)

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0C101C")
        self.controller = controller

        BASE_DIR = os.path.dirname(__file__)
        self.ICON_DIR = os.path.abspath(os.path.join(BASE_DIR, "UI/icons"))
        self.icon_cache = {}
        self.animation_frames = {}
        self.animated_widgets = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        BASE_DIR = os.path.dirname(__file__)
        image_path = os.path.join(BASE_DIR, "UI", "rainy.png")
        if os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize((120, 120))
            self.photo = ImageTk.PhotoImage(image)
        else:
            default_img = Image.new("RGB", (120, 120), color="#1F2C3C")
            self.photo = ImageTk.PhotoImage(default_img)

        # ------------------- LEFT PANEL -----------------
        frame1 = Frame(self, bg="#0C101C")
        frame1.grid(row=0, column=0, sticky="ewns")
        frame1.grid_columnconfigure(0, weight=1)
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_rowconfigure(1, weight=0)
        frame1.grid_rowconfigure(2, weight=3)

        # -- box1 --
        box1 = Frame(frame1, bg="#0C101C", padx=10)
        box1.grid(row=0, column=0, padx=10, sticky="nsew")
        box1.grid_columnconfigure(0, weight=1)
        box1.grid_rowconfigure(0, weight=1)
        box1.grid_rowconfigure(1, weight=1)
        box1.grid_rowconfigure(2, weight=1)

        top_frame = Frame(box1, bg="#1F2C3C")
        top_frame.grid(row=0, column=0, sticky="ewns", pady=(10, 0))

        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=0)
        top_frame.grid_columnconfigure(2, weight=1)
        top_frame.grid_rowconfigure(0, weight=1)

        back = Button(
            top_frame,
            text="Back",
            font=("Segoe UI", 14),
            bd=0,
            bg="#1F2C3C",
            fg="grey",
            command=lambda: self.controller.show_frame("Dashboard"),
        )
        back.grid(row=0, column=0, sticky="w")

        self.unit_var = StringVar(value="Metric")

        Label(
            top_frame, text="Units:", font=("Segoe UI", 12), bg="#1F2C3C", fg="white"
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))

        units = ttk.Combobox(
            top_frame,
            textvariable=self.unit_var,
            values=["Metric", "Imperial"],
            state="readonly",
            width=10,
        )
        units.grid(row=0, column=2, sticky="w", padx=(5, 0))

        def on_unit_change(event=None):
            mode = getattr(self, "last_mode", "daily")
            self.update_weather(mode)

        units.bind("<<ComboboxSelected>>", on_unit_change)

        self.city_label = Label(
            box1,
            text="",
            font=("Segoe UI", 14),
            bg="#1F2C3C",
            fg="white",
            anchor="w",
            padx=10,
            pady=5,
        )
        self.city_label.grid(row=1, column=0, sticky="ewns", pady=(10, 0))

        # --- sub-box1 ---
        sub_box1 = Frame(box1, bg="#1F2C3C")
        sub_box1.grid(row=2, column=0, sticky="ewns")
        sub_box1.grid_rowconfigure(0, weight=1)
        sub_box1.grid_columnconfigure(0, weight=1)
        sub_box1.grid_columnconfigure(1, weight=2)
        sub_box1.grid_columnconfigure(2, weight=1)

        self.curr_temp = Label(
            sub_box1, text="", font=("", 50), bg="#1F2C3C", fg="white"
        )
        self.curr_temp.grid(row=0, column=0, sticky="w", padx=10)
        self.curr_icon = Label(sub_box1, image=self.photo,
                               bg="#1F2C3C", fg="white")
        self.curr_icon.grid(row=0, column=2, sticky="e", padx=10)
        self.description = Label(
            box1,
            text="",
            font=("Segoe UI", 12),
            bg="#1F2C3C",
            fg="white",
            anchor="w",
            padx=10,
            pady=5,
        )
        self.description.grid(row=3, column=0, sticky="ewsn")

        # -- seperator
        Frame(frame1, height=2).grid(
            row=1, column=0, sticky="ew", padx=20, pady=5)

        # -- box2 --
        box2 = Frame(frame1, bg="#1F2C3C", padx=10, pady=10)
        box2.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")

        for i in range(6):
            box2.grid_rowconfigure(i, weight=1)

        def add_label(idx, text):
            label = Label(
                box2,
                text=text,
                font=("Segoe UI", 10),
                bg="#1F2C3C",
                fg="white",
                padx=20,
                anchor="w",
            )
            label.grid(row=idx, column=0, sticky="ew")
            return label

        self.visibility = add_label(0, "")
        self.humidity = add_label(1, "")
        self.feels_like = add_label(2, "")
        self.wind_speed = add_label(3, "")
        self.sunrise = add_label(4, "")
        self.sunset = add_label(5, "")

        # -- box3 --
        self.frame2 = Frame(self, bg="#1F2C3C")
        self.frame2.grid(row=0, column=1, padx=(0, 15), pady=10, sticky="ewns")

        self.frame2.grid_rowconfigure(0, weight=0)
        for c in range(5):
            self.frame2.grid_columnconfigure(c, weight=1, uniform="col")

        for i in range(1, 13):
            self.frame2.grid_rowconfigure(i, weight=1)

    def show_daily(self):
        self.last_mode = "daily"
        self.update_weather("daily")

    def show_hourly(self):
        self.last_mode = "hourly"
        self.update_weather("hourly")

    def c_to_f(self, c):
        return round((c * 9 / 5) + 32, 1)

    def kmh_to_mph(self, kmh):
        return round(kmh * 0.621371, 1)
