import sys
import threading
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QScrollArea, QTextEdit,
    QFrame, QRadioButton, QButtonGroup, QDialog, QDialogButtonBox,
    QGridLayout, QSizePolicy, QStyle, QStackedWidget, QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QSize, QPropertyAnimation
from PyQt5.QtGui import QFont, QPalette, QColor, QDesktopServices
import imaplib

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gmail Bulk Deleter - Help")
        self.setMinimumSize(700, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a1a;
                color: #00ffcc;
            }
            QTextEdit {
                background-color: #1a1a2e;
                color: #00ffcc;
                border: 2px solid #00ffcc;
                border-radius: 5px;
                padding: 15px;
                font-size: 13px;
                line-height: 1.6;
            }
            QPushButton {
                background-color: #00ffcc;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-family: 'Orbitron', sans-serif;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00cc99;
            }
        """)

        layout = QVBoxLayout(self)

        title = QLabel("📚 HELP & DOCUMENTATION")
        title.setFont(QFont("Orbitron", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #39ff14; margin-bottom: 10px;")
        layout.addWidget(title)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
            <h2 style="color: #39ff14;">🚀 Getting Started</h2>
            <p><b>Step 1: Enable Gmail IMAP</b></p>
            <ul>
                <li>Go to Gmail Settings → See all settings → Forwarding and POP/IMAP</li>
                <li>Enable IMAP access</li>
                <li>Click "Save Changes"</li>
            </ul>

            <p><b>Step 2: Create App Password</b></p>
            <ul>
                <li>Go to your Google Account → Security</li>
                <li>Enable 2-Step Verification (if not already enabled)</li>
                <li>Go to "App passwords" under 2-Step Verification</li>
                <li>Generate a new app password for "Mail"</li>
                <li>Copy the 16-character password</li>
            </ul>

            <h2 style="color: #39ff14;">📋 How to Use</h2>
            <p><b>1. Connect to Gmail</b></p>
            <ul>
                <li>Enter just your Gmail username (without @gmail.com)</li>
                <li>Enter your App Password (not regular password!)</li>
                <li>Click "CONNECT TO GMAIL"</li>
            </ul>

            <p><b>2. Select Folders</b></p>
            <ul>
                <li>Check the folders you want to scan/delete</li>
                <li>Use "SELECT ALL" or "DESELECT ALL" for convenience</li>
                <li>Common folders: INBOX, Sent, Spam, Drafts</li>
            </ul>

            <p><b>3. Choose Delete Mode</b></p>
            <ul>
                <li><b>Move to Trash:</b> Emails can be recovered from Trash folder</li>
                <li><b>Permanent Delete:</b> Emails are permanently deleted (cannot be recovered)</li>
            </ul>

            <p><b>4. Scan or Delete</b></p>
            <ul>
                <li><b>SCAN:</b> Count emails in selected folders (safe, no deletion)</li>
                <li><b>DELETE:</b> Delete emails from selected folders</li>
                <li><b>STOP:</b> Abort the current operation</li>
            </ul>

            <h2 style="color: #39ff14;">⚠️ Important Notes</h2>
            <ul>
                <li><b>Always scan first</b> to verify what will be deleted</li>
                <li><b>Permanent deletion cannot be undone</b></li>
                <li>Large deletions may take several minutes</li>
                <li>Keep the application open during deletion</li>
                <li>Gmail may have rate limits for bulk operations</li>
            </ul>

            <h2 style="color: #39ff14;">🔒 Security</h2>
            <ul>
                <li>Your credentials are <b>never stored</b></li>
                <li>Connection is encrypted via IMAP SSL</li>
                <li>Use App Passwords, not your main Gmail password</li>
                <li>Revoke App Password after use if desired</li>
            </ul>

            <h2 style="color: #39ff14;">❓ Troubleshooting</h2>
            <p><b>"Authentication failed" error:</b></p>
            <ul>
                <li>Make sure you're using an App Password, not your regular password</li>
                <li>Check that IMAP is enabled in Gmail settings</li>
                <li>Verify 2-Step Verification is enabled</li>
            </ul>

            <p><b>"Connection timeout" error:</b></p>
            <ul>
                <li>Check your internet connection</li>
                <li>Verify firewall/antivirus isn't blocking port 993</li>
                <li>Try disabling VPN if active</li>
            </ul>

            <p><b>Deletion is slow:</b></p>
            <ul>
                <li>Gmail IMAP has rate limits for bulk operations</li>
                <li>Large folders (10,000+ emails) will take time</li>
                <li>Be patient and don't close the application</li>
            </ul>

            <h2 style="color: #39ff14;">🌐 Resources</h2>
            <p>
                Visit <a href="https://angrysysops.com" style="color: #00ffff;">angrysysops.com</a>
                and <a href="https://playhackmenow.com" style="color: #00ffff;">playhackmenow.com</a>
                for more tools and information.
            </p>
        """)
        layout.addWidget(help_text)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

class CyberpunkGmailDeleter(QMainWindow):
    connection_success = pyqtSignal(object)
    auth_error = pyqtSignal(str)
    connection_error = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gmail Bulk Deleter - Provided by Angry Admin")
        self.setGeometry(120, 80, 880, 760)
        self.setMinimumSize(780, 680)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a1a;
                color: #00ffcc;
            }
            QLabel {
                font-family: 'Orbitron', sans-serif;
                font-size: 16px;
            }
            QLineEdit, QTextEdit {
                background-color: #1a1a2e;
                color: #00ffcc;
                border: 2px solid #00ffcc;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #00ffcc;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 12px 24px;
                font-family: 'Orbitron', sans-serif;
                font-weight: bold;
                font-size: 16px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #00cc99;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QCheckBox {
                font-family: 'Rajdhani', sans-serif;
                font-size: 14px;
                spacing: 8px;
                padding: 5px;
            }
            QRadioButton {
                font-family: 'Rajdhani', sans-serif;
                font-size: 14px;
                spacing: 8px;
                padding: 5px;
            }
            QFrame#cyberFrame {
                border: 2px solid #00ffcc;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
            }
            QScrollArea {
                background-color: #1a1a2e;
                border: 2px solid #00ffcc;
                border-radius: 5px;
            }
            QTextEdit {
                background-color: #000000;
                border: 2px solid #00ffcc;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                border-radius: 5px;
            }
        """)
        self.imap = None
        self.is_running = False
        self.folder_checks = {}
        self.connect_icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        self.connecting_icon = self.style().standardIcon(QStyle.SP_BrowserStop)
        self.connected_icon = self.style().standardIcon(QStyle.SP_DialogApplyButton)

        self.connection_success.connect(self.handle_connection_success)
        self.auth_error.connect(self.handle_auth_error)
        self.connection_error.connect(self.handle_connection_error)
        self.log_signal.connect(self._append_log)

        self.init_ui()

    def init_ui(self):
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { border: none; background-color: #0a0a1a; }")
        self.setCentralWidget(self.stack)

        self.login_widget = self.create_login_screen()
        self.main_widget = self.create_main_screen()

        self.stack.addWidget(self.login_widget)
        self.stack.addWidget(self.main_widget)
        self.stack.setCurrentWidget(self.login_widget)

        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("color: #00ffcc; font-size: 14px; padding: 5px;")
        self.status_bar.showMessage("🔌 Disconnected - Click HELP for setup instructions")

        # Initial log messages
        self.log("⚡ GMAIL BULK DELETER - PROVIDED BY ANGRY ADMIN")
        self.log("=" * 60)
        self.log("⚡ Click the HELP button for setup instructions")
        self.log("⚠️ You need a Gmail App Password to connect")
        self.log("⚙️ Ready for action. Connect to Gmail.")
        self.log("=" * 60)

    def create_login_screen(self):
        login_widget = QWidget()
        login_widget.setStyleSheet("background-color: #050510;")
        layout = QVBoxLayout(login_widget)
        layout.setContentsMargins(120, 80, 120, 80)
        layout.setSpacing(25)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("⚡ GMAIL BULK DELETER ⚡")
        title.setFont(QFont("Orbitron", 30, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        intro = QLabel("Enter your Gmail username and App Password to begin the purge.")
        intro.setAlignment(Qt.AlignCenter)
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #00ffcc; font-size: 14px;")
        layout.addWidget(intro)

        auth_frame = QFrame()
        auth_frame.setFrameShape(QFrame.StyledPanel)
        auth_frame.setObjectName("cyberFrame")
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setSpacing(15)

        auth_title = QLabel("🔐 AUTHENTICATION")
        auth_title.setFont(QFont("Orbitron", 20, QFont.Bold))
        auth_title.setAlignment(Qt.AlignCenter)
        auth_layout.addWidget(auth_title)

        auth_form = QGridLayout()
        auth_form.setHorizontalSpacing(15)
        auth_form.setVerticalSpacing(12)
        auth_form.setColumnStretch(1, 1)

        email_label = QLabel("USERNAME:")
        email_label.setStyleSheet("color: #39ff14; font-size: 16px;")
        email_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.username (without @gmail.com)")
        self.email_input.setMinimumHeight(40)
        self.email_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        password_label = QLabel("APP PASSWORD:")
        password_label.setStyleSheet("color: #39ff14; font-size: 16px;")
        password_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("16-character app password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        auth_form.addWidget(email_label, 0, 0)
        auth_form.addWidget(self.email_input, 0, 1)
        auth_form.addWidget(password_label, 1, 0)
        auth_form.addWidget(self.password_input, 1, 1)

        auth_layout.addLayout(auth_form)

        self.connect_btn = QPushButton("CONNECT TO GMAIL")
        self.connect_btn.setFont(QFont("Orbitron", 16, QFont.Bold))
        self.connect_btn.clicked.connect(self.connect_imap)
        self.connect_btn.setMinimumHeight(55)
        self.connect_btn.setIcon(self.connect_icon)
        self.connect_btn.setIconSize(QSize(28, 28))
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #39ff14;
                color: #050510;
                border: 2px solid #39ff14;
                border-radius: 8px;
                padding: 12px 28px;
            }
            QPushButton:hover {
                background-color: #2ed96a;
            }
            QPushButton:disabled {
                background-color: #144c28;
                color: #9cf5c6;
                border: 2px dashed #39ff14;
            }
        """)
        auth_layout.addWidget(self.connect_btn)

        self.login_feedback = QLabel("🔐 Use Gmail App Passwords, not your main password.")
        self.login_feedback.setAlignment(Qt.AlignCenter)
        self.login_feedback.setWordWrap(True)
        self.login_feedback.setStyleSheet("color: #00ffcc; font-size: 14px;")
        auth_layout.addWidget(self.login_feedback)

        layout.addWidget(auth_frame)

        help_button = QPushButton("Need HELP / SETUP? Click Here")
        help_button.setFont(QFont("Orbitron", 12, QFont.Bold))
        help_button.setFixedHeight(45)
        help_button.setStyleSheet("""
            QPushButton {
                background-color: #0099ff;
                color: #ffffff;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        help_button.clicked.connect(self.show_help)
        layout.addWidget(help_button)

        layout.addStretch()
        return login_widget

    def create_main_screen(self):
        self.main_scroll = QScrollArea()
        self.main_scroll.setWidgetResizable(True)
        self.main_scroll.setStyleSheet("QScrollArea { border: none; background-color: #0a0a1a; }")

        container = QWidget()
        container.setStyleSheet("background-color: #0a0a1a;")
        self.main_scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("⚡ GMAIL BULK DELETER ⚡")
        header.setFont(QFont("Orbitron", 28, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        subtitle_layout = QHBoxLayout()
        subtitle_layout.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Provided by Angry Admin | ")
        subtitle.setFont(QFont("Consolas", 12))
        subtitle.setStyleSheet("color: #ff00ff;")
        link1 = QLabel('<a href="https://angrysysops.com" style="color: #00ffff; text-decoration: none;">angrysysops.com</a>')
        link1.setFont(QFont("Consolas", 12))
        link1.setOpenExternalLinks(True)
        link2 = QLabel(' | <a href="https://playhackmenow.com" style="color: #00ffff; text-decoration: none;">playhackmenow.com</a>')
        link2.setFont(QFont("Consolas", 12))
        link2.setOpenExternalLinks(True)
        subtitle_layout.addWidget(subtitle)
        subtitle_layout.addWidget(link1)
        subtitle_layout.addWidget(link2)
        layout.addLayout(subtitle_layout)

        help_btn_layout = QHBoxLayout()
        help_btn_layout.setAlignment(Qt.AlignCenter)
        help_btn_layout.setSpacing(10)

        self.coffee_btn = QPushButton("BUY ME A COFFEE")
        self.coffee_btn.setFont(QFont("Orbitron", 11, QFont.Bold))
        self.coffee_btn.setFixedHeight(35)
        self.coffee_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffde59;
                color: #2c1f00;
                border-radius: 6px;
                padding: 6px 18px;
            }
            QPushButton:hover {
                background-color: #ffcc00;
            }
        """)
        self.coffee_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://buymeacoffee.com/angrysysops"))
        )

        self.youtube_btn = QPushButton("YOUTUBE")
        self.youtube_btn.setFont(QFont("Orbitron", 11, QFont.Bold))
        self.youtube_btn.setFixedHeight(35)
        self.youtube_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff0050;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px 18px;
            }
            QPushButton:hover {
                background-color: #cc0040;
            }
        """)
        self.youtube_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://www.youtube.com/channel/UCRTcKGl0neismSRpDMK_M4A?sub_confirmation=1")
            )
        )

        self.help_btn = QPushButton("HELP")
        self.help_btn.setFont(QFont("Orbitron", 11, QFont.Bold))
        self.help_btn.setFixedHeight(35)
        self.help_btn.setStyleSheet("""
            QPushButton {
                background-color: #0099ff;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px 18px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        self.help_btn.clicked.connect(self.show_help)

        help_btn_layout.addWidget(self.coffee_btn)
        help_btn_layout.addWidget(self.youtube_btn)
        help_btn_layout.addWidget(self.help_btn)
        layout.addLayout(help_btn_layout)

        folder_frame = QFrame()
        folder_frame.setObjectName("cyberFrame")
        folder_layout_main = QVBoxLayout(folder_frame)
        folder_layout_main.setSpacing(10)

        folder_title = QLabel("📂 FOLDER SELECTION")
        folder_title.setFont(QFont("Orbitron", 18, QFont.Bold))
        folder_layout_main.addWidget(folder_title)

        folder_buttons_layout = QHBoxLayout()
        folder_buttons_layout.setSpacing(10)

        self.select_all_btn = QPushButton("🗂️ SELECT ALL")
        self.select_all_btn.setFont(QFont("Orbitron", 12, QFont.Bold))
        self.select_all_btn.setFixedHeight(45)
        self.select_all_btn.clicked.connect(self.select_all_folders)
        self.select_all_btn.setEnabled(False)

        self.deselect_all_btn = QPushButton("🗂️ DESELECT ALL")
        self.deselect_all_btn.setFont(QFont("Orbitron", 12, QFont.Bold))
        self.deselect_all_btn.setFixedHeight(45)
        self.deselect_all_btn.clicked.connect(self.deselect_all_folders)
        self.deselect_all_btn.setEnabled(False)

        folder_button_style = """
            QPushButton {
                background-color: #142248;
                color: #f7fbff;
                border: 1px solid #39ff14;
                border-radius: 6px;
                padding: 10px 24px;
            }
            QPushButton:hover {
                background-color: #1f3c78;
            }
            QPushButton:disabled {
                background-color: #0f1a33;
                color: #4dd0ff;
                border: 1px dashed #4dd0ff;
            }
        """
        self.select_all_btn.setStyleSheet(folder_button_style)
        self.deselect_all_btn.setStyleSheet(folder_button_style)

        folder_buttons_layout.addWidget(self.select_all_btn)
        folder_buttons_layout.addWidget(self.deselect_all_btn)
        folder_buttons_widget = QWidget()
        folder_buttons_widget.setLayout(folder_buttons_layout)
        folder_buttons_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        folder_layout_main.addWidget(folder_buttons_widget)

        self.folder_scroll = QScrollArea()
        self.folder_scroll.setWidgetResizable(True)
        self.folder_scroll.setMinimumHeight(180)
        self.folder_scroll.setMaximumHeight(220)

        self.folder_container = QWidget()
        self.folder_container.setStyleSheet("background-color: #1a1a2e;")
        self.folder_scroll.setWidget(self.folder_container)

        self.folder_layout = QVBoxLayout(self.folder_container)
        self.folder_layout.setSpacing(8)
        self.folder_layout.setContentsMargins(10, 10, 10, 10)

        self.folder_placeholder = QLabel("🔌 Connect to Gmail to load your folders...")
        self.folder_placeholder.setStyleSheet("""
            color: #00ffcc;
            font-style: italic;
            padding: 30px;
            font-size: 14px;
            background-color: transparent;
        """)
        self.folder_placeholder.setAlignment(Qt.AlignCenter)
        self.folder_layout.addWidget(self.folder_placeholder)

        folder_layout_main.addWidget(self.folder_scroll, 1)
        layout.addWidget(folder_frame)

        delete_mode_frame = QFrame()
        delete_mode_frame.setObjectName("cyberFrame")
        delete_mode_layout = QVBoxLayout(delete_mode_frame)
        delete_mode_layout.setSpacing(10)

        delete_mode_title = QLabel("⚠️ DELETE MODE")
        delete_mode_title.setFont(QFont("Orbitron", 18, QFont.Bold))
        delete_mode_layout.addWidget(delete_mode_title)

        self.delete_mode_group = QButtonGroup()
        self.trash_radio = QRadioButton("♻️ Move to Trash (Recoverable - Recommended)")
        self.trash_radio.setFont(QFont("Rajdhani", 14))
        self.trash_radio.setMinimumHeight(30)

        self.permanent_radio = QRadioButton("🗑️ Permanent Delete (NOT Recoverable - Use with Caution!)")
        self.permanent_radio.setFont(QFont("Rajdhani", 14))
        self.permanent_radio.setMinimumHeight(30)
        self.trash_radio.setChecked(True)

        delete_mode_layout.addWidget(self.trash_radio)
        delete_mode_layout.addWidget(self.permanent_radio)
        self.delete_mode_group.addButton(self.trash_radio)
        self.delete_mode_group.addButton(self.permanent_radio)

        layout.addWidget(delete_mode_frame)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)

        self.scan_btn = QPushButton("🔍 SCAN FOLDERS")
        self.scan_btn.setFont(QFont("Orbitron", 14, QFont.Bold))
        self.scan_btn.clicked.connect(self.scan_emails)
        self.scan_btn.setEnabled(False)
        self.scan_btn.setFixedHeight(50)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f4473;
                color: #e9f7ff;
                border: 2px solid #39ff14;
                border-radius: 8px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #1663a7;
            }
            QPushButton:disabled {
                background-color: #0a273d;
                color: #6fe1ff;
                border: 2px dashed #39c3ff;
            }
        """)

        self.delete_btn = QPushButton("⚠️ DELETE EMAILS")
        self.delete_btn.setFont(QFont("Orbitron", 14, QFont.Bold))
        self.delete_btn.clicked.connect(self.delete_emails)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setFixedHeight(50)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff3333;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)

        self.stop_btn = QPushButton("⛔ STOP")
        self.stop_btn.setFont(QFont("Orbitron", 14, QFont.Bold))
        self.stop_btn.clicked.connect(self.stop_process)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFixedHeight(50)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9900;
                color: #000000;
            }
            QPushButton:hover {
                background-color: #cc7700;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)

        action_layout.addWidget(self.scan_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addWidget(self.stop_btn)
        layout.addLayout(action_layout)

        terminal_frame = QFrame()
        terminal_frame.setObjectName("cyberFrame")
        terminal_layout = QVBoxLayout(terminal_frame)
        terminal_layout.setSpacing(10)

        terminal_title = QLabel("🖥️ TERMINAL OUTPUT")
        terminal_title.setFont(QFont("Orbitron", 18, QFont.Bold))
        terminal_layout.addWidget(terminal_title)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(220)
        self.terminal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        terminal_layout.addWidget(self.terminal)

        layout.addWidget(terminal_frame)
        return self.main_scroll

    def transition_to_main_screen(self):
        if self.stack.currentWidget() == self.main_widget:
            return

        login_effect = QGraphicsOpacityEffect()
        self.login_widget.setGraphicsEffect(login_effect)
        login_effect.setOpacity(1.0)

        fade_out = QPropertyAnimation(login_effect, b"opacity", self)
        fade_out.setDuration(450)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        def start_main_fade():
            self.login_widget.setGraphicsEffect(None)
            self.stack.setCurrentWidget(self.main_widget)
            main_effect = QGraphicsOpacityEffect()
            self.main_widget.setGraphicsEffect(main_effect)
            main_effect.setOpacity(0.0)

            fade_in = QPropertyAnimation(main_effect, b"opacity", self)
            fade_in.setDuration(450)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.finished.connect(lambda: self.main_widget.setGraphicsEffect(None))

            self.fade_in_animation = fade_in
            self.main_widget_effect = main_effect
            fade_in.start()

        fade_out.finished.connect(start_main_fade)
        self.fade_out_animation = fade_out
        self.login_widget_effect = login_effect
        fade_out.start()

    def show_help(self):
        help_dialog = HelpDialog(self)
        help_dialog.exec_()

    def log(self, message):
        if threading.current_thread() is threading.main_thread():
            self._append_log(message)
        else:
            self.log_signal.emit(message)

    def _append_log(self, message):
        self.terminal.append(message)
        scrollbar = self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def select_all_folders(self):
        for check in self.folder_checks.values():
            check.setChecked(True)
        self.log("✅ All folders selected.")

    def deselect_all_folders(self):
        for check in self.folder_checks.values():
            check.setChecked(False)
        self.log("✅ All folders deselected.")

    def connect_imap(self):
        username = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            self.log('\u26a0\ufe0f Error: Username and password are required!')
            self.log('\U0001f4a1 Tip: Click HELP for setup instructions')
            if hasattr(self, 'login_feedback'):
                self.login_feedback.setText('\u26a0\ufe0f Enter both username and App Password to continue.')
            return

        if '@' not in username:
            email = f"{username}@gmail.com"
            self.log(f'\U0001f4e7 Using email: {email}')
        else:
            email = username
            self.log(f'\U0001f4e7 Using email: {email}')
        self.log(f"\U0001f50c Connecting to Gmail...")
        self.status_bar.showMessage('\U0001f50c Connecting...')
        if hasattr(self, 'login_feedback'):
            self.login_feedback.setText('\U0001f50c Connecting to Gmail...')
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText('CONNECTING...')
        self.connect_btn.setIcon(self.connecting_icon)

        def connect_thread():
            try:
                imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
                imap.login(email, password)
                self.connection_success.emit(imap)
            except imaplib.IMAP4.error as e:
                self.auth_error.emit(str(e))
            except Exception as e:
                self.connection_error.emit(str(e))

        threading.Thread(target=connect_thread, daemon=True).start()

    def handle_connection_success(self, imap):
        self.imap = imap
        self.log('\u2705 Connected successfully!')
        self.status_bar.showMessage('\U0001f50c Connected to Gmail')
        self.connect_btn.setText('CONNECTED')
        self.connect_btn.setIcon(self.connected_icon)
        if hasattr(self, 'login_feedback'):
            self.login_feedback.setText('\u2705 Connected! Loading folders...')
        self.transition_to_main_screen()
        self.load_folders()

    def handle_auth_error(self, error):
        self.log(f'\u274c Authentication Error: {error}')
        self.log('\U0001f4a1 Make sure you\'re using an App Password, not your regular Gmail password')
        self.log('\U0001f4a1 Click HELP for instructions on creating an App Password')
        self.status_bar.showMessage('\u274c Authentication Failed')
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText('CONNECT TO GMAIL')
        self.connect_btn.setIcon(self.connect_icon)
        if hasattr(self, 'login_feedback'):
            self.login_feedback.setText(f'\u274c Authentication Error: {error}')

    def handle_connection_error(self, error):
        self.log(f'\u274c Connection Error: {error}')
        self.log('\U0001f4a1 Check your internet connection and firewall settings')
        self.status_bar.showMessage('\u274c Connection Error')
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText('CONNECT TO GMAIL')
        self.connect_btn.setIcon(self.connect_icon)
        if hasattr(self, 'login_feedback'):
            self.login_feedback.setText(f'\u274c Connection Error: {error}')

    def load_folders(self):
        try:
            if self.folder_placeholder:
                self.folder_placeholder.deleteLater()
                self.folder_placeholder = None

            status, folders = self.imap.list()
            if status == "OK":
                self.log("📁 Loading folders...")
                folder_count = 0

                for folder in folders:
                    folder_name = folder.decode().split('"')[-2]
                    if folder_name not in ["[Gmail]", "Notes"]:
                        check = QCheckBox(folder_name)
                        check.setStyleSheet("color: #00ffcc; font-size: 14px;")
                        check.setMinimumHeight(25)
                        self.folder_layout.addWidget(check)
                        self.folder_checks[folder_name] = check
                        folder_count += 1

                self.scan_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.select_all_btn.setEnabled(True)
                self.deselect_all_btn.setEnabled(True)
                self.log(f"📁 Loaded {folder_count} folders successfully!")
                self.log("💡 Select folders and click SCAN to count emails")
            else:
                self.log("❌ Failed to load folders.")
        except Exception as e:
            self.log(f"❌ Error loading folders: {e}")

    def scan_emails(self):
        selected_folders = [folder for folder, check in self.folder_checks.items() if check.isChecked()]
        if not selected_folders:
            self.log("⚠️ Error: No folders selected!")
            self.log("💡 Select at least one folder to scan")
            return

        self.log("=" * 60)
        self.log("🔍 Starting scan operation...")
        self.status_bar.showMessage("🔍 Scanning folders...")
        self.scan_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        def scan_thread():
            try:
                total_emails = 0
                for folder in selected_folders:
                    if not self.is_running:
                        self.log("⏹️ Scan stopped by user")
                        break
                    self.log(f"📁 Scanning: {folder}")
                    quoted_folder = f'"{folder}"' if any(c in folder for c in ['/', ' ', '\\']) else folder
                    status, _ = self.imap.select(quoted_folder, readonly=True)
                    if status != "OK":
                        self.log(f"❌ Failed to access folder: {folder}")
                        continue
                    status, messages = self.imap.search(None, "ALL")
                    if status == "OK":
                        count = len(messages[0].split())
                        total_emails += count
                        self.log(f"   └─ Found {count:,} emails")
                    else:
                        self.log(f"❌ Failed to search folder: {folder}")

                self.log("─" * 60)
                self.log(f"📊 SCAN COMPLETE: Total {total_emails:,} emails in {len(selected_folders)} folders")
                self.log("=" * 60)
                self.status_bar.showMessage(f"📊 Scan complete - {total_emails:,} emails found")
            except Exception as e:
                self.log(f"❌ Scan Error: {e}")
                self.status_bar.showMessage("❌ Scan Error")
            finally:
                self.scan_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.is_running = False

        self.is_running = True
        threading.Thread(target=scan_thread, daemon=True).start()

    def delete_emails(self):
        selected_folders = [folder for folder, check in self.folder_checks.items() if check.isChecked()]
        if not selected_folders:
            self.log("⚠️ Error: No folders selected!")
            self.log("💡 Select at least one folder to delete from")
            return

        is_permanent = self.permanent_radio.isChecked()
        mode_text = "PERMANENT DELETION" if is_permanent else "MOVE TO TRASH"

        self.log("=" * 60)
        self.log(f"🗑️ Starting deletion operation - Mode: {mode_text}")
        self.log(f"📁 Folders to process: {len(selected_folders)}")
        self.status_bar.showMessage(f"🗑️ Deleting emails - {mode_text}")
        self.scan_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        def delete_thread():
            try:
                total_deleted = 0
                for folder in selected_folders:
                    if not self.is_running:
                        self.log("⏹️ Deletion stopped by user")
                        break
                    self.log(f"🗑️ Processing folder: {folder}")
                    quoted_folder = f'"{folder}"' if any(c in folder for c in ['/', ' ', '\\']) else folder
                    status, _ = self.imap.select(quoted_folder)
                    if status != "OK":
                        self.log(f"❌ Failed to access folder: {folder}")
                        continue
                    status, messages = self.imap.uid('SEARCH', None, "ALL")
                    if status == "OK":
                        email_uids = messages[0].split()
                        if not email_uids:
                            self.log(f"   └─ No emails to delete in {folder}")
                            continue
                        count = len(email_uids)
                        self.log(f"   └─ Deleting {count:,} emails...")

                        trash_msgids = []
                        for i, email_uid in enumerate(email_uids, 1):
                            if not self.is_running:
                                break

                            if is_permanent:
                                msg_id = self._prepare_permanent_delete(email_uid)
                                if not msg_id:
                                    self.log("   └─ ⚠️ Failed to prepare email for permanent removal, skipping.")
                                    continue
                                trash_msgids.append(msg_id)
                            else:
                                if not self._move_to_trash(email_uid):
                                    self.log("   └─ ⚠️ Failed to move an email to Trash, skipping.")
                                    continue

                            if i % 100 == 0:
                                self.log(f"   └─ Progress: {i}/{count} ({(i/count*100):.1f}%)")

                        if is_permanent:
                            self._delete_permanently(trash_msgids, quoted_folder)
                        else:
                            self.imap.expunge()
                        total_deleted += count
                        self.log(f"   └─ ✅ Deleted {count:,} emails from {folder}")

                self.log("─" * 60)
                self.log(f"🗑️ DELETION COMPLETE: {total_deleted:,} emails deleted")
                self.log("=" * 60)
                self.status_bar.showMessage(f"🗑️ Deletion complete - {total_deleted:,} emails deleted")
            except Exception as e:
                self.log(f"❌ Deletion Error: {e}")
                self.status_bar.showMessage("❌ Deletion Error")
            finally:
                self.scan_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.is_running = False

        self.is_running = True
        threading.Thread(target=delete_thread, daemon=True).start()

    def _uid_to_str(self, email_uid):
        if isinstance(email_uid, bytes):
            return email_uid.decode()
        return str(email_uid)

    def _move_to_trash(self, email_uid):
        """
        Move the given email (by UID) to Gmail Trash and flag it as deleted.
        Returns True on success, False otherwise.
        """
        uid = self._uid_to_str(email_uid)
        status, _ = self.imap.uid('COPY', uid, '[Gmail]/Trash')
        if status != 'OK':
            return False
        status, _ = self.imap.uid('STORE', uid, '+FLAGS.SILENT', '(\\Deleted)')
        return status == 'OK'

    def _prepare_permanent_delete(self, email_uid):
        """
        Move the message into Gmail Trash and return its Gmail message ID so we can delete forever.
        """
        uid = self._uid_to_str(email_uid)
        status, data = self.imap.uid('FETCH', uid, '(X-GM-MSGID)')
        if status != 'OK' or not data:
            return None

        msg_id = None
        for resp in data:
            if isinstance(resp, tuple):
                resp = resp[0]
            if not resp:
                continue
            decoded = resp.decode('utf-8', errors='ignore') if isinstance(resp, bytes) else str(resp)
            match = re.search(r'X-GM-MSGID (\d+)', decoded)
            if match:
                msg_id = match.group(1)
                break

        if not msg_id:
            return None

        status, _ = self.imap.uid('STORE', uid, '+X-GM-LABELS', '(\Trash)')
        if status != 'OK':
            return None
        self.imap.uid('STORE', uid, '-X-GM-LABELS', '(\Inbox)')
        return msg_id

    def _delete_permanently(self, msg_id_list, return_mailbox):
        if not msg_id_list:
            return
        try:
            status, _ = self.imap.select('[Gmail]/Trash')
            if status != 'OK':
                self.log('?? Unable to access Gmail Trash for permanent deletion.')
                return

            trash_uids = []
            for msg_id in msg_id_list:
                search_status, search_data = self.imap.uid('SEARCH', None, 'X-GM-MSGID', msg_id)
                if search_status == 'OK' and search_data and search_data[0]:
                    trash_uids.extend(search_data[0].decode().split())

            if not trash_uids:
                self.log('?? No matching messages located in Trash for permanent removal.')
                return

            uid_set = ','.join(trash_uids)
            self.imap.uid('STORE', uid_set, '+FLAGS.SILENT', '(\Deleted)')
            self.imap.uid('EXPUNGE', uid_set)
        except Exception as e:
            self.log(f'?? Error while permanently deleting from Trash: {e}')
        finally:
            try:
                self.imap.select(return_mailbox)
            except Exception:
                pass
    def stop_process(self):
        self.is_running = False
        self.log("⏹️ Stopping operation...")
        self.status_bar.showMessage("⏹️ Stopped")
        self.scan_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def closeEvent(self, event):
        self.is_running = False
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
                self.log("🔌 Disconnected from Gmail")
            except:
                pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(10, 10, 10))
    palette.setColor(QPalette.WindowText, QColor(0, 255, 204))
    palette.setColor(QPalette.Base, QColor(26, 26, 46))
    palette.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 255, 204))
    palette.setColor(QPalette.ToolTipText, QColor(10, 10, 10))
    palette.setColor(QPalette.Text, QColor(0, 255, 204))
    palette.setColor(QPalette.Button, QColor(0, 255, 204))
    palette.setColor(QPalette.ButtonText, QColor(10, 10, 10))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 127))
    app.setPalette(palette)
    window = CyberpunkGmailDeleter()
    window.show()
    sys.exit(app.exec_())
