def start_menu():
    """Keyboard-driven interactive selection menu."""
    print("\n" + "="*40)
    print("      AI AGENT DEBATE SYSTEM")
    print("="*40)
    print("Topic: Do social media algorithms do more harm to democratic discourse than good?")
    print("-"*40)
    print("1. Start Debate")
    print("2. Export Last Session to README")
    print("3. Exit")
    print("="*40)
    choice = input("Select an option: ")
    
    return choice
