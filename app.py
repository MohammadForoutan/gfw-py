import time
import webbrowser
import threading
import os
import sys
import yt_dlp
from urllib.parse import urlparse
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton, 
    QVBoxLayout, QMessageBox, QProgressBar, QComboBox, QFileDialog, QHBoxLayout
)

# GFW Proxy import (assumed it's correct)
from gfw.pyprox_HTTPS_current import start as gfw_proxy_start

# Set the ffmpeg path based on OS
def get_ffmpeg_path():
    if sys.platform == "win32":
        return os.path.join(os.path.dirname(__file__), 'ffmpeg', 'ffmpeg.exe')
    elif sys.platform == "darwin":  # macOS
        return os.path.join(os.path.dirname(__file__), 'ffmpeg', 'ffmpeg')
    else:  # Linux or Unix
        return os.path.join(os.path.dirname(__file__), 'ffmpeg', 'ffmpeg')


class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)

    def __init__(self, video_url, proxy, is_playlist, quality, audio_only, download_path):
        super().__init__()
        self.video_url = video_url
        self.proxy = proxy
        self.is_playlist = is_playlist
        self.quality = quality
        self.audio_only = audio_only
        self.download_path = download_path

    def run(self):
        # Get the FFmpeg location
        ffmpeg_path = get_ffmpeg_path()

        # Basic YDL options
        ydl_opts = {
            'progress_hooks': [self.progress_hook],
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_path,  # Specify FFmpeg binary
            'retries': 5,
            'noprogress': True,
            'ignoreerrors': True,
            'continuedl': False,
        }

        if self.proxy:
            ydl_opts['proxy'] = self.proxy

        if self.audio_only:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            # Set video quality based on user selection
            if self.quality == '720p':
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
            elif self.quality == '480p':
                ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best'
            elif self.quality == '1080p':
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
            else:
                ydl_opts['format'] = 'best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])
            self.finished_signal.emit("دانلود و ترکیب فایل‌ها با موفقیت به پایان رسید!")

        except Exception as e:
            self.finished_signal.emit(f"دانلود شکست خورد: {str(e)}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes', d.get('total_bytes_estimate', 0))

            if total_bytes > 0:
                progress = int(downloaded_bytes / total_bytes * 100)
                self.progress_signal.emit(progress)
        elif d['status'] == 'error':
            self.finished_signal.emit("دانلود شکست خورد. لطفا دوباره تلاش کنید.")


class YouTubeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def open_link(self, url):
        webbrowser.open(url)

    def init_ui(self):
        # Create the widgets
        self.note_label = QLabel("با باز بودن برنامه میتونید روی پورت ۴۵۰۰ یوتوب روی بدون فیلترشکن نگاه کنید")

        self.tut_label = QLabel('<a href="https://www.example.com">برای آموزش کلید کنید</a>')
        self.tut_label.linkActivated.connect(self.open_link)

        self.url_label = QLabel("YouTube Video URL:")
        self.url_input = QLineEdit(self)

        self.proxy_label = QLabel("Proxy (optional):")
        self.proxy_input = QLineEdit(self)
        self.proxy_input.setText("http://127.0.0.1:4500")

        self.playlist_checkbox = QCheckBox("Is this a playlist?", self)

        self.quality_label = QLabel("Select Quality:")
        self.quality_combo = QComboBox(self)
        self.quality_combo.addItems(['720p', '480p', '1080p'])
        self.quality_combo.setCurrentText('720p')

        self.audio_only_checkbox = QCheckBox("Download Audio Only (MP3)", self)

        self.path_label = QLabel("Download Path:")
        self.path_input = QLineEdit(self)
        self.path_input.setReadOnly(True)

        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_folder)

        self.set_default_download_path()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)

        self.progress_bar_note = QLabel("تکمیل شدن دانلود چند مرحله داره.\n"
                                        "۱. دانلود ویدیو\n"
                                        "۲. دانلود صدا\n"
                                        "۳. ترکیب کردن تصویر و صدا\n"
                                        "به همین دلیل ممکنه چند بار به صد درصد برسه.")

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.start_download)

        # Layout configuration
        layout = QVBoxLayout()
        layout.addWidget(self.note_label)
        layout.addWidget(self.tut_label)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.proxy_label)
        layout.addWidget(self.proxy_input)
        layout.addWidget(self.playlist_checkbox)
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_combo)
        layout.addWidget(self.audio_only_checkbox)
        layout.addWidget(self.path_label)
        layout.addWidget(self.path_input)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_bar_note)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.setWindowTitle('YouTube Video Downloader')
        self.setGeometry(100, 100, 400, 350)

    def set_default_download_path(self):
        if sys.platform == 'win32':
            default_path = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
        elif sys.platform == 'darwin':
            default_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        else:
            default_path = os.path.join(os.path.expanduser('~'), 'Downloads')

        self.path_input.setText(default_path)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.path_input.setText(folder)

    def start_download(self):
        video_url = self.url_input.text()
        proxy = self.proxy_input.text()
        is_playlist = self.playlist_checkbox.isChecked()
        quality = self.quality_combo.currentText()
        audio_only = self.audio_only_checkbox.isChecked()
        download_path = self.path_input.text()

        if not video_url:
            QMessageBox.warning(self, "Input Error", "لطفا لینک ویدیو یوتیوب را وارد کنید")
            return

        if not download_path:
            QMessageBox.warning(self, "Input Error", "لطفا مسیر ذخیره‌سازی را انتخاب کنید")
            return

        self.submit_button.setEnabled(False)

        self.download_thread = DownloadThread(video_url, proxy, is_playlist, quality, audio_only, download_path)
        self.download_thread.progress_signal.connect(self.update_progress_bar)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def download_finished(self, message):
        QMessageBox.information(self, "Download Status", message)
        self.submit_button.setEnabled(True)
        self.progress_bar.setValue(0)


if __name__ == '__main__':
    # Start the GFW proxy in a separate thread
    gfw_thread = threading.Thread(target=gfw_proxy_start)
    gfw_thread.daemon = True
    gfw_thread.start()
    time.sleep(1)

    app = QApplication(sys.argv)
    window = YouTubeApp()
    window.show()
    sys.exit(app.exec_())
