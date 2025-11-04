# startup.py
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import udp_client for OSC
from pythonosc import udp_client

class StartupPage(QWidget):
    def __init__(self, parent, controller, qlabsClient, mosaicClient=None):
        super().__init__(parent)
        self.controller = controller
        self.qlabsClient = qlabsClient
        self.mosaicClient = mosaicClient

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(50)

        self.ready_label = QLabel("Ready to start?")
        self.ready_label.setObjectName("StartupLabel")
        self.ready_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.ready_label)

        self.start_button = QPushButton("GO!")
        self.start_button.setObjectName("StartupButton")
        # MODIFIED: The button now directly calls go_to_main_page
        self.start_button.clicked.connect(self.go_to_main_page)
        self.start_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def go_to_main_page(self):
        """Sends initial OSC messages and switches to the MainControlPage."""
        self.controller.logger.log("Startup 'GO!' button clicked.")
        # Send initial OSC messages
        self.send_osc_message("/cue/SYSON/go", [])
        self.send_udp_message("FOG1ON")
        
        # Switch to the main page
        self.controller.showFrame("MainControlPage")

    def send_osc_message(self, address, args):
        """Sends an OSC message using the provided qlabsClient."""
        try:
            self.qlabsClient.send_message(address, args)
            print(f"[START UP] sending {address}")
        except Exception as e:
            print(f"Failed to send OSC message from StartupPage: {e}")

    def send_udp_message(self, address):
        """Sends a UDP message using the mosaicClient if it exists."""
        if not self.mosaicClient:
            print("Failed to send UDP: Mosaic client is not available.")
            return
        try:
            # The second argument is an empty list to match the client's method signature
            self.mosaicClient.send_message(address, [])
        except Exception as e:
            print(f"Failed to send UDP message from StartupPage: {e}")
