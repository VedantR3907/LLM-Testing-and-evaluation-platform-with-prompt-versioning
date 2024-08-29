from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import os

load_dotenv()

# Use a valid key size for AES (256 bits)
key_hex = os.environ.get('ENCRYPTION_KEY')
key = bytes.fromhex(key_hex)

if len(key) != 32:
    raise ValueError("Key must be exactly 32 bytes long")

def encrypt_data(data, key):
    try:
        # Pad the data to meet block size requirements
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        # Initialize the AES cipher with the key and mode
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt the padded data
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted_data
    except Exception as e:
        return f"Encryption error: {str(e)}"

def decrypt_data(encrypted_data, key):
    try:
        # Initialize the AES cipher with the key and mode
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the encrypted data
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # Unpad the decrypted data
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

        return unpadded_data
    except Exception as e:
        return f"Decryption error: {str(e)}"
    

if __name__ == "__main__":
    # Original data (plaintext)
    original_data = b"Hello, this is a secret message!"

    # Encrypt the data
    encrypted_data = encrypt_data(original_data, key)
    print("Encrypted Data:", encrypted_data)

    decrypted_data = decrypt_data(encrypted_data, key)
    print("Decrypted Data:", decrypted_data.decode())
