import tkinter as tk
from manageUser import manageUser
from userApp import LoginRegisterApp

if __name__ == "__main__":
    # root = tk.Tk()
    # app = TodoApp(root)
    # root.mainloop()


    root = tk.Tk()
    app = LoginRegisterApp(root, manageUser())
    root.mainloop()