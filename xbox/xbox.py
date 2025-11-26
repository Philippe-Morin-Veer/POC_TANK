from inputs import get_gamepad
import time

def stop_tank():
    # Ici tu mets ton code pour arrêter les moteurs
    print("Tank arrêté (sécurité).")

def main():
    print("Lecture des événements de la manette (Ctrl+C pour arrêter)...")
    try:
        while True:
            try:
                events = get_gamepad()
            except Exception as e:
                print("Manette non détectée :", e)
                stop_tank()
                time.sleep(1)  # évite de spammer
                continue

            for event in events:
                if event.ev_type == "Absolute":
                    if event.code in ("ABS_X", "ABS_Y", "ABS_RX", "ABS_RY"):
                        print(f"{event.code} = {event.state}")
                        # Ici tu traduis en vitesse moteur
                elif event.ev_type == "Key":
                    print(f"{event.code} = {event.state}")
                    # Boutons → actions

    except KeyboardInterrupt:
        print("\nArrêt du script.")
        stop_tank()  # sécurité à la fermeture