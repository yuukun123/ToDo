if __name__ == "__main__":
    import tkinter as tk
    from manageUser import manageUser
    from userApp import LoginRegisterApp

    root = tk.Tk()
    app = LoginRegisterApp(root, manageUser())
    root.mainloop()
