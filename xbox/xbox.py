from inputs import get_gamepad

def main():
    print("Lecture des événements de la manette (Ctrl+C pour arrêter)...")
    while True:
        events = get_gamepad()
        print(events)
        for event in events:
            # Joystick gauche: ABS_X (gauche/droite), ABS_Y (haut/bas)
            # Joystick droit : ABS_RX, ABS_RY
            # Valeurs typiques: -32768 à 32767 ou 0 à 65535 selon le driver
            if event.ev_type == "Absolute":
                if event.code in ("ABS_X", "ABS_Y", "ABS_RX", "ABS_RY"):
                    print(f"{event.code} = {event.state}")
            elif event.ev_type == "Key":
                # Boutons (A, B, X, Y, etc.)
                print(f"{event.code} = {event.state}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArrêt du script.")
