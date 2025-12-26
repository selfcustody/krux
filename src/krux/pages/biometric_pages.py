# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

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

import time
import os
import struct
import hashlib
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
)
from ..krux_settings import t, Settings
from ..settings import store
from ..display import FONT_HEIGHT
from ..themes import theme
from ..input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH

# Constants for storage
try:
    os.stat("/flash")
    BIOMETRIC_PATH_PREFIX = "/flash/biometric"
except:
    BIOMETRIC_PATH_PREFIX = "biometric"

BIOMETRIC_DIR = BIOMETRIC_PATH_PREFIX
QR_DATA_FILE = BIOMETRIC_PATH_PREFIX + "/qr.dat"

class BiometricRegistration(Page):
    """Class to manage biometric registration"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        try:
            if not os.path.exists(BIOMETRIC_DIR):
                os.makedirs(BIOMETRIC_DIR)
        except:
            pass

    def _enable_biometric_unlock(self):
        """Auto-enable biometric unlock setting"""
        if not Settings().security.biometric_unlock:
            Settings().security.biometric_unlock = True
            store.save_settings()

    def _get_registration_count(self, filename):
        """Returns 1 if file exists, 0 otherwise (since we overwrite)"""
        try:
            os.stat(filename)
            return 1
        except:
            return 0

    def manage(self):
        """Manage biometric registrations"""
        while True:
            qr_count = self._get_registration_count(QR_DATA_FILE)
            
            items = [
                (t("({}) Add QR Code").format(qr_count), self.register_qr),
                (t("Clear All"), self.clear_all),
            ]
            
            # Show status
            status_text = ""
            if self._file_exists(QR_DATA_FILE): 
                status_text += "QR "
            
            if status_text:
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(t("Registered: ") + status_text)
                time.sleep(1)

            submenu = Menu(self.ctx, items)
            index, status = submenu.run_loop()
            if index == submenu.back_index:
                return MENU_CONTINUE

    def _file_exists(self, path):
        try:
            os.stat(path)
            return True
        except:
            return False
    
    def _validate_biometric_data(self, data, min_size=1, max_size=10240):
        """Validate biometric data before storing"""
        if len(data) < min_size:
            raise ValueError("Data too small")
        if len(data) > max_size:
            raise ValueError("Data too large")
        
        # Check for all zeros or repeated patterns
        if data == b'\x00' * len(data):
            raise ValueError("Invalid data pattern")
        
        # Simple entropy check for binary data
        if min_size > 1:  # Only check for non-text data
            unique_bytes = len(set(data))
            if unique_bytes < len(data) * 0.05:  # At least 5% unique bytes
                raise ValueError("Low entropy data")
        
        return True
    
    
    def _initialize_camera(self):
        """Initialize camera and return success status"""
        try:
            print("[DEBUG] Checking camera availability...")
            
            # Check if camera module exists in context
            if not hasattr(self.ctx, 'camera'):
                print("[ERROR] No 'camera' attribute in ctx")
                return False
            
            # Check if camera object exists
            if self.ctx.camera is None:
                print("[ERROR] ctx.camera is None")
                return False
            
            print("[DEBUG] Camera object found, attempting initialization...")
            
            # Try to initialize the camera
            try:
                self.ctx.camera.initialize_run()
                print("[DEBUG] Camera initialized successfully")
                return True
            except AttributeError as e:
                print("[ERROR] Camera initialization failed - AttributeError:", e)
                return False
            except Exception as e:
                print("[ERROR] Camera initialization failed:", e)
                return False
                
        except Exception as e:
            print("[ERROR] Camera check failed:", e)
            return False
    

    def register_qr(self):
        """Register a QR code using QRCodeCapture"""
        print("[DEBUG] Starting QR registration")
        
        from .qr_capture import QRCodeCapture
        
        # Use the standard QR code capture system
        qr_capture = QRCodeCapture(self.ctx)
        data, qr_format = qr_capture.qr_capture_loop()
        
        if data is None:
            self.flash_text(t("Cancelled"))
            return MENU_CONTINUE
        
        # Convert to string if bytes
        if isinstance(data, bytes):
            try:
                qr_data = data.decode('utf-8')
            except:
                qr_data = str(data)
        else:
            qr_data = str(data)
        
        print("[DEBUG] QR captured:", qr_data[:50])
        
        # Show captured data for confirmation using standard Krux prompt
        # Display QR content in a more readable format
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            t("QR content:"),
            FONT_HEIGHT,
            theme.fg_color,
            theme.bg_color
        )
        # Display the QR data text using draw_hcentered_text for better readability
        self.ctx.display.draw_hcentered_text(
            qr_data,
            FONT_HEIGHT * 3,
            theme.fg_color,
            theme.bg_color
        )
        
        # Use standard Krux prompt
        if not self.prompt(t("Register this QR?"), FONT_HEIGHT * 6):
            # User said No - retry
            return self.register_qr()
        
        # Save the QR data
        try:
            # Convert to bytes if it's a string
            if isinstance(qr_data, str):
                data_bytes = qr_data.encode('utf-8')
            else:
                data_bytes = qr_data
            
            self._validate_biometric_data(data_bytes, min_size=1, max_size=4096)
            
            # Add salt and hash
            salt = os.urandom(16)
            data_hash = hashlib.sha256(salt + data_bytes).digest()
            
            with open(QR_DATA_FILE, "wb") as f:
                # Store with format identifier (0x02 = QR text)
                f.write(struct.pack('<B16s32s', 0x02, salt, data_hash))
                f.write(struct.pack('<I', len(data_bytes)))
                f.write(data_bytes)
            
            self._enable_biometric_unlock()
            
            # Show success with first few chars
            preview = qr_data[:20] + ("..." if len(qr_data) > 20 else "")
            self.flash_text(t("QR Registered: ") + preview)
            
            # Return MENU_EXIT to force menu refresh (updates counters)
            return MENU_EXIT
            
        except ValueError as e:
            self.flash_error(t("Invalid QR: %s") % str(e))
            
        return MENU_CONTINUE

    def clear_all(self):
        """Clear all biometric registrations"""
        try:
            os.remove(QR_DATA_FILE)
            print("[DEBUG] Removed QR data")
        except: 
            pass
        if Settings().security.biometric_unlock:
            Settings().security.biometric_unlock = False
            store.save_settings()
        self.flash_text(t("All Cleared"))
        return MENU_EXIT

class BiometricUnlock(BiometricRegistration):
    """Class to manage biometric unlock at startup"""

    def __init__(self, ctx):
        # BiometricRegistration init needs ctx
        super().__init__(ctx)
        self.ctx = ctx
        self.qr_data = None
        self._load_registrations()

    def _load_registrations(self):
        """Load all registered biometric data"""
        # Load QR data
        try:
            with open(QR_DATA_FILE, "rb") as f:
                data_type = struct.unpack('<B', f.read(1))[0]
                if data_type == 0x02:  # QR text format
                    salt = f.read(16)
                    stored_hash = f.read(32)
                    data_len = struct.unpack('<I', f.read(4))[0]
                    data_bytes = f.read(data_len)
                    self.qr_data = struct.pack('<B16s32sI', data_type, salt, stored_hash, data_len) + data_bytes
                else:
                    # Old format - read entire file
                    f.seek(0)
                    self.qr_data = f.read()
            print("[DEBUG] QR data loaded")
        except: 
            self.qr_data = None
            print("[DEBUG] No QR data found")

    def _verify_hash(self, stored_data, input_data):
        """Verify hash of input data against stored hash"""
        if not stored_data:
            return False
        
        try:
            # Check data type
            data_type = struct.unpack_from('<B', stored_data)[0]
            
            if data_type == 0x02:  # QR format
                salt = stored_data[1:17]
                stored_hash = stored_data[17:49]
                data_len = struct.unpack_from('<I', stored_data[49:53])[0]
                
                input_hash = hashlib.sha256(salt + input_data).digest()
                return input_hash == stored_hash
        except:
            return False
        
        return False

    def run(self):
        """Run the unlock sequence"""
        print("[DEBUG] Starting biometric unlock")
        
        # If setting is disabled, skip
        if not Settings().security.biometric_unlock:
            print("[DEBUG] Biometric unlock disabled in settings")
            return True
            
        # If no QR data registered, skip
        if not self.qr_data:
            print("[DEBUG] No QR data found")
            return True

        # Start auto-scan immediately
        return self.auto_scan_unlock()

    def auto_scan_unlock(self):
        """Automatically scan for QR code unlock"""
        print("[DEBUG] Starting auto-scan unlock")
        
        # Initial clear
        self.ctx.display.clear()
        
        # Try to initialize camera
        if not self._initialize_camera():
            print("[ERROR] Camera init failed")
            return False
            
        self.ctx.display.to_landscape()
        
        # Continuous scan loop - no max attempts, just keep trying
        showing_red_border = False
        red_border_start_time = 0
        
        while True:
            # If we're showing red border, check if 1 second has passed
            if showing_red_border:
                if time.ticks_ms() - red_border_start_time >= 1000:
                    # 1 second passed, stop showing border and continue scanning
                    showing_red_border = False
                else:
                    # Still showing border, skip frame capture
                    time.sleep(0.1)
                    continue
            
            captured_img = None
            
            # Capture frame
            try:
                img = self.ctx.camera.snapshot()
                if img:
                    self.ctx.display.render_image(img)
                    captured_img = img
            except Exception as e:
                print("[ERROR] Capture error:", e)
                time.sleep(0.1)
                continue
            
            success = False
            qr_found = False
            
            if captured_img and self.qr_data:
                # Check QR
                try:
                    res = captured_img.find_qrcodes()
                    if res:
                        qr_found = True
                        qr_text = res[0].payload()
                        print("[DEBUG] QR found in image, payload:", qr_text[:50] if isinstance(qr_text, str) else str(qr_text)[:50])
                        
                        if isinstance(qr_text, str):
                            qr_bytes = qr_text.encode('utf-8')
                        else:
                            qr_bytes = qr_text
                        
                        # Verify hash
                        if self._verify_hash(self.qr_data, qr_bytes):
                            success = True
                            print("[DEBUG] QR verified successfully - hash matches!")
                        else:
                            print("[DEBUG] QR found but hash does not match")
                except Exception as e:
                    print("[DEBUG] QR check error:", e)
            
            # Handle red border feedback for wrong QR
            if captured_img:
                if qr_found and not success:
                    # QR found but doesn't match - flash red border for 1 second
                    # Draw thick red border on top of the image
                    border_width = 5
                    red_color = theme.no_esc_color
                    
                    # Draw top border
                    self.ctx.display.fill_rectangle(
                        0, 0, 
                        self.ctx.display.width(), 
                        border_width, 
                        red_color
                    )
                    # Draw bottom border
                    self.ctx.display.fill_rectangle(
                        0, 
                        self.ctx.display.height() - border_width, 
                        self.ctx.display.width(), 
                        border_width, 
                        red_color
                    )
                    # Draw left border
                    self.ctx.display.fill_rectangle(
                        0, 0, 
                        border_width, 
                        self.ctx.display.height(), 
                        red_color
                    )
                    # Draw right border
                    self.ctx.display.fill_rectangle(
                        self.ctx.display.width() - border_width, 
                        0, 
                        border_width, 
                        self.ctx.display.height(), 
                        red_color
                    )
                    
                    showing_red_border = True
                    red_border_start_time = time.ticks_ms()
                    print("[DEBUG] Wrong QR detected - showing red border for 1 second")
            
            if success:
                # QR verified - stop camera first
                self.ctx.camera.stop_sensor()
                # Return to portrait mode
                self.ctx.display.to_portrait()
                # Small delay to ensure rotation is applied
                time.sleep(0.1)
                # Clear screen to ensure clean state before returning
                self.ctx.display.clear()
                print("[DEBUG] QR verified, unlocking...")
                return True
            
            # Small delay to prevent too fast scanning
            time.sleep(0.1)

    def flash_text(self, text):
        """Show success message"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(text, color=theme.success_color)
        time.sleep(1)

    def flash_error(self, text):
        """Show error message"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(text, color=theme.error_color)
        time.sleep(1)
