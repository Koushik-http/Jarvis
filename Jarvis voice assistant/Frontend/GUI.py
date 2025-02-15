from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

def initialize_directories():
    """Create necessary directories and files if they don't exist."""
    base_dir = os.getcwd()
    frontend_dir = os.path.join(base_dir, 'Frontend')
    file_dir = os.path.join(frontend_dir, 'Files')
    graphics_dir = os.path.join(frontend_dir, 'Graphics')

    # Create directories if they don't exist
    os.makedirs(file_dir, exist_ok=True)
    os.makedirs(graphics_dir, exist_ok=True)

    # Initialize required data files with default content
    required_files = {
        'Mic.data': 'False',
        'Status.data': '',
        'Text.data': '',
        'Responses.data': ''
    }

    for filename, default_content in required_files.items():
        file_path = os.path.join(file_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(default_content)

def query_modifier(query):
    """Modify the query to ensure proper formatting."""
    new_query = query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which",
                     "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word in query_words for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def answer_modifier(answer):
    """Modify the answer to ensure proper formatting."""
    lines = answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_timer()
        self.old_chat_messages = ""

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 10, 40, 100)
        layout.setSpacing(-100)

        # Chat text area
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)

        # Set text color
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(Qt.white))  # Change this to your desired color
        self.chat_text_edit.setCurrentCharFormat(text_format)
        
        # Set font and size
        font = QFont()
        font.setPointSize(13)  # Correct way to set font size
        self.chat_text_edit.setFont(font)
        
        # Set text color
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(Qt.white))
        self.chat_text_edit.setCurrentCharFormat(text_format)

        # GIF animation
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(self.get_graphics_path('Jarvis.gif'))
        movie.setScaledSize(QSize(450, 350))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            margin-right: 195px;
            border: none;
            margin-top: -30px
        """)
        self.status_label.setAlignment(Qt.AlignRight)

        # Add widgets to layout
        layout.addWidget(self.chat_text_edit)
        layout.addWidget(self.gif_label)
        layout.addWidget(self.status_label)
        
        self.setup_scrollbar_style()

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_messages)
        self.timer.timeout.connect(self.update_speech_recognition_text)
        self.timer.start(5)

    def setup_scrollbar_style(self):
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def load_messages(self):
        try:
            with open(self.get_temp_path('Responses.data'), 'r', encoding='utf-8') as file:
                messages = file.read()
                
            if messages and messages != self.old_chat_messages:
                self.add_message(messages, 'White')
                self.old_chat_messages = messages
        except Exception as e:
            print(f"Error loading messages: {e}")

    def update_speech_recognition_text(self):
        try:
            with open(self.get_temp_path('Status.data'), 'r', encoding='utf-8') as file:
                status = file.read()
            self.status_label.setText(status)
        except Exception as e:
            print(f"Error updating speech recognition text: {e}")

    def add_message(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        
        char_format = QTextCharFormat()
        char_format.setForeground(QColor(color))
        
        block_format = QTextBlockFormat()
        block_format.setTopMargin(10)
        block_format.setLeftMargin(10)
        
        cursor.setCharFormat(char_format)
        cursor.setBlockFormat(block_format)
        cursor.movePosition(cursor.End)
        cursor.insertText(f"{message}\n")
        self.chat_text_edit.setTextCursor(cursor)
        self.chat_text_edit.verticalScrollBar().setValue(
            self.chat_text_edit.verticalScrollBar().maximum()
        )

    @staticmethod
    def get_temp_path(filename):
        return os.path.join(os.getcwd(), 'Frontend', 'Files', filename)

    @staticmethod
    def get_graphics_path(filename):
        return os.path.join(os.getcwd(), 'Frontend', 'Graphics', filename)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        # Create a main layout for the screen
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # No margins

        # Create a container widget to center the GIF and other widgets
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)  # Center everything vertically and horizontally

        # GIF Setup
        self.gif_label = QLabel()
        movie = QMovie(self.get_graphics_path('Jarvis.gif'))  # Updated GIF name
        movie.setScaledSize(QSize(600, 450))  # Adjust size as needed
        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignCenter)
        movie.start()

        # Add GIF to the container layout
        container_layout.addWidget(self.gif_label)

        # Microphone Icon Setup
        self.mic_icon = QLabel()
        self.mic_icon.setFixedSize(150, 150)
        self.mic_icon.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_mic_icon()
        self.mic_icon.mousePressEvent = self.toggle_mic_icon

        # Status Label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            margin-bottom: 0;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)

        # Add other widgets to the container layout
        container_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        container_layout.addWidget(self.mic_icon, alignment=Qt.AlignCenter)

        # Add the container to the main layout
        main_layout.addWidget(container)

        # Set the main layout for the screen
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: black;")

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5)

    def update_status(self):
        try:
            with open(self.get_temp_path('Status.data'), 'r', encoding='utf-8') as file:
                status = file.read()
            self.status_label.setText(status)
        except Exception as e:
            print(f"Error updating status: {e}")

    def toggle_mic_icon(self, event=None):
        icon_name = 'Mic_on.png' if self.toggled else 'Mic_off.png'
        pixmap = QPixmap(self.get_graphics_path(icon_name))
        self.mic_icon.setPixmap(pixmap.scaled(60, 60))
        
        try:
            with open(self.get_temp_path('Mic.data'), 'w', encoding='utf-8') as file:
                file.write(str(not self.toggled))
        except Exception as e:
            print(f"Error toggling microphone: {e}")
            
        self.toggled = not self.toggled

    @staticmethod
    def get_temp_path(filename):
        return os.path.join(os.getcwd(), 'Frontend', 'Files', filename)

    @staticmethod
    def get_graphics_path(filename):
        return os.path.join(os.getcwd(), 'Frontend', 'Graphics', filename)

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(""))  # Spacer

        # Create and assign the ChatSection widget to self.chat_section
        self.chat_section = ChatSection()
        layout.addWidget(self.chat_section)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.parent_window = parent
        self.stacked_widget = stacked_widget
        self.setup_ui()
        self.draggable = True
        self.offset = None

    def setup_ui(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        # Title
        title_label = QLabel(f" {self.get_assistant_name()} AI   ")
        title_label.setStyleSheet("""
            color: black;
            font-size: 18px;
            background-color: white;
        """)

        # Navigation Buttons
        home_button = self.create_nav_button("Home.png", " Home", 
                                           lambda: self.stacked_widget.setCurrentIndex(0))
        chat_button = self.create_nav_button("Chats.png", " Chat", 
                                           lambda: self.stacked_widget.setCurrentIndex(1))
        
        # Window Control Buttons
        minimize_button = self.create_window_button("Minimize2.png", self.minimize_window)
        self.maximize_button = self.create_window_button("Maximize.png", self.maximize_window)
        close_button = self.create_window_button("Close.png", self.close_window)

        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(chat_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

    def create_nav_button(self, icon_name, text, callback):
        button = QPushButton()
        button.setIcon(QIcon(self.get_graphics_path(icon_name)))
        button.setText(text)
        button.clicked.connect(callback)
        button.setStyleSheet("""
            height: 40px;
            line-height: 40px;
            background-color: white;
            color: black;
        """)
        return button

    def create_window_button(self, icon_name, callback):
        button = QPushButton()
        button.setIcon(QIcon(self.get_graphics_path(icon_name)))
        button.setStyleSheet("background-color: white;")
        button.clicked.connect(callback)
        return button

    def minimize_window(self):
        self.parent_window.showMinimized()

    def maximize_window(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.maximize_button.setIcon(QIcon(self.get_graphics_path('Maximize.png')))
        else:
            self.parent_window.showMaximized()
            self.maximize_button.setIcon(QIcon(self.get_graphics_path('Minimize.png')))

    def close_window(self):
        self.parent_window.close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            self.parent_window.move(event.globalPos() - self.offset)

    @staticmethod
    def get_graphics_path(filename):
        return os.path.join(os.getcwd(), 'Frontend', 'Graphics', filename)

    @staticmethod
    def get_assistant_name():
        env_vars = dotenv_values(".env")
        return env_vars.get("Assistantname", "Assistant").capitalize()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove default window borders
        self.setWindowTitle("Jarvis Voice Assistant")
        self.setStyleSheet("background-color: black;")

        # Initialize directories and files
        initialize_directories()

        # Create a stacked widget to manage screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Add screens to the stacked widget
        self.initial_screen = InitialScreen()
        self.message_screen = MessageScreen()
        self.stacked_widget.addWidget(self.initial_screen)
        self.stacked_widget.addWidget(self.message_screen)

        # Add the custom top bar
        self.top_bar = CustomTopBar(self, self.stacked_widget)
        self.setMenuWidget(self.top_bar)

        # Set the initial screen
        self.stacked_widget.setCurrentIndex(0)

        # Set a minimum size for the window (optional)
        self.setMinimumSize(800, 600)

    def closeEvent(self, event):
        """Override close event to ensure proper cleanup."""
        # Add any cleanup logic here if needed
        event.accept()

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()