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

def login(sock):

    #login_root is the name of the pop-up window
    login_root = tk.Tk()
    #this line adds text to the top of the window as a title
    login_root.title("Simple RPG Game")
    login_root.geometry('500x500')

    #username = input("Enter your username: ").strip()
    #password = input("Enter your password: ").strip()
    #tk.Label is essentially just a text box
    tk.Label(login_root, text="Username:", font=("Helvetica")).pack(pady=5, padx=3)
    #Entry allows for user input, assigns ti variable ('username' in this case)
    username_entry = tk.Entry(login_root)
    #pady=5 and padx=3 just adds pixel padding to text box, 5 pixels on y axis and 3 on x 
    username_entry.pack(pady=5, padx=3)
    tk.Label(login_root, text="Password:", font=("Helvetica")).pack(pady=5, padx=3)
    password_entry= tk.Entry(login_root)
    password_entry.pack(pady=5, padx=3)

    def login_attempt():

        #get username and password from user
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        request = {"action": "login", "username": username, "password": password}
        response = send_request(sock, request)

        
        if response.get("status") == "success":
            #print("[Client] Login successful!")
            #return username

            #.confif just updates username, fg sets color of text, bg sets background
            status_label.config(text=f"Login successful. Welcome, {username}!", fg ="green", bg="lightblue")  

            #return control to main program
            login_root.destroy()
            
        else:
            #print("[Client] Login failed.")
            #return None
            status_label.config(text="Login failed. Try again.", fg = "white", bg="red")
            
    #adds a login button to physically click to run the login command
    tk.Button(login_root, text="Login", command = login_attempt).pack(pady=6, padx=2)
    tk.Button(login_root, text = "Quit", font=("Arial", 10), fg = "red", 
              activebackground="red", activeforeground="white", command=login_root.destroy).pack(pady=6, padx=2)

def assign_strengths(sock, username):

    def submit_strengths():
        try:
            sword = int(sword_entry.get())
            shield = int(shield_entry.get())
            slaying_potion = int(sp_entry.get())
            healing_potion = int(hp_entry.get())

            #validate ranges and total
            if any(x < 0 or x > 3 for x in [sword, shield, slaying_potion, healing_potion]) or \
               (sword + shield + slaying_potion + healing_potion != 10):
                raise ValueError

            strengths = {
                "sword": sword,
                "shield": shield,
                "slaying_potion": slaying_potion,
                "healing_potion": healing_potion
            }

            #send request if everything is valid
            request = {"action": "assign_strengths", "username": username, "strengths": strengths}
            response = send_request(sock, request)
            print(f"[Client] {response.get('message')}")

            strengths_root.destroy()  # Close window after successful submission

        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid inputs, try again!")

    #print("Assign your strengths (total must be 10, max 3 per item):")
    strengths_root = tk.Tk()

    tk.Label(text="Assign your strengths (total must equal 10, each between 0 and 3):", justify="left", 
             anchor="n", font=("Times", 14, 'bold'))
    
    tk.Label(strengths_root, text = "Sword strength:", font = ("Times", 8, "underline"), fg = "white", bg = "darkgreen")
    sword_entry = tk.Entry(strengths_root)
    sword_entry.pack()
    tk.Label(strengths_root, text = "Shield strength:", font = ("Times", 8, "underline"), fg = "white", bg = "darkgreen")
    shield_entry = tk.Entry(strengths_root)
    shield_entry.pack()
    tk.Label(strengths_root, text = "Slaying Potion strength:", font = ("Times", 8, "underline"), fg = "white", bg = "darkgreen")
    sp_entry = tk.Entry(strengths_root)
    sp_entry.pack()
    tk.Label(strengths_root, text = "Healing Potion strength:", font = ("Times", 8, "underline"), fg = "white", bg = "darkgreen")
    hp_entry = tk.Entry(strengths_root)
    hp_entry.pack()

    tk.Button(strengths_root, text="Submit", font = ("Times", 8, "bold"), command=submit_strengths, bg="white", fg="black").pack(pady=10)

    strengths_root.mainloop()
    
    
def view_active_users(sock):
    request = {"action": "get_active_users"}
    response = send_request(sock, request)
    #print("[Client] Active users:", response.get("active_users"))

    active_gamers = response.get("active_users")

    active_root = tk.Tk()
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
    
def send_fight_request(sock, username):

    #fight_root
    #boss = input("Enter the username of the gamer you want to fight: ").strip()
    #item = input("Choose item (sword/slaying_potion): ").strip()
    
    try:
        strength = int(input("Enter strength to use (0-3): ").strip())
    except ValueError:
        print("[Client] Invalid strength.")
        return

    request = {
        "action": "fight_request",
        "username": username,
        "boss": boss,
        "fighting_item": item,
        "fighting_strength": strength
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

def view_active_gamer_info(sock):
    request = {"action": "get_active_gamer_info"}
    response = send_request(sock, request)
    if response.get("status") == "success":
        print("\n[Client] Active Gamers Info:")
        print("{:<10} {:<6} {:<6} {:<15} {:<15} {:<6}".format(
            "Username", "Sword", "Shield", "Slaying Potion", "Healing Potion", "Lives"
        ))
        for user, info in response.get("gamers", {}).items():
            print("{:<10} {:<6} {:<6} {:<15} {:<15} {:<6}".format(
                user, info["sword"], info["shield"],
                info["slaying_potion"], info["healing_potion"], info["lives"]
            ))
    else:
        print("[Client] Failed to retrieve gamer info.")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    username = login(sock)
    if not username:
        return

    while True:

        action_root = tk.Tk()
        action_root.title("Choose an action:", fg = 'darkblue', bg = 'white')
        
        #first parameter ID's root button belongs to, 'active' params affect button when clicked, fg/bg are base colors for text/background respectively
        tk.Button(action_root, text = "Assign Strengths", activebackground="darkblue", 
                  activeforeground="white", fg = "darkblue", bg = "white", command = assign_strengths(sock, username)).pack(pady =5, padx=2)
        tk.Button(action_root, text = "Upload Avatar", activebackground="darkblue", 
                  activeforeground="white", fg = "darkblue", bg = "white", command = upload_avatar(sock, username)).pack(pady =5, padx=2)
        tk.Button(action_root, text = "View Active Users", activebackground="darkblue", 
                  activeforeground="white", fg = "darkblue", bg = "white", command = get_active_users(sock, username)).pack(pady =5, padx=2)
        tk.Button(action_root, text = "Quit", activebackground="red", 
                  activeforeground="white", fg = "red", bg = "white", command = action_root.destroy).pack(pady =5, padx=2)
        
        action_root.destroy()
        
        
        #print("\nMenu:")
        #print("1. Assign strengths")
        #print("2. View active users")
        #print("3. Fight another gamer")
        #print("4. View fight logs")
        #print("5. View full info of active gamers")
        #print("6. Quit")
        #choice = input("Enter your choice: ").strip()

        #if choice == "1":
            #assign_strengths(sock, username)
        #elif choice == "2":
            #view_active_users(sock)
        #elif choice == "3":
            #send_fight_request(sock, username)
        #elif choice == "4":
            #view_fight_logs(sock)
        #elif choice == "5":
            #view_active_gamer_info(sock)
        #elif choice == "6":
            #print("[Client] Goodbye!")
            #break
        #else:
            #print("[Client] Invalid choice.")

if __name__ == "__main__":
    main()
