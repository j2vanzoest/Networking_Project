import socket
import json
import os

SERVER_ADDRESS = ("127.0.0.1", 21000)
BUFFER_SIZE = 4096

def send_request(sock, request):
    sock.sendto(json.dumps(request).encode(), SERVER_ADDRESS)
    response_data, _ = sock.recvfrom(BUFFER_SIZE)
    return json.loads(response_data.decode())

def login(sock):
    username = input("Enter your username (A, B, C, D): ").strip()
    password = input("Enter your password: ").strip()
    request = {
        "action": "login",
        "username": username,
        "password": password
    }
    response = send_request(sock, request)
    if response.get("status") == "success":
        print(f"[Client] Login successful for {username}")
        return username
    else:
        print(f"[Client] Login failed: {response.get('message')}")
        return None

def assign_strengths(sock, username):
    print("Assign your strengths (total must equal 10, each between 0 and 3):")
    strengths = {}
    total = 0
    for item in ["sword", "shield", "slaying_potion", "healing_potion"]:
        while True:
            try:
                value = int(input(f"{item}: "))
                if 0 <= value <= 3:
                    strengths[item] = value
                    total += value
                    break
                else:
                    print("Value must be between 0 and 3.")
            except ValueError:
                print("Please enter a valid integer.")
    if total != 10:
        print("[Client] Invalid total strength. Must equal 10.")
        return
    request = {
        "action": "assign_strengths",
        "username": username,
        "strengths": strengths
    }
    response = send_request(sock, request)
    print(f"[Client] {response.get('message')}")

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

def get_active_users(sock, username):
    request = {
        "action": "get_active_users",
        "username": username
    }
    response = send_request(sock, request)
    if response.get("status") == "success":
        print("[Client] Active users:")
        for user in response.get("active_users", []):
            print(f"- {user}")
    else:
        print(f"[Client] Failed to get active users: {response.get('message')}")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    username = None
    while not username:
        username = login(sock)
    while True:
        print("\nChoose an action:")
        print("1. Assign strengths")
        print("2. Upload avatar")
        print("3. View active users")
        print("4. Quit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            assign_strengths(sock, username)
        elif choice == "2":
            upload_avatar(sock, username)
        elif choice == "3":
            get_active_users(sock, username)
        elif choice == "4":
            print("[Client] Exiting...")
            break
        else:
            print("[Client] Invalid choice. Try again.")
    sock.close()

if __name__ == "__main__":
    main()
