import sys
from backend.upload_file import get_file, get_destination
from backend.put_to_respective_folder import put_file


def organize(file_path, destination=None):
    """
    Programmatic entry point for organizing a single file.

    :param file_path: Path to the source file to organize.
    :param destination: Optional explicit destination directory.
    :return: Path to the moved destination file.
    """
    return put_file(file_path, destination)


def main():
    file_path = get_file()
    destination = get_destination()
    moved_file = put_file(file_path, destination)
    print(f"File moved to: {moved_file}")
    return moved_file


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, FileExistsError, ValueError) as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"Unexpected error: {err}", file=sys.stderr)
        sys.exit(1)
