import tkinter as tk
from manageUser import manageUser
from userApp import LoginRegisterApp

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginRegisterApp(root, manageUser())
    # các thiết lập và tạo widget khác

    def on_closing():
        app.stop_checking()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()