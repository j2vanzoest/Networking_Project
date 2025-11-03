import socket
import json
import os
import sys
import tkinter as tk
from tkinter import messagebox

SERVER_ADDRESS = ("127.0.0.1", 21000) #server ip and port
BUFFER_SIZE = 4096 #socket buffer

def send_request(sock, request): #send request to server and receive response
    sock.sendto(json.dumps(request).encode(), SERVER_ADDRESS)
    response_data, _ = sock.recvfrom(BUFFER_SIZE)
    return json.loads(response_data.decode())

def login(sock): #login window
    user_result = None #store username on success

    login_root = tk.Toplevel() #popup window
    login_root.geometry('200x300') #size
    login_root.title("Login") #title

    tk.Label(login_root, text="Username:", font=("Helvetica")).pack(pady=5, padx=3) #username label
    username_entry = tk.Entry(login_root) #username entry
    username_entry.pack(pady=5, padx=3)
    tk.Label(login_root, text="Password:", font=("Helvetica")).pack(pady=5, padx=3) #password label
    password_entry = tk.Entry(login_root, show="*") #password entry
    password_entry.pack(pady=5, padx=3)

    status_label = tk.Label(login_root, text="") #status display
    status_label.pack(pady=5, padx=3)
    
    def login_attempt(): #login button callback
        nonlocal user_result
        username = username_entry.get().strip() #get username
        password = password_entry.get().strip() #get password
        request = {"action": "login", "username": username, "password": password} #login request
        response = send_request(sock, request) #send to server
        if response.get("status") == "success": #check server response
            status_label.config(text=f"Login successful. Welcome, {username}!", fg="green", bg="lightblue") #success
            user_result = username
            login_root.destroy() #close window
        else:
            status_label.config(text="Login failed. Try again.", fg="white", bg="red") #fail
    
    tk.Button(login_root, text="Login", command=lambda: login_attempt()).pack(pady=6, padx=2) #login button
    tk.Button(login_root, text="Quit", font=("Arial", 10), fg="red", activebackground="red", activeforeground="white",
              command=lambda: os._exit(0)).pack(pady=6, padx=2) #quit app completely

    login_root.grab_set() #prevent other windows
    login_root.wait_window() #wait until login closed

    return user_result #return username if success

def assign_strengths(sock, username): #assign strengths window
    strengths_root = tk.Toplevel() #popup
    strengths_root.configure(bg="lightgreen") #bg color

    tk.Label(strengths_root, text="Assign your strengths.\n(Total must equal 10, each between 0 and 3):", 
             justify="center", anchor="n", fg="white", relief=tk.RAISED, bg="darkblue", font=("Times", 10, 'bold')).pack(padx=10, pady=10) #instructions
    
    tk.Label(strengths_root, text="Sword strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify="left").pack(padx=10, pady=10) #sword
    sword_entry = tk.Entry(strengths_root)
    sword_entry.pack(padx=10, pady=10)
    tk.Label(strengths_root, text="Shield strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify="left").pack(padx=10, pady=10) #shield
    shield_entry = tk.Entry(strengths_root)
    shield_entry.pack(padx=10, pady=10)
    tk.Label(strengths_root, text="Slaying Potion strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify="left").pack(padx=10, pady=10) #slaying potion
    sp_entry = tk.Entry(strengths_root)
    sp_entry.pack(padx=10, pady=10)
    tk.Label(strengths_root, text="Healing Potion strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify="left").pack(padx=10, pady=10) #healing potion
    hp_entry = tk.Entry(strengths_root)
    hp_entry.pack(padx=10, pady=10)

    def submit_strengths(): #submit button callback
        try:
            sword = int(sword_entry.get())
            shield = int(shield_entry.get())
            slaying_potion = int(sp_entry.get())
            healing_potion = int(hp_entry.get())
            if any(x < 0 or x > 3 for x in [sword, shield, slaying_potion, healing_potion]) or \
               (sword + shield + slaying_potion + healing_potion != 10): #validate
                raise ValueError
            strengths = {"sword": sword, "shield": shield, "slaying_potion": slaying_potion, "healing_potion": healing_potion}
            request = {"action": "assign_strengths", "username": username, "strengths": strengths} #request
            response = send_request(sock, request) #send
            messagebox.showinfo("", response.get("message")) #show result
            strengths_root.destroy() #close window
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid inputs, try again!") #error

    tk.Button(strengths_root, text="Submit", font=("Times", 8, "bold"), command=submit_strengths, bg="white", fg="black").pack(pady=10) #submit button

    strengths_root.grab_set() #block other windows
    strengths_root.wait_window() #wait until closed  

def view_active_users(sock): #view users
    request = {"action": "get_active_users"} #request
    response = send_request(sock, request)
    active_gamers = response.get("active_users")

    users_root = tk.Toplevel()
    users_root.title("Active Users")

    tk.Label(users_root, text="Active Users", font=("Helvetica", 14, "bold"),
             fg="white", bg="darkgreen", width=20, relief="ridge", borderwidth=2).grid(row=0, column=0, sticky="nsew") #header

    for i, username in enumerate(active_gamers.keys(), start=1):
        tk.Label(users_root, text=username, font=("Helvetica", 11),
                 width=20, relief="ridge", borderwidth=2).grid(row=i, column=0, sticky="nsew") #list users
    
def main(): #main app
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #udp socket

    root = tk.Tk() #main tk root
    root.withdraw() #hide root

    username = login(sock) #login call
    
    action_root = tk.Toplevel() #actions window
    action_root.title("Choose an action:")
    action_root.geometry('150x200')
    action_root.configure(bg="white")
    
    tk.Button(action_root, text="Assign Strengths", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: assign_strengths(sock, username)).pack(pady=5, padx=2) #strengths
    tk.Button(action_root, text="Upload Avatar", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: upload_avatar(sock, username)).pack(pady=5, padx=2) #avatar
    tk.Button(action_root, text="View Active Users", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: view_active_users(sock)).pack(pady=5, padx=2) #view users
    tk.Button(action_root, text="Quit", activebackground="red", 
              activeforeground="white", fg="red", bg="white", command=action_root.destroy).pack(pady=5, padx=2) #quit

    action_root.mainloop() #start main loop
    sock.close() #close socket

if __name__ == "__main__":
    main()
