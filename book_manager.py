import json
import os

BOOKS_FILE = "books.json"
DEFAULT_FILIA = "Filia 21 (ul. Królewska) - dorośli"

def load_books():
    if not os.path.exists(BOOKS_FILE):
        return []
    with open(BOOKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_books(books):
    with open(BOOKS_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=4, ensure_ascii=False)

def add_book():
    url = input("Podaj URL książki: ").strip()
    name = input("Podaj nazwę książki (lub ENTER aby pominąć): ").strip()
    if not name:
        name = "Książka (domyślna nazwa)"

    books = load_books()
    if any(book["url"] == url for book in books):
        print("Ta książka jest już na liście.")
        return

    books.append({
        "url": url,
        "name": name,
        "filia_name": DEFAULT_FILIA
    })
    save_books(books)
    print("Dodano książkę.")

def remove_book():
    books = load_books()
    if not books:
        print("Brak książek do usunięcia.")
        return

    for i, book in enumerate(books, start=1):
        print(f"{i}. {book['name']} ({book['url']})")
    choice = input("Podaj numer książki do usunięcia: ")
    try:
        index = int(choice) - 1
        if 0 <= index < len(books):
            removed = books.pop(index)
            save_books(books)
            print(f"Usunięto: {removed['name']}")
        else:
            print("Nieprawidłowy numer.")
    except ValueError:
        print("Nieprawidłowy numer.")

def show_books():
    books = load_books()
    if not books:
        print("Brak zapisanych książek.")
        return
    for book in books:
        print(f"- {book['name']} ({book['url']}) - Filia: {book['filia_name']}")

def main():
    while True:
        print("\n--- MENEDŻER KSIĄŻEK ---")
        print("1. Dodaj książkę")
        print("2. Usuń książkę")
        print("3. Pokaż wszystkie")
        print("4. Wyjście")
        choice = input("Wybierz opcję: ")

        if choice == "1":
            add_book()
        elif choice == "2":
            remove_book()
        elif choice == "3":
            show_books()
        elif choice == "4":
            break
        else:
            print("Nieprawidłowy wybór.")

if __name__ == "__main__":
    main()
