# pages/flagPage.py

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel
# MODIFIED: Import QTimer
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie
from utils import resource_path

class ArmenianFlagPage(QWidget):
    """
    A widget to display the animated Armenian flag GIF full-screen
    with a back button layered on top.
    """
    def __init__(self, parent, controller, qlabsClient, **kwargs):
        super().__init__(parent)
        self.controller = controller
        # NEW: Store the qlabsClient to send OSC messages
        self.qlabsClient = qlabsClient

        self.gif_label = QLabel(self)
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setScaledContents(True)

        self.movie = QMovie(resource_path("images/armenianFlag.gif"))
        self.gif_label.setMovie(self.movie)

        back_button = QPushButton("〈", self)
        back_button.setObjectName("BackButton")
        # MODIFIED: The back button now calls the new shared go_back method
        back_button.clicked.connect(self.go_back)
        back_button.move(20, 20)
        back_button.raise_()

        # NEW: Create and configure the 10-second timer
        self.return_timer = QTimer(self)
        self.return_timer.setSingleShot(True)  # The timer will only fire once
        self.return_timer.setInterval(10000)   # 10,000 milliseconds = 10 seconds
        # Connect the timer's timeout signal to the go_back method
        self.return_timer.timeout.connect(self.go_back)

    def preload(self):
        """
        Forces the QMovie to load data from disk by briefly
        starting and stopping it.
        """
        self.movie.start()
        self.movie.stop()
        self.movie.jumpToFrame(0)
        
    # MODIFIED: This method now contains all the logic for leaving the page.
    def go_back(self):
        """
        Stops the timer and animation, sends an OSC signal, and returns
        to the main control page.
        """
        self.controller.logger.log("Exiting Armenian Flag page.")
        self.return_timer.stop()
        self.movie.stop()
        
        # NEW: Send the OSC "stop" signal
        try:
            if self.qlabsClient:
                self.qlabsClient.send_message("/cue/ARAOFF/go", [])
                print("[OSC SENT] Armenian Flag Stop: /cue/ARAOFF/go")
        except Exception as e:
            print(f"NETWORK ERROR: Could not send OSC for Armenian Flag stop. {e}")

        self.controller.showFrame("MainControlPage")

    def enter_page(self):
        """
        A function to be called when this page is shown.
        Starts the GIF animation and the 10-second return timer.
        """
        self.movie.start()
        # NEW: Start the timer when the page is entered
        self.return_timer.start()

    def leave_page(self):
        """
        A function to be called when this page is hidden.
        Stops the GIF animation and timer to save resources.
        """
        self.movie.stop()
        # NEW: Stop the timer to prevent it from firing after leaving the page
        self.return_timer.stop()

    def resizeEvent(self, event):
        """
        This special function is called every time the page is resized.
        It ensures the background GIF label always fills the entire page.
        """
        super().resizeEvent(event)
        self.gif_label.resize(self.size())
