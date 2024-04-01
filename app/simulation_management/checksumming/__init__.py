import hashlib

def calculate_checksum(file_path):
    """Calculate the SHA-256 checksum of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def combine_checksums(file_paths):
    """Combine the checksums of a list of files."""
    combined_checksum = ""
    for file_path in file_paths:
        checksum = calculate_checksum(file_path)
        combined_checksum += checksum  # Concatenate checksums
    return combined_checksum