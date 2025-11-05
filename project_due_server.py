import socket
import threading
import json
import os
import base64
import tkinter as tk
from tkinter import ttk, messagebox

SERVER_PORT = 21000
BUFFER_SIZE = 16384
AVATAR_FOLDER = "avatars"
FIGHT_SERVER_ADDRESS = ("127.0.0.1", 22000)

os.makedirs(AVATAR_FOLDER, exist_ok=True)

fight_logs = []

#GamerManager class manages all the gamer data and synchronization between threads
class GamerManager:
    def __init__(self):
        #Initialize all gamer states with default values
        self.gamers = {
            "A": {"password": "A", "lives": 2, "sword": -1, "shield": -1, "slaying_potion": -1, "healing_potion": -1, "avatar": None},
            "B": {"password": "B", "lives": 2, "sword": -1, "shield": -1, "slaying_potion": -1, "healing_potion": -1, "avatar": None},
            "C": {"password": "C", "lives": 2, "sword": -1, "shield": -1, "slaying_potion": -1, "healing_potion": -1, "avatar": None},
            "D": {"password": "D", "lives": 2, "sword": -1, "shield": -1, "slaying_potion": -1, "healing_potion": -1, "avatar": None}
        }
        self.lock = threading.Lock()

    #Return only active gamers (any alive and armed/with stats)
    def get_active_gamers(self):
        return {u: g for u, g in self.gamers.items() if g["lives"] > 0 and g["sword"] != -1}

    #Display gamer data in a popup table window
    def display_gamers(self):
        #Creates a hidden root window
        root = tk.Tk()
        root.title("Current Gamer States")

        #Setup a table using ttk Treeview
        tree = ttk.Treeview(root, columns=("password","lives","sword","shield","slaying_potion","healing_potion","avatar"), show="headings")

        #Set column headers
        for col in tree["columns"]:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=120, anchor="center")

        #Insert each gamer's info into the table
        for username, info in self.gamers.items():
            tree.insert("", "end", values=(info["password"], info["lives"], info["sword"], info["shield"],
                                           info["slaying_potion"], info["healing_potion"], info["avatar"]))
        tree.pack(padx=10, pady=10)

        ##Old print-based display, kept for reference
        ##print("\n[Server] Current Gamer States:")
        ##for username, info in self.gamers.items():
        ##    print(f"{username}: {info}")

#Send a request to the fight server via UDP
def send_fight_request_to_fight_server(request_data):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.sendto(json.dumps(request_data).encode(), FIGHT_SERVER_ADDRESS)
        response_data, _ = sock.recvfrom(BUFFER_SIZE)
        return json.loads(response_data.decode())
    except Exception as e:
        print(f"[Server] Error contacting fight server: {e}")
        return None

#Handle each incoming client request
def handle_request(sock, data, address, manager):
    try:
        request = json.loads(data.decode())  #Decode the JSON data from client
        action = request.get("action")  #Determine requested action
        username = request.get("username")
        print(f"[Server] Received '{action}' request from {username}")
        print(f"[Server] Processing action: {action}")

        #Login logic
        if action == "login":
            password = request.get("password")
            gamer = manager.gamers.get(username)
            if gamer and gamer["password"] == password and gamer["lives"] > 0:
                response = {"status": "success", "gamer": gamer}
                print(f"[Server] {username} authenticated.")
            elif gamer and gamer["password"] == password and gamer["lives"] <= 0:
                print(f"[Server] User {username} inactive (game over)")
                response = {"status": "inactive", "message": "User out of lives!"}
            else:    
                print(f"[Server] Rejected login for {username}")
                response = {"status": "fail", "message": "Invalid credentials"}

        #Assign strengths to a players attributes
        elif action == "assign_strengths":
            strengths = request.get("strengths")
            total = sum(strengths.values())
            if total != 10 or any(v > 3 or v < 0 for v in strengths.values()):
                response = {"status": "fail", "message": "Invalid strength assignment"}
                print(f"[Server] Strength assignment failed for {username}: {strengths}")
            else:
                print(f"[Server] Rejected login for {username}")
                with manager.lock:
                    manager.gamers[username].update(strengths)
                response = {"status": "success", "message": "Strengths assigned"}
                print(f"[Server] Strengths assigned for {username}")

        #Handle any avatar uploads
        elif action == "upload_avatar":
            filename = request.get("filename")
            avatar_data = request.get("avatar_data")
            try:
                avatar_bytes = bytes(avatar_data)

                #Create user-specific folder if missing
                user_folder = os.path.join(AVATAR_FOLDER, f"{username}'s Avatar")
                os.makedirs(user_folder, exist_ok=True)

                #Save the avatar to the user's folder
                avatar_path = os.path.join(user_folder, f"{username}.jpg")
                with open(avatar_path, "wb") as f:
                    f.write(avatar_bytes)

                #Update manager record
                manager.gamers[username]["avatar"] = f"{username}.jpg"
                response = {"status": "success", "message": f"Avatar uploaded to {user_folder}"}
                print(f"[Server] Avatar uploaded for {username} -> {avatar_path}")
            except Exception as e:
                response = {"status": "fail", "message": f"Avatar upload failed: {e}"}
                print(f"[Server] Error uploading avatar for {username}: {e}")

        #Handle downloading avatars from other users
        elif action == "get_avatar":
            target_user = request.get("username")
            avatar_path = manager.gamers.get(target_user, {}).get("avatar")
            user_folder = os.path.join(AVATAR_FOLDER, f"{target_user}'s Avatar")
            full_path = os.path.join(user_folder, avatar_path) if avatar_path else None

            if avatar_path and os.path.exists(full_path):
                with open(full_path, "rb") as f:
                    avatar_bytes = f.read()
                avatar_encoded = base64.b64encode(avatar_bytes).decode()
                response = {"status": "success", "avatar_data": avatar_encoded}
            else:
                response = {"status": "fail", "message": "Avatar not found or user invalid."}
                print(f"[Server] Avatar retrieval failed for target user: {target_user}")

        #Return all active usernames
        elif action == "get_active_users":
            active = list(manager.get_active_gamers().keys())
            response = {"status": "success", "active_users": active}
            if not active:
                print(f"[Server] Active user list is empty")
            else:
                print(f"[Server] Sent active user list to {username}")

        #Return all fight logs
        elif action == "get_fight_logs":
            response = {"status": "success", "logs": fight_logs}
            print(f"[Server] Sent fight logs to {username}")

        #Return detailed info about all active gamers
        elif action == "get_active_gamer_info":
            active = manager.get_active_gamers()
            response = {"status": "success", "gamers": active}
            print(f"[Server] Sent active gamer info to {username}")

        #Handle viewing user stats
        elif action == "get_stats":
            username = request.get("username")
            gamer = manager.gamers.get(username)

            if gamer:
                response = {"status": "success", "gamer": gamer}
                print(f"[Server] Sent stats for {username}")
            else:
                response = {"status": "fail", "message": "User not found"}     

        #Handle fight requests between two gamers
        elif action == "fight_request":
            boss = request.get("boss")
            item = request.get("fighting_item")
            strength = request.get("fighting_strength")

            if username not in manager.gamers or boss not in manager.gamers:
                response = {"status": "fail", "message": "Invalid usernames"}
                print(f"[Server] Fight request rejected: invalid usernames {username}, {boss}")
            else:
                requester_state = manager.gamers[username] 
                
                #Game-over check; Double checks any that died cannot play 
                if requester_state["lives"] <= 0:
                     response = {"status": "fail", "message": "You cannot fight. Game over!"}
                     sock.sendto(json.dumps(response).encode(), address)
                     return

                boss_state = manager.gamers[boss]

                #Ensure player has enough strength for the requested item
                if requester_state[item] < strength:
                    response = {"status": "fail", "message": "Not enough strength"}
                    print(f"[Server] Fight request rejected for {username}: insufficient strength for {item}")
                else:
                    #Prepare data for fight server
                    fight_data = {
                        "requester": username,
                        "boss": boss,
                        "fighting_item": item,
                        "fighting_strength": strength,
                        "requester_state": requester_state,
                        "boss_state": boss_state
                    }
                    result = send_fight_request_to_fight_server(fight_data)
                    if result:
                        with manager.lock:
                            manager.gamers[username].update(result["requester_update"])
                            manager.gamers[boss].update(result["boss_update"])
                            fight_logs.append(result["log_entry"])
                        response = {
                            "status": "success",
                            "message": f"Fight processed. Winner: {result['winner']}",
                            "updated_state": manager.gamers[username]
                        }
                        print(f"[Server] Fight confirmed between {username} and {boss}")
                        print(f"[Server] Sent updated state to {username}")
                    else:
                        response = {"status": "fail", "message": "Fight server error"}

        #Unknown action fallback
        else:
            response = {"status": "fail", "message": "Unknown action"}
            print(f"[Server] Unknown action received: {action}")

        #Sends response back to client
        sock.sendto(json.dumps(response).encode(), address)

        #Display gamer states in popup window
        manager.display_gamers()

    except Exception as e:
        print(f"[Server] Error handling request: {e}")

#Main entry point for the server
def main():
    manager = GamerManager()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", SERVER_PORT))
    print(f"[Server] RPG Game Server running on port {SERVER_PORT}")
    print("[Server] Waiting for client requests...")

    try:
        while True:
            data, address = sock.recvfrom(BUFFER_SIZE)  #Receive client message
            threading.Thread(target=handle_request, args=(sock, data, address, manager)).start()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
        print("[Server] Closing socket and cleaning up resources")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
