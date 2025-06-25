#!/usr/bin/env python3
import sys
import time
import psutil
import socket
import threading
import json
import datetime
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QFormLayout, QComboBox, QCheckBox,
                           QLineEdit, QSpinBox, QMessageBox, QSplitter, QFrame, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread
from PyQt5.QtGui import QColor, QPalette, QFont

# Kích thước lịch sử dữ liệu
HISTORY_SIZE = 60  # 60 điểm dữ liệu

class NetworkStats:
    """Lớp thu thập thống kê mạng"""
    def __init__(self):
        self.interfaces = {}  # {interface_name: (bytes_sent, bytes_recv, packets_sent, packets_recv)}
        self.connections = []  # [(local_addr, remote_addr, status, pid, process_name)]
        self.history = {
            'time': deque(maxlen=HISTORY_SIZE),
            'bytes_sent': deque(maxlen=HISTORY_SIZE),
            'bytes_recv': deque(maxlen=HISTORY_SIZE),
            'connections': deque(maxlen=HISTORY_SIZE)
        }
        self.last_check = None
        self.last_bytes = None
    
    def update(self):
        """Cập nhật thống kê mạng"""
        # Lấy thông tin giao diện mạng
        net_io = psutil.net_io_counters(pernic=True)
        self.interfaces = {}
        
        for interface, stats in net_io.items():
            self.interfaces[interface] = (
                stats.bytes_sent,
                stats.bytes_recv,
                stats.packets_sent,
                stats.packets_recv
            )
        
        # Lấy thông tin kết nối
        self.connections = []
        for conn in psutil.net_connections(kind='inet'):
            try:
                if conn.pid:
                    process = psutil.Process(conn.pid)
                    process_name = process.name()
                else:
                    process_name = "Unknown"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown"
            
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
            
            self.connections.append((
                laddr,
                raddr,
                conn.status,
                conn.pid or 0,
                process_name
            ))
        
        # Cập nhật lịch sử
        now = time.time()
        self.history['time'].append(now)
        
        total_sent = sum(stats[0] for stats in self.interfaces.values())
        total_recv = sum(stats[1] for stats in self.interfaces.values())
        
        # Tính tốc độ
        if self.last_check is not None:
            time_diff = now - self.last_check
            bytes_sent_diff = total_sent - self.last_bytes[0]
            bytes_recv_diff = total_recv - self.last_bytes[1]
            
            # Bytes per second
            bytes_sent_rate = bytes_sent_diff / time_diff
            bytes_recv_rate = bytes_recv_diff / time_diff
            
            self.history['bytes_sent'].append(bytes_sent_rate)
            self.history['bytes_recv'].append(bytes_recv_rate)
        else:
            self.history['bytes_sent'].append(0)
            self.history['bytes_recv'].append(0)
        
        self.history['connections'].append(len(self.connections))
        
        self.last_check = now
        self.last_bytes = (total_sent, total_recv)
        
        return {
            'interfaces': self.interfaces,
            'connections': self.connections,
            'history': {
                'time': list(self.history['time']),
                'bytes_sent': list(self.history['bytes_sent']),
                'bytes_recv': list(self.history['bytes_recv']),
                'connections': list(self.history['connections'])
            }
        }

class NetworkMonitorCanvas(FigureCanvas):
    """Lớp hiển thị biểu đồ giám sát mạng"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(NetworkMonitorCanvas, self).__init__(self.fig)
        
        self.setParent(parent)
        
        # Dữ liệu biểu đồ
        self.times = []
        self.download_rates = []
        self.upload_rates = []
        self.connection_counts = []
        
        # Thiết lập biểu đồ
        self.setup_plot()
    
    def setup_plot(self):
        """Thiết lập biểu đồ"""
        self.axes.set_title('Băng thông mạng theo thời gian')
        self.axes.set_xlabel('Thời gian (s)')
        self.axes.set_ylabel('Tốc độ (KB/s)')
        self.axes.grid(True)
        
        # Tạo các đường
        self.download_line, = self.axes.plot([], [], 'b-', label='Tải xuống')
        self.upload_line, = self.axes.plot([], [], 'r-', label='Tải lên')
        
        # Tạo trục phụ cho số lượng kết nối
        self.ax2 = self.axes.twinx()
        self.ax2.set_ylabel('Số kết nối')
        self.connection_line, = self.ax2.plot([], [], 'g-', label='Kết nối')
        
        # Tạo legend
        lines = [self.download_line, self.upload_line, self.connection_line]
        labels = [line.get_label() for line in lines]
        self.axes.legend(lines, labels, loc='upper left')
        
        self.fig.tight_layout()
    
    def update_plot(self, stats):
        """Cập nhật dữ liệu biểu đồ"""
        history = stats['history']
        
        # Chuyển đổi thời gian tuyệt đối thành tương đối
        if history['time']:
            base_time = history['time'][0]
            times = [t - base_time for t in history['time']]
        else:
            times = []
        
        # Chuyển đổi bytes/s thành KB/s
        download_rates = [r / 1024 for r in history['bytes_recv']]
        upload_rates = [r / 1024 for r in history['bytes_sent']]
        
        self.times = times
        self.download_rates = download_rates
        self.upload_rates = upload_rates
        self.connection_counts = history['connections']
        
        # Cập nhật dữ liệu cho các đường
        self.download_line.set_data(self.times, self.download_rates)
        self.upload_line.set_data(self.times, self.upload_rates)
        self.connection_line.set_data(self.times, self.connection_counts)
        
        # Tự động điều chỉnh trục
        if self.times:
            self.axes.set_xlim(min(self.times), max(self.times) + 1)
            
            max_rate = max(
                max(self.download_rates) if self.download_rates else 0,
                max(self.upload_rates) if self.upload_rates else 0
            )
            self.axes.set_ylim(0, max_rate * 1.1 or 10)
            
            max_conn = max(self.connection_counts) if self.connection_counts else 10
            self.ax2.set_ylim(0, max_conn * 1.1 or 10)
        
        self.fig.canvas.draw_idle()

class NetworkMonitorApp(QMainWindow):
    """Ứng dụng giám sát mạng"""
    def __init__(self):
        super().__init__()
        self.network_stats = NetworkStats()
        self.setup_ui()
        
        # Bắt đầu cập nhật
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # Cập nhật mỗi giây
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        self.setWindowTitle("Network Monitor")
        self.setGeometry(100, 100, 1000, 600)
        
        # Widget chính
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Tạo tab widget
        tabs = QTabWidget()
        
        # Tab tổng quan
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        
        # Thêm biểu đồ
        self.plot_canvas = NetworkMonitorCanvas(width=8, height=4, dpi=100)
        overview_layout.addWidget(self.plot_canvas)
        
        # Thông tin tổng quan
        overview_stats = QGroupBox("Thống kê mạng")
        stats_layout = QFormLayout()
        
        self.download_rate_label = QLabel("0 KB/s")
        self.upload_rate_label = QLabel("0 KB/s")
        self.active_connections_label = QLabel("0")
        self.total_downloaded_label = QLabel("0 KB")
        self.total_uploaded_label = QLabel("0 KB")
        
        stats_layout.addRow("Tốc độ tải xuống:", self.download_rate_label)
        stats_layout.addRow("Tốc độ tải lên:", self.upload_rate_label)
        stats_layout.addRow("Kết nối đang hoạt động:", self.active_connections_label)
        stats_layout.addRow("Tổng dữ liệu đã tải xuống:", self.total_downloaded_label)
        stats_layout.addRow("Tổng dữ liệu đã tải lên:", self.total_uploaded_label)
        
        overview_stats.setLayout(stats_layout)
        overview_layout.addWidget(overview_stats)
        
        overview_tab.setLayout(overview_layout)
        
        # Tab kết nối
        connections_tab = QWidget()
        connections_layout = QVBoxLayout()
        
        self.connections_table = QTableWidget(0, 5)
        self.connections_table.setHorizontalHeaderLabels([
            "Địa chỉ cục bộ", "Địa chỉ từ xa", "Trạng thái", "PID", "Tiến trình"
        ])
        self.connections_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        connections_layout.addWidget(QLabel("Danh sách kết nối mạng:"))
        connections_layout.addWidget(self.connections_table)
        
        connections_tab.setLayout(connections_layout)
        
        # Tab giao diện mạng
        interfaces_tab = QWidget()
        interfaces_layout = QVBoxLayout()
        
        self.interfaces_table = QTableWidget(0, 5)
        self.interfaces_table.setHorizontalHeaderLabels([
            "Giao diện", "Bytes gửi", "Bytes nhận", "Gói tin gửi", "Gói tin nhận"
        ])
        self.interfaces_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        interfaces_layout.addWidget(QLabel("Thông tin giao diện mạng:"))
        interfaces_layout.addWidget(self.interfaces_table)
        
        interfaces_tab.setLayout(interfaces_layout)
        
        # Thêm các tab
        tabs.addTab(overview_tab, "Tổng quan")
        tabs.addTab(connections_tab, "Kết nối")
        tabs.addTab(interfaces_tab, "Giao diện mạng")
        
        main_layout.addWidget(tabs)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def update_stats(self):
        """Cập nhật thống kê mạng và giao diện"""
        stats = self.network_stats.update()
        
        # Cập nhật biểu đồ
        self.plot_canvas.update_plot(stats)
        
        # Cập nhật nhãn thống kê
        if stats['history']['bytes_recv']:
            download_rate = stats['history']['bytes_recv'][-1] / 1024  # KB/s
            self.download_rate_label.setText(f"{download_rate:.2f} KB/s")
        
        if stats['history']['bytes_sent']:
            upload_rate = stats['history']['bytes_sent'][-1] / 1024  # KB/s
            self.upload_rate_label.setText(f"{upload_rate:.2f} KB/s")
        
        self.active_connections_label.setText(str(len(stats['connections'])))
        
        # Tính tổng dữ liệu
        total_downloaded = sum(stats[1] for stats in stats['interfaces'].values()) / 1024  # KB
        total_uploaded = sum(stats[0] for stats in stats['interfaces'].values()) / 1024  # KB
        
        # Định dạng đơn vị phù hợp
        self.total_downloaded_label.setText(self.format_size(total_downloaded))
        self.total_uploaded_label.setText(self.format_size(total_uploaded))
        
        # Cập nhật bảng kết nối
        self.connections_table.setRowCount(0)
        for i, (laddr, raddr, status, pid, process_name) in enumerate(stats['connections']):
            self.connections_table.insertRow(i)
            self.connections_table.setItem(i, 0, QTableWidgetItem(laddr))
            self.connections_table.setItem(i, 1, QTableWidgetItem(raddr))
            self.connections_table.setItem(i, 2, QTableWidgetItem(status))
            self.connections_table.setItem(i, 3, QTableWidgetItem(str(pid)))
            self.connections_table.setItem(i, 4, QTableWidgetItem(process_name))
        
        # Cập nhật bảng giao diện mạng
        self.interfaces_table.setRowCount(0)
        for i, (interface, (bytes_sent, bytes_recv, packets_sent, packets_recv)) in enumerate(stats['interfaces'].items()):
            self.interfaces_table.insertRow(i)
            self.interfaces_table.setItem(i, 0, QTableWidgetItem(interface))
            self.interfaces_table.setItem(i, 1, QTableWidgetItem(self.format_size(bytes_sent / 1024)))
            self.interfaces_table.setItem(i, 2, QTableWidgetItem(self.format_size(bytes_recv / 1024)))
            self.interfaces_table.setItem(i, 3, QTableWidgetItem(str(packets_sent)))
            self.interfaces_table.setItem(i, 4, QTableWidgetItem(str(packets_recv)))
    
    def format_size(self, size_kb):
        """Định dạng kích thước từ KB sang đơn vị phù hợp"""
        if size_kb < 1024:
            return f"{size_kb:.2f} KB"
        elif size_kb < 1024 * 1024:
            return f"{size_kb/1024:.2f} MB"
        else:
            return f"{size_kb/(1024*1024):.2f} GB"
    
    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ"""
        self.update_timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NetworkMonitorApp()
    window.show()
    sys.exit(app.exec_()) 