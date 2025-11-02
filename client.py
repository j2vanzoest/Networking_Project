import socket
import json
import tkinter as tk

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
    
    request = {"action": "login", "username": username, "password": password}
    response = send_request(sock, request)
    if response.get("status") == "success":
        print("[Client] Login successful!")
        return username
    else:
        print("[Client] Login failed.")
        return None

def assign_strengths(sock, username):
    print("Assign your strengths (total must be 10, max 3 per item):")
    try:
        sword = int(input("Sword: "))
        shield = int(input("Shield: "))
        slaying_potion = int(input("Slaying Potion: "))
        healing_potion = int(input("Healing Potion: "))
    except ValueError:
        print("[Client] Invalid input.")
        return
    strengths = {
        "sword": sword,
        "shield": shield,
        "slaying_potion": slaying_potion,
        "healing_potion": healing_potion
    }
    request = {"action": "assign_strengths", "username": username, "strengths": strengths}
    response = send_request(sock, request)
    print(f"[Client] {response.get('message')}")

def view_active_users(sock):
    request = {"action": "get_active_users"}
    response = send_request(sock, request)
    print("[Client] Active users:", response.get("active_users"))

def send_fight_request(sock, username):
    boss = input("Enter the username of the gamer you want to fight: ").strip()
    item = input("Choose item (sword/slaying_potion): ").strip()
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
        print("\nMenu:")
        print("1. Assign strengths")
        print("2. View active users")
        print("3. Fight another gamer")
        print("4. View fight logs")
        print("5. View full info of active gamers")
        print("6. Quit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            assign_strengths(sock, username)
        elif choice == "2":
            view_active_users(sock)
        elif choice == "3":
            send_fight_request(sock, username)
        elif choice == "4":
            view_fight_logs(sock)
        elif choice == "5":
            view_active_gamer_info(sock)
        elif choice == "6":
            print("[Client] Goodbye!")
            break
        else:
            print("[Client] Invalid choice.")

if __name__ == "__main__":
    main()
