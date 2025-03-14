import random

def guess_number():
    # Randomly select a number between 1 and 100
    target_number = random.randint(1, 100)
    print("I have selected a number between 1 and 100. Try to guess it!")

    previous_guess = None
    while True:
        # Get the user's guess
        guess = int(input("Enter your guess: "))
        
        # Check if the guess is correct
        if guess == target_number:
            print(f"Congratulations! You guessed the correct number: {target_number}")
            break
        
        # Give feedback (warmer/colder)
        if previous_guess is not None:
            if abs(guess - target_number) < abs(previous_guess - target_number):
                print("Warmer!")
            else:
                print("Colder!")
        else:
            print("Start guessing!")
        
        # Update previous guess
        previous_guess = guess

# Run the guessing game
guess_number()
input("press to exit")