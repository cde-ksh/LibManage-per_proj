from backend.upload_file import get_file, get_destination
from backend.put_to_respective_folder import put_file

def main():
    file_path = get_file()

    destination = get_destination()

    moved_file = put_file(file_path, destination)

    print(f"File moved to: {moved_file}")


if __name__ == "__main__":
    main()