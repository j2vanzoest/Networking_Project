import socket
import threading
import json
import os

SERVER_PORT = 21000
FIGHT_SERVER_ADDRESS = ("127.0.0.1", 22000)
BUFFER_SIZE = 4096
AVATAR_FOLDER = "avatars"

os.makedirs(AVATAR_FOLDER, exist_ok=True)

class GamerManager:
    def __init__(self):
        self.gamers = {
            "A": {"password": "A", "lives": 2, "sword": -1, "shield": -1, "slaying_potion": -1, "healing_potion": -1, "avatar": None},
            "B": {"password": "B", "lives": 2, "sword": -1, "shield": -1, "slaying_potion": -1, "healing_potion": -1, "avatar": None},
            "C": {"password": "C", "lives": 2, "sword": -1, "shield": -1, "slaying_potion": -1, "healing_potion": -1, "avatar": None},
            "D": {"password": "D", "lives": 2, "sword": -1, "shield": -1, "slaying_potion": -1, "healing_potion": -1, "avatar": None}
        }
        self.fight_requests = []
        self.lock = threading.Lock()

    def get_active_gamers(self):
        return {u: g for u, g in self.gamers.items() if g["lives"] > 0 and g["sword"] != -1}

    def display_gamers(self):
        print("\n[Server] Current Gamer States:")
        for username, info in self.gamers.items():
            print(f"{username}: {info}")

def send_to_fight_server(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(request).encode(), FIGHT_SERVER_ADDRESS)
    response_data, _ = sock.recvfrom(BUFFER_SIZE)
    return json.loads(response_data.decode())

def handle_request(sock, data, address, manager):
    try:
        request = json.loads(data.decode())
        action = request.get("action")
        username = request.get("username")
        print(f"[Server] Received '{action}' request from {username}")

        if action == "login":
            password = request.get("password")
            gamer = manager.gamers.get(username)
            if gamer and gamer["password"] == password:
                response = {"status": "success", "gamer": gamer}
                print(f"[Server] {username} authenticated.")
            else:
                response = {"status": "fail", "message": "Invalid credentials"}

        elif action == "assign_strengths":
            strengths = request.get("strengths")
            total = sum(strengths.values())
            if total != 10 or any(v > 3 or v < 0 for v in strengths.values()):
                response = {"status": "fail", "message": "Invalid strength assignment"}
            else:
                with manager.lock:
                    manager.gamers[username].update(strengths)
                response = {"status": "success", "message": "Strengths assigned"}
                print(f"[Server] Strengths assigned for {username}")

        elif action == "get_active_users":
            active = list(manager.get_active_gamers().keys())
            response = {"status": "success", "active_users": active}

        elif action == "upload_avatar":
            filename = request.get("filename")
            avatar_data = request.get("avatar_data")
            with open(os.path.join(AVATAR_FOLDER, f"{username}.jpg"), "wb") as f:
                f.write(bytes(avatar_data))
            manager.gamers[username]["avatar"] = f"{username}.jpg"
            response = {"status": "success", "message": "Avatar uploaded"}
            print(f"[Server] Avatar uploaded for {username}")

        elif action == "fight_request":
            boss = request.get("boss")
            item = request.get("fighting_item")
            strength = request.get("fighting_strength")

            with manager.lock:
                requester_state = manager.gamers[username]
                boss_state = manager.gamers[boss]

            if requester
