# led.py
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGridLayout, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QTimer

from customSlider import LabeledSlider # Import the slider widget

class Led(QWidget):
    # --- A matrix to combine color and intensity for cues ---
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
    BORDER_STYLE = "border: 2px solid #E0E0E0; border-radius: 8px;"

    def __init__(self, master, controller, mosaicClient, **kwargs):
        super().__init__(master)
        self.controller = controller
        self.mosaicClient = mosaicClient

        # --- Main Layout ---
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 6)
        main_layout.setColumnStretch(0, 1)
        main_layout.setSpacing(2)
        
        self.setStyleSheet("background-color: transparent; color: #E0E0E0;")

        # --- Top Header Frame ---
        top_header_frame = QFrame(self)
        top_header_frame.setObjectName("TopFrame")
        top_header_layout = QGridLayout(top_header_frame)
        top_header_frame.setLayout(top_header_layout)
        top_header_layout.setContentsMargins(0, 25, 0, 0)
        
        top_header_layout.setColumnStretch(0, 1); top_header_layout.setColumnStretch(1, 2) 
        top_header_layout.setColumnStretch(2, 4); top_header_layout.setColumnStretch(3, 2) 
        top_header_layout.setColumnStretch(4, 1); top_header_layout.setRowStretch(0, 1)

        back_button = QPushButton("〈")
        back_button.setObjectName("BackButton")
        back_button.clicked.connect(lambda: self.controller.showFrame("MainControlPage"))
        top_header_layout.addWidget(back_button, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        page_label = QLabel("LED Signs")
        page_label.setObjectName("HeaderStyle")
        page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_header_layout.addWidget(page_label, 0, 2, Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(top_header_frame, 0, 0)

        # --- Content Grouping ---
        content_container_layout = QVBoxLayout()
        content_container_layout.setContentsMargins(10, 10, 10, 10)
        content_container_layout.setSpacing(2)

        content_container_layout.addStretch(1)

        # --- Color Buttons Section ---
        color_buttons_layout = QHBoxLayout()
        color_buttons_layout.setContentsMargins(10, 10, 10, 10)
        color_buttons_layout.setSpacing(0)
        color_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.colorNames = ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet", "White"]
        self.colors = ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "#8A2BE2", "White"]
        
        button_width = 120
        self.colorButtons = []
        self.lastSelectedButton = None

        # --- State tracking for color and intensity ---
        self.lastSelectedColorIndex = 7 # Default to White
        self.lastSelectedIntensity = 3  # Default to an initial intensity

        color_buttons_layout.addStretch(1)

        for i, n in enumerate(self.colorNames):
            button = QPushButton("")
            button.clicked.connect(lambda checked, cIndex=i, btn=button: self.handleColorButtonClick(cIndex, btn))
            button.setFixedSize(button_width, 450)
            color_buttons_layout.addWidget(button)
            self.colorButtons.append(button)

            if i == self.lastSelectedColorIndex:
                self._apply_button_stylesheet(button, self.colors[i], is_selected=True)
                self.lastSelectedButton = button
            else:
                self._apply_button_stylesheet(button, self.colors[i], is_selected=False)
        
        color_buttons_layout.addStretch(1)
        content_container_layout.addLayout(color_buttons_layout)
        content_container_layout.addStretch(1)
        
        # --- Slider Section ---
        slider_centering_layout = QHBoxLayout()

        slider_frame = QFrame(self)
        slider_frame.setObjectName("SliderFrame")
        slider_frame.setStyleSheet(self.BORDER_STYLE)
        
        total_button_width = button_width * len(self.colorNames)
        slider_frame.setFixedWidth(total_button_width)

        slider_layout = QHBoxLayout(slider_frame)
        slider_frame.setLayout(slider_layout)
        slider_layout.setContentsMargins(10, 10, 10, 10)
        slider_layout.setSpacing(10)
        
        self.slider = LabeledSlider(
            parent=slider_frame,
            mosaicClient=self.mosaicClient,
            initial_state='enabled',
            orient=Qt.Orientation.Horizontal,
            from_=0, to=5, resolution=1, tickinterval=1,
            callback_on_release=self._send_udp
        )
        self.slider.set_slider_value(self.lastSelectedIntensity)
        
        slider_layout.addWidget(self.slider)

        slider_centering_layout.addStretch()
        slider_centering_layout.addWidget(slider_frame)
        slider_centering_layout.addStretch()
        
        content_container_layout.addLayout(slider_centering_layout)

        content_container_layout.addStretch(1)
        
        main_layout.addLayout(content_container_layout, 1, 0)

    def _send_udp(self, slider_value):
        self.controller.logger.log(f"LED Sign brightness changed to: {slider_value}")
        self.lastSelectedIntensity = int(slider_value)
        try:
            # Look up the correct cue part from the matrix
            resultCombo = self.matrix[self.lastSelectedColorIndex][self.lastSelectedIntensity]
            
            # Construct the final UDP message and send it
            udp_message = f"LED{resultCombo}"
            print(f"Sending UDP message to Mosaic: {udp_message}")
            self.mosaicClient.send_message(udp_message, [])
        except IndexError:
            print(f"Error: Invalid color/intensity index. C:{self.lastSelectedColorIndex}, I:{self.lastSelectedIntensity}")
        except Exception as e:
            print(f"NETWORK ERROR in LED page: Could not send UDP message. {e}")

    def _get_button_stylesheet(self, color_hex, is_selected=False):
        base_style = f"""
            QPushButton {{
                background-color: {color_hex}; border: none; border-radius: 0px; padding: 0px;
            }}
            QPushButton:hover {{
                background-color: rgba({QColor(color_hex).red()}, {QColor(color_hex).green()}, {QColor(color_hex).blue()}, 200);
            }}
            QPushButton:disabled {{ background-color: #606060; }}
        """
        selected_style_addition = f"""
            QPushButton {{
                border-style: inset; border-width: 5px; border-color: #333333;
                background-color: rgba({QColor(color_hex).red()}, {QColor(color_hex).green()}, {QColor(color_hex).blue()}, 220);
            }}
        """
        return base_style + selected_style_addition if is_selected else base_style

    def _apply_button_stylesheet(self, button, color_hex, is_selected):
        button.setStyleSheet(self._get_button_stylesheet(color_hex, is_selected))
        button.style().polish(button)

    def handleColorButtonClick(self, colorIndex, clickedButton):
        self.controller.logger.log(f"LED Sign color changed to: {self.colorNames[colorIndex]}")
        self.lastSelectedColorIndex = colorIndex
        print(f"Color selected: {self.colorNames[colorIndex]}")
        
        # Send the UDP message with the new color and current intensity
        self._send_udp(self.lastSelectedIntensity)

        # Update button styling
        if self.lastSelectedButton:
            old_idx = self.colorButtons.index(self.lastSelectedButton)
            self._apply_button_stylesheet(self.lastSelectedButton, self.colors[old_idx], is_selected=False)

        self.lastSelectedButton = clickedButton
        self._apply_button_stylesheet(self.lastSelectedButton, self.colors[colorIndex], is_selected=True)

        # led.py - FIXED
        # Temporarily disable all OTHER buttons to prevent rapid clicking
        for button in self.colorButtons:
            if button is not self.lastSelectedButton:
                button.setDisabled(True)
        QTimer.singleShot(500, self.enableColorButtons)

    def enableColorButtons(self):
        for i, button in enumerate(self.colorButtons):
            button.setDisabled(False)
            is_selected = (button == self.lastSelectedButton)
            self._apply_button_stylesheet(button, self.colors[i], is_selected=is_selected)
