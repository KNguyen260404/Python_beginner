#!/usr/bin/env python3
import os
import sys
import time
import threading
import requests
import urllib.parse
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QProgressBar, QLineEdit, QFileDialog,
                            QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot


class DownloadThread(QThread):
    """Thread for downloading a chunk of a file"""
    progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(int, bool)
    error_signal = pyqtSignal(int, str)

    def __init__(self, url, start_byte, end_byte, chunk_id, save_path):
        super().__init__()
        self.url = url
        self.start_byte = start_byte
        self.end_byte = end_byte
        self.chunk_id = chunk_id
        self.save_path = save_path
        self.temp_file = f"{save_path}.part{chunk_id}"

    def run(self):
        try:
            # Create headers for range request
            headers = {'Range': f'bytes={self.start_byte}-{self.end_byte}'}
            
            # Make request
            response = requests.get(self.url, headers=headers, stream=True)
            
            if response.status_code not in [200, 206]:
                self.error_signal.emit(self.chunk_id, f"Error: HTTP {response.status_code}")
                return
                
            # Get total size for this chunk
            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0:
                total_size = self.end_byte - self.start_byte + 1
                
            # Download the chunk
            downloaded = 0
            with open(self.temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = int(downloaded / total_size * 100)
                        self.progress_signal.emit(self.chunk_id, progress)
            
            self.finished_signal.emit(self.chunk_id, True)
            
        except Exception as e:
            self.error_signal.emit(self.chunk_id, str(e))


class Downloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multithreaded Downloader")
        self.setMinimumSize(700, 500)
        
        self.threads = []
        self.download_path = ""
        self.filename = ""
        self.downloading = False
        self.file_size = 0
        
        self.init_ui()
        
    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        
        # Save location
        save_layout = QHBoxLayout()
        save_label = QLabel("Save to:")
        self.save_path = QLineEdit()
        self.save_path.setReadOnly(True)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_location)
        save_layout.addWidget(save_label)
        save_layout.addWidget(self.save_path)
        save_layout.addWidget(browse_btn)
        
        # Thread count
        thread_layout = QHBoxLayout()
        thread_label = QLabel("Number of threads:")
        self.thread_count = QSpinBox()
        self.thread_count.setMinimum(1)
        self.thread_count.setMaximum(32)
        self.thread_count.setValue(4)
        thread_layout.addWidget(thread_label)
        thread_layout.addWidget(self.thread_count)
        thread_layout.addStretch()
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Download")
        self.start_btn.clicked.connect(self.start_download)
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.pause_btn)
        action_layout.addWidget(self.cancel_btn)
        
        # Overall progress
        overall_layout = QHBoxLayout()
        overall_label = QLabel("Overall Progress:")
        self.overall_progress = QProgressBar()
        overall_layout.addWidget(overall_label)
        overall_layout.addWidget(self.overall_progress)
        
        # Thread progress table
        table_label = QLabel("Thread Progress:")
        self.progress_table = QTableWidget(0, 3)
        self.progress_table.setHorizontalHeaderLabels(["Thread #", "Progress", "Status"])
        self.progress_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.progress_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Add everything to main layout
        main_layout.addLayout(url_layout)
        main_layout.addLayout(save_layout)
        main_layout.addLayout(thread_layout)
        main_layout.addLayout(action_layout)
        main_layout.addLayout(overall_layout)
        main_layout.addWidget(table_label)
        main_layout.addWidget(self.progress_table)
        
        # Set the main widget
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def browse_location(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Download Location")
        if directory:
            self.save_path.setText(directory)
    
    def get_file_info(self, url):
        try:
            # Send HEAD request to get file info
            response = requests.head(url, allow_redirects=True)
            
            if response.status_code != 200:
                QMessageBox.warning(self, "Error", f"Failed to access URL: HTTP {response.status_code}")
                return False
            
            # Get file size
            self.file_size = int(response.headers.get('content-length', 0))
            
            # Get filename from Content-Disposition or URL
            if 'content-disposition' in response.headers:
                import re
                content_disposition = response.headers['content-disposition']
                filename = re.findall('filename="(.+)"', content_disposition)
                if filename:
                    self.filename = filename[0]
            
            if not self.filename:
                self.filename = os.path.basename(urllib.parse.urlparse(url).path)
            
            if not self.filename:
                self.filename = "download"
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get file information: {str(e)}")
            return False
    
    def start_download(self):
        url = self.url_input.text().strip()
        save_dir = self.save_path.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
            
        if not save_dir:
            QMessageBox.warning(self, "Error", "Please select a save location")
            return
            
        if not self.get_file_info(url):
            return
            
        # Set up download
        self.download_path = os.path.join(save_dir, self.filename)
        thread_count = self.thread_count.value()
        
        # If file size is unknown or too small, use single thread
        if self.file_size <= 0 or self.file_size < thread_count * 1024 * 10:  # Less than 10KB per thread
            thread_count = 1
            
        # Update UI
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.thread_count.setEnabled(False)
        self.downloading = True
        
        # Clear previous download threads
        self.threads = []
        
        # Set up progress table
        self.progress_table.setRowCount(thread_count)
        for i in range(thread_count):
            # Thread number
            self.progress_table.setItem(i, 0, QTableWidgetItem(f"Thread {i+1}"))
            
            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setValue(0)
            self.progress_table.setCellWidget(i, 1, progress_bar)
            
            # Status
            self.progress_table.setItem(i, 2, QTableWidgetItem("Starting..."))
        
        # Calculate chunk sizes
        if thread_count == 1:
            # Single thread download
            thread = DownloadThread(url, 0, self.file_size-1 if self.file_size > 0 else 0, 0, self.download_path)
            thread.progress_signal.connect(self.update_thread_progress)
            thread.finished_signal.connect(self.thread_finished)
            thread.error_signal.connect(self.thread_error)
            self.threads.append(thread)
            thread.start()
        else:
            # Multi-threaded download
            chunk_size = self.file_size // thread_count
            for i in range(thread_count):
                start_byte = i * chunk_size
                # Last thread gets the remainder
                end_byte = self.file_size - 1 if i == thread_count - 1 else (i + 1) * chunk_size - 1
                
                thread = DownloadThread(url, start_byte, end_byte, i, self.download_path)
                thread.progress_signal.connect(self.update_thread_progress)
                thread.finished_signal.connect(self.thread_finished)
                thread.error_signal.connect(self.thread_error)
                self.threads.append(thread)
                thread.start()
    
    @pyqtSlot(int, int)
    def update_thread_progress(self, thread_id, progress):
        # Update thread progress bar
        progress_bar = self.progress_table.cellWidget(thread_id, 1)
        if progress_bar:
            progress_bar.setValue(progress)
        
        # Update status
        self.progress_table.setItem(thread_id, 2, QTableWidgetItem(f"Downloading ({progress}%)"))
        
        # Update overall progress
        self.update_overall_progress()
    
    @pyqtSlot(int, bool)
    def thread_finished(self, thread_id, success):
        if success:
            self.progress_table.setItem(thread_id, 2, QTableWidgetItem("Completed"))
        
        # Check if all threads are finished
        all_finished = True
        for thread in self.threads:
            if thread.isRunning():
                all_finished = False
                break
        
        if all_finished:
            self.finalize_download()
    
    @pyqtSlot(int, str)
    def thread_error(self, thread_id, error_msg):
        self.progress_table.setItem(thread_id, 2, QTableWidgetItem(f"Error: {error_msg}"))
        
        # Check if all threads have errored out
        all_errored = True
        for i in range(len(self.threads)):
            status = self.progress_table.item(i, 2).text()
            if not status.startswith("Error"):
                all_errored = False
                break
        
        if all_errored:
            QMessageBox.critical(self, "Download Failed", "All download threads failed.")
            self.reset_ui()
    
    def update_overall_progress(self):
        if not self.threads:
            return
            
        total_progress = 0
        for i in range(len(self.threads)):
            progress_bar = self.progress_table.cellWidget(i, 1)
            if progress_bar:
                total_progress += progress_bar.value()
        
        overall_progress = total_progress // len(self.threads)
        self.overall_progress.setValue(overall_progress)
    
    def finalize_download(self):
        # For multi-threaded downloads, combine the chunks
        if len(self.threads) > 1:
            try:
                with open(self.download_path, 'wb') as outfile:
                    for i in range(len(self.threads)):
                        temp_file = f"{self.download_path}.part{i}"
                        with open(temp_file, 'rb') as infile:
                            outfile.write(infile.read())
                        os.remove(temp_file)
                
                QMessageBox.information(self, "Download Complete", 
                                       f"File downloaded successfully to:\n{self.download_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to combine file chunks: {str(e)}")
        else:
            # For single-threaded downloads, just rename the file
            try:
                temp_file = f"{self.download_path}.part0"
                if os.path.exists(temp_file):
                    os.rename(temp_file, self.download_path)
                QMessageBox.information(self, "Download Complete", 
                                       f"File downloaded successfully to:\n{self.download_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to finalize download: {str(e)}")
        
        self.reset_ui()
    
    def cancel_download(self):
        # Stop all threads
        for thread in self.threads:
            if thread.isRunning():
                thread.terminate()
                thread.wait()
        
        # Clean up temp files
        for i in range(len(self.threads)):
            temp_file = f"{self.download_path}.part{i}"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        QMessageBox.information(self, "Download Cancelled", "Download has been cancelled.")
        self.reset_ui()
    
    def reset_ui(self):
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.thread_count.setEnabled(True)
        self.overall_progress.setValue(0)
        self.threads = []
        self.downloading = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Downloader()
    window.show()
    sys.exit(app.exec_()) 