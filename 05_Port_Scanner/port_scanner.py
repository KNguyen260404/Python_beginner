#!/usr/bin/env python3
import sys
import socket
import threading
import time
import ipaddress
from queue import Queue
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QLineEdit, QSpinBox, QProgressBar,
                           QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                           QCheckBox, QGroupBox, QFormLayout, QMessageBox, QTabWidget,
                           QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer
from PyQt5.QtGui import QFont, QColor

# Danh sách các cổng phổ biến và dịch vụ tương ứng
COMMON_PORTS = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    115: "SFTP",
    123: "NTP",
    143: "IMAP",
    161: "SNMP",
    194: "IRC",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    587: "SMTP Submission",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS Proxy",
    1194: "OpenVPN",
    1433: "MS SQL",
    1521: "Oracle DB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    5938: "TeamViewer",
    6379: "Redis",
    8080: "HTTP Proxy",
    8443: "HTTPS Alt",
    27017: "MongoDB"
}

class ScannerSignals(QObject):
    """Tín hiệu cho scanner thread"""
    progress = pyqtSignal(int)
    port_result = pyqtSignal(str, int, bool, str, float)
    scan_complete = pyqtSignal()
    error = pyqtSignal(str)

class PortScanner(QThread):
    """Thread quét cổng mạng"""
    def __init__(self, target, port_range, timeout=1.0, scan_type="TCP", threads=100):
        super().__init__()
        self.target = target
        self.port_range = port_range
        self.timeout = timeout
        self.scan_type = scan_type
        self.max_threads = threads
        self.signals = ScannerSignals()
        
        self.queue = Queue()
        self.total_ports = len(port_range)
        self.ports_scanned = 0
        self.stop_scan = False
    
    def run(self):
        """Chạy quét cổng"""
        try:
            # Kiểm tra target hợp lệ
            try:
                socket.gethostbyname(self.target)
            except socket.gaierror:
                self.signals.error.emit(f"Không thể phân giải tên miền: {self.target}")
                return
            
            # Đưa các cổng vào hàng đợi
            for port in self.port_range:
                self.queue.put(port)
            
            # Tạo và khởi động các thread
            threads = []
            for _ in range(min(self.max_threads, self.total_ports)):
                thread = threading.Thread(target=self.scan_worker)
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            # Chờ tất cả các thread hoàn thành
            for thread in threads:
                thread.join()
            
            self.signals.scan_complete.emit()
            
        except Exception as e:
            self.signals.error.emit(f"Lỗi: {str(e)}")
    
    def scan_worker(self):
        """Worker thread để quét cổng"""
        while not self.queue.empty() and not self.stop_scan:
            port = self.queue.get()
            
            start_time = time.time()
            is_open = False
            service = COMMON_PORTS.get(port, "Unknown")
            
            try:
                if self.scan_type == "TCP":
                    is_open = self.scan_tcp_port(port)
                elif self.scan_type == "UDP":
                    is_open = self.scan_udp_port(port)
                elif self.scan_type == "SYN":
                    is_open = self.scan_syn_port(port)
            except Exception as e:
                print(f"Error scanning port {port}: {str(e)}")
            
            scan_time = time.time() - start_time
            
            # Báo cáo kết quả
            self.signals.port_result.emit(self.target, port, is_open, service, scan_time)
            
            # Cập nhật tiến trình
            self.ports_scanned += 1
            progress = int((self.ports_scanned / self.total_ports) * 100)
            self.signals.progress.emit(progress)
            
            # Giảm tải CPU
            time.sleep(0.01)
    
    def scan_tcp_port(self, port):
        """Quét cổng TCP"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        result = sock.connect_ex((self.target, port))
        sock.close()
        return result == 0
    
    def scan_udp_port(self, port):
        """Quét cổng UDP (đơn giản)"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        
        try:
            sock.sendto(b'', (self.target, port))
            sock.recvfrom(1024)
            return True
        except socket.timeout:
            return False
        except Exception:
            return False
        finally:
            sock.close()
    
    def scan_syn_port(self, port):
        """Giả lập quét SYN (thực tế cần quyền root và raw socket)"""
        # Trong thực tế, quét SYN cần sử dụng raw socket và quyền root
        # Đây chỉ là mô phỏng
        return self.scan_tcp_port(port)
    
    def stop(self):
        """Dừng quét"""
        self.stop_scan = True

class PortScannerApp(QMainWindow):
    """Ứng dụng quét cổng mạng"""
    def __init__(self):
        super().__init__()
        self.scanner = None
        self.scan_results = []  # [(target, port, is_open, service, scan_time)]
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        self.setWindowTitle("Port Scanner")
        self.setGeometry(100, 100, 900, 600)
        
        # Widget chính
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Tạo tab widget
        tabs = QTabWidget()
        
        # Tab quét
        scan_tab = QWidget()
        scan_layout = QVBoxLayout()
        
        # Nhóm cấu hình quét
        config_group = QGroupBox("Cấu hình quét")
        config_layout = QFormLayout()
        
        # Target input
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Nhập IP hoặc tên miền (vd: 192.168.1.1 hoặc example.com)")
        config_layout.addRow("Mục tiêu:", self.target_input)
        
        # Port range
        port_range_layout = QHBoxLayout()
        self.port_start = QSpinBox()
        self.port_start.setRange(1, 65535)
        self.port_start.setValue(1)
        self.port_end = QSpinBox()
        self.port_end.setRange(1, 65535)
        self.port_end.setValue(1000)
        port_range_layout.addWidget(self.port_start)
        port_range_layout.addWidget(QLabel("-"))
        port_range_layout.addWidget(self.port_end)
        config_layout.addRow("Dải cổng:", port_range_layout)
        
        # Scan type
        self.scan_type = QComboBox()
        self.scan_type.addItems(["TCP", "UDP", "SYN"])
        config_layout.addRow("Kiểu quét:", self.scan_type)
        
        # Timeout
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(1, 10)
        self.timeout_input.setValue(1)
        config_layout.addRow("Timeout (giây):", self.timeout_input)
        
        # Threads
        self.threads_input = QSpinBox()
        self.threads_input.setRange(1, 500)
        self.threads_input.setValue(100)
        config_layout.addRow("Số luồng:", self.threads_input)
        
        # Scan common ports only
        self.common_ports_only = QCheckBox("Chỉ quét các cổng phổ biến")
        config_layout.addRow("", self.common_ports_only)
        
        config_group.setLayout(config_layout)
        scan_layout.addWidget(config_group)
        
        # Scan controls
        controls_layout = QHBoxLayout()
        self.scan_button = QPushButton("Bắt đầu quét")
        self.scan_button.clicked.connect(self.start_scan)
        self.stop_button = QPushButton("Dừng")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.scan_button)
        controls_layout.addWidget(self.stop_button)
        scan_layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        scan_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Sẵn sàng")
        scan_layout.addWidget(self.status_label)
        
        # Results table
        self.results_table = QTableWidget(0, 5)
        self.results_table.setHorizontalHeaderLabels([
            "Mục tiêu", "Cổng", "Trạng thái", "Dịch vụ", "Thời gian (ms)"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        scan_layout.addWidget(QLabel("Kết quả quét:"))
        scan_layout.addWidget(self.results_table)
        
        scan_tab.setLayout(scan_layout)
        
        # Tab báo cáo
        report_tab = QWidget()
        report_layout = QVBoxLayout()
        
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        
        report_controls = QHBoxLayout()
        self.generate_report_button = QPushButton("Tạo báo cáo")
        self.generate_report_button.clicked.connect(self.generate_report)
        self.save_report_button = QPushButton("Lưu báo cáo")
        self.save_report_button.clicked.connect(self.save_report)
        report_controls.addWidget(self.generate_report_button)
        report_controls.addWidget(self.save_report_button)
        
        report_layout.addLayout(report_controls)
        report_layout.addWidget(self.report_text)
        
        report_tab.setLayout(report_layout)
        
        # Thêm các tab
        tabs.addTab(scan_tab, "Quét")
        tabs.addTab(report_tab, "Báo cáo")
        
        main_layout.addWidget(tabs)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def start_scan(self):
        """Bắt đầu quét cổng"""
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mục tiêu")
            return
        
        # Lấy dải cổng
        port_start = self.port_start.value()
        port_end = self.port_end.value()
        
        if port_start > port_end:
            QMessageBox.warning(self, "Lỗi", "Cổng bắt đầu phải nhỏ hơn hoặc bằng cổng kết thúc")
            return
        
        # Tạo danh sách cổng cần quét
        if self.common_ports_only.isChecked():
            ports = [p for p in COMMON_PORTS.keys() if port_start <= p <= port_end]
        else:
            ports = list(range(port_start, port_end + 1))
        
        # Cập nhật UI
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Đang quét {target}...")
        self.results_table.setRowCount(0)
        self.scan_results = []
        
        # Tạo và khởi động scanner thread
        self.scanner = PortScanner(
            target=target,
            port_range=ports,
            timeout=self.timeout_input.value(),
            scan_type=self.scan_type.currentText(),
            threads=self.threads_input.value()
        )
        
        self.scanner.signals.progress.connect(self.update_progress)
        self.scanner.signals.port_result.connect(self.add_result)
        self.scanner.signals.scan_complete.connect(self.scan_finished)
        self.scanner.signals.error.connect(self.show_error)
        
        self.scanner.start()
    
    def stop_scan(self):
        """Dừng quét cổng"""
        if self.scanner:
            self.scanner.stop()
            self.status_label.setText("Đã dừng quét")
            self.scan_button.setEnabled(True)
            self.stop_button.setEnabled(False)
    
    def update_progress(self, value):
        """Cập nhật thanh tiến trình"""
        self.progress_bar.setValue(value)
    
    def add_result(self, target, port, is_open, service, scan_time):
        """Thêm kết quả vào bảng"""
        # Lưu kết quả
        self.scan_results.append((target, port, is_open, service, scan_time))
        
        # Chỉ hiển thị cổng mở trong bảng
        if is_open:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            self.results_table.setItem(row, 0, QTableWidgetItem(target))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(port)))
            
            status_item = QTableWidgetItem("Mở")
            status_item.setForeground(QColor("green"))
            self.results_table.setItem(row, 2, status_item)
            
            self.results_table.setItem(row, 3, QTableWidgetItem(service))
            self.results_table.setItem(row, 4, QTableWidgetItem(f"{scan_time*1000:.2f}"))
    
    def scan_finished(self):
        """Xử lý khi quét hoàn tất"""
        self.status_label.setText("Quét hoàn tất")
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Đếm số cổng mở
        open_ports = sum(1 for _, _, is_open, _, _ in self.scan_results if is_open)
        QMessageBox.information(self, "Quét hoàn tất", 
                              f"Đã quét xong {len(self.scan_results)} cổng, tìm thấy {open_ports} cổng mở")
    
    def show_error(self, message):
        """Hiển thị thông báo lỗi"""
        self.status_label.setText(f"Lỗi: {message}")
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        QMessageBox.critical(self, "Lỗi", message)
    
    def generate_report(self):
        """Tạo báo cáo quét"""
        if not self.scan_results:
            QMessageBox.warning(self, "Cảnh báo", "Không có kết quả quét nào để tạo báo cáo")
            return
        
        # Tạo báo cáo
        report = []
        report.append("====== BÁO CÁO QUÉT CỔNG ======")
        report.append(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Mục tiêu: {self.scan_results[0][0]}")
        report.append(f"Kiểu quét: {self.scan_type.currentText()}")
        report.append(f"Số cổng đã quét: {len(self.scan_results)}")
        
        # Thống kê cổng mở
        open_ports = [(port, service) for _, port, is_open, service, _ in self.scan_results if is_open]
        report.append(f"Số cổng mở: {len(open_ports)}")
        report.append("\n=== CỔNG MỞ ===")
        
        if open_ports:
            for port, service in open_ports:
                report.append(f"Cổng {port}: {service}")
        else:
            report.append("Không tìm thấy cổng mở nào")
        
        # Hiển thị báo cáo
        self.report_text.setText("\n".join(report))
    
    def save_report(self):
        """Lưu báo cáo ra file"""
        if not self.report_text.toPlainText():
            QMessageBox.warning(self, "Cảnh báo", "Không có báo cáo nào để lưu")
            return
        
        try:
            with open(f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w") as f:
                f.write(self.report_text.toPlainText())
            QMessageBox.information(self, "Thành công", "Đã lưu báo cáo")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu báo cáo: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PortScannerApp()
    window.show()
    sys.exit(app.exec_())
