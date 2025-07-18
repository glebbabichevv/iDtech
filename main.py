import sys
from recognizer import add_student, recognize, reset_db, reset_csv, reset_snapshots, pp

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py [add|recognize|reset]")
        sys.exit(1)

    import sys
    from recognizer import add_student

    if sys.argv[1] == "add":
        name = input("Enter name: ")
        class_name = input("Enter class: ")
        add_student.run(name, class_name)

    elif sys.argv[1] == "recognize":
        recognize.run()
    elif sys.argv[1] == "reset_db":
        reset_db.run()
    elif sys.argv[1] == "reset_csv":
        reset_csv.run()
    elif sys.argv[1] == "reset_snapshots":
        reset_snapshots.run()
    elif sys.argv[1] == "pp":
        pp.run()
    else:
        print("Unknown command. Use 'add', 'recognize' or 'reset db/csv/snapshots'.")
