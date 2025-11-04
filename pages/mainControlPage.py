from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QGridLayout, QHBoxLayout, QVBoxLayout,
    QFrame, QSizePolicy, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap
from customSlider import LabeledSlider
from utils import resource_path

class ClickableFrame(QFrame):
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class MainControlPage(QWidget):
    def __init__(self, parent, controller, qlabsClient, **kwargs):
        super().__init__(parent)
        self.controller = controller
        self.qlabsClient = qlabsClient
        
        SLIDER_COLUMN_WIDTH = 150
        
        self.fogger_column_frame = None

        self.intensity_buttons = {"Misters": [], "Foggers": []}
        self.selected_intensity = {"Misters": 0, "Foggers": 0}
        self.last_fogger_intensity = 1 
        
        self.mister_is_on = False
        self.selected_mister_level = None
        self.mister_level_buttons = {}

        pa_on_icon = QIcon(resource_path('images/PAOn.svg'))
        self.pa_on_pixmap = pa_on_icon.pixmap(QSize(30, 30))
        pa_off_icon = QIcon(resource_path('images/PAOff.svg'))
        self.pa_off_pixmap = pa_off_icon.pixmap(QSize(30, 30))

        sound_on_icon = QIcon(resource_path('images/soundOn.svg'))
        self.sound_on_pixmap = sound_on_icon.pixmap(QSize(30, 30))
        sound_off_icon = QIcon(resource_path('images/soundOff.svg'))
        self.sound_off_pixmap = sound_off_icon.pixmap(QSize(30, 30))

        power_on_icon = QIcon(resource_path('images/powerOn.svg'))
        self.power_on_pixmap = power_on_icon.pixmap(QSize(30, 30))
        power_off_icon = QIcon(resource_path('images/powerOff.svg'))
        self.power_off_pixmap = power_off_icon.pixmap(QSize(30, 30))
        
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setVerticalSpacing(30)
        main_layout.setHorizontalSpacing(30)
        
        main_layout.setRowStretch(0, 1) 
        main_layout.setRowStretch(1, 4) 
        main_layout.setColumnStretch(0, 2) 
        main_layout.setColumnStretch(1, 1)

        top_left_controls_frame = QFrame(self)
        top_left_controls_frame.setStyleSheet("border: 2px solid #E0E0E0; border-radius: 10px;")
        
        five_button_layout = QGridLayout(top_left_controls_frame)
        five_button_layout.setContentsMargins(0, 0, 0, 0)
        five_button_layout.setSpacing(0)

        five_button_layout.setColumnStretch(0, 1) 
        five_button_layout.setColumnStretch(2, 1)
        five_button_layout.setColumnStretch(4, 1)
        five_button_layout.setColumnStretch(6, 1)
        five_button_layout.setColumnStretch(8, 1)

        self.sound_button = ClickableFrame()
        
        self.sound_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sound_layout = QVBoxLayout(self.sound_button)
        self.sound_icon_label = QLabel()
        self.sound_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sound_label = QLabel("Sound")
        sound_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sound_status_label = QLabel("OFF")
        self.sound_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sound_layout.addStretch(1)
        sound_layout.addWidget(self.sound_icon_label)
        sound_layout.addWidget(sound_label)
        sound_layout.addWidget(self.sound_status_label)
        sound_layout.addStretch(1)
        self.sound_button.clicked.connect(lambda: self.toggle_button(self.sound_button, 'sound', "Sound", not getattr(self.sound_button, 'toggled', False)))
        five_button_layout.addWidget(self.sound_button, 0, 0)
        
        separator1 = QFrame(); separator1.setFrameShape(QFrame.Shape.VLine); separator1.setFrameShadow(QFrame.Shadow.Sunken)
        five_button_layout.addWidget(separator1, 0, 1)

        self.pa_button = ClickableFrame()
        self.pa_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        pa_layout = QVBoxLayout(self.pa_button)
        self.pa_icon_label = QLabel()
        self.pa_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pa_label = QLabel("PA")
        pa_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pa_status_label = QLabel("OFF")
        self.pa_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pa_layout.addStretch(1)
        pa_layout.addWidget(self.pa_icon_label)
        pa_layout.addWidget(pa_label)
        pa_layout.addWidget(self.pa_status_label)
        pa_layout.addStretch(1)
        self.pa_button.clicked.connect(lambda: self.toggle_button(self.pa_button, 'pa', "PA", not getattr(self.pa_button, 'toggled', False)))
        five_button_layout.addWidget(self.pa_button, 0, 2)

        separator2 = QFrame(); separator2.setFrameShape(QFrame.Shape.VLine); separator2.setFrameShadow(QFrame.Shadow.Sunken)
        five_button_layout.addWidget(separator2, 0, 3)

        self.led_panel_button = ClickableFrame()
        self.led_panel_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        led_panel_layout = QVBoxLayout(self.led_panel_button)
        led_panel_label = QLabel("LED Signs")
        led_panel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.led_status_label = QLabel("OFF")
        self.led_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        led_panel_layout.addStretch(1)
        led_panel_layout.addWidget(led_panel_label)
        led_panel_layout.addWidget(self.led_status_label)
        led_panel_layout.addStretch(1)
        self.led_panel_button.clicked.connect(lambda: self.toggle_button(self.led_panel_button, 'led_signs', "LED Signs", not getattr(self.led_panel_button, 'toggled', False)))
        five_button_layout.addWidget(self.led_panel_button, 0, 4)

        separator3 = QFrame(); separator3.setFrameShape(QFrame.Shape.VLine); separator3.setFrameShadow(QFrame.Shadow.Sunken)
        five_button_layout.addWidget(separator3, 0, 5)

        self.scenes_button = ClickableFrame()
        self.scenes_button.setObjectName("ScenesButtonFrame")
        self.scenes_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scenes_layout = QVBoxLayout(self.scenes_button)
        self.scenes_icon_label = QLabel()
        scenes_icon = QIcon(resource_path('images/sceneOff.svg'))
        scenes_pixmap = scenes_icon.pixmap(QSize(30, 30))
        self.scenes_icon_label.setPixmap(scenes_pixmap)
        self.scenes_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scenes_label = QLabel("Scenes")
        self.scenes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scenes_layout.addStretch(1)
        scenes_layout.addWidget(self.scenes_icon_label)
        scenes_layout.addWidget(self.scenes_label)
        scenes_layout.addStretch(1)
        self.scenes_button.clicked.connect(self.log_scenes_click)
        five_button_layout.addWidget(self.scenes_button, 0, 6)

        separator4 = QFrame(); separator4.setFrameShape(QFrame.Shape.VLine); separator4.setFrameShadow(QFrame.Shadow.Sunken)
        five_button_layout.addWidget(separator4, 0, 7)

        lights_frame = ClickableFrame()
        lights_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lights_layout = QVBoxLayout(lights_frame)
        lights_icon_label = QLabel()
        lights_icon = QIcon(resource_path('images/light.svg'))
        lights_pixmap = lights_icon.pixmap(QSize(30, 30))
        lights_icon_label.setPixmap(lights_pixmap)
        lights_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lights_label = QLabel("Lights")
        lights_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lights_layout.addStretch(1)
        lights_layout.addWidget(lights_icon_label)
        lights_layout.addWidget(lights_label)
        lights_layout.addStretch(1)
        lights_frame.clicked.connect(self.log_lights_click)
        five_button_layout.addWidget(lights_frame, 0, 8)
        
        main_layout.addWidget(top_left_controls_frame, 0, 0)

        top_right_controls_frame = QFrame(self)
        top_right_controls_frame.setStyleSheet("border: 2px solid #E0E0E0; border-radius: 10px;")
        top_right_layout = QHBoxLayout(top_right_controls_frame)
        top_right_layout.setContentsMargins(0, 0, 0, 0)
        top_right_layout.setSpacing(0)
        
        self.main_power_button = ClickableFrame()
        self.main_power_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_power_layout = QVBoxLayout(self.main_power_button)
        self.main_power_icon_label = QLabel()
        self.main_power_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_power_label = QLabel("Main Power")
        main_power_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_power_status_label = QLabel("ON")
        self.main_power_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_power_layout.addStretch(1)
        main_power_layout.addWidget(self.main_power_icon_label)
        main_power_layout.addWidget(main_power_label)
        main_power_layout.addWidget(self.main_power_status_label)
        main_power_layout.addStretch(1)
        self.main_power_button.clicked.connect(lambda: self.toggle_button(self.main_power_button, 'main_power', "Main Power", not getattr(self.main_power_button, 'toggled', True)))
        top_right_layout.addWidget(self.main_power_button)

        separator_power_wifi = QFrame(); separator_power_wifi.setFrameShape(QFrame.Shape.VLine); separator_power_wifi.setFrameShadow(QFrame.Shadow.Sunken)
        top_right_layout.addWidget(separator_power_wifi)

        self.wifi_button = ClickableFrame()
        self.wifi_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        wifi_layout = QVBoxLayout(self.wifi_button)
        
        wifi_icon_label = QLabel()
        wifi_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wifi_icon = QIcon(resource_path('images/wifi.svg'))
        wifi_pixmap = wifi_icon.pixmap(QSize(30, 30))
        wifi_icon_label.setPixmap(wifi_pixmap)

        wifi_label = QLabel("WiFi")
        wifi_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        wifi_layout.addStretch(1)
        wifi_layout.addWidget(wifi_icon_label)
        wifi_layout.addWidget(wifi_label)
        wifi_layout.addStretch(1)
        
        self.wifi_button.clicked.connect(self.log_wifi_click)
        top_right_layout.addWidget(self.wifi_button)

        main_layout.addWidget(top_right_controls_frame, 0, 1)

        right_column_frame = QFrame(self)
        right_column_layout = QVBoxLayout(right_column_frame)
        right_column_layout.setContentsMargins(0, 0, 0, 0)
        right_column_layout.setSpacing(15)

        mister_controls_group_frame = QFrame(self)
        mister_controls_group_frame.setStyleSheet("border: 2px solid #E0E0E0; border-radius: 10px;")
        mister_controls_group_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        misters_main_layout = QVBoxLayout(mister_controls_group_frame)
        misters_main_layout.setContentsMargins(10, 10, 10, 10)
        misters_main_layout.setSpacing(30)

        misters_label = QLabel("Misters")
        misters_label.setObjectName("LabelStyle")
        misters_label.setStyleSheet("border: none;")
        misters_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        misters_main_layout.addWidget(misters_label)

        misters_level_layout = QHBoxLayout()
        misters_level_layout.setSpacing(0)

        low_button = QPushButton("Low")
        low_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        low_button.clicked.connect(lambda: self._on_mister_level_clicked('low'))
        self.mister_level_buttons['low'] = low_button

        high_button = QPushButton("High")
        high_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        high_button.clicked.connect(lambda: self._on_mister_level_clicked('high'))
        self.mister_level_buttons['high'] = high_button

        misters_level_layout.addWidget(self.mister_level_buttons['low'])
        misters_level_layout.addWidget(self.mister_level_buttons['high'])
        misters_main_layout.addLayout(misters_level_layout)

        self.mister_toggle_button = ClickableFrame()
        self.mister_toggle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        mister_toggle_layout = QVBoxLayout(self.mister_toggle_button)
        self.mister_status_label = QLabel("OFF")
        self.mister_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mister_toggle_layout.addWidget(self.mister_status_label)
        self.mister_toggle_button.clicked.connect(self._on_mister_toggle_clicked)
        misters_main_layout.addWidget(self.mister_toggle_button)

        right_column_layout.addWidget(mister_controls_group_frame)

        image_frame = QFrame()
        image_frame_layout = QVBoxLayout(image_frame)
        
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        try:
            pixmap = QPixmap(resource_path('images/logo.svg'))
            image_label.setPixmap(pixmap)
            image_label.setMinimumSize(1, 1)
            image_label.setMaximumSize(351, 99)
        except Exception as e:
            image_label.setText("Image not found")
            print("Warning: Could not load 'images/logo.svg'")
        
        image_label.setScaledContents(True)
        image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        image_frame_layout.addWidget(image_label)
        right_column_layout.addWidget(image_frame)

        right_column_layout.setContentsMargins(0,0,0,30)
        main_layout.addWidget(right_column_frame, 1, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("WarmupProgressBar")
        progress_bar_font = QFont()
        progress_bar_font.setPointSize(20)
        self.progress_bar.setFont(progress_bar_font)
        self.progress_bar.setOrientation(Qt.Orientation.Vertical)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()

        slider_frame = QFrame(self)
        slider_layout = QHBoxLayout(slider_frame)
        slider_frame.setLayout(slider_layout)
        slider_layout.setContentsMargins(14, 0, 14, 0)
        slider_layout.setSpacing(20)
        slider_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.sliders = {}; self.slider_labels = {}
        slider_names = ["Aux", "PA", "Foggers", "Exterior Lights", "Interior Lights"]
        
        class MockSliderControl:
            def __init__(self, buttons_list):
                self._buttons = buttons_list
            def set_state(self, state):
                is_enabled = (state == 'normal')
                for button in self._buttons:
                    button.setEnabled(is_enabled)
        
        slider_layout.addStretch(1)

        for i, name in enumerate(slider_names):
            column_widget = QWidget()
            column_widget.setFixedWidth(SLIDER_COLUMN_WIDTH)

            full_column_layout = QVBoxLayout(column_widget)
            full_column_layout.setSpacing(5)
            full_column_layout.setContentsMargins(0, 0, 0, 0)
            
            container_frame = QFrame()
            container_frame.setStyleSheet("border: 2px solid #E0E0E0; border-radius: 10px;")
            
            label_text = name
            if name == "Foggers":
                self.fogger_column_frame = container_frame
                label_text = "Fogger"

            if name in ["Foggers"]:
                button_stack_layout = QVBoxLayout(container_frame)
                button_stack_layout.setContentsMargins(0, 0, 0, 0)
                button_stack_layout.setSpacing(0)
                
                for j in range(5, 0, -1):
                    button = QPushButton(f"{j}")
                    button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                    button.clicked.connect(lambda checked=False, n=name, v=j: self._on_intensity_button_clicked(n, v))
                    self.intensity_buttons[name].append(button)
                    button_stack_layout.addWidget(button)

                self.fogger_off_button = ClickableFrame()
                self.fogger_off_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                fogger_off_layout = QVBoxLayout(self.fogger_off_button)
                self.fogger_toggle_label = QLabel("ON")
                self.fogger_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                fogger_off_layout.addWidget(self.fogger_toggle_label)
                self.fogger_off_button.clicked.connect(self._on_fogger_toggle_clicked)

                button_stack_layout.addWidget(self.fogger_off_button)
                self.intensity_buttons[name].append(self.fogger_off_button)
                
                self.intensity_buttons[name].reverse()

                if name == "Foggers":
                    self.sliders['Foggers'] = MockSliderControl(self.intensity_buttons['Foggers'])

            else:
                slider_container_layout = QVBoxLayout(container_frame)
                slider_container_layout.setContentsMargins(25, 5, 25, 5)
                
                initial_slider_state = 'normal' if name in ["Exterior Lights", "Interior Lights"] else 'disabled'
                to_value = 100 if name == "Aux" else 5
                
                slider_kwargs = {
                    'name': name,
                    'orient': Qt.Orientation.Vertical,
                    'from_': 0, 'to': to_value,
                    'resolution': 1,
                    'qlabsClient': self.qlabsClient,
                    'initial_state': initial_slider_state
                }
                
                if name == "PA":
                    slider_kwargs['icon_path_on'] = 'images/PAOn.svg'
                    slider_kwargs['icon_path_off'] = 'images/PAOff.svg'
                elif name == "Aux":
                    slider_kwargs['icon_path_on'] = 'images/soundOn.svg'
                    slider_kwargs['icon_path_off'] = 'images/soundOff.svg'
                
                slider = LabeledSlider(self, **slider_kwargs)
                
                slider.slider.setValue(0)
                slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                slider.slider.valueChanged.connect(lambda value, s_name=name: self.controller.onSliderChange(s_name, value))
                
                slider_container_layout.addWidget(slider)
                
                if name in ["Exterior Lights", "Interior Lights"]: slider.slider.setValue(3)
                self.sliders[name] = slider

            full_column_layout.addWidget(container_frame, 1)

            slider_label = QLabel(label_text)
            slider_label.setObjectName("LabelStyle")
            slider_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            
            full_column_layout.addWidget(slider_label)
            
            slider_layout.addWidget(column_widget)

        slider_layout.addStretch(1)

        if self.fogger_column_frame:
            self.progress_bar.setParent(self.fogger_column_frame)
        
        main_layout.addWidget(slider_frame, 1, 0)

        self._style_mister_controls()
        self._style_intensity_buttons("Foggers")

        self.toggle_button(self.main_power_button, 'main_power', "Main Power", True, is_initial_setup=True)
        self.toggle_button(self.pa_button, 'pa', "PA", False, is_initial_setup=True)
        self.toggle_button(self.sound_button, 'sound', "Sound", False, is_initial_setup=True)
        self.toggle_button(self.led_panel_button, 'led_signs', "LED Signs", False, is_initial_setup=True)
        
        self.wifi_button.setStyleSheet("background-color: transparent; border: none; font-size: 30px;")
        self.scenes_button.setStyleSheet("background-color: transparent; border: none; font-size: 30px;")
        lights_frame.setStyleSheet("background-color: transparent; border: none; font-size: 30px;")

        self.controller.onSliderChange("Foggers", self.selected_intensity["Foggers"])

    def log_scenes_click(self):
        self.controller.logger.log("Button clicked: Scenes")
        self.controller.showFrame("ScenesPage")

    def log_lights_click(self):
        self.controller.logger.log("Button clicked: Lights")
        self.controller.showFrame("LightsPage")

    def log_wifi_click(self):
        self.controller.logger.log("Button clicked: WiFi")
        self.controller.showFrame("WifiPage")

    def _on_fogger_toggle_clicked(self):
        is_on = self.selected_intensity["Foggers"] != 0
        
        self.controller.on_fogger_toggle()

        if is_on:
            if self.selected_intensity["Foggers"] > 0:
                self.last_fogger_intensity = self.selected_intensity["Foggers"]
            self.selected_intensity["Foggers"] = 0
            for button in self.intensity_buttons["Foggers"][1:]:
                button.setEnabled(False)
        else:
            self.selected_intensity["Foggers"] = -1
            for button in self.intensity_buttons["Foggers"][1:]:
                button.setEnabled(True)
            
            is_main_power_on = getattr(self.main_power_button, 'toggled', True)
            if is_main_power_on:
                self.controller.start_initial_system_warmup()
        
        self._style_intensity_buttons("Foggers")

    def _on_mister_toggle_clicked(self):
        self.mister_is_on = not self.mister_is_on
        self.controller.logger.log(f"Misters Toggled: {'ON' if self.mister_is_on else 'OFF'}")
        
        if not self.mister_is_on:
            self.selected_mister_level = None
        
        self.controller.on_mister_change(self.mister_is_on, None)
        self._style_mister_controls()

    def _on_mister_level_clicked(self, level):
        if not self.mister_is_on:
            return

        self.selected_mister_level = level
        self.controller.logger.log(f"Mister level set to: {level}")
        
        self.controller.on_mister_change(True, level)
        self._style_mister_controls()

    def _style_mister_controls(self):
        is_on = self.mister_is_on
        
        for level, button in self.mister_level_buttons.items():
            button.setEnabled(is_on)
            is_selected = (self.selected_mister_level == level)
            
            base_style = "font-size: 24px; border: 2px solid #E0E0E0;"
            
            if not is_on:
                style = f"{base_style} background-color: #282828; color: #555;"
            elif is_selected:
                style = f"{base_style} background-color: white; color: black;"
            else:
                style = f"{base_style} background-color: transparent; color: white;"
                
            button_radius = "8px"
            if level == 'low':
                style += f"border-top-left-radius: {button_radius}; border-bottom-left-radius: {button_radius}; border-top-right-radius: 0px; border-bottom-right-radius: 0px; border-right-width: 1px;"
            else:
                style += f"border-top-right-radius: {button_radius}; border-bottom-right-radius: {button_radius}; border-top-left-radius: 0px; border-bottom-left-radius: 0px; border-left-width: 1px;"
                
            button.setStyleSheet(f"QPushButton {{ {style} }}")

        if is_on:
            self.mister_status_label.setText("ON")
            self.mister_status_label.setStyleSheet("color: #148CE8; font-size: 30px; border: none;")
            self.mister_toggle_button.setStyleSheet("QFrame { background-color: transparent; border: 2px solid #E0E0E0; border-radius: 8px; }")
        else:
            self.mister_status_label.setText("OFF")
            self.mister_status_label.setStyleSheet("color: red; font-size: 30px; border: none;")
            self.mister_toggle_button.setStyleSheet("QFrame { background-color: transparent; border: 2px solid #E0E0E0; border-radius: 8px; }")

    def _on_intensity_button_clicked(self, group_name: str, value: int):
        self.controller.logger.log(f"{group_name} intensity changed to: {value}")
        
        self.selected_intensity[group_name] = value
        
        self.controller.onSliderChange(group_name, value)
        
        if group_name == "Foggers":
            is_off = (value == 0)
            if is_off:
                for button in self.intensity_buttons["Foggers"][1:]:
                    button.setEnabled(False)
        
        self._style_intensity_buttons(group_name)

    def _style_intensity_buttons(self, group_name: str):
        buttons = self.intensity_buttons.get(group_name, [])
        selected_index = self.selected_intensity.get(group_name, -1)
        num_buttons = len(buttons)
        if num_buttons == 0:
            return

        if group_name == "Foggers":
            selected_index = self.selected_intensity.get("Foggers", 0)

            if selected_index == 0:
                self.fogger_toggle_label.setText("OFF")
            else:
                self.fogger_toggle_label.setText("ON")
                
            for i, button in enumerate(buttons):
                if isinstance(button, QPushButton) and not button.isEnabled():
                    bg_color = "#282828"
                    text_color = "#555"
                    border_color = "#444"
                else:
                    is_selected = (i == selected_index)
                    if selected_index == -1 and i == 0:
                        is_selected = True

                    if is_selected:
                        bg_color = "white"
                        text_color = "black"
                        border_color = "white"
                    else:
                        bg_color = "transparent"
                        text_color = "white"
                        border_color = "#888888"

                base_style = f"background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; font-size: 20px;"
                
                button_radius = "8px"
                if i == (num_buttons - 1):
                    radius_style = (f"border-top-left-radius: {button_radius}; "
                                  f"border-top-right-radius: {button_radius}; "
                                  f"border-bottom-left-radius: 0px; "
                                  f"border-bottom-right-radius: 0px;")
                elif i == 0:
                    radius_style = (f"border-top-left-radius: 0px; "
                                  f"border-top-right-radius: 0px; "
                                  f"border-bottom-left-radius: {button_radius}; "
                                  f"border-bottom-right-radius: {button_radius};")
                else:
                    radius_style = "border-radius: 0px;"

                full_style = base_style + radius_style

                if isinstance(button, ClickableFrame):
                    button.setStyleSheet(f"QFrame {{ {full_style} }}")
                    label = button.findChild(QLabel)
                    if label:
                        label.setStyleSheet(f"color: {text_color}; background-color: transparent; border: none; font-size: 20px;")
                else:
                    button.setStyleSheet(f"QPushButton {{ {full_style} }}")
            return

    def _update_progress_bar_geometry(self):
        if self.fogger_column_frame and self.progress_bar:
            self.progress_bar.setGeometry(0, 0, self.fogger_column_frame.width(), self.fogger_column_frame.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_progress_bar_geometry()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_progress_bar_geometry()

    def toggle_button(self, button_widget, button_type, button_label_text, is_checked, is_initial_setup=False):
        if not is_initial_setup:
            self.controller.logger.log(f"Toggled {button_label_text}: {'ON' if is_checked else 'OFF'}")

        setattr(button_widget, 'toggled', is_checked)

        bg_color = "#3059d9" if is_checked else "transparent"
        status_text = "ON" if is_checked else "OFF"
        status_color = "#148CE8" if is_checked else "red"

        radius = "9px"
        border_radius_style = ""

        if button_type in ['sound', 'main_power']:
            border_radius_style = f"""
                border-top-left-radius: {radius};
                border-bottom-left-radius: {radius};
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            """
        elif button_type in ["pa", "led_signs"]:
            border_radius_style = f"""
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            """
        
        stylesheet = f"""
            QFrame {{
                background-color: {bg_color};
                border: none;
                font-size: 30px;
                {border_radius_style}
            }}
            QLabel {{
                border: none;
                background-color: transparent;
            }}
        """
        button_widget.setStyleSheet(stylesheet)

        if button_type == 'sound':
            self.sound_icon_label.setPixmap(self.sound_on_pixmap if is_checked else self.sound_off_pixmap)
            self.sound_status_label.setText(status_text)
            self.sound_status_label.setStyleSheet(f"color: {status_color};")
        
        elif button_type == 'pa':
            self.pa_icon_label.setPixmap(self.pa_on_pixmap if is_checked else self.pa_off_pixmap)
            self.pa_status_label.setText(status_text)
            self.pa_status_label.setStyleSheet(f"color: {status_color};")
        
        elif button_type == 'led_signs':
            self.led_status_label.setText(status_text)
            self.led_status_label.setStyleSheet(f"color: {status_color};")
            
        elif button_type == 'main_power':
            self.scenes_button.setEnabled(is_checked)
            if is_checked:
                self.scenes_button.setStyleSheet("QFrame#ScenesButtonFrame QLabel { color: #E0E0E0; }")
            else:
                self.scenes_button.setStyleSheet("QFrame#ScenesButtonFrame QLabel { color: #888888; }")


            self.main_power_icon_label.setPixmap(self.power_on_pixmap if is_checked else self.power_off_pixmap)
            self.main_power_status_label.setText(status_text)
            self.main_power_status_label.setStyleSheet(f"color: {status_color};")

            controls_state = 'normal' if is_checked else 'disabled'
            
            self.sliders["Exterior Lights"].set_state(controls_state)
            self.sliders["Interior Lights"].set_state(controls_state)
            
            self.mister_is_on = is_checked
            if not is_checked:
                self.selected_mister_level = None
            self._style_mister_controls()

            if not is_checked:
                self.toggle_button(self.sound_button, 'sound', "Sound", False)
                self.toggle_button(self.pa_button, 'pa', "PA", False)
                self.toggle_button(self.led_panel_button, 'led_signs', "LED Signs", False)

                for slider_name, slider_obj in self.sliders.items():
                    if slider_name == "Foggers":
                        self._on_intensity_button_clicked("Foggers", 0)
                    elif hasattr(slider_obj, 'slider'):
                        slider_obj.slider.setValue(0)
                
                try:
                    if self.controller.mosaicClient: self.controller.mosaicClient.send_message("MSTOFF", [])
                except Exception as e:
                    print(f"NETWORK ERROR: Could not send Mister OFF command. {e}")

        if not is_initial_setup:
            actions = {
                'main_power': f"/cue/MNP{'ON' if is_checked else 'OFF'}/go",
                'pa': f"/cue/MIC{'ON' if is_checked else 'OFF'}/go",
                'sound': f"/cue/AUX{'ON' if is_checked else 'OFF'}/go"
            }
            if button_type in actions:
                try:
                    if self.qlabsClient: self.qlabsClient.send_message(actions[button_type], [])
                    print(f"[MAIN] OSC sent: {actions[button_type]}")
                except Exception as e:
                    print(f"NETWORK ERROR in MainControlPage: Could not send OSC message for {button_type}. {e}")
            
            if button_type == 'led_signs':
                udp_message = "LEDON" if is_checked else "LEDOFF"
                try:
                    if self.controller.mosaicClient:
                        self.controller.mosaicClient.send_message(udp_message, [])
                    print(f"[MAIN] UDP sent: {udp_message}")
                except Exception as e:
                    print(f"NETWORK ERROR in MainControlPage: Could not send UDP message for {button_type}. {e}")

            slider_map = {'pa': 'PA', 'sound': 'Aux'}
            if button_type in slider_map:
                slider_name = slider_map[button_type]
                if slider_name in self.sliders:
                    self.sliders[slider_name].set_state('normal' if is_checked else 'disabled')
                    if not is_checked: self.sliders[slider_name].slider.setValue(0)