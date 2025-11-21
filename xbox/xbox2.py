from evdev import InputDevice, categorize, ecodes

# Adapter si ton event n'est pas event5
DEVICE_PATH = "/dev/input/event5"

def main():
    gamepad = InputDevice(DEVICE_PATH)
    print(f"Connecté à : {gamepad.name} ({DEVICE_PATH})")
    print("Lecture des événements (Ctrl+C pour arrêter)...")

    for event in gamepad.read_loop():
        # 1) On ignore les events de synchronisation
        if event.type == ecodes.EV_SYN:
            continue

        # 2) Joysticks / axes (EV_ABS)
        if event.type == ecodes.EV_ABS:
            absevent = categorize(event)
            code_name = ecodes.ABS[absevent.event.code]
            value = absevent.event.value
            # Tu verras des choses comme ABS_X, ABS_Y, ABS_RX, ABS_RY
            print(f"{code_name} = {value}")

        # 3) Boutons (EV_KEY)
        elif event.type == ecodes.EV_KEY:
            keyevent = categorize(event)
            code_name = ecodes.BTN[keyevent.scancode] if keyevent.scancode in ecodes.BTN else keyevent.scancode
            print(f"{code_name} = {keyevent.keystate}")  # 1 = press, 0 = release

if __name__ == "__main__":
    try:
        main()
    except PermissionError:
        print("Permission refusée. Relance ce script avec sudo :")
        print("  sudo python3 test_xbox_evdev.py")
    except KeyboardInterrupt:
        print("\nArrêt du script.")
