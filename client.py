import socket
import json
import os
import tkinter as tk
from tkinter import messagebox

SERVER_ADDRESS = ("127.0.0.1", 21000)
BUFFER_SIZE = 4096

def send_request(sock, request):
    sock.sendto(json.dumps(request).encode(), SERVER_ADDRESS)
    response_data, _ = sock.recvfrom(BUFFER_SIZE)
    return json.loads(response_data.decode())

def login(sock):

    login_root = tk.Toplevel()
    login_root.geometry('500x800')
    login_root.title("Login")

    tk.Label(login_root, text="Username:", font=("Helvetica")).pack(pady=5, padx=3)
    username_entry = tk.Entry(login_root)
    username_entry.pack(pady=5, padx=3)
    tk.Label(login_root, text="Password:", font=("Helvetica")).pack(pady=5, padx=3)
    password_entry = tk.Entry(login_root, show="*")
    password_entry.pack(pady=5, padx=3)

    status_label = tk.Label(login_root, text="")
    status_label.pack(pady=5, padx=3)
    
    def login_attempt():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        request = {"action": "login", "username": username, "password": password}
        response = send_request(sock, request)

        if response.get("status") == "success":
            status_label.config(text=f"Login successful. Welcome, {username}!", fg="green", bg="lightblue")  
            login_root.destroy()
        else:
            status_label.config(text="Login failed. Try again.", fg="white", bg="red")
            
    tk.Button(login_root, text="Login", command=login_attempt).pack(pady=6, padx=2)
    tk.Button(login_root, text="Quit", font=("Arial", 10), fg="red", 
              activebackground="red", activeforeground="white", command=login_root.destroy).pack(pady=6, padx=2)
    
    login_root.mainloop()
    
def assign_strengths(sock, username):

    def submit_strengths():
        try:
            sword = int(sword_entry.get())
            shield = int(shield_entry.get())
            slaying_potion = int(sp_entry.get())
            healing_potion = int(hp_entry.get())

            if any(x < 0 or x > 3 for x in [sword, shield, slaying_potion, healing_potion]) or \
               (sword + shield + slaying_potion + healing_potion != 10):
                raise ValueError

            strengths = {
                "sword": sword,
                "shield": shield,
                "slaying_potion": slaying_potion,
                "healing_potion": healing_potion
            }

            request = {"action": "assign_strengths", "username": username, "strengths": strengths}
            response = send_request(sock, request)
            #print(f"[Client] {response.get('message')}")

            messagebox.showinfo("", response.get("message"))
            
            strengths_root.destroy()

        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid inputs, try again!")

    strengths_root = tk.Toplevel()

    tk.Label(text="Assign your strengths (total must equal 10, each between 0 and 3):", justify="left", 
             anchor="n", font=("Times", 14, 'bold')).pack(padx=10, pady=10)
    
    tk.Label(strengths_root, text="Sword strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify = "left").pack(padx=10, pady=10)
    sword_entry = tk.Entry(strengths_root)
    sword_entry.pack(padx=10, pady=10)
    tk.Label(strengths_root, text="Shield strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify = "left").pack(padx=10, pady=10)
    shield_entry = tk.Entry(strengths_root)
    shield_entry.pack(padx=10, pady=10)
    tk.Label(strengths_root, text="Slaying Potion strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify = "left").pack(padx=10, pady=10)
    sp_entry = tk.Entry(strengths_root)
    sp_entry.pack(padx=10, pady=10)
    tk.Label(strengths_root, text="Healing Potion strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify = "left").pack(padx=10, pady=10)
    hp_entry = tk.Entry(strengths_root)
    hp_entry.pack(padx=10, pady=10)

    tk.Button(strengths_root, text="Submit", font=("Times", 8, "bold"), command=submit_strengths, bg="white", fg="black").pack(pady=10)

    strengths_root.mainloop()
    
    
def view_active_users(sock):
    
    request = {"action": "get_active_users"}
    response = send_request(sock, request)
    active_gamers = response.get("active_users")

    users_root = tk.Toplevel()
    users_root.title("Active Users")

    tk.Label(users_root, text="Active Users", font=("Helvetica", 14, "bold"),
             fg="white", bg="darkgreen", width=20, relief="ridge", borderwidth=2).grid(row=0, column=0, sticky="nsew")

    for i, username in enumerate(active_gamers.keys(), start=1):
        tk.Label(users_root, text=username, font=("Helvetica", 11),
                 width=20, relief="ridge", borderwidth=2).grid(row=i, column=0, sticky="nsew")
    
def send_fight_request(sock, username):

    fight_root = tk.Toplevel()
    fight_root.title("Initiating Fight Request...")

    tk.Label(fight_root, text="Which user will you attempt to slay?:", font=("Helvetica", 10, "underline", "bold"), fg="darkred", bg="white").pack(padx=5, pady=10)
    fight_entry = tk.Entry(fight_root)
    fight_entry.pack(padx=10, pady=10)
    tk.Label(fight_root, text="Choose what to fight with:", font=("Helvetica", 10, "underline", "bold"), fg="black", bg="white").pack(padx=5, pady=10)
    item_entry = tk.Entry(fight_root)
    item_entry.pack(padx=10, pady=10)

    boss = fight_entry.get().strip()
    item = item_entry.get().strip()
    
    request = {
        "action": "fight_request",
        "username": username,
        "boss": boss,
        "fighting_item": item,
        "fighting_strength": 3
    }
    response = send_request(sock, request)
    print(f"[Client] {response.get('message')}")
    if "updated_state" in response:
        print("[Client] Your updated state:")
        print(json.dumps(response["updated_state"], indent=2))

def view_fight_logs(sock):
    request = {"action": "get_fight_logs"}
    response = send_request(sock, request)
    if response.get("status") == "success":
        print("\n[Client] Confirmed Fight Logs:")
        print("{:<10} {:<10} {:<15} {:<10} {:<10}".format("Requester", "Boss", "Item", "Strength", "Winner"))
        for log in response.get("logs", []):
            print("{:<10} {:<10} {:<15} {:<10} {:<10}".format(
                log["requester"], log["boss"], log["fighting_item"],
                log["fighting_strength"], log["winner"]
            ))
    else:
        print("[Client] Failed to retrieve logs.") 

def upload_avatar(sock, username):
    avatar_path = input("Enter the path to your avatar image (JPG): ").strip()
    if not os.path.isfile(avatar_path):
        print("[Client] File not found.")
        return
    with open(avatar_path, "rb") as f:
        avatar_data = list(f.read())
    request = {
        "action": "upload_avatar",
        "username": username,
        "filename": os.path.basename(avatar_path),
        "avatar_data": avatar_data
    }
    response = send_request(sock, request)
    print(f"[Client] {response.get('message')}")

def view_active_gamer_info(sock):
    
    request = {"action": "get_active_gamers"}
    response = send_request(sock, request)
    active_gamers = response.get("active_users")

    active_root = tk.Toplevel()
    active_root.title("Active Gamers")

    headers = ["Active User:", "Sword", "Shield", "Slaying-Potion", "Healing-Potion", "Lives"]

    for row, (username, stats) in enumerate(active_gamers.items(), start=1):
        tk.Label(active_root, text=username, borderwidth=2, relief="ridge", width=15).grid(row=row, column=0, sticky="nsew")
        tk.Label(active_root, text=stats["sword"], borderwidth=2, relief="ridge", width=15).grid(row=row, column=1, sticky="nsew")
        tk.Label(active_root, text=stats["shield"], borderwidth=2, relief="ridge", width=15).grid(row=row, column=2, sticky="nsew")
        tk.Label(active_root, text=stats["slaying_potion"], borderwidth=2, relief="ridge", width=15).grid(row=row, column=3, sticky="nsew")
        tk.Label(active_root, text=stats["healing_potion"], borderwidth=2, relief="ridge", width=15).grid(row=row, column=4, sticky="nsew")
        tk.Label(active_root, text=stats["lives"], borderwidth=2, relief="ridge", width=15).grid(row=row, column=5, sticky="nsew")

    active_root.mainloop()
    

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    root = tk.Tk()
    root.withdraw()

    action_root = tk.Toplevel()
    action_root.title("Choose an action:")
    action_root.geometry('800x800')
    action_root.configure(bg="white")
    
    tk.Button(action_root, text="Assign Strengths", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: assign_strengths(sock, username)).pack(pady=5, padx=2)
    tk.Button(action_root, text="Upload Avatar", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: upload_avatar(sock, username)).pack(pady=5, padx=2)
    tk.Button(action_root, text="View Active Users", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: view_active_users(sock)).pack(pady=5, padx=2)
    tk.Button(action_root, text="Quit", activebackground="red", 
              activeforeground="white", fg="red", bg="white", command=action_root.destroy).pack(pady=5, padx=2)
        
    action_root.mainloop()
    sock.close()
    
if __name__ == "__main__":
    main()
