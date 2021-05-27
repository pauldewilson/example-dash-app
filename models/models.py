def print_current_step(message="", final=False):
    """
    Prints the current step to the screen to inform user of progress
    """
    print("-" * 100)
    if not final:
        print(message + "...")
    elif final:
        print(message)
        print("-" * 100)