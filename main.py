import sys, os, time
from datetime import datetime
import socket
import inspect
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap
from pythonosc import udp_client

from utils import resource_path
from scenes import Scene
from lights import Light
from startup import StartupPage
from led import Led
from pages.armenianFlagPage import ArmenianFlagPage
from outside.topRing import TopRing as TopRingOutside
from outside.middleRing import MiddleRing as MiddleRingOutside
from outside.bottomRing import BottomRing as BottomRingOutside
from outside.puckLights import PuckLights
from outside.ufoBeam import UfoBeam
from outside.ufoRing import UfoRing
from outside.ringGroup1 import RingGroup1
from outside.ringGroup2 import RingGroup2
from inside.topRing import TopRing as TopRingInside
from inside.middleRing import MiddleRing as MiddleRingInside
from inside.bottomRing import BottomRing as BottomRingInside
from pages.mainControlPage import MainControlPage
from pages.wifiPage import WifiPage

# --- START: LOGGER CLASS ---
class Logger:
    def __init__(self):
        self.log_file = None
        self.start_time = time.monotonic()
        log_number = 1
        while True:
            log_filename = f"log{log_number}.txt"
            if not os.path.exists(log_filename):
                break
            log_number += 1
        
        try:
            self.log_file = open(log_filename, 'w')
            self.log(f"--- Log session started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            print(f"Logging application events to {log_filename}")
        except IOError as e:
            print(f"CRITICAL: Could not open log file {log_filename}. Error: {e}")
            self.log_file = None

    def log(self, message):
        if not self.log_file:
            return
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = f"[{timestamp}] {message}\n"
        self.log_file.write(log_entry)
        self.log_file.flush()

    def close(self):
        if self.log_file:
            self.log("--- Log session ended ---")
            self.log_file.close()
            self.log_file = None
# --- END: LOGGER CLASS ---


class UdpClient:
    def __init__(self, ip, port):
        self.target_ip = ip
        self.target_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"UDP client (Mosaic) configured to send to {ip}:{port}")

    def send_message(self, address, value):
        message = address.encode('utf-8')
        try:
            self.sock.sendto(message, (self.target_ip, self.target_port))
            print(f"[UDP] sending {message} to {(self.target_ip, self.target_port)}")
        except Exception as e:
            print(f"UDP send error for message '{address}': {e}")

class MainApplication(QMainWindow):
    FOGGER_WARMUP_SECONDS = 300      # 5 minutes

    exterior_intensity_changed = pyqtSignal()
    interior_intensity_changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.logger = Logger()
        
        self.setWindowTitle("Main Control (PyQt)")
        self.resize(1600, 900)
        self.showFullScreen()
        
        try:
            self.qlabsClient = udp_client.SimpleUDPClient("192.168.0.160", 53000)
            print("OSC Client (QLab) created for 192.168.0.160:53000")
        except Exception as e:
            print(f"CRITICAL: Could not create QLab OSC client. Error: {e}")
            self.qlabsClient = None
            
        try:
            self.mosaicClient = UdpClient("192.168.1.10", 33)
            print("UDP Client (Mosaic) created for 192.168.1.10:33")
        except Exception as e:
            print(f"CRITICAL: Could not create Mosaic UDP client. Error: {e}")
            self.mosaicClient = None

        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainBackground")
        self.setCentralWidget(self.central_widget)
        self.stacked_widget = QStackedWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.stacked_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(self._get_global_stylesheet())
        
        self._has_started_initial_warmup = False
        self.previous_exterior_lights_value = 3
        self.previous_interior_lights_value = 3
        
        self.fogger_is_on = False
        self.fogger_intensity_value = 0

        self.initial_warmup_timer = QTimer(self)
        self.initial_warmup_timer.setSingleShot(True)
        self.initial_warmup_timer.timeout.connect(self._on_initial_warmup_finished)

        self.initial_progress_timer = QTimer(self)
        self.initial_progress_timer.setInterval(1000)
        self.initial_progress_timer.timeout.connect(self._update_initial_warmup_progress)
        self.initial_warmup_seconds = 0
        
        self.page_configs = {}
        self.page_instances = {}
        
        self._setup_page_configs()
        
        armenian_page = self._create_page_instance("ArmenianFlagPage")
        if armenian_page:
            armenian_page.preload()

        self.showFrame("StartupPage")

        self.exterior_intensity_changed.connect(lambda: self._update_master_slider_from_slaves("Exterior Lights"))
        self.interior_intensity_changed.connect(lambda: self._update_master_slider_from_slaves("Interior Lights"))

    def keyPressEvent(self, event):
        try:
            key_name = Qt.Key(event.key()).name
        except ValueError:
            key_name = f"Unknown Key ({event.key()})"
        
        self.logger.log(f"Key Press: {key_name}")

        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()
        elif event.key() == Qt.Key.Key_F1:
            self.showFullScreen()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        self.logger.log("Application closing.")
        self.logger.close()
        super().closeEvent(event)
            
    def _get_global_stylesheet(self):
        try:
            with open(resource_path("stylesheet.qss"), "r") as f:
                stylesheet_content = f.read()
            base_path = resource_path('.')
            final_stylesheet = stylesheet_content.replace(
                "%%RESOURCE_PATH%%", base_path.replace('\\', '/')
            )
            return final_stylesheet
        except FileNotFoundError:
            return ""

    def _setup_page_configs(self):
        page_configs = [
            ("StartupPage", StartupPage, {}),
            ("MainControlPage", MainControlPage, {"instance_attr": "main_control_page_instance"}),
            ("LaserProjectorPage", Led, {"light_control": True}),
            ("ScenesPage", Scene, {"master": True}),
            ("LightsPage", Light, {"master": True, "instance_attr": "lights_page"}),
            ("TopRingOutsideControlPage", TopRingOutside, {"light_control": True, "instance_attr": "TopRingOutsideControlPage"}),
            ("MiddleRingOutsideControlPage", MiddleRingOutside, {"light_control": True, "instance_attr": "MiddleRingOutsideControlPage"}),
            ("BottomRingOutsideControlPage", BottomRingOutside, {"light_control": True, "instance_attr": "BottomRingOutsideControlPage"}),
            ("TopRingInsideControlPage", TopRingInside, {"light_control": True, "instance_attr": "TopRingInsideControlPage"}),
            ("MiddleRingInsideControlPage", MiddleRingInside, {"light_control": True, "instance_attr": "MiddleRingInsideControlPage"}),
            ("BottomRingInsideControlPage", BottomRingInside, {"light_control": True, "instance_attr": "BottomRingInsideControlPage"}),
            ("PuckLightsControlPage", PuckLights, {"light_control": True, "instance_attr": "PuckLightsControlPage"}),
            ("UfoRingOutsideControlPage", UfoRing, {"light_control": True, "instance_attr": "UfoRingOutsideControlPage"}),
            ("UfoBeamControlPage", UfoBeam, {"light_control": True, "instance_attr": "UfoBeamControlPage"}),
            ("LightZone1ControlPage", RingGroup1, {"light_control": True, "instance_attr": "LightZone1ControlPage"}),
            ("LightZone2ControlPage", RingGroup2, {"light_control": True, "instance_attr": "LightZone2ControlPage"}),
            ("ArmenianFlagPage", ArmenianFlagPage, {}),
            ("WifiPage", WifiPage, {}),
        ]
        
        for name, page_class, config in page_configs:
            params = {'controller': self, 'logger': self.logger}
            
            if config.get("light_control"):
                params['mosaicClient'] = self.mosaicClient
            else:
                params['qlabsClient'] = self.qlabsClient
                if self.mosaicClient:
                    params['mosaicClient'] = self.mosaicClient

            if config.get("master"):
                params['master'] = self
            elif config.get("light_control"):
                params['master'] = self
            else: 
                params['parent'] = self
            
            self.page_configs[name] = {"class": page_class, "params": params, "config": config}

    def _create_page_instance(self, pageName):
        if pageName in self.page_instances:
            return self.page_instances[pageName]

        page_info = self.page_configs.get(pageName)
        if not page_info:
            print(f"Page '{pageName}' not found in configs.")
            return None

        params = page_info["params"].copy()
        config = page_info["config"]
        
        if config.get("light_control"):
            if not hasattr(self, 'lights_page'):
                self._create_page_instance("LightsPage")
            params.update({'light_instance_ref': self.lights_page, 'main_app_instance': self})
        
        sig = inspect.signature(page_info["class"].__init__)
        filtered_params = {k: v for k, v in params.items() if k in sig.parameters}
        
        widget = page_info["class"](**filtered_params)
        
        self.page_instances[pageName] = widget
        self.stacked_widget.addWidget(widget)

        if "instance_attr" in config:
            setattr(self, config["instance_attr"], widget)
        
        return widget

    def _preload_all_pages(self):
        pages_to_load = [
            "LightsPage",
            "TopRingOutsideControlPage", "MiddleRingOutsideControlPage", "BottomRingOutsideControlPage",
            "TopRingInsideControlPage", "MiddleRingInsideControlPage", "BottomRingInsideControlPage",
            "PuckLightsControlPage", "UfoRingOutsideControlPage", "UfoBeamControlPage",
            "LightZone1ControlPage", "LightZone2ControlPage",
            "LaserProjectorPage", "ScenesPage", "WifiPage"
        ]
        for page_name in pages_to_load:
            self._create_page_instance(page_name)

    def showFrame(self, pageName):
        self.logger.log(f"Navigating to page: {pageName}")
        
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'leave_page'):
            current_widget.leave_page()
            
        widget = self._create_page_instance(pageName)
        if not widget:
            return

        self.stacked_widget.setCurrentWidget(widget)
        
        if hasattr(widget, 'enter_page'):
            widget.enter_page()

        if pageName == "MainControlPage" and not self._has_started_initial_warmup:
            self._has_started_initial_warmup = True
            QTimer.singleShot(0, self._preload_all_pages)
            QTimer.singleShot(0, self.start_initial_system_warmup)
    
    def start_initial_system_warmup(self):
        try:
            self.main_control_page_instance.scenes_button.setEnabled(False)

            off_icon = QIcon(resource_path('images/sceneOff.svg'))
            off_pixmap = off_icon.pixmap(QSize(30, 30))
            self.main_control_page_instance.scenes_icon_label.setPixmap(off_pixmap)
            
            self.main_control_page_instance.sliders["Foggers"].set_state('disabled')
            self.initial_warmup_seconds = 0
            self.main_control_page_instance.progress_bar.setMaximum(self.FOGGER_WARMUP_SECONDS)
            self.main_control_page_instance.progress_bar.setValue(0)
            self.main_control_page_instance.progress_bar.show()
            self.main_control_page_instance.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #52E538; border-radius: 10px;}")
            self.initial_progress_timer.start()
        except (AttributeError, KeyError) as e:
            print(f"CRITICAL WARNING: Could not configure UI for initial warm-up. Error: {e}")

        self.initial_warmup_timer.start(self.FOGGER_WARMUP_SECONDS * 1000)

    def _update_initial_warmup_progress(self):
        self.initial_warmup_seconds += 1
        if hasattr(self, 'main_control_page_instance'):
            remaining_seconds_total = self.FOGGER_WARMUP_SECONDS - self.initial_warmup_seconds
            minutes = remaining_seconds_total // 60
            seconds = remaining_seconds_total % 60
            time_format = f"{minutes}:{seconds:02d}"
            
            self.main_control_page_instance.progress_bar.setValue(self.initial_warmup_seconds)
            self.main_control_page_instance.progress_bar.setFormat(f"{time_format}")

    def _on_initial_warmup_finished(self):
        print("Initial 5-minute warmup UI finished.")
        self.initial_progress_timer.stop()
        
        try:
            self.main_control_page_instance.progress_bar.hide()
            self.main_control_page_instance.sliders["Foggers"].set_state('normal')
            self.main_control_page_instance.scenes_button.setEnabled(True)
            new_icon = QIcon(resource_path('images/scene.svg'))
            new_pixmap = new_icon.pixmap(QSize(30, 30))
            self.main_control_page_instance.scenes_icon_label.setPixmap(new_pixmap)
        except (AttributeError, KeyError) as e:
            print(f"Warning: Could not restore UI after initial warm-up. Error: {e}")

    def on_mister_change(self, is_on, level=None):
        self.logger.log(f"Mister state changed: is_on={is_on}, level={level}")
        
        udp_message = ""
        if level:
            udp_message = f"MST{level.upper()}"
        elif is_on:
            udp_message = "MSTON"
        else:
            udp_message = "MSTOFF"

        if self.mosaicClient and udp_message:
            self.mosaicClient.send_message(udp_message, [])
        else:
            print(f"NETWORK ERROR: Could not send mister command (is_on={is_on}, level={level})")

    def on_fogger_toggle(self):
        self.fogger_is_on = not self.fogger_is_on
        self.logger.log(f"Fogger Toggled: {'ON' if self.fogger_is_on else 'OFF'}")

        if self.fogger_is_on:
            if self.mosaicClient: self.mosaicClient.send_message("FOG1on", [])
        else:
            if self.mosaicClient: self.mosaicClient.send_message("FOG1OFF", [])
            self.fogger_intensity_value = 0

    def onSliderChange(self, slider_name, value):
        self.logger.log(f"Slider '{slider_name}' changed to value: {value}")
        
        try:
            if slider_name == "Foggers":
                if value > 0:
                    self.fogger_intensity_value = value
                    if not self.fogger_is_on:
                        self.fogger_is_on = True
                        if self.mosaicClient: self.mosaicClient.send_message("FOG1on", [])
                    
                    value_map = [0, 2, 4, 6, 8, 10]
                    final_value = value_map[value]
                    udp_message = f"FOG1{final_value}"
                    if self.mosaicClient: self.mosaicClient.send_message(udp_message, [])
                return

            osc_message = ""
            if slider_name == "Aux": 
                osc_message = f"/cue/AUX{round((value/100)*24)}/go"
            elif slider_name == "PA":
                prefix = "MIC"
                osc_value_map = [0, 2, 4, 6, 8, 10]
                final_osc_value = osc_value_map[value]
                osc_message = f"/cue/{prefix}{final_osc_value}/go"
            elif slider_name in ["Exterior Lights", "Interior Lights"]: 
                self._handle_master_light_slider_change(slider_name, value)
                return 

            if self.qlabsClient and osc_message:
                self.qlabsClient.send_message(osc_message, [])
                print(f"Sending OSC: {osc_message}")

        except Exception as e:
            print(f"NETWORK ERROR: Could not send message for {slider_name}. {e}")
    
    def _handle_master_light_slider_change(self, light_group_name, value):
        is_exterior = "Exterior" in light_group_name
        previous_value = self.previous_exterior_lights_value if is_exterior else self.previous_interior_lights_value
        delta = value - previous_value
        if is_exterior: self.previous_exterior_lights_value = value; slave_pages = self._get_slave_light_pages_outside()
        else: self.previous_interior_lights_value = value; slave_pages = self._get_slave_light_pages_inside()
        
        if not slave_pages: return
        
        slave_intensities = {p.get_current_intensity() for p in slave_pages}; synced = slave_intensities.issubset({0, 1})
        for page in slave_pages: page.adjust_intensity_by_delta(delta, synced)

    def _get_slave_light_pages_inside(self):
        page_names = ["TopRingInsideControlPage", "MiddleRingInsideControlPage", "BottomRingInsideControlPage"]
        return [self.page_instances.get(name) for name in page_names if self.page_instances.get(name)]
    
    def _get_slave_light_pages_outside(self):
        page_names = [
            "TopRingOutsideControlPage", "MiddleRingOutsideControlPage", "BottomRingOutsideControlPage", 
            "PuckLightsControlPage", "UfoRingOutsideControlPage", "UfoBeamControlPage",
            "LightZone1ControlPage", "LightZone2ControlPage"
        ]
        return [self.page_instances.get(name) for name in page_names if self.page_instances.get(name)]
    
    def _update_master_slider_from_slaves(self, light_group_name):
        is_exterior = "Exterior" in light_group_name
        slave_pages = self._get_slave_light_pages_outside() if is_exterior else self._get_slave_light_pages_inside()
        
        if not slave_pages: return

        def get_slider_val(p):
            if hasattr(p, 'slider') and p.slider is not None:
                return p.slider.slider_value()
            return -1

        try:
            max_slave_intensity = max(get_slider_val(p) for p in slave_pages)
            if max_slave_intensity == -1: max_slave_intensity = 0
        except (ValueError, AttributeError):
            max_slave_intensity = 0
        
        if hasattr(self, 'main_control_page_instance'):
            master_slider = self.main_control_page_instance.sliders[light_group_name].slider
            master_slider.blockSignals(True); target_value = min(max_slave_intensity, master_slider.maximum())
            master_slider.setValue(target_value); master_slider.blockSignals(False)
            if is_exterior: self.previous_exterior_lights_value = target_value
            else: self.previous_interior_lights_value = target_value

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec())