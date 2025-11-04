from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QGridLayout, QHBoxLayout, QVBoxLayout, QFrame,
    QDialog, QTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
from typing import Any, Optional, List

class Light(QWidget):
    """Manages the main lights page and centralizes the state for all light groups."""
    light_state_updated = pyqtSignal(str, str, int)

    BORDER_COLOR = "#E0E0E0"
    BORDER_STYLE = f"border: 2px solid {BORDER_COLOR}; border-radius: 8px;"

    LIGHT_GROUPS = [
        "Top Ring [Outside]", "Middle Ring [Outside]", "Bottom Ring [Outside]",
        "Puck Lights", "UFO Ring", "UFO Beam", "Light Zone 1 [Outside]", "Light Zone 2 [Outside]",
        "Top Ring [Inside]", "Middle Ring [Inside]", "Bottom Ring [Inside]",
    ]

    def __init__(self, master, qlabsClient, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller
        self.qlabsClient = qlabsClient

        self.saved_slider_values = {
            name: ("W", 0) if "Beam" in name else ("W", 3)
            for name in self.LIGHT_GROUPS
        }
        
        self._registered_sliders = {}
        self.initUI()

    def initUI(self):
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)
        main_layout.setRowStretch(0, 1) # Header row
        main_layout.setRowStretch(1, 6) # Content row
        main_layout.setColumnStretch(0, 1)
        main_layout.setSpacing(2)

        self._create_header()
        
        outside_grid_frame = self._create_outside_grid()
        inside_column_frame = self._create_button_column()

        outside_col = self._create_column("Outside", outside_grid_frame)
        inside_col = self._create_column("Inside", inside_column_frame)

        content_h_layout = QHBoxLayout()
        content_h_layout.setContentsMargins(0, 0, 0, 30)

        content_h_layout.addStretch(1)
        content_h_layout.addLayout(outside_col, 2)
        content_h_layout.addStretch(1)
        content_h_layout.addLayout(inside_col, 1)
        content_h_layout.addStretch(1)
        
        main_layout.addLayout(content_h_layout, 1, 0, 1, 1)

    def _create_header(self):
        top_frame = QFrame(self)
        top_frame.setObjectName("TopFrame")
        top_layout = QGridLayout(top_frame)
        top_frame.setLayout(top_layout)
        top_layout.setColumnStretch(0, 1)
        top_layout.setColumnStretch(1, 8)
        top_layout.setColumnStretch(2, 1)
        
        back_button = QPushButton("〈")
        back_button.setObjectName("BackButton")
        back_button.clicked.connect(lambda: self.controller.showFrame("MainControlPage"))
        top_layout.addWidget(back_button, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        header = QLabel("Lights")
        header.setObjectName("HeaderStyle")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(header, 0, 1, Qt.AlignmentFlag.AlignCenter)
        
        self.layout().addWidget(top_frame, 0, 0)

    def _create_column(self, title, content_widget):
        column_layout = QVBoxLayout()
        column_layout.setSpacing(30)
        
        label = QLabel(title)
        label.setObjectName("GroupStyle")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        column_layout.addWidget(label, stretch=0)
        column_layout.addWidget(content_widget, stretch=1)
        
        return column_layout

    def _create_outside_grid(self):
        grid_container = QFrame()
        grid_container.setObjectName("OutsideGridContainer")
        grid_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QGridLayout(grid_container)
        
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        button_configs = [
            [("Top Ring", "TopRingOutsideControlPage"), ("Puck Lights", "PuckLightsControlPage")],
            [("Middle Ring", "MiddleRingOutsideControlPage"), ("UFO Ring", "UfoRingOutsideControlPage")],
            [("Bottom Ring", "BottomRingOutsideControlPage"), ("UFO Beam", "UfoBeamControlPage")],
            [("Ring Group 1", "LightZone1ControlPage"), ("Ring Group 2", "LightZone2ControlPage")]
        ]
        
        num_rows = 4
        num_cols = 2
        
        for row in range(num_rows): layout.setRowStretch(row, 1)
        for col in range(num_cols): layout.setColumnStretch(col, 1)

        for row in range(num_rows):
            for col in range(num_cols):
                text, page_name = button_configs[row][col]
                button = QPushButton(text)
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                button.clicked.connect(lambda _, p=page_name: self.controller.showFrame(p))
                
                if text not in ["Puck Lights", "UFO Beam", "Ring Group 1"]:
                    button.setEnabled(False)
                    style = "background-color: #282828; color: #555; font-size: 24px;"
                    # --- FIX: Add border-radius to the top-left disabled button ---
                    if row == 0 and col == 0:
                        style += " border-top-left-radius: 6px;"
                    button.setStyleSheet(f"QPushButton {{ {style} }}")

                css_classes = []
                if row == num_rows - 1: css_classes.append("last-row")
                if col == num_cols - 1: css_classes.append("last-column")
                
                if css_classes: button.setProperty("class", " ".join(css_classes))

                layout.addWidget(button, row, col)
                
        return grid_container

    def _create_button_column(self):
        button_configs = [
            ("Top Ring", "TopRingInsideControlPage"),
            ("Middle Ring", "MiddleRingInsideControlPage"),
            ("Bottom Ring", "BottomRingInsideControlPage"),
        ]
        
        button_frame = QFrame(self)
        button_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        frame_layout = QVBoxLayout(button_frame)
        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(0,0,0,0)
        button_frame.setLayout(frame_layout)
        
        num_buttons = len(button_configs)
        for i, (text, page_name) in enumerate(button_configs):
            button = QPushButton(text)
            button.setObjectName("SceneButton")
            
            if num_buttons == 1: button.setProperty("position", "single")
            elif i == 0: button.setProperty("position", "top")
            elif i == num_buttons - 1: button.setProperty("position", "bottom")
            else: button.setProperty("position", "middle")
            
            button.style().unpolish(button)
            button.style().polish(button)
            if(text not in [] ):
                button.setEnabled(False)
                style = "background-color: #282828; color: #555; border: 2px solid #E0E0E0; font-size: 24px;"
                button.setStyleSheet(f"QPushButton {{ {style} }}")
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            button.clicked.connect(lambda _, p=page_name: self.controller.showFrame(p))
            frame_layout.addWidget(button)
        
        return button_frame

    def register_slider(self, slider_name: str, slider_instance: QWidget):
        self._registered_sliders[slider_name] = slider_instance
        light_group_name = slider_name.replace(" Brightness", "")
        if light_group_name in self.saved_slider_values:
            _color_code, intensity = self.saved_slider_values[light_group_name]
            self._set_slider_value_silently(slider_instance, intensity)
    
    def _set_slider_value_silently(self, slider_instance: QWidget, value: int):
        qslider = slider_instance.slider if hasattr(slider_instance, 'slider') else slider_instance
        qslider.blockSignals(True)
        try:
            if hasattr(slider_instance, 'set_slider_value'):
                slider_instance.set_slider_value(value)
            else:
                qslider.setValue(value)
        finally:
            qslider.blockSignals(False)

    def update_light_state(self, light_group: str, color_code: str, intensity: int):
        self.saved_slider_values[light_group] = (color_code, intensity)

    def sendCue(self, cue: str):
        osc_address = "/cue/EMS/go" if cue == "stop" else f"/cue/{cue}/go"
        try:
            if self.qlabsClient: self.qlabsClient.send_message(osc_address, [])
            print(f"[LIGHT] Sending OSC: {osc_address}")
        except Exception as e:
            print(f"NETWORK ERROR in Light page: Could not send OSC message. {e}")