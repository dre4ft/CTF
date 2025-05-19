import argparse
import hashlib

# Define the target hash
TARGET_HASH = "f30fc26aeb141acd27ef659374f8b2dde43922ea8b526d1018085f831fb35232"

def calculate_sha256(input_string):
    """Calculate the SHA256 hash of a given string."""
    return hashlib.sha256(input_string.encode()).hexdigest()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="enter your password or the file containing it")
    parser.add_argument("-s", "--string", type=str, help="password as a string ")
    parser.add_argument("-f", "--file", type=str, help="password as a file")
    
    # Parse arguments
    args = parser.parse_args()

    # Ensure either -s or -f is provided, but not both
    if not args.string and not args.file:
        print("Error: You must provide either a string with -s or a file with -f.")
        return
    if args.string and args.file:
        print("Error: You can only provide one of -s or -f, not both.")
        return

    # Calculate hash based on input
    if args.string:
        input_hash = calculate_sha256(args.string)
    elif args.file:
        try:
            with open(args.file, "r") as file:
                file_content = file.read()
                input_hash = calculate_sha256(file_content)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            return

    # Compare the hash and print the result
    if input_hash == TARGET_HASH:
        text = """
        Your balence is 1678565,78 DOGE



        congratulation! You found the flag of this CTF
        """
        print(text)
    else:
        print("Wrong input.")

if __name__ == "__main__":
    main()