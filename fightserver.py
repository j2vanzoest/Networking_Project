import socket
import threading
import json

FIGHT_SERVER_PORT = 22000
BUFFER_SIZE = 4096

fight_log = []
lock = threading.Lock()

def process_fight(data):
    requester = data["requester"]
    boss = data["boss"]
    item = data["fighting_item"]
    #requester_strength = requester_state.get(item, 0)
    #strength = requester_strength  # Use the actual strength from the requester's state

    requester_state = data["requester_state"]
    boss_state = data["boss_state"]
    # Extract strength from requester's state based on item
    strength = requester_state.get(item, 0)
    
    result = {
        "winner": "none",
        "requester_update": {},
        "boss_update": {},
        "log_entry": {}
    }

    if item == "sword":
        attacker_strength = requester_state["sword"]
        defender_strength = boss_state["shield"]
        attacker_life = requester_state["lives"]
        defender_life = boss_state["lives"]
    elif item == "slaying_potion":
        attacker_strength = requester_state["slaying_potion"]
        defender_strength = boss_state["healing_potion"]
        attacker_life = requester_state["lives"]
        defender_life = boss_state["lives"]
    else:
         print(f"[FightServer] Invalid item: {item}")
        return result  # Invalid item

    # Validate strength internally

    if attacker_strength <= 0:
        print(f"[FightServer] {requester} tried to use {item} with insufficient strength ({attacker_strength})")
        return result
        
    print(f"[FightServer] {requester} is using {item} with strength {attacker_strength}")

    # Apply game rules
    if defender_strength == attacker_strength:
        attacker_life -= 1
        defender_life -= 1
        attacker_strength -= 2
        defender_strength -= 2
        winner = "none"
    elif defender_strength < attacker_strength:
        attacker_life += 1
        defender_life -= 1
        attacker_strength -= (attacker_strength - defender_strength)
        defender_strength -= 0
        winner = requester
    else:
        attacker_life -= 1
        defender_life += 1
        attacker_strength -= attacker_strength
        defender_strength -= (defender_strength - attacker_strength)
        winner = boss

    # Clamp values
    attacker_strength = max(0, attacker_strength)
    defender_strength = max(0, defender_strength)
    attacker_life = max(0, attacker_life)
    defender_life = max(0, defender_life)

    # Update result
    result["winner"] = winner
    result["requester_update"] = {
        "lives": attacker_life,
        item: attacker_strength
    }
    result["boss_update"] = {
        "lives": defender_life,
        "shield" if item == "sword" else "healing_potion": defender_strength
    }
    result["log_entry"] = {
        "requester": requester,
        "boss": boss,
        "fighting_item": item,
        "fighting_strength": strength,
        "winner": winner
    }

    with lock:
        fight_log.append(result["log_entry"])

    return result

def handle_request(sock, data, address):
    try:
        request = json.loads(data.decode())
        print(f"[FightServer] Received fight request: {request}")
        result = process_fight(request)
        sock.sendto(json.dumps(result).encode(), address)
        print(f"[FightServer] Fight processed. Result: {result['winner']}")
    except Exception as e:
        print(f"[FightServer] Error: {e}")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", FIGHT_SERVER_PORT))
    print(f"[FightServer] Running on port {FIGHT_SERVER_PORT}")

    try:
        while True:
            data, address = sock.recvfrom(BUFFER_SIZE)
            threading.Thread(target=handle_request, args=(sock, data, address)).start()
    except KeyboardInterrupt:
        print("\n[FightServer] Shutting down...")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
