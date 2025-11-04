# pages/wifiPage.py

import sys
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLineEdit, QMessageBox, QScrollArea, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize
from PyQt6.QtGui import QIcon
import time
import pywifi
from pywifi import const
# NEW: Import the helper function for asset paths
from utils import resource_path

class WifiConnectorThread(QThread):
    connection_status = pyqtSignal(str)
    connection_finished = pyqtSignal(bool)

    def __init__(self, ssid, password):
        super().__init__()
        self.ssid = ssid
        self.password = password

    def run(self):
        try:
            wifi = pywifi.PyWiFi()
            ifaces = wifi.interfaces()
            if not ifaces:
                self.connection_status.emit("No Wi-Fi interface found.")
                self.connection_finished.emit(False)
                return

            iface = ifaces[0]

            profiles_to_try = [
                {
                    "name": "WPA2-AES",
                    "auth": const.AUTH_ALG_OPEN,
                    "akm": [const.AKM_TYPE_WPA2PSK],
                    "cipher": const.CIPHER_TYPE_CCMP
                },
                {
                    "name": "WPA2-TKIP",
                    "auth": const.AUTH_ALG_OPEN,
                    "akm": [const.AKM_TYPE_WPA2PSK],
                    "cipher": const.CIPHER_TYPE_TKIP
                },
                {
                    "name": "WPA-TKIP",
                    "auth": const.AUTH_ALG_OPEN,
                    "akm": [const.AKM_TYPE_WPAPSK],
                    "cipher": const.CIPHER_TYPE_TKIP
                }
            ]

            is_connected = False
            for profile_config in profiles_to_try:
                self.connection_status.emit(f"Trying connection with {profile_config['name']}...")
                iface.disconnect()
                time.sleep(2)

                profile = pywifi.Profile()
                profile.ssid = self.ssid
                profile.auth = profile_config["auth"]
                profile.akm = profile_config["akm"]
                profile.cipher = profile_config["cipher"]
                profile.key = self.password

                iface.remove_all_network_profiles()
                tmp_profile = iface.add_network_profile(profile)
                iface.connect(tmp_profile)

                timeout = 15
                while timeout > 0:
                    status_msg = f"Attempting ({profile_config['name']})... ({timeout}s left)"
                    self.connection_status.emit(status_msg)
                    if iface.status() == const.IFACE_CONNECTED:
                        is_connected = True
                        break
                    time.sleep(1)
                    timeout -= 1
                
                if is_connected:
                    break

            if is_connected:
                self.connection_status.emit(f"Successfully connected to {self.ssid}!")
                self.connection_finished.emit(True)
            else:
                self.connection_status.emit("Failed: All common security types were attempted.")
                self.connection_finished.emit(False)

        except Exception as e:
            self.connection_status.emit(f"An error occurred: {e}")
            self.connection_finished.emit(False)

# pages/wifiPage.py

class OnScreenKeyboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # REVERTED: The widget's main layout is now a simple grid.
        self.layout = QGridLayout(self)
        self.layout.setSpacing(5)

        self.target_input = None
        self.is_shifted = False
        self.buttons = []

        # This map ensures '&&' on a button outputs a single '&'
        self.output_map = {"&&": "&"}

        self.create_keyboard()
        
        # REVERTED: Stylesheet for smaller, uniform buttons.
        self.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 10px;
                background-color: transparent;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #555;
            }
        """)

    def set_target_input(self, input_widget):
        self.target_input = input_widget

    def _on_key_press(self):
        button = self.sender()
        if button:
            display_text = button.text()
            # Use the map to get the real character ('&'), defaulting to the display text.
            output_character = self.output_map.get(display_text, display_text)
            self.insert_char(output_character)

    def create_keyboard(self):
        # Using your preferred 5-row keyboard layout
        self.normal_keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'Backspace'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'Delete'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '@', 'Shift'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '-', '_', ' '],
            ['!', '#', '$', '%', '^', '&&', '*', '(', ')', '=', '+']
        ]
        self.shifted_keys = [
            ['!', '@', '#', '$', '%', '^', '&&', '*', '(', ')', 'Backspace'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'Delete'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', 'Shift'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', ' '],
            ['~', '`', '{', '}', '[', ']', '|', '\\', '"', "'", '/']
        ]

        # REVERTED: Simplified loop for a perfectly uniform grid.
        for row_index, row_keys in enumerate(self.normal_keys):
            row_of_buttons = []
            for col_index, key in enumerate(row_keys):
                button = QPushButton(key)
                if key == 'Delete':
                    button.clicked.connect(self.delete_char)
                elif key == 'Backspace':
                    button.clicked.connect(self.backspace_char)
                elif key == 'Shift':
                    button.clicked.connect(self.toggle_shift)
                else:
                    button.clicked.connect(self._on_key_press)
                
                self.layout.addWidget(button, row_index, col_index)
                row_of_buttons.append(button)
            
            self.buttons.append(row_of_buttons)

    def insert_char(self, char):
        if self.target_input: self.target_input.insert(char)

    def delete_char(self):
        if self.target_input: self.target_input.clear()

    def backspace_char(self):
        if self.target_input: self.target_input.backspace()

    def toggle_shift(self):
        self.is_shifted = not self.is_shifted
        current_keys = self.shifted_keys if self.is_shifted else self.normal_keys
        
        for row_index, row_of_buttons in enumerate(self.buttons):
            for col_index, button in enumerate(row_of_buttons):
                button.setText(current_keys[row_index][col_index])

class WifiPage(QWidget):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent)
        self.controller = controller
        self.thread = None
        
        # MODIFIED: All icon paths are now wrapped with resource_path()
        self.icon_show = QIcon(resource_path('images/show.svg'))
        self.icon_hide = QIcon(resource_path('images/showOff.svg'))

        self.status_check_timer = QTimer(self)
        self.status_check_timer.setInterval(5000)
        self.status_check_timer.timeout.connect(self.update_connection_status)

        self.initUI()

    def showEvent(self, event):
        super().showEvent(event)
        self.update_connection_status()
        self.status_check_timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.status_check_timer.stop()

    def initUI(self):
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 6)
        main_layout.setColumnStretch(0, 1)
        main_layout.setSpacing(2)

        self._create_header()
        self._create_content_area()

    def _create_header(self):
        top_frame = QFrame(self)
        top_frame.setObjectName("TopFrame")
        top_layout = QGridLayout(top_frame)
        top_frame.setLayout(top_layout)
        top_layout.setColumnStretch(0, 1)
        top_layout.setColumnStretch(1, 8)
        top_layout.setColumnStretch(2, 1)
        top_layout.setContentsMargins(0, 25, 0, 0)
        
        back_button = QPushButton("〈")
        back_button.setObjectName("BackButton")
        back_button.clicked.connect(lambda: self.controller.showFrame("MainControlPage"))
        top_layout.addWidget(back_button, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        header = QLabel("Wi-Fi Settings")
        header.setObjectName("HeaderStyle")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(header, 0, 1, Qt.AlignmentFlag.AlignCenter)

        self.starlink_button = QPushButton("Starlink")
        self.starlink_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
                font-weight: bold;
                color: #E0E0E0;
                background-color: transparent;
                margin-right: 30px;
            }
            QPushButton:pressed {
                background-color: #555;
            }
        """)
        self.starlink_button.clicked.connect(self._on_starlink_button_clicked)
        top_layout.addWidget(self.starlink_button, 0, 2, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.layout().addWidget(top_frame, 0, 0)

    def _create_content_area(self):
        scroll_area = QScrollArea()
        scroll_area.setObjectName("ContentScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        
        content_widget = QWidget()
        content_widget.setObjectName("ScrollAreaContent")
        
        grid_layout = QGridLayout(content_widget)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(2, 1)

        self.ssid_label = QLabel('SSID:')
        self.ssid_input = QLineEdit()
        self.ssid_input.setPlaceholderText('Enter wifi SSID')

        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.show_hide_button = QPushButton()
        self.show_hide_button.setIcon(self.icon_hide)
        self.show_hide_button.setIconSize(QSize(32, 32))
        self.show_hide_button.setCheckable(True)
        self.show_hide_button.setStyleSheet("QPushButton { border: none; padding: 5px; }")
        self.show_hide_button.setFixedSize(45, 45)
        self.show_hide_button.toggled.connect(self.toggle_password_visibility)

        password_layout = QHBoxLayout()
        password_layout.setSpacing(5)
        password_layout.setContentsMargins(0,0,0,0)
        password_layout.addWidget(self.show_hide_button)
        password_layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.start_connection)
        
        self.disconnect_button = QPushButton('Disconnect')
        self.disconnect_button.clicked.connect(self.disconnect_wifi)

        button_style = """
            QPushButton {
                background-color: transparent;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 18px;
                font-weight: bold;
                color: #E0E0E0;
            }
            QPushButton:hover {
                background-color: rgba(51, 51, 51, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.5);
            }
        """
        self.connect_button.setStyleSheet(button_style)
        self.disconnect_button.setStyleSheet(button_style)
        
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)
        
        self.status_label = QLabel('Checking status...')
        self.keyboard = OnScreenKeyboard()
        grid_layout.addWidget(self.status_label, 0, 1)
        grid_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 0, 1)
        grid_layout.addWidget(self.ssid_label, 1, 1)
        grid_layout.addWidget(self.ssid_input, 2, 1)
        grid_layout.addWidget(self.password_label, 3, 1)
        grid_layout.addLayout(password_layout, 4, 1)
        grid_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed), 5, 1)
        grid_layout.addLayout(button_layout, 6, 1)
        grid_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed), 7, 1)
        grid_layout.addWidget(self.keyboard, 8, 0, 1, 3)
        grid_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 9, 1)

        scroll_area.setWidget(content_widget)
        self.layout().addWidget(scroll_area, 1, 0)

        self.ssid_input.installEventFilter(self)
        self.password_input.installEventFilter(self)
        self.connect_button.installEventFilter(self)

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_hide_button.setIcon(self.icon_show)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_hide_button.setIcon(self.icon_hide)
        
    def eventFilter(self, obj, event):
        if event.type() == event.Type.FocusIn:
            if obj == self.ssid_input: self.keyboard.set_target_input(self.ssid_input)
            elif obj == self.password_input: self.keyboard.set_target_input(self.password_input)
        elif event.type() == event.Type.MouseButtonPress:
            if obj == self.connect_button: self.keyboard.set_target_input(None)
        return super().eventFilter(obj, event)

    def disconnect_wifi(self):
        self.controller.logger.log("WiFi Disconnect button clicked.")
        try:
            wifi = pywifi.PyWiFi()
            iface = wifi.interfaces()[0]
            iface.disconnect()
            iface.remove_all_network_profiles()
            print("Disconnected and removed all profiles.")
            self.status_label.setText("Status: Disconnected")
        except Exception as e:
            self.status_label.setText("Status: Disconnection failed.")
            print(f"Error during disconnect: {e}")

    def update_connection_status(self):
        try:
            wifi = pywifi.PyWiFi()
            iface = wifi.interfaces()[0]
            if iface.status() == const.IFACE_CONNECTED:
                profiles = iface.network_profiles()
                current_ssid = "Unknown"
                if profiles:
                    current_ssid = profiles[0].ssid
                self.status_label.setText(f"Status: Connected to {current_ssid}")
            else:
                self.status_label.setText("Status: Disconnected")
        except Exception as e:
            self.status_label.setText("Status: Error checking Wi-Fi")
            print(f"Could not check Wi-Fi status: {e}")

    def _on_starlink_button_clicked(self):
        self.controller.logger.log("WiFi Starlink button clicked.")
        STARLINK_SSID = "Offroadkings"
        STARLINK_PASSWORD = "9495108110"

        self.status_label.setText("Disconnecting from current network...")
        self.disconnect_wifi()
        
        QTimer.singleShot(2500, lambda: self._attempt_connection(STARLINK_SSID, STARLINK_PASSWORD))

    def _attempt_connection(self, ssid, password):
        if not ssid or not password:
            self.show_message("Error", "SSID and password cannot be empty.", QMessageBox.Icon.Warning)
            return
        
        self.status_label.setText(f"Connecting to {ssid}...")
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(False)
        
        self.thread = WifiConnectorThread(ssid, password)
        self.thread.connection_status.connect(self.update_status_from_thread)
        self.thread.connection_finished.connect(self.on_connection_finished)
        self.thread.start()

    def start_connection(self):
        ssid = self.ssid_input.text()
        password = self.password_input.text()
        self.controller.logger.log(f"WiFi Connect button clicked for SSID: {ssid}")
        self._attempt_connection(ssid, password)

    def update_status_from_thread(self, message):
        self.status_label.setText(message)
    
    def on_connection_finished(self, success):
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(True)
        if success:
            self.show_message("Success", "Successfully connected!", QMessageBox.Icon.Information)
        else:
            self.show_message("Failed", "Failed to connect. Check credentials and try again.", QMessageBox.Icon.Critical)
        self.update_connection_status()

    def show_message(self, title, message, icon):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
