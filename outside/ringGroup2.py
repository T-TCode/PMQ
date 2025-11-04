# ringGroup2.py
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGridLayout, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from customSlider import LabeledSlider

class RingGroup2(QWidget):
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
    slider_value_changed = pyqtSignal(str, int)

    BORDER_COLOR = "#E0E0E0"
    BORDER_STYLE = f"border: 2px solid {BORDER_COLOR}; border-radius: 8px;"

    def __init__(self, master, mosaicClient, controller, light_instance_ref, logger, main_app_instance=None):
        super().__init__(master)
        self.controller = controller
        self.mosaicClient = mosaicClient
        self.logger = logger
        
        self.main_app_instance = main_app_instance
        self.max_intensity = 5
        self.light_instance_ref = light_instance_ref
        self.light_group_name = "Ring Group 2"
        self.name = "Ring Group 2"
        self.is_locked_at_zero = False
        self.light_instance_ref.light_state_updated.connect(self.update_color_and_intensity)
        initial_color_code, initial_brightness = self.light_instance_ref.saved_slider_values.get(
            self.light_group_name, ("W", 3)
        )
        self.setStyleSheet("background-color: transparent; color: #E0E0E0;")

        initial_brightness = self.light_instance_ref.saved_slider_values.get("Ring Group 2 Brightness", 3)
        initial_color_code = self.light_instance_ref.saved_slider_values.get("Ring Group 2 Color Code", "W")
        initial_color_name = self.light_instance_ref.saved_slider_values.get("Ring Group 2 Color Name", "White")

        self.selectedColorCode = initial_color_code
        self.lastSelectedColor = initial_color_name
        self.lastSelectedIntensity = initial_brightness

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

        page_label = QLabel("Ring Group 2")
        page_label.setObjectName("HeaderStyle")
        page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_header_layout.addWidget(page_label, 0, 2, Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(top_header_frame, 0, 0)
        
        content_container_layout = QVBoxLayout()
        content_container_layout.setContentsMargins(10, 10, 10, 10)
        content_container_layout.setSpacing(2)

        content_container_layout.addStretch(1)

        color_buttons_layout = QHBoxLayout()
        color_buttons_layout.setContentsMargins(10, 10, 10, 10)
        color_buttons_layout.setSpacing(0)
        color_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.colorNames = ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet", "White"]
        self.colors = ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "#8A2BE2", "White"]
        self.code = ["R", "O", "Y", "G", "B", "I", "V", "W"]
        self.intensity = [0, 2, 4, 6, 8, 10]
        
        button_width = 120
        self.colorButtons = []
        self.lastSelectedButton = None

        color_buttons_layout.addStretch(1)

        for i, n in enumerate(self.colorNames):
            button = QPushButton("")
            button.clicked.connect(lambda checked, cName=n, btn=button: self.handleColorButtonClick(cName, btn))
            button.setFixedSize(button_width, 450)
            color_buttons_layout.addWidget(button)
            self.colorButtons.append(button)

            if n == initial_color_name:
                self._apply_button_stylesheet(button, self.colors[i], is_selected=True)
                self.lastSelectedButton = button
            else:
                self._apply_button_stylesheet(button, self.colors[i], is_selected=False)
        
        color_buttons_layout.addStretch(1)
        
        content_container_layout.addLayout(color_buttons_layout)
        content_container_layout.addStretch(1)

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
            callback_on_release=self._handle_slider_release,
            orient=Qt.Orientation.Horizontal,
            from_=0, to=self.max_intensity, resolution=1, tickinterval=1
        )
        
        slider_layout.addWidget(self.slider)

        slider_centering_layout.addStretch()
        slider_centering_layout.addWidget(slider_frame)
        slider_centering_layout.addStretch()
        
        content_container_layout.addLayout(slider_centering_layout)
        content_container_layout.addStretch(1)

        main_layout.addLayout(content_container_layout, 1, 0)
        
        self.slider.set_slider_value(initial_brightness)
        self.light_instance_ref.register_slider("Ring Group 2", self.slider)
        self.logger.log(f"{self.name} page initialized.")

    def _get_button_stylesheet(self, color_hex, is_selected=False):
        base_style = f"""
            QPushButton {{
                background-color: {color_hex};
                border: none;
                border-radius: 0px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: rgba({QColor(color_hex).red()}, {QColor(color_hex).green()}, {QColor(color_hex).blue()}, 200);
            }}
            QPushButton:disabled {{
                background-color: #606060;
            }}
        """
        selected_style_addition = f"""
            QPushButton {{
                border-style: inset;
                border-width: 5px;
                border-color: #333333;
                background-color: rgba({QColor(color_hex).red()}, {QColor(color_hex).green()}, {QColor(color_hex).blue()}, 220);
            }}
        """
        
        if is_selected:
            return base_style + selected_style_addition
        return base_style

    def _apply_button_stylesheet(self, button, color_hex, is_selected):
        button.setStyleSheet(self._get_button_stylesheet(color_hex, is_selected))
        button.style().polish(button)

    def _handle_slider_release(self, value):
        self.logger.log(f"{self.name} slider released at value: {value}")
        slider_val = int(value)
        
        if slider_val == 0:
            if not self.is_locked_at_zero:
                self.is_locked_at_zero = True
                self.slider.set_state('locked_at_zero')
        elif self.is_locked_at_zero:
            self.is_locked_at_zero = False
            self.slider.set_state('normal')

        self._update_and_send_udp(value)
        if hasattr(self.controller, 'exterior_intensity_changed'):
            self.controller.exterior_intensity_changed.emit()

    def _update_and_send_udp(self, slider_value):
        self.lastSelectedIntensity = int(slider_value)
        self.light_instance_ref.update_light_state(self.light_group_name, self.selectedColorCode, self.lastSelectedIntensity)

        try:
            intensityIndex = self.lastSelectedIntensity
            colorIndex = self.code.index(self.selectedColorCode)
            if 0 <= intensityIndex < len(self.matrix[colorIndex]):
                resultCombo = self.matrix[colorIndex][intensityIndex]
                self.logger.log(f"Sending UDP from {self.name}: LZ2{resultCombo}")
                self.mosaicClient.send_message(f"LZ2{resultCombo}", [])
            else:
                print(f"Invalid intensity index: {intensityIndex}. Cannot send message.")
        except Exception as e:
            print(f"NETWORK ERROR in RingGroup2 page: Could not send UDP message. {e}")

    def handleColorButtonClick(self, colorName, clickedButton):
        self.logger.log(f"{self.name} color button clicked: {colorName}")
        self.lastSelectedColor = colorName
        self.selectedColorCode = self.code[self.colorNames.index(colorName)]
        self.light_instance_ref.update_light_state(self.light_group_name, self.selectedColorCode, self.lastSelectedIntensity)
        print(f"Color selected: {colorName} (Code: {self.selectedColorCode})")

        if self.lastSelectedButton:
            idx = self.colorButtons.index(self.lastSelectedButton)
            self._apply_button_stylesheet(self.lastSelectedButton, self.colors[idx], is_selected=False)

        self.lastSelectedButton = clickedButton
        idx = self.colorButtons.index(self.lastSelectedButton)
        self._apply_button_stylesheet(self.lastSelectedButton, self.colors[idx], is_selected=True)

        if self.lastSelectedIntensity is not None:
            self._update_and_send_udp(self.lastSelectedIntensity)

        for button in self.colorButtons:
            if button != self.lastSelectedButton:
                button.setDisabled(True)
        QTimer.singleShot(1000, self.enableColorButtons)

    def enableColorButtons(self):
        for i, button in enumerate(self.colorButtons):
            button.setDisabled(False)
            if button != self.lastSelectedButton:
                self._apply_button_stylesheet(button, self.colors[i], is_selected=False)
            else:
                self._apply_button_stylesheet(button, self.colors[i], is_selected=True)

    def adjust_intensity_by_delta(self, delta, synced):
        if self.is_locked_at_zero:
            return

        current_intensity = self.lastSelectedIntensity
        proposed_intensity = current_intensity + delta

        if current_intensity == 1 and proposed_intensity < 1:
            new_intensity = 1 if not synced else 0
        else:
            new_intensity = max(0, min(proposed_intensity, self.max_intensity))

        if new_intensity != current_intensity:
            self.set_intensity(new_intensity)

    def get_current_intensity(self):
        return self.lastSelectedIntensity

    def set_intensity(self, value):
        clamped_value = max(0, min(value, self.max_intensity))
        self.logger.log(f"{self.name} intensity programmatically set to {clamped_value}")
        
        if self.is_locked_at_zero and clamped_value != 0:
            self.is_locked_at_zero = False
            self.slider.set_state('normal')
        
        if clamped_value != self.lastSelectedIntensity:
            self.slider.blockSignals(True)
            self.slider.set_slider_value(clamped_value)
            self.slider.blockSignals(False)
            self.lastSelectedIntensity = clamped_value
            self._update_and_send_udp(clamped_value)

    def update_color_and_intensity(self, light_group_name: str, color_code: str, intensity: int):
        if light_group_name == self.light_group_name:
            self.selectedColorCode = color_code
            try:
                self.lastSelectedColor = self.colorNames[self.code.index(color_code)]
            except ValueError:
                self.lastSelectedColor = "White"
            self.lastSelectedIntensity = intensity
            self.update_color_display_ui(color_code)

            if intensity == 0 and not self.is_locked_at_zero:
                pass
            elif intensity != 0 and self.is_locked_at_zero:
                self.is_locked_at_zero = False
                self.slider.set_state('normal')

    def update_color_display_ui(self, new_color_code: str):
        try:
            idx = self.code.index(new_color_code)
            new_color_name = self.colorNames[idx]
        except ValueError:
            return

        if self.lastSelectedButton:
            old_idx = self.colorButtons.index(self.lastSelectedButton)
            self._apply_button_stylesheet(self.lastSelectedButton, self.colors[old_idx], is_selected=False)

        for i, button in enumerate(self.colorButtons):
            if self.colorNames[i] == new_color_name:
                self._apply_button_stylesheet(button, self.colors[i], is_selected=True)
                self.lastSelectedButton = button
                break