import socket
import json
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog #file dialog for GUI avatar selection

SERVER_ADDRESS = ("127.0.0.1", 21000) #server ip/port
BUFFER_SIZE = 4096 #udp buffer size

def send_request(sock, request):
    sock.sendto(json.dumps(request).encode(), SERVER_ADDRESS) #send json request
    response_data, _ = sock.recvfrom(BUFFER_SIZE) #receive response
    return json.loads(response_data.decode()) #decode json

def login(sock):
    user_result = None #store logged in username

    login_root = tk.Toplevel() #popup window
    login_root.geometry('200x300')
    login_root.title("Login")

    tk.Label(login_root, text="Username:", font=("Helvetica")).pack(pady=5, padx=3) #username label
    username_entry = tk.Entry(login_root) #username entry
    username_entry.pack(pady=5, padx=3)
    tk.Label(login_root, text="Password:", font=("Helvetica")).pack(pady=5, padx=3) #password label
    password_entry = tk.Entry(login_root, show="*") #hide password input
    password_entry.pack(pady=5, padx=3)

    status_label = tk.Label(login_root, text="") #status feedback
    status_label.pack(pady=5, padx=3)
    
    def login_attempt():
        nonlocal user_result
        username = username_entry.get().strip() #get username
        password = password_entry.get().strip() #get password
        request = {"action": "login", "username": username, "password": password} #create request
        response = send_request(sock, request) #send to server
        if response.get("status") == "success":
            status_label.config(text=f"Login successful. Welcome, {username}!", fg="green", bg="lightblue") #success feedback
            user_result = username #store username
            login_root.destroy() #close login
        else:
            status_label.config(text="Login failed. Try again.", fg="white", bg="red") #failure feedback
            
    tk.Button(login_root, text="Login", command=lambda: login_attempt()).pack(pady=6, padx=2) #login button
    tk.Button(login_root, text="Quit", font=("Arial", 10), fg="red", activebackground="red", activeforeground="white",
              command=lambda: os._exit(0)).pack(pady=6, padx=2) #quit program

    login_root.grab_set() #focus on window
    login_root.wait_window() #wait until closed

    return user_result #return username

def assign_strengths(sock, username):
    strengths_root = tk.Toplevel() #popup for strengths
    strengths_root.configure(bg="lightgreen")

    tk.Label(strengths_root, text="Assign your strengths.\n(Total must equal 10, each between 0 and 3):", 
             justify="center", anchor="n", fg="white", relief=tk.RAISED, bg="darkblue", font=("Times", 10, 'bold')).pack(padx=10, pady=10) #instructions
    
    tk.Label(strengths_root, text="Sword strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify="left").pack(padx=10, pady=10)
    sword_entry = tk.Entry(strengths_root)
    sword_entry.pack(padx=10, pady=10)
    tk.Label(strengths_root, text="Shield strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify="left").pack(padx=10, pady=10)
    shield_entry = tk.Entry(strengths_root)
    shield_entry.pack(padx=10, pady=10)
    tk.Label(strengths_root, text="Slaying Potion strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify="left").pack(padx=10, pady=10)
    sp_entry = tk.Entry(strengths_root)
    sp_entry.pack(padx=10, pady=10)
    tk.Label(strengths_root, text="Healing Potion strength:", font=("Times", 8, "underline", "bold"), fg="white", bg="darkgreen", justify="left").pack(padx=10, pady=10)
    hp_entry = tk.Entry(strengths_root)
    hp_entry.pack(padx=10, pady=10)

    def submit_strengths():
        try:
            sword = int(sword_entry.get()) #parse input
            shield = int(shield_entry.get())
            slaying_potion = int(sp_entry.get())
            healing_potion = int(hp_entry.get())
            if any(x < 0 or x > 3 for x in [sword, shield, slaying_potion, healing_potion]) or \
               (sword + shield + slaying_potion + healing_potion != 10):
                raise ValueError
            strengths = {"sword": sword, "shield": shield, "slaying_potion": slaying_potion, "healing_potion": healing_potion} #strength dict
            request = {"action": "assign_strengths", "username": username, "strengths": strengths} #request
            response = send_request(sock, request)
            messagebox.showinfo("", response.get("message")) #server feedback
            strengths_root.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid inputs, try again!") #input error

    tk.Button(strengths_root, text="Submit", font=("Times", 8, "bold"), command=submit_strengths, bg="white", fg="black").pack(pady=10)

    strengths_root.grab_set() #focus
    strengths_root.wait_window() #wait until closed  

def view_active_users(sock):
    request = {"action": "get_active_users"} #request active users
    response = send_request(sock, request)
    active_gamers = response.get("active_users")

    users_root = tk.Toplevel() #popup window
    users_root.title("Active Users")

    tk.Label(users_root, text="Active Users", font=("Helvetica", 14, "bold"),
             fg="white", bg="darkgreen", width=20, relief="ridge", borderwidth=2).grid(row=0, column=0, sticky="nsew") #header

    for i, username in enumerate(active_gamers, start=1):
        tk.Label(users_root, text=username, font=("Helvetica", 11),
                 width=20, relief="ridge", borderwidth=2).grid(row=i, column=0, sticky="nsew") #list users

def send_fight_request(sock, username):
    fight_root = tk.Toplevel() #fight popup
    fight_root.title("Initiating Fight Request...")
    fight_root.configure(bg="lightyellow")

    #label for opponent entry
    tk.Label(fight_root, text="Which user will you attempt to slay?:", font=("Helvetica", 10, "underline", "bold"), fg="darkred", bg="white").pack(pady=10)
    fight_entry = tk.Entry(fight_root) #opponent username entry
    fight_entry.pack(padx=10, pady=10)

    #label for dropdown
    tk.Label(fight_root, text="Choose what to fight with:", font=("Helvetica", 10, "underline", "bold"), fg="black", bg="white").pack(pady=10)

    #dropdown for selecting item
    item_var = tk.StringVar(value="sword") #default value
    item_dropdown = tk.OptionMenu(fight_root, item_var, "sword", "slaying potion")
    item_dropdown.config(width=20, bg="lightgray")
    item_dropdown.pack(padx=10, pady=10)

    #label and entry for fighting strength
    tk.Label(fight_root, text="Enter fighting strength (number):", font=("Helvetica", 10, "underline", "bold"), fg="black", bg="white").pack(padx=5, pady=10)
    strength_entry = tk.Entry(fight_root)
    strength_entry.pack(padx=10, pady=10)

    #function to submit the request
    def submit_fight():
        boss = fight_entry.get().strip()
        selected_item = item_var.get()
        fighting_item = "sword" if selected_item == "sword" else "slaying_potion" #convert dropdown text to key
        try:
            fighting_strength = int(strength_entry.get()) #parse strength
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for strength.") #input error
            return

        if not boss:
            messagebox.showerror("Invalid Input", "Please enter a valid opponent username.") #missing opponent
            return

        #create and send request to server
        request = {"action": "fight_request", "username": username, "boss": boss, "fighting_item": fighting_item, "fighting_strength": fighting_strength}
        response = send_request(sock, request) #send and receive
        messagebox.showinfo("Fight Result", response.get("message")) #feedback popup

        #if fight success, print updated state if present
        if "updated_state" in response:
            print("[Client] Your updated state:")
            print(json.dumps(response["updated_state"], indent=2)) #pretty print dict

    #function to go back to action window
    def go_back():
        fight_root.destroy() #close this window

    #button frame for submit/go back
    button_frame = tk.Frame(fight_root, bg="white")
    button_frame.pack(pady=15)

    #submit and go back buttons
    tk.Button(button_frame, text="Submit", command=submit_fight, width=12, bg="darkblue", fg="white", activebackground="blue").grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Go Back", command=go_back, width=12, bg="gray", fg="white", activebackground="darkgray").grid(row=0, column=1, padx=5)

def view_fight_logs(sock):
    request = {"action": "get_fight_logs"} #request fight logs
    response = send_request(sock, request) #send to server
    
    if response.get("status") == "success":
        logs = response.get("logs", [])

        #create a popup window for fight logs
        logs_root = tk.Toplevel()
        logs_root.title("Confirmed Fight Logs")
        logs_root.configure(bg="white")

        #header label
        tk.Label(logs_root, text="Confirmed Fight Logs", font=("Helvetica", 14, "bold"),
                 fg="white", bg="darkgreen", width=60, relief="ridge", borderwidth=2).grid(row=0, column=0, columnspan=5, sticky="nsew")

        #create column headers
        headers = ["Requester", "Boss", "Item", "Strength", "Winner"]
        for col, header in enumerate(headers):
            tk.Label(logs_root, text=header, font=("Helvetica", 11, "bold"),
                     bg="lightgray", borderwidth=2, relief="ridge", width=15).grid(row=1, column=col, sticky="nsew")

        #populate rows with fight logs
        for i, log in enumerate(logs, start=2):
            tk.Label(logs_root, text=log["requester"], borderwidth=2, relief="ridge", width=15).grid(row=i, column=0, sticky="nsew")
            tk.Label(logs_root, text=log["boss"], borderwidth=2, relief="ridge", width=15).grid(row=i, column=1, sticky="nsew")
            tk.Label(logs_root, text=log["fighting_item"], borderwidth=2, relief="ridge", width=15).grid(row=i, column=2, sticky="nsew")
            tk.Label(logs_root, text=log["fighting_strength"], borderwidth=2, relief="ridge", width=15).grid(row=i, column=3, sticky="nsew")
            tk.Label(logs_root, text=log["winner"], borderwidth=2, relief="ridge", width=15).grid(row=i, column=4, sticky="nsew")

        #make columns expand evenly
        for col in range(5):
            logs_root.grid_columnconfigure(col, weight=1)

        logs_root.mainloop() #keep window open

    else:
        messagebox.showerror("Error", "Failed to retrieve fight logs.") #error popup

#original upload_avatar commented
#def upload_avatar(sock, username):
#    avatar_path = input("Enter the path to your avatar image (JPG): ").strip()
#    if not os.path.isfile(avatar_path):
#        print("[Client] File not found.")
#        return
#    with open(avatar_path, "rb") as f:
#        avatar_data = list(f.read())
#    request = {"action": "upload_avatar", "username": username, "filename": os.path.basename(avatar_path), "avatar_data": avatar_data}
#    response = send_request(sock, request)
#    print(f"[Client] {response.get('message')}")

def upload_avatar(sock, username):
    avatar_path = filedialog.askopenfilename(title="Select Avatar", filetypes=[("JPG files", "*.jpg"), ("All files", "*.*")]) #file chooser
    if not avatar_path:
        return #cancel
    if not os.path.isfile(avatar_path):
        messagebox.showerror("Error", "File not found") #file missing
        return
    with open(avatar_path, "rb") as f:
        avatar_data = list(f.read()) #read bytes
    request = {"action": "upload_avatar", "username": username, "filename": os.path.basename(avatar_path), "avatar_data": avatar_data} #server request
    response = send_request(sock, request)
    messagebox.showinfo("Upload Avatar", response.get("message")) #feedback

def view_active_gamer_info(sock):
    request = {"action": "get_active_gamers"} #request
    response = send_request(sock, request)
    active_gamers = response.get("active_users")

    active_root = tk.Toplevel() #popup
    active_root.title("Active Gamers")

    headers = ["Active User:", "Sword", "Shield", "Slaying-Potion", "Healing-Potion", "Lives"]

    for row, (username, stats) in enumerate(active_gamers.items(), start=1):
        tk.Label(active_root, text=username, borderwidth=2, relief="ridge", width=15).grid(row=row, column=0, sticky="nsew")
        tk.Label(active_root, text=stats["sword"], borderwidth=2, relief="ridge", width=15).grid(row=row, column=1, sticky="nsew")
        tk.Label(active_root, text=stats["shield"], borderwidth=2, relief="ridge", width=15).grid(row=row, column=2, sticky="nsew")
        tk.Label(active_root, text=stats["slaying_potion"], borderwidth=2, relief="ridge", width=15).grid(row=row, column=3, sticky="nsew")
        tk.Label(active_root, text=stats["healing_potion"], borderwidth=2, relief="ridge", width=15).grid(row=row, column=4, sticky="nsew")
        tk.Label(active_root, text=stats["lives"], borderwidth=2, relief="ridge", width=15).grid(row=row, column=5, sticky="nsew")

    active_root.mainloop() #keep window open
    
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #udp socket

    root = tk.Tk()
    root.withdraw() #hide root

    username = login(sock) #call login

    action_root = tk.Toplevel() #main action window
    action_root.title("Choose an action:")
    action_root.geometry('300x250')
    action_root.configure(bg="white")
    
    tk.Button(action_root, text="Assign Strengths", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: assign_strengths(sock, username)).pack(pady=5, padx=2)
    tk.Button(action_root, text="Upload Avatar", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: upload_avatar(sock, username)).pack(pady=5, padx=2)
    tk.Button(action_root, text="View Active Users", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: view_active_users(sock)).pack(pady=5, padx=2)
    tk.Button(action_root, text="Send Fight Request", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: send_fight_request(sock, username)).pack(pady=5, padx=2)
    tk.Button(action_root, text="View Fight Logs", activebackground="darkblue", 
              activeforeground="white", fg="darkblue", bg="white", command=lambda: view_fight_logs(sock)).pack(pady=5, padx=2)
    tk.Button(action_root, text="Quit", activebackground="red", 
              activeforeground="white", fg="red", bg="white", command=action_root.destroy).pack(pady=5, padx=2) #close action window
        
    action_root.mainloop() #keep window open
    sock.close() #close socket
    
if __name__ == "__main__":
    main()
