from tkinter import *
import dashboard
import weather


class App(Tk):
    def __init__(self):
        super().__init__()

        container = Frame(self, bd=0)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (dashboard.Dashboard, weather.Weather):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Dashboard")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    app = App()  # ----->app.Tk() or root = Tk()
    app.title("Weather App")

    app.state("zoomed")
    app.minsize(1200, 600)
    app.configure(bg="white")
    app.mainloop()  # --->root.mainloop()
