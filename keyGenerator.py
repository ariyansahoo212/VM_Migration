import os

def generate_and_save_key(file_path):
    # Generate a 256-bit random key
    key_bytes = os.urandom(32)

    # Convert the key to a hexadecimal string
    key_hex = key_bytes.hex()

    # Write the key to the file
    with open(file_path, 'w') as file:
        file.write(key_hex)

    print("Generated 256-bit hexadecimal key:", key_hex)
    return key_hex

# Specify the file path
key_file_path = r"C:\Users\aryan\Downloads\New folder\key.txt"

# Generate and save the key
generate_and_save_key(key_file_path)
