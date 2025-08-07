import typer
import json
import random
from pathlib import Path
from typing_extensions import Annotated

# --- Configuration ---
# The name of the JSON file where quotes are stored.
# Using Path from pathlib makes it work across different operating systems.
DATA_FILE = Path("quotes.json")

# --- Helper Functions ---

def load_quotes() -> list[dict]:
    """
    Loads the list of quotes from the JSON file.
    Handles file creation and UTF-8 encoding for macrons.
    """
    if not DATA_FILE.exists():
        # If the file doesn't exist, create it with an empty list.
        # This prevents errors on the first run.
        save_quotes([])
        return []
    
    # It's crucial to specify encoding='utf-8' to correctly read
    # special characters like macrons (ā, ē, ī, ō, ū).
    with DATA_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or corrupted, return an empty list.
            return []

def save_quotes(quotes: list[dict]):
    """
    Saves the list of quotes back to the JSON file.
    Handles UTF-8 encoding and pretty-printing.
    """
    # Use encoding='utf-8' to write macrons correctly.
    # 'ensure_ascii=False' is required for json.dump to output non-ASCII chars.
    # 'indent=2' makes the JSON file human-readable.
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(quotes, f, indent=2, ensure_ascii=False)

def get_next_id(quotes: list[dict]) -> int:
    """Calculates the next unique ID for a new quote."""
    if not quotes:
        return 1
    # Find the highest existing ID and add 1
    return max(q["id"] for q in quotes) + 1


# --- Typer Application Setup ---

# This creates the main Typer application object.
# We can add commands to this object.
app = typer.Typer(
    help="A simple CLI game for learning Latin quotes.",
    no_args_is_help=True
)

# --- Typer Commands ---

@app.command()
def play(
    rounds: Annotated[int, typer.Option(help="Number of questions to ask.")] = 5
):
    """
    Play the Latin quiz game.
    """
    quotes = load_quotes()
    if not quotes:
        print("❌ No quotes found in the database. Add some with the 'add' command first!")
        raise typer.Exit()

    print("--- 🏛️ Welcome to the Latin Quote Quiz! ---")
    score = 0
    
    # Ensure we don't ask for more rounds than available quotes
    num_rounds = min(rounds, len(quotes))
    
    # Get a random sample of quotes for the game session
    game_quotes = random.sample(quotes, num_rounds)

    for i, quote in enumerate(game_quotes):
        print(f"\n--- Round {i + 1} of {num_rounds} ---")
        
        # Randomly choose one of the three game modes
        game_modes = ["translate", "author", "work"]
        chosen_mode = random.choice(game_modes)

        if chosen_mode == "translate":
            question = f"Translate this quote to English:\n\n> {quote['latin_text']}"
            answer = quote['english_translation']
        elif chosen_mode == "author":
            question = f"Who is the author of this quote?\n\n> {quote['latin_text']}"
            answer = quote['author']
        else: # chosen_mode == "work"
            question = f"What work is this quote from?\n\n> {quote['latin_text']}"
            answer = quote['work']

        print(question)
        user_input = input("\nYour answer: ")

        # Simple check for correctness (case-insensitive)
        if user_input.strip().lower() == answer.strip().lower():
            print(f"✅ Correct! The answer is: {answer}")
            score += 1
        else:
            print(f"❌ Incorrect. The correct answer was: {answer}")

    print("\n--- 🏆 Game Over! ---")
    print(f"Your final score: {score}/{num_rounds}")


@app.command()
def add():
    """
    Add a new quote to the database.
    """
    print("--- ✍️ Add a New Latin Quote ---")
    print("Please provide the following details (press Enter to skip a field).")

    latin_text = typer.prompt("Latin Text")
    english_translation = typer.prompt("English Translation")
    author = typer.prompt("Author")
    work = typer.prompt("Work")
    notes = typer.prompt("Notes (optional)")

    new_quote = {
        "latin_text": latin_text,
        "english_translation": english_translation,
        "author": author,
        "work": work,
        "notes": notes,
    }

    quotes = load_quotes()
    new_quote["id"] = get_next_id(quotes)
    quotes.append(new_quote)
    save_quotes(quotes)

    print(f"\n✨ Quote added successfully with ID: {new_quote['id']}")


@app.command(name="list")
def list_quotes():
    """
    List all quotes in the database.
    """
    quotes = load_quotes()
    if not quotes:
        print("📚 The database is empty.")
        return

    print("--- 📖 All Quotes in Database ---")
    for quote in quotes:
        print(f"\nID: {quote['id']}")
        print(f"  Latin: {quote.get('latin_text', 'N/A')}")
        print(f"  English: {quote.get('english_translation', 'N/A')}")
        print(f"  Author: {quote.get('author', 'N/A')}")
        print(f"  Work: {quote.get('work', 'N/A')}")
        if quote.get('notes'):
            print(f"  Notes: {quote.get('notes')}")
    print("------------------------------")


if __name__ == "__main__":
    # This makes the script runnable.
    # Typer will process the command-line arguments.
    app()

