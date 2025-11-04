# customSlider.py

from PyQt6.QtWidgets import QWidget, QSlider, QStyleOptionSlider, QStyle, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QFont, QIcon, QPixmap

# NEW: Import the helper function to handle asset paths
from utils import resource_path

class CustomSlider(QSlider):
    """A QSlider subclass with improved mouse handling and state management."""
    sliderReleased = pyqtSignal(int)

    def __init__(self, parent=None, qlabsClient=None, initial_state='disabled', callback_on_release=None, icon_path_on='images/sliderIconLights.svg', icon_path_off=None, **kwargs):
        super().__init__(parent)
        self.qlabsClient = qlabsClient
        self._callback_on_release = callback_on_release

        self.setOrientation(kwargs.get('orient', Qt.Orientation.Horizontal))
        self.setRange(kwargs.get('from_', 0), kwargs.get('to', 100))
        self.setSingleStep(kwargs.get('resolution', 1))
        self.setPageStep(kwargs.get('resolution', 1))
        self.setTickPosition(QSlider.TickPosition.NoTicks)
        self.setTickInterval(kwargs.get('tickinterval', self.singleStep()))

        # MODIFIED: Use resource_path to correctly locate the icons
        icon_on = QIcon(resource_path(icon_path_on))
        self.handle_pixmap_on = icon_on.pixmap(QSize(30, 30))

        # Use the 'off' icon if provided, otherwise fallback to the 'on' icon
        icon_path_off = icon_path_off if icon_path_off is not None else icon_path_on
        # MODIFIED: Use resource_path for the off icon as well
        icon_off = QIcon(resource_path(icon_path_off))
        self.handle_pixmap_off = icon_off.pixmap(QSize(30, 30))

        self.current_handle_pixmap = self.handle_pixmap_on

        self.set_state(initial_state)
        if self.orientation() == Qt.Orientation.Vertical:
            self.setMinimumWidth(30)
        else: # Horizontal
            self.setFixedHeight(30)

        self.sliderReleased.connect(self._handle_slider_release)

    def paintEvent(self, event):
        """Custom paint event to draw the handle manually for high quality."""
        super().paintEvent(event)
        opt = self.sliderStyleOption()
        handle_rect = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, self)
        
        painter = QPainter(self)
        painter.drawPixmap(handle_rect.topLeft(), self.current_handle_pixmap)

    def _handle_slider_release(self):
        if self._callback_on_release:
            self._callback_on_release(self.value())

    def _set_value_from_pos(self, pos: QPoint):
        value = self._value_from_position(pos)
        snapped_value = round(value / self.singleStep()) * self.singleStep()
        clamped_value = max(self.minimum(), min(self.maximum(), snapped_value))
        self.setValue(int(clamped_value))

    def mousePressEvent(self, event):
        if self.isEnabled() and event.button() == Qt.MouseButton.LeftButton:
            self._set_value_from_pos(event.pos())
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.isEnabled() and event.buttons() == Qt.MouseButton.LeftButton:
            self._set_value_from_pos(event.pos())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.sliderReleased.emit(self.value())

    def _value_from_position(self, pos: QPoint):
        opt = self.sliderStyleOption()
        groove_rect = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderGroove, self)

        if self.orientation() == Qt.Orientation.Horizontal:
            pos_in_groove = pos.x() - groove_rect.x()
            total_length = groove_rect.width()
        else: # Vertical
            pos_in_groove = groove_rect.height() - (pos.y() - groove_rect.y())
            total_length = groove_rect.height()

        if total_length <= 0: return self.value()

        normalized_pos = max(0.0, min(1.0, pos_in_groove / total_length))
        return self.minimum() + normalized_pos * (self.maximum() - self.minimum())

    def set_state(self, state: str):
        """Sets the visual and enabled state of the slider, and updates the icon."""
        is_disabled = state == 'disabled'
        
        if is_disabled:
            self.current_handle_pixmap = self.handle_pixmap_off
        else:
            self.current_handle_pixmap = self.handle_pixmap_on
            
        self.setDisabled(is_disabled)
        self.setStyleSheet(self._get_stylesheet(state))
        self.update()

    def sliderStyleOption(self):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        return opt

    def _get_stylesheet(self, state: str):
        base_style = """
            QSlider:horizontal {
                border: none;
                padding: 0 15px;
            }
            QSlider:vertical {
                border: none;
                padding: 15px 0;
            }

            QSlider::groove:vertical {
                background: #FFFFFF;
                width: 2px;
                border-radius: 0px;
                border: none;
            }

            QSlider::handle:vertical {
                background: transparent;
                border: none;
                width: 30px;
                height: 30px;
                margin: -14px -14px;
            }
            QSlider::sub-page:vertical {
                background: #FFFFFF;
                border-radius: 0px;
                border: none;
            }

            QSlider::groove:horizontal {
                background: #FFFFFF;
                height: 2px;
                border-radius: 0px;
                border: none;
            }
            QSlider::handle:horizontal {
                background: transparent;
                border: none;
                width: 30px;
                height: 30px;
                margin: -14px -14px;
            }
            QSlider::sub-page:horizontal {
                background: #FFFFFF;
                border-radius: 0px;
                border: none;
            }
        """
        if state == 'disabled':
            return base_style + """
                QSlider::groove:vertical:disabled, QSlider::groove:horizontal:disabled { background: #888888; border: none; }
                QSlider::handle:vertical:disabled, QSlider::handle:horizontal:disabled { background: transparent; border: none; }
                QSlider::sub-page:vertical:disabled, QSlider::sub-page:horizontal:disabled { background: #666666; border: none; }
            """
        return base_style

class LabeledSlider(QWidget):
    """A widget that wraps a CustomSlider. Now just a wrapper for layout purposes."""
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None, name="", **kwargs):
        super().__init__(parent)
        self.name = name
        self.orientation = kwargs.get('orient', Qt.Orientation.Horizontal)

        self.setStyleSheet("background-color: transparent;")

        if self.orientation == Qt.Orientation.Horizontal:
            self.main_layout = QVBoxLayout(self)
        else: # Vertical
            self.main_layout = QHBoxLayout(self)

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.setMouseTracking(True)

        self.slider = CustomSlider(parent=self, **kwargs)

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.slider)
        self.main_layout.addStretch()

    def set_state(self, state: str):
        """Passes the state change to the internal CustomSlider."""
        self.slider.set_state(state)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

    def slider_value(self):
        return self.slider.value()

    def set_slider_value(self, value: int):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self.update()

    def slider_released_signal(self):
        return self.slider.sliderReleased