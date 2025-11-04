from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QGridLayout, QHBoxLayout, QVBoxLayout, QFrame,
    QSizePolicy, QDialog, QSpacerItem
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from typing import List, Optional
from utils import resource_path
from customSlider import LabeledSlider
import random
class Scene(QWidget):
    # Define style constants for consistency
    BORDER_COLOR = "#E0E0E0"  # An off-white color
    BORDER_STYLE = f"border: 2px solid {BORDER_COLOR}; border-radius: 8px;"

    def __init__(self, master, qlabsClient, controller, mosaicClient=None):
        super().__init__(master)
        self.controller = controller
        self.qlabsClient = qlabsClient
        self.mosaicClient = mosaicClient

        self.scene_names = {}
        self.current_abduction_cue = None
        self.last_abducted_scene_name = None
        self.current_roaming_cue = None
        
        self.roaming_stop_map = {
            "RO1": "CRLS",  # Classic Roaming -> /cue/CRLS/go
            "RO2": "PRLS"   # Party Roaming -> /cue/PRLS/go
        }

        self.lights_only_button = None
        self.lights_only_status_label = None

        self.abduction_mic_slider = None
        self.abduction_mic_toggle = None
        self.roaming_mic_slider = None
        self.roaming_mic_toggle = None
        
        self.abduction_mic_slider_frame = None
        self.roaming_mic_slider_frame = None
        self.stop_roaming_button = None
        self.roaming_confirmation_label = None
        
        self.stop_timer = QTimer(self)
        self.stop_timer.setSingleShot(True)
        self.stop_timer.timeout.connect(self.hide_countdown_dialog)
        
        self.roaming_stop_timer = QTimer(self)
        self.roaming_stop_timer.setSingleShot(True)
        self.roaming_stop_timer.timeout.connect(self.hide_roaming_dialog)

        self._setup_ui()
        self.countdown_dialog = self._create_countdown_dialog()
        self.roaming_dialog = self._create_roaming_dialog()

    def _setup_ui(self):
        """Sets up the main layout and widgets for the page."""
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 6)
        main_layout.setColumnStretch(0, 1)
        main_layout.setSpacing(2)

        self._create_header()
        self._create_button_layout()

    def _create_header(self):
        """Creates the top header bar with back, title, and stop buttons."""
        top_frame = QFrame(self)
        top_frame.setObjectName("TopFrame")
        top_layout = QGridLayout(top_frame)
        top_frame.setLayout(top_layout)

        top_layout.setColumnStretch(0, 1)
        top_layout.setColumnStretch(1, 2)
        top_layout.setColumnStretch(2, 4)
        top_layout.setColumnStretch(3, 2)
        top_layout.setColumnStretch(4, 1)
        top_layout.setRowStretch(0, 1)

        back_button = QPushButton("〈")
        back_button.setObjectName("BackButton")

        back_button.clicked.connect(lambda: self.controller.showFrame("MainControlPage"))
        top_layout.addWidget(back_button, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        header = QLabel("Scenes")
        header.setObjectName("HeaderStyle")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(header, 0, 2, Qt.AlignmentFlag.AlignCenter)

        self.layout().addWidget(top_frame, 0, 0, 1, 1)

    def _create_button_layout(self):
        """Creates the three columns of buttons using the same helper method."""
        button_frames_h_layout = QHBoxLayout()
        button_frames_h_layout.setContentsMargins(0, 0, 0, 30)
        button_frames_h_layout.setSpacing(0)

        abduction_buttons = [
            ("Classical Abduction", "SC1", self.startAbductionCountdown),
            ("Romantic Abduction", "SC2", self.startAbductionCountdown),
            ("Party Abduction", "SC3", self.startAbductionCountdown),
        ]
        roaming_buttons = [
            ("Classic Roaming", "RO1", self.startRoamingScene),
            ("Party Roaming", "RO2", self.startRoamingScene),
            ("Lights Only", "LO1", self.handleLightsOnlyToggle), 
        ]

        for text, cue, _ in abduction_buttons + roaming_buttons:
            self.scene_names[cue] = text

        abduction_col = self._create_button_column("Abductions", abduction_buttons)
        roaming_col = self._create_button_column("Roaming", roaming_buttons)
        
        button_frames_h_layout.addStretch(1)
        button_frames_h_layout.addLayout(abduction_col)
        button_frames_h_layout.addStretch(1)
        button_frames_h_layout.addLayout(roaming_col)
        button_frames_h_layout.addStretch(1)
        
        self.layout().addLayout(button_frames_h_layout, 1, 0, 1, 1)

    def _create_button_column(self, title: str, button_configs: list, stretch_factors: Optional[List[int]] = None):
        """Helper to create a vertical column with a label, frame, and buttons."""
        group_v_layout = QVBoxLayout()
        group_v_layout.setSpacing(30)
        group_v_layout.setContentsMargins(20, 0, 20, 0)

        label = QLabel(title)
        label.setObjectName("GroupStyle")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_v_layout.addWidget(label, stretch=0)

        button_frame = QFrame(self)
        button_frame.setObjectName("ButtonFrame")
        frame_layout = QVBoxLayout(button_frame)
        frame_layout.setSpacing(0)
        button_frame.setLayout(frame_layout)

        num_buttons = len(button_configs)
        for i, (text, cue, handler) in enumerate(button_configs):
            
            button_widget = QPushButton(text)
            button_widget.setObjectName("SceneButton")
            if text in ["Romantic Abduction", "Classic Roaming", "Party Roaming"]:
                button_widget.setEnabled(False)
                style = "background-color: #282828; color: #555; font-size: 24px;"
                button_widget.setStyleSheet(f"QPushButton {{ {style} }}")
            if text == "Lights Only":
                button_widget.setObjectName("LightsOnlyButton")
                self.lights_only_button = button_widget
                button_widget.setCheckable(True)
                
                button_widget.setText("")
                
                layout = QVBoxLayout(button_widget)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(5)
                title_label = QLabel("Lights Only")
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                title_label.setStyleSheet("background-color: transparent; font-size: 24px; font-weight: bold;")
                self.lights_only_status_label = QLabel()
                self.lights_only_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addStretch(1)
                layout.addWidget(title_label)
                layout.addWidget(self.lights_only_status_label)
                layout.addStretch(1)
                
                button_widget.toggled.connect(self.handleLightsOnlyToggle)
                self.update_lights_only_visuals(button_widget.isChecked())
            else:
                if handler:
                    button_widget.clicked.connect(lambda _, c=cue, h=handler, t=text: self.log_and_call(h, c, t))

            if num_buttons == 1:
                button_widget.setProperty("position", "single")
            elif i == 0:
                button_widget.setProperty("position", "top")
            elif i == num_buttons - 1:
                button_widget.setProperty("position", "bottom")
            else:
                button_widget.setProperty("position", "middle")
            
            button_widget.style().unpolish(button_widget)
            button_widget.style().polish(button_widget)
            
            button_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            frame_layout.addWidget(button_widget)

        group_v_layout.addWidget(button_frame, stretch=1)
        return group_v_layout

    def log_and_call(self, handler, cue, text):
        """Logs the button press then calls the original handler function."""
        self.controller.logger.log(f"Scene button clicked: '{text}' (Cue: {cue})")
        handler(cue)

    def handleLightsOnlyToggle(self, is_on):
        """Handles the toggled signal for the Lights Only button."""
        srSelector = random.randint(1, 4)
        self.controller.logger.log(f"Lights Only toggled: {'ON' if is_on else 'OFF'}")
        if is_on:
            udp_message = f"SR{srSelector}start"
        else:
            udp_message = "SRstop"
        
        try:
            self.mosaicClient.send_message(udp_message, [])
            print(f"Sending UDP: {udp_message}")
        except Exception as e:
            print(f"NETWORK ERROR in Scene page: Could not send OSC message. {e}")
        
        self.update_lights_only_visuals(is_on)
        
    def update_lights_only_visuals(self, is_on):
        """Updates the status label text and color, and button style."""
        if is_on:
            status_text = "ON"
            status_color = "#148CE8" # Blue
        else:
            status_text = "OFF"
            status_color = "red"
        
        if self.lights_only_button:
            border_style = f"border: 2px solid {self.BORDER_COLOR};"
            border_radius = "border-top-left-radius: 0px; border-top-right-radius: 0px; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;"

            off_style = f"""
                QPushButton#LightsOnlyButton {{
                    {border_style}
                    {border_radius}
                    background-color: transparent;
                }}
            """
            
            on_style = f"""
                QPushButton#LightsOnlyButton:checked {{
                    {border_style}
                    {border_radius}
                    background-color: rgba(40, 40, 40, 0.85);
                }}
            """
            self.lights_only_button.setStyleSheet(off_style + on_style)

        if self.lights_only_status_label:
            self.lights_only_status_label.setText(status_text)
            self.lights_only_status_label.setStyleSheet(
                f"background-color: transparent; border: none; color: {status_color}; font-size: 24px; font-weight: bold;"
            )

    def _create_separator(self):
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"border-left: 2px solid {self.BORDER_COLOR};")
        return separator

    def _create_countdown_dialog(self):
        dialog = QDialog(self, Qt.WindowType.FramelessWindowHint)
        dialog.setObjectName("AbductionDialog")
        dialog.setStyleSheet("""
            #AbductionDialog {
                background: qlineargradient(x1:1, y1:1, x2:0, y2:0, stop:0 #010101, stop:0.5 #333333, stop:1 #010101);
            }
        """)
        dialog_layout = QGridLayout(dialog)
        dialog_layout.setRowStretch(0, 1)
        dialog_layout.setRowStretch(1, 8)

        header_frame = QFrame()
        header_layout = QGridLayout(header_frame)
        header_layout.setColumnStretch(0, 1)
        header_layout.setColumnStretch(1, 1)
        header_layout.setColumnStretch(2, 1)

        title_label = QLabel("Abduction")
        title_label.setObjectName("HeaderStyle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.abduction_mic_toggle = QPushButton("Mic Off")
        self.abduction_mic_toggle.setCheckable(True)
        self.abduction_mic_toggle.setChecked(False)
        self.abduction_mic_toggle.toggled.connect(self._handle_abduction_mic_toggle)
        self.abduction_mic_toggle.setObjectName("HeaderToggleButton")

        header_layout.addWidget(title_label, 0, 1, Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.abduction_mic_toggle, 0, 2, Qt.AlignmentFlag.AlignRight)
        
        dialog_layout.addWidget(header_frame, 0, 0)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        self.stop_abduction_dialog_button = QPushButton("Stop")
        self.stop_abduction_dialog_button.setObjectName("StopButtonCircular")
        self.stop_abduction_dialog_button.clicked.connect(self.stop_abduction_sequence)
        button_size, border_radius = 250, 125
        self.stop_abduction_dialog_button.setFixedSize(button_size, button_size)
        self.confirmation_label = QLabel("")
        self.confirmation_label.setObjectName("HeaderStyle")
        self.confirmation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.confirmation_label.hide()

        self.abduction_mic_slider_frame = QFrame(dialog)
        self.abduction_mic_slider_frame.setStyleSheet(self.BORDER_STYLE)
        self.abduction_mic_slider_frame.setFixedWidth(960)
        mic_slider_layout = QHBoxLayout(self.abduction_mic_slider_frame)
        self.abduction_mic_slider_frame.setLayout(mic_slider_layout)

        self.abduction_mic_slider = LabeledSlider(
            parent=self.abduction_mic_slider_frame, name="Mic", qlabsClient=self.qlabsClient, 
            initial_state='disabled',
            orient=Qt.Orientation.Horizontal, from_=0, to=5, resolution=1, tickinterval=1,
            icon_path_on='images/soundOn.svg', icon_path_off='images/soundOff.svg'
        )
        self.abduction_mic_slider.slider.valueChanged.connect(
            lambda val: self._send_mic_osc(val, "ABD")
        )
        mic_slider_layout.addWidget(self.abduction_mic_slider)

        content_layout.addStretch(1)
        content_layout.addWidget(self.stop_abduction_dialog_button, 0, Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.confirmation_label, 0, Qt.AlignmentFlag.AlignCenter)
        content_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        content_layout.addWidget(self.abduction_mic_slider_frame, 0, Qt.AlignmentFlag.AlignCenter)
        content_layout.addStretch(1)

        dialog_layout.addWidget(content_widget, 1, 0)
        return dialog

    def _create_roaming_dialog(self):
        dialog = QDialog(self, Qt.WindowType.FramelessWindowHint)
        dialog.setObjectName("RoamingDialog")
        dialog.setStyleSheet("""
            #RoamingDialog {
                background: qlineargradient(x1:1, y1:1, x2:0, y2:0, stop:0 #010101, stop:0.5 #333333, stop:1 #010101);
            }
        """)
        dialog_layout = QGridLayout(dialog)
        dialog_layout.setRowStretch(0, 1)
        dialog_layout.setRowStretch(1, 8)

        header_frame = QFrame()
        header_layout = QGridLayout(header_frame)
        header_layout.setColumnStretch(0, 1)
        header_layout.setColumnStretch(1, 1)
        header_layout.setColumnStretch(2, 1)

        title_label = QLabel("Roaming")
        title_label.setObjectName("HeaderStyle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.roaming_mic_toggle = QPushButton("Mic Off")
        self.roaming_mic_toggle.setCheckable(True)
        self.roaming_mic_toggle.setChecked(False)
        self.roaming_mic_toggle.toggled.connect(self._handle_roaming_mic_toggle)
        self.roaming_mic_toggle.setObjectName("HeaderToggleButton")

        header_layout.addWidget(title_label, 0, 1, Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.roaming_mic_toggle, 0, 2, Qt.AlignmentFlag.AlignRight)

        dialog_layout.addWidget(header_frame, 0, 0)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.stop_roaming_button = QPushButton("Stop")
        self.stop_roaming_button.setObjectName("StopButtonCircular")
        self.stop_roaming_button.clicked.connect(self.stopRoamingScene)
        button_size, border_radius = 250, 125
        self.stop_roaming_button.setFixedSize(button_size, button_size)
        
        self.roaming_confirmation_label = QLabel("")
        self.roaming_confirmation_label.setObjectName("HeaderStyle")
        self.roaming_confirmation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.roaming_confirmation_label.hide()

        self.roaming_mic_slider_frame = QFrame(dialog)
        self.roaming_mic_slider_frame.setStyleSheet(self.BORDER_STYLE)
        self.roaming_mic_slider_frame.setFixedWidth(960)
        mic_slider_layout = QHBoxLayout(self.roaming_mic_slider_frame)
        self.roaming_mic_slider_frame.setLayout(mic_slider_layout)

        self.roaming_mic_slider = LabeledSlider(
            parent=self.roaming_mic_slider_frame, name="Mic", qlabsClient=self.qlabsClient, 
            initial_state='disabled',
            orient=Qt.Orientation.Horizontal, from_=0, to=5, resolution=1, tickinterval=1,
            icon_path_on='images/soundOn.svg', icon_path_off='images/soundOff.svg'
        )
        self.roaming_mic_slider.slider.valueChanged.connect(
            lambda val: self._send_mic_osc(val, "RO")
        )
        mic_slider_layout.addWidget(self.roaming_mic_slider)

        content_layout.addStretch(1)
        content_layout.addWidget(self.stop_roaming_button, 0, Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.roaming_confirmation_label, 0, Qt.AlignmentFlag.AlignCenter)
        content_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        content_layout.addWidget(self.roaming_mic_slider_frame, 0, Qt.AlignmentFlag.AlignCenter)
        content_layout.addStretch(1)
        
        dialog_layout.addWidget(content_widget, 1, 0)
        return dialog

    def sendCue(self, cue):
        osc_address = "/cue/EMS/go" if cue == "stop" else f"/cue/{cue}/go"
        try:
            self.qlabsClient.send_message(osc_address, [])
            print(f"Sending OSC: {osc_address}")
        except Exception as e:
            print(f"NETWORK ERROR in Scene page: Could not send OSC message. {e}")

    def startAbductionCountdown(self, cue_id):
        self.current_abduction_cue = cue_id
        self.last_abducted_scene_name = self.scene_names.get(cue_id, "Scene")
        
        try:
            if self.last_abducted_scene_name == "Classical Abduction":
                self.qlabsClient.send_message("SC1F1start", [])
            elif self.last_abducted_scene_name == "Romantic Abduction":
                self.qlabsClient.send_message("SC2F1start", [])
            else:
                self.qlabsClient.send_message("SC3F1start", [])
        except Exception as e:
            print(f"NETWORK ERROR: Could not send original fogger OSC messages. {e}")

        udp_msg_f1 = f"{cue_id}F1start"
        self.mosaicClient.send_message(udp_msg_f1, [])
        
        self.stop_abduction_dialog_button.show()
        self.confirmation_label.hide()
        self.abduction_mic_toggle.show()
        self.abduction_mic_slider_frame.show()
        self.countdown_dialog.showFullScreen()
        self.sendCue(self.current_abduction_cue)

    def stop_abduction_sequence(self):
        self.controller.logger.log(f"Abduction scene stopped: '{self.last_abducted_scene_name}'")
        self.stop_abduction_dialog_button.hide()
        self.abduction_mic_toggle.hide()
        self.abduction_mic_slider_frame.hide()
        self.confirmation_label.setText(f"{self.last_abducted_scene_name} Stopped")
        
        try:
            if self.last_abducted_scene_name == "Classical Abduction":
                self.qlabsClient.send_message("SC1F1stop", [])
                self.mosaicClient.send_message("CALS", [])
            elif self.last_abducted_scene_name == "Romantic Abduction":
                self.qlabsClient.send_message("SC2F1stop", [])
            else:
                self.qlabsClient.send_message("SC3F1stop", [])
                self.mosaicClient.send_message("PALS", [])
        except Exception as e:
            print(f"NETWORK ERROR: Could not send original fogger OSC stop messages. {e}")

        base_cue = self.current_abduction_cue
        self.mosaicClient.send_message(f"{base_cue}F1stop", [])

        self.confirmation_label.show()
        self.stop_timer.start(2000)

    def hide_countdown_dialog(self):
        self.countdown_dialog.hide()
        self.stop_abduction_dialog_button.show()
        self.confirmation_label.hide()
        self.abduction_mic_toggle.show()
        self.abduction_mic_slider_frame.show()

    def startRoamingScene(self, cue_id):
        self.current_roaming_cue = cue_id
        
        try:
            if cue_id == "RO1":
                self.qlabsClient.send_message("RO1F1start", [])
            elif cue_id == "RO2":
                self.qlabsClient.send_message("RO2F1start", [])
        except Exception as e:
            print(f"NETWORK ERROR: Could not send roaming fogger OSC messages. {e}")

        udp_msg_f1 = f"{cue_id}F1start"
        self.mosaicClient.send_message(udp_msg_f1, [])
        
        self.stop_roaming_button.show()
        self.roaming_confirmation_label.hide()
        self.roaming_mic_toggle.show()
        self.roaming_mic_slider_frame.show()
        self.roaming_dialog.showFullScreen()
        self.sendCue(self.current_roaming_cue)

    def stopRoamingScene(self):
        scene_name = self.scene_names.get(self.current_roaming_cue, "Roaming")
        self.controller.logger.log(f"Roaming scene stopped: '{scene_name}'")
        self.stop_roaming_button.hide()
        self.roaming_mic_toggle.hide()
        self.roaming_mic_slider_frame.hide()
        
        try:
            if self.current_roaming_cue == "RO1":
                self.qlabsClient.send_message("RO1F1stop", [])
            elif self.current_roaming_cue == "RO2":
                self.qlabsClient.send_message("RO2F1stop", [])
        except Exception as e:
            print(f"NETWORK ERROR: Could not send roaming fogger OSC stop messages. {e}")

        try:
            if self.controller.fogger_is_on:
                if self.mosaicClient and self.current_roaming_cue:
                    base_cue = self.current_roaming_cue
                    self.mosaicClient.send_message(f"{base_cue}F1stop", [])
                else:
                    print("WARNING: Mosaic UDP client not available for roaming stop.")
        except AttributeError as e:
            print(f"ERROR: Could not access fogger state for stopping roaming. {e}")
        
        self.roaming_confirmation_label.setText(f"{scene_name} Stopped")
        self.roaming_confirmation_label.show()
        self.roaming_stop_timer.start(2000)

    def hide_roaming_dialog(self):
        """Hides the roaming dialog and resets its widgets."""
        self.roaming_dialog.hide()
        self.stop_roaming_button.show()
        self.roaming_confirmation_label.hide()
        self.roaming_mic_toggle.show()
        self.roaming_mic_slider_frame.show()
    
    def _on_armenian_flag_button_clicked(self, cue_id=None):
        osc_address = "/cue/ARAON/go"
        
        try:
            if self.qlabsClient:
                self.qlabsClient.send_message(osc_address, [])
                print(f"[OSC SENT] Armenian Flag button clicked: {osc_address}")
        except Exception as e:
            print(f"NETWORK ERROR: Could not send OSC for Armenian Flag button. {e}")
            
        self.controller.showFrame("ArmenianFlagPage")

    def _handle_abduction_mic_toggle(self, is_on):
        self.controller.logger.log(f"Abduction Mic toggled: {'ON' if is_on else 'OFF'}")
        if self.abduction_mic_slider:
            self.abduction_mic_slider.set_state('normal' if is_on else 'disabled')
            self.abduction_mic_toggle.setText("Mic On" if is_on else "Mic Off")
            osc_address = "/cue/ABDMICON/go" if is_on else "/cue/ABDMICOFF/go"
            self.sendCue(osc_address.split('/cue/')[1].split('/go')[0])

    def _handle_roaming_mic_toggle(self, is_on):
        self.controller.logger.log(f"Roaming Mic toggled: {'ON' if is_on else 'OFF'}")
        if self.roaming_mic_slider:
            self.roaming_mic_slider.set_state('normal' if is_on else 'disabled')
            self.roaming_mic_toggle.setText("Mic On" if is_on else "Mic Off")
            osc_address = "/cue/ROMICON/go" if is_on else "/cue/ROMICOFF/go"
            self.sendCue(osc_address.split('/cue/')[1].split('/go')[0])

    def _send_mic_osc(self, value, scene_type_prefix):
        """Sends an OSC message for a mic slider change."""
        self.controller.logger.log(f"{scene_type_prefix} Mic slider changed to: {value}")
        osc_address = f"/cue/{scene_type_prefix}MIC{int(value)}/go"
        self.sendCue(osc_address.split('/cue/')[1].split('/go')[0])