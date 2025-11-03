import socket
import json
import tkinter as tk
from tkinter import messagebox

SERVER_ADDRESS = ("127.0.0.1", 21000)
BUFFER_SIZE = 4096

def send_request(sock, request):
    sock.sendto(json.dumps(request).encode(), SERVER_ADDRESS)
    response_data, _ = sock.recvfrom(BUFFER_SIZE)
    return json.loads(response_data.decode())

# ---------------- LOGIN WINDOW ----------------
def login(sock):
    user_result = None

    def login_attempt():
        nonlocal user_result
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        request = {"action": "login", "username": username, "password": password}
        response = send_request(sock, request)
        if response.get("status") == "success":
            status_label.config(text=f"Login successful! Welcome, {username}", fg="green", bg="lightblue")
            user_result = username
            login_root.after(1000, login_root.destroy)  # Close after 1 second
        else:
            status_label.config(text="Login failed. Try again.", fg="white", bg="red")

    login_root = tk.Tk()
    login_root.title("Simple RPG Game")
    login_root.geometry('400x250')

    tk.Label(login_root, text="Username:", font=("Helvetica")).pack(pady=5)
    username_entry = tk.Entry(login_root)
    username_entry.pack(pady=5)

    tk.Label(login_root, text="Password:", font=("Helvetica")).pack(pady=5)
    password_entry = tk.Entry(login_root, show="*")
    password_entry.pack(pady=5)

    tk.Button(login_root, text="Login", command=login_attempt).pack(pady=6)
    tk.Button(login_root, text="Quit", fg="red", command=login_root.destroy).pack(pady=6)

    status_label = tk.Label(login_root, text="", font=("Arial", 10))
    status_label.pack(pady=10)

    login_root.mainloop()
    return user_result

# ---------------- MENU ----------------
def show_menu(sock, username):
    menu_root = tk.Tk()
    menu_root.title("Game Menu")
    menu_root.geometry("300x300")

    tk.Label(menu_root, text=f"Welcome, {username}!", font=("Arial", 14)).pack(pady=10)

    tk.Button(menu_root, text="Assign Strengths", command=lambda: assign_strengths(sock, username)).pack(pady=5)
    tk.Button(menu_root, text="View Active Users", command=lambda: view_active_users(sock)).pack(pady=5)
    tk.Button(menu_root, text="View Fight Logs", command=lambda: view_fight_logs(sock)).pack(pady=5)
    tk.Button(menu_root, text="Quit", fg="red", command=menu_root.destroy).pack(pady=10)

    menu_root.mainloop()

# ---------------- ASSIGN STRENGTHS ----------------
def assign_strengths(sock, username):
    strengths_root = tk.Toplevel()
    strengths_root.title("Assign Strengths")

    tk.Label(strengths_root, text="Assign strengths (total = 10, each 0-3):").pack(pady=5)
    entries = {}
    for item in ["sword", "shield", "slaying_potion", "healing_potion"]:
        tk.Label(strengths_root, text=f"{item.capitalize()}:").pack()
        entry = tk.Entry(strengths_root)
        entry.pack()
        entries[item] = entry

    def submit_strengths():
        try:
            strengths = {k: int(v.get()) for k, v in entries.items()}
            if sum(strengths.values()) != 10 or any(x < 0 or x > 3 for x in strengths.values()):
                raise ValueError
            request = {"action": "assign_strengths", "username": username, "strengths": strengths}
            response = send_request(sock, request)
            messagebox.showinfo("Result", response.get("message"))
            strengths_root.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Total must be 10, each between 0-3.")

    tk.Button(strengths_root, text="Submit", command=submit_strengths).pack(pady=10)

# ---------------- VIEW ACTIVE USERS ----------------
def view_active_users(sock):
    request = {"action": "get_active_users"}
    response = send_request(sock, request)
    active_users = response.get("active_users", [])
    messagebox.showinfo("Active Users", "\n".join(active_users) if active_users else "No active users.")

# ---------------- VIEW FIGHT LOGS ----------------
def view_fight_logs(sock):
    request = {"action": "get_fight_logs"}
    response = send_request(sock, request)
    logs = response.get("logs", [])
    if logs:
        log_text = "\n".join([f"{log['requester']} vs {log['boss']} ({log['fighting_item']} {log['fighting_strength']}) -> Winner: {log['
