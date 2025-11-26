from inputs import get_gamepad
import time



def read_gamepad():
    """Retourne un dictionnaire avec les valeurs utiles de la manette."""
    events = get_gamepad()
    values = {}
    for event in events:
        if event.ev_type == "Absolute":
            if event.code in ("ABS_X", "ABS_Y", "ABS_RX", "ABS_RY"):
                values[event.code] = event.state
        elif event.ev_type == "Key":
            values[event.code] = event.state
    return values


if __name__ == "__main__":
    try:
        read_gamepad()
    except KeyboardInterrupt:
        print("\nArrêt du script.")
