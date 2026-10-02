import os
import hashlib


def release_folder():
    """Returns release folder specified on pyproject.toml"""
    version = ""
    with open("pyproject.toml", "r") as project_file:
        lines = project_file.readlines()
        for line in lines:
            if line.startswith("version"):
                version = line.split('"')[-2]
    release_folder_name = "krux-v" + version
    print("Hashing binaries for:", release_folder_name)
    return release_folder_name


def calculate_sha256(file_path):
    """Calculate the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def finder(root_dir):
    """Yield raw (dirpath, filename) pairs."""
    for dirpath, _, filenames in sorted(os.walk(root_dir)):
        for filename in sorted(filenames):
            yield dirpath, filename


def find_bin_files(root_dir, extension=".bin"):
    """Find .bin files in root directory and its subdirectories."""
    print(f"\nDevice: SHA256 of {extension} file")
    for dirpath, filename in finder(root_dir):
        if filename.endswith(extension):
            file_path = os.path.join(dirpath, filename)
            sha256_hash = calculate_sha256(file_path)
            device_name = dirpath.split("/")[-1].split("_", 1)[-1]
            print(f"{device_name}: {sha256_hash}")


def find_ktool_files(root_dir):
    """Find ktool files under the release folder."""
    print("\nFlasher: SHA256 of ktool file")
    for dirpath, filename in finder(root_dir):
        if filename.startswith("ktool"):
            file_path = os.path.join(dirpath, filename)
            sha256_hash = calculate_sha256(file_path)
            print(f"{filename}: {sha256_hash}")


if __name__ == "__main__":
    root_directory = release_folder()
    find_bin_files(root_directory, extension=".bin")
    find_bin_files(root_directory, extension=".kfpkg")
    find_ktool_files(root_directory)
