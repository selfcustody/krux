# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This script batch signs firmware releases through air-gapped interaction with
# a Krux signing device.
# Load a 24 words mnemonic in testnet to sign the firmware hashes as messages.

import os
import cv2
import hashlib
from io import StringIO
import base64
from qrcode import QRCode
import subprocess

DEVICES = [
    "maixpy_m5stickv",
    "maixpy_amigo_ips",
    "maixpy_amigo_tft",
    "maixpy_bit",
    "maixpy_dock",
    "maixpy_yahboom",
]


def release_folder():
    """Returns release folder specified on pyproject.toml"""
    with open("pyproject.toml", "r") as project_file:
        lines = project_file.readlines()
        for line in lines:
            if line.startswith("version"):
                version = line.split('"')[-2]
    release_folder_name = "krux-v" + version
    print("Signing firmwares in:", release_folder_name)
    return release_folder_name


def print_qr_code(data):
    """Prints ascii QR code"""
    qr_code = QRCode()
    qr_code.add_data(data)
    qr_string = StringIO()
    qr_code.print_ascii(out=qr_string, invert=True)
    print(qr_string.getvalue())


def scan():
    """Opens a scan window and uses cv2 to detect and decode a QR code, returning its data"""
    vid = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    qr_data = None
    while True:
        # Capture the video frame by frame
        _, frame = vid.read()
        qr_data, _, _ = detector.detectAndDecode(frame)
        if len(qr_data) > 0:
            break
        # Display the resulting frame
        cv2.imshow("frame", frame)
        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()
    return qr_data


def verify(file_to_verify, key_to_verify, signature_to_verify):
    """Uses openssl to verify the signature and public key"""
    print("Verifying signature of",file_to_verify.split("/")[1] )
    verification = subprocess.run(
        "openssl sha256 <%s -binary | openssl pkeyutl -verify -pubin -inkey %s -sigfile %s"
        % (file_to_verify, key_to_verify, signature_to_verify),
        shell=True,
        capture_output=True,
        text=True,
        check=True
    )
    print(verification.stdout)


# Main routine
folder = release_folder()
for device in DEVICES:
    print("Signing", device)
    file_name = os.path.join(folder, device, "firmware.bin")
    hash_string = ""
    try:
        with open(file_name, "rb") as f:
            sig_bytes = f.read()  # read file as bytes
            hash_string = hashlib.sha256(sig_bytes).hexdigest()
    except:
        print("Unable to read target file")
    # Prints the hash of the file
    print("Hash of", file_name, ":")
    print(hash_string + "\n")

    # Prints the QR code
    print_qr_code(hash_string)

    # Scans the signature QR code
    _ = input("Press enter to scan signature")
    signature = scan()
    binary_signature = base64.b64decode(signature.encode())
    # Prints signature
    print("Signature:", signature)
    # Saves a signature file
    signature_file = os.path.join(folder, device, "firmware.bin.sig")

    print("Saving a signature file:", signature_file, "\n\n")
    with open(signature_file, "wb") as f:
        f.write(binary_signature)

# Verify signatures
PUBLIC_KEY_FILE = "odudex.PEM"  # "selfcustody.PEM"
for device in DEVICES:
    file_name = os.path.join(folder, device, "firmware.bin")
    signature_file = os.path.join(folder, device, "firmware.bin.sig")
    verify(file_name, PUBLIC_KEY_FILE, signature_file)
