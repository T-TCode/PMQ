# ufoBeam.py
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGridLayout, QFrame, QSizePolicy
)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt

from customSlider import LabeledSlider

class UfoBeam(QWidget):
    # The matrix is kept to format the UDP message correctly, assuming a default color.
    matrix = [
        ["R0", "R2", "R4", "R6", "R8", "R10"], # Red
        ["O0", "O2", "O4", "O6", "O8", "O10"], # Orange
        ["Y0", "Y2", "Y4", "Y6", "Y8", "Y10"], # Yellow
        ["G0", "G2", "G4", "G6", "G8", "G10"], # Green
        ["B0", "B2", "B4", "B6", "B8", "B10"], # Blue
        ["I0", "I2", "I4", "I6", "I8", "I10"], # Indigo
        ["V0", "V2", "V4", "V6", "V8", "V10"], # Violet
        ["W0", "W2", "W4", "W6", "W8", "W10"]  # White
    ]

    BORDER_COLOR = "#E0E0E0"
    BORDER_STYLE = f"border: 2px solid {BORDER_COLOR}; border-radius: 8px;"

    def __init__(self, master, mosaicClient, controller, logger):
        super().__init__(master)
        self.controller = controller
        self.mosaicClient = mosaicClient
        self.logger = logger
        self.lastSelectedIntensity = 0 # Default to 0

        self.setStyleSheet("background-color: transparent; color: #E0E0E0;")

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 6)
        main_layout.setColumnStretch(0, 1)
        main_layout.setSpacing(2)

        top_header_frame = QFrame(self)
        top_header_frame.setObjectName("TopFrame")
        top_header_layout = QGridLayout(top_header_frame)
        top_header_frame.setLayout(top_header_layout)
        top_header_layout.setContentsMargins(0, 25, 0, 0)

        top_header_layout.setColumnStretch(0, 1)
        top_header_layout.setColumnStretch(1, 2)
        top_header_layout.setColumnStretch(2, 4)
        top_header_layout.setColumnStretch(3, 2)
        top_header_layout.setColumnStretch(4, 1)
        top_header_layout.setRowStretch(0, 1)

        back_button = QPushButton("〈")
        back_button.setObjectName("BackButton")
        back_button.clicked.connect(lambda: self.controller.showFrame("LightsPage"))
        top_header_layout.addWidget(back_button, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        page_label = QLabel("UFO Beam")
        page_label.setObjectName("HeaderStyle")
        page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_header_layout.addWidget(page_label, 0, 2, Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(top_header_frame, 0, 0)
        
        content_container_layout = QVBoxLayout()
        content_container_layout.setContentsMargins(10, 10, 10, 10)
        content_container_layout.setSpacing(20)

        slider_frame = QFrame(self)
        slider_frame.setObjectName("SliderFrame")
        slider_frame.setStyleSheet(self.BORDER_STYLE)
        slider_frame.setFixedSize(960, 120)

        slider_layout = QHBoxLayout(slider_frame)
        slider_frame.setLayout(slider_layout)
        slider_layout.setContentsMargins(15, 15, 15, 15)
        slider_layout.setSpacing(10)
        
        self.slider = LabeledSlider(
            parent=slider_frame,
            mosaicClient=self.mosaicClient,
            initial_state='enabled',
            callback_on_release=self._update_and_send_udp,
            orient=Qt.Orientation.Horizontal,
            from_=0, to=5, resolution=1, tickinterval=1
        )
        
        slider_layout.addWidget(self.slider)
        
        # MODIFIED: A new QHBoxLayout to handle horizontal centering
        slider_centering_layout = QHBoxLayout()
        slider_centering_layout.addStretch(1)
        slider_centering_layout.addWidget(slider_frame)
        slider_centering_layout.addStretch(1)

        # The main vertical layout now holds the centering layout
        content_container_layout.addStretch(1)
        content_container_layout.addLayout(slider_centering_layout)
        content_container_layout.addStretch(1)

        main_layout.addLayout(content_container_layout, 1, 0)
        self.logger.log("UFO Beam page initialized.")

    def _update_and_send_udp(self, slider_value):
        """
        Sends a UDP message with the selected intensity, assuming a default color of White.
        """
        self.logger.log(f"UFO Beam slider released at value: {slider_value}")
        self.lastSelectedIntensity = int(slider_value)

        try:
            colorIndex = 7 # Assume a default color of White
            intensityIndex = self.lastSelectedIntensity
            
            if 0 <= intensityIndex < len(self.matrix[colorIndex]):
                resultCombo = self.matrix[colorIndex][intensityIndex]
                self.logger.log(f"Sending UDP from UFO Beam: LZ6{resultCombo}")
                self.mosaicClient.send_message(f"LZ6{resultCombo}", [])
            else:
                print(f"Invalid intensity index: {intensityIndex}. Cannot send message.")
        except Exception as e:
            print(f"NETWORK ERROR in UfoBeam page: Could not send UDP message. {e}")