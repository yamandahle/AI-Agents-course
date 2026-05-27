def start_menu():
    """Keyboard-driven interactive selection menu."""
    print("\n" + "="*40)
    print("      AI AGENT DEBATE SYSTEM")
    print("="*40)
    print("Topic: Do social media algorithms do more harm to democratic discourse than good?")
    print("-"*40)
    print("1. Start Debate")
    print("2. Exit")
    print("="*40)
    choice = input("Select an option: ")
    
    # Map '2' to Exit for consistency with the new simplified menu
    if choice == "2":
        return "3"
    return choice
