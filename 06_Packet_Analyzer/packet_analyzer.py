#!/usr/bin/env python3
import sys
import socket
import struct
import time
import threading
import os
from datetime import datetime
import scapy.all as scapy
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                           QHeaderView, QComboBox, QCheckBox, QGroupBox, QFormLayout,
                           QSpinBox, QMessageBox, QTabWidget, QSplitter, QFileDialog,
                           QLineEdit, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon

# Định nghĩa các giao thức phổ biến
PROTOCOLS = {
    1: "ICMP",
    6: "TCP",
    17: "UDP",
    2: "IGMP",
    8: "EGP",
    9: "IGP",
    41: "IPv6",
    50: "ESP",
    51: "AH",
    88: "EIGRP",
    89: "OSPF"
}

# Định nghĩa các cổng phổ biến
COMMON_PORTS = {
    20: "FTP-Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP-Server",
    68: "DHCP-Client",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    161: "SNMP",
    443: "HTTPS",
    3389: "RDP"
}

class PacketCaptureSignals(QObject):
    """Tín hiệu cho thread bắt gói tin"""
    packet_captured = pyqtSignal(object)
    capture_started = pyqtSignal()
    capture_stopped = pyqtSignal()
    error = pyqtSignal(str)

class PacketCapture(QThread):
    """Thread bắt gói tin"""
    def __init__(self, interface=None, filter_str="", count=0, timeout=None):
        super().__init__()
        self.interface = interface
        self.filter_str = filter_str
        self.count = count
        self.timeout = timeout
        self.signals = PacketCaptureSignals()
        self.stop_capture = False
    
    def run(self):
        """Chạy bắt gói tin"""
        try:
            self.signals.capture_started.emit()
            
            # Thiết lập tham số bắt gói tin
            kwargs = {}
            if self.interface:
                kwargs["iface"] = self.interface
            if self.filter_str:
                kwargs["filter"] = self.filter_str
            if self.count > 0:
                kwargs["count"] = self.count
            if self.timeout:
                kwargs["timeout"] = self.timeout
            
            # Bắt gói tin
            scapy.sniff(prn=self.process_packet, store=False, stop_filter=lambda _: self.stop_capture, **kwargs)
            
            if not self.stop_capture:
                self.signals.capture_stopped.emit()
        except Exception as e:
            self.signals.error.emit(f"Lỗi bắt gói tin: {str(e)}")
    
    def process_packet(self, packet):
        """Xử lý gói tin bắt được"""
        self.signals.packet_captured.emit(packet)
    
    def stop(self):
        """Dừng bắt gói tin"""
        self.stop_capture = True

class PacketAnalyzerApp(QMainWindow):
    """Ứng dụng phân tích gói tin"""
    def __init__(self):
        super().__init__()
        self.packet_capture = None
        self.packets = []  # Danh sách các gói tin đã bắt được
        self.setup_ui()
        
        # Lấy danh sách giao diện mạng
        self.get_interfaces()
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        self.setWindowTitle("Packet Analyzer")
        self.setGeometry(100, 100, 1200, 700)
        
        # Widget chính
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Nhóm cấu hình bắt gói tin
        config_group = QGroupBox("Cấu hình bắt gói tin")
        config_layout = QFormLayout()
        
        # Chọn giao diện mạng
        self.interface_combo = QComboBox()
        config_layout.addRow("Giao diện:", self.interface_combo)
        
        # Bộ lọc
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Nhập bộ lọc (vd: tcp port 80)")
        config_layout.addRow("Bộ lọc:", self.filter_input)
        
        # Số lượng gói tin tối đa
        self.count_input = QSpinBox()
        self.count_input.setRange(0, 10000)
        self.count_input.setValue(0)
        self.count_input.setSpecialValueText("Không giới hạn")
        config_layout.addRow("Số lượng gói tin:", self.count_input)
        
        # Timeout
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(0, 3600)
        self.timeout_input.setValue(0)
        self.timeout_input.setSpecialValueText("Không giới hạn")
        config_layout.addRow("Thời gian (giây):", self.timeout_input)
        
        config_group.setLayout(config_layout)
        
        # Các nút điều khiển
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Bắt đầu bắt gói tin")
        self.start_button.clicked.connect(self.start_capture)
        
        self.stop_button = QPushButton("Dừng")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        
        self.clear_button = QPushButton("Xóa dữ liệu")
        self.clear_button.clicked.connect(self.clear_data)
        
        self.save_button = QPushButton("Lưu gói tin")
        self.save_button.clicked.connect(self.save_packets)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addWidget(self.save_button)
        
        # Thêm config và control vào layout chính
        main_layout.addWidget(config_group)
        main_layout.addLayout(control_layout)
        
        # Tạo splitter cho phần hiển thị gói tin
        splitter = QSplitter(Qt.Vertical)
        
        # Bảng danh sách gói tin
        self.packet_table = QTableWidget(0, 7)
        self.packet_table.setHorizontalHeaderLabels([
            "No.", "Thời gian", "Nguồn", "Đích", "Giao thức", "Độ dài", "Thông tin"
        ])
        self.packet_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.packet_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.packet_table.itemSelectionChanged.connect(self.packet_selected)
        
        # Chi tiết gói tin
        detail_widget = QWidget()
        detail_layout = QVBoxLayout()
        
        self.packet_tree = QTreeWidget()
        self.packet_tree.setHeaderLabels(["Phần", "Giá trị"])
        self.packet_tree.setColumnWidth(0, 300)
        
        self.packet_hex = QTextEdit()
        self.packet_hex.setReadOnly(True)
        self.packet_hex.setFont(QFont("Courier New", 10))
        
        detail_tabs = QTabWidget()
        
        tree_tab = QWidget()
        tree_layout = QVBoxLayout()
        tree_layout.addWidget(self.packet_tree)
        tree_tab.setLayout(tree_layout)
        
        hex_tab = QWidget()
        hex_layout = QVBoxLayout()
        hex_layout.addWidget(self.packet_hex)
        hex_tab.setLayout(hex_layout)
        
        detail_tabs.addTab(tree_tab, "Chi tiết gói tin")
        detail_tabs.addTab(hex_tab, "Hex View")
        
        detail_layout.addWidget(detail_tabs)
        detail_widget.setLayout(detail_layout)
        
        # Thêm các widget vào splitter
        splitter.addWidget(self.packet_table)
        splitter.addWidget(detail_widget)
        splitter.setSizes([300, 400])
        
        # Thêm splitter vào layout chính
        main_layout.addWidget(splitter, 1)
        
        # Thanh trạng thái
        self.status_label = QLabel("Sẵn sàng")
        main_layout.addWidget(self.status_label)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def get_interfaces(self):
        """Lấy danh sách giao diện mạng"""
        try:
            interfaces = scapy.get_if_list()
            self.interface_combo.addItems(interfaces)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lấy danh sách giao diện mạng: {str(e)}")
    
    def start_capture(self):
        """Bắt đầu bắt gói tin"""
        interface = self.interface_combo.currentText() if self.interface_combo.currentText() else None
        filter_str = self.filter_input.text()
        count = self.count_input.value()
        timeout = self.timeout_input.value() if self.timeout_input.value() > 0 else None
        
        try:
            self.packet_capture = PacketCapture(
                interface=interface,
                filter_str=filter_str,
                count=count,
                timeout=timeout
            )
            
            self.packet_capture.signals.packet_captured.connect(self.process_packet)
            self.packet_capture.signals.capture_started.connect(self.on_capture_started)
            self.packet_capture.signals.capture_stopped.connect(self.on_capture_stopped)
            self.packet_capture.signals.error.connect(self.show_error)
            
            self.packet_capture.start()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể bắt đầu bắt gói tin: {str(e)}")
    
    def stop_capture(self):
        """Dừng bắt gói tin"""
        if self.packet_capture:
            self.packet_capture.stop()
            self.status_label.setText("Đang dừng bắt gói tin...")
    
    def on_capture_started(self):
        """Xử lý khi bắt đầu bắt gói tin"""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Đang bắt gói tin...")
    
    def on_capture_stopped(self):
        """Xử lý khi dừng bắt gói tin"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Đã dừng bắt gói tin. Tổng số gói tin: {len(self.packets)}")
    
    def show_error(self, message):
        """Hiển thị thông báo lỗi"""
        self.status_label.setText(f"Lỗi: {message}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        QMessageBox.critical(self, "Lỗi", message)
    
    def process_packet(self, packet):
        """Xử lý gói tin bắt được"""
        # Lưu gói tin
        self.packets.append(packet)
        
        # Thêm vào bảng
        row = self.packet_table.rowCount()
        self.packet_table.insertRow(row)
        
        # Số thứ tự
        self.packet_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        
        # Thời gian
        timestamp = packet.time
        time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]
        self.packet_table.setItem(row, 1, QTableWidgetItem(time_str))
        
        # Nguồn và đích
        src = ""
        dst = ""
        protocol = ""
        info = ""
        
        # Xử lý theo loại gói tin
        if packet.haslayer(scapy.Ether):
            if packet.haslayer(scapy.IP):
                src = packet[scapy.IP].src
                dst = packet[scapy.IP].dst
                proto_num = packet[scapy.IP].proto
                protocol = PROTOCOLS.get(proto_num, str(proto_num))
                
                # Thông tin chi tiết theo giao thức
                if packet.haslayer(scapy.TCP):
                    sport = packet[scapy.TCP].sport
                    dport = packet[scapy.TCP].dport
                    flags = self.get_tcp_flags(packet[scapy.TCP])
                    
                    src_port = COMMON_PORTS.get(sport, str(sport))
                    dst_port = COMMON_PORTS.get(dport, str(dport))
                    
                    src = f"{src}:{src_port}"
                    dst = f"{dst}:{dst_port}"
                    info = f"TCP {sport} → {dport} {flags}"
                    
                elif packet.haslayer(scapy.UDP):
                    sport = packet[scapy.UDP].sport
                    dport = packet[scapy.UDP].dport
                    
                    src_port = COMMON_PORTS.get(sport, str(sport))
                    dst_port = COMMON_PORTS.get(dport, str(dport))
                    
                    src = f"{src}:{src_port}"
                    dst = f"{dst}:{dst_port}"
                    info = f"UDP {sport} → {dport}"
                    
                elif packet.haslayer(scapy.ICMP):
                    icmp_type = packet[scapy.ICMP].type
                    icmp_code = packet[scapy.ICMP].code
                    
                    if icmp_type == 8:
                        info = "ICMP Echo request"
                    elif icmp_type == 0:
                        info = "ICMP Echo reply"
                    else:
                        info = f"ICMP type={icmp_type}, code={icmp_code}"
            
            elif packet.haslayer(scapy.ARP):
                src = packet[scapy.ARP].psrc
                dst = packet[scapy.ARP].pdst
                protocol = "ARP"
                
                if packet[scapy.ARP].op == 1:
                    info = "ARP Request"
                else:
                    info = "ARP Reply"
            
            else:
                src = packet[scapy.Ether].src
                dst = packet[scapy.Ether].dst
                protocol = hex(packet[scapy.Ether].type)
                info = "Unknown Ethernet packet"
        
        # Độ dài gói tin
        length = len(packet)
        
        # Thêm thông tin vào bảng
        self.packet_table.setItem(row, 2, QTableWidgetItem(src))
        self.packet_table.setItem(row, 3, QTableWidgetItem(dst))
        self.packet_table.setItem(row, 4, QTableWidgetItem(protocol))
        self.packet_table.setItem(row, 5, QTableWidgetItem(str(length)))
        self.packet_table.setItem(row, 6, QTableWidgetItem(info))
        
        # Cuộn xuống hàng mới thêm
        self.packet_table.scrollToItem(self.packet_table.item(row, 0))
        
        # Cập nhật trạng thái
        self.status_label.setText(f"Đã bắt {len(self.packets)} gói tin")
    
    def get_tcp_flags(self, tcp_packet):
        """Lấy các cờ TCP"""
        flags = []
        
        if tcp_packet.flags.S:
            flags.append("SYN")
        if tcp_packet.flags.A:
            flags.append("ACK")
        if tcp_packet.flags.F:
            flags.append("FIN")
        if tcp_packet.flags.R:
            flags.append("RST")
        if tcp_packet.flags.P:
            flags.append("PSH")
        if tcp_packet.flags.U:
            flags.append("URG")
        
        return "[" + " ".join(flags) + "]"
    
    def packet_selected(self):
        """Xử lý khi chọn một gói tin trong bảng"""
        selected_rows = self.packet_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if row < 0 or row >= len(self.packets):
            return
        
        packet = self.packets[row]
        self.display_packet_details(packet)
        self.display_packet_hex(packet)
    
    def display_packet_details(self, packet):
        """Hiển thị chi tiết gói tin"""
        self.packet_tree.clear()
        
        # Hiển thị các lớp của gói tin
        for layer in packet.layers():
            layer_name = layer.__name__
            layer_item = QTreeWidgetItem([layer_name, ""])
            
            # Lấy các trường của lớp
            if packet.haslayer(layer):
                layer_packet = packet.getlayer(layer)
                for field in layer_packet.fields:
                    value = layer_packet.fields[field]
                    
                    # Định dạng giá trị
                    if isinstance(value, bytes):
                        try:
                            value_str = value.decode('utf-8', errors='replace')
                        except:
                            value_str = value.hex()
                    else:
                        value_str = str(value)
                    
                    field_item = QTreeWidgetItem([field, value_str])
                    layer_item.addChild(field_item)
            
            self.packet_tree.addTopLevelItem(layer_item)
            layer_item.setExpanded(True)
        
        # Mở rộng tất cả các mục
        self.packet_tree.expandAll()
    
    def display_packet_hex(self, packet):
        """Hiển thị gói tin dưới dạng hex"""
        raw_bytes = bytes(packet)
        hex_dump = self.format_hex_dump(raw_bytes)
        self.packet_hex.setText(hex_dump)
    
    def format_hex_dump(self, data, bytes_per_line=16):
        """Định dạng hex dump"""
        result = []
        
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i+bytes_per_line]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            
            # Đảm bảo phần hex có độ dài cố định
            hex_padding = " " * (3 * (bytes_per_line - len(chunk)))
            
            # Phần ASCII
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            
            line = f"{i:08x}:  {hex_part}{hex_padding}  |{ascii_part}|"
            result.append(line)
        
        return "\n".join(result)
    
    def clear_data(self):
        """Xóa dữ liệu"""
        if self.packets:
            reply = QMessageBox.question(
                self, "Xác nhận", "Bạn có chắc muốn xóa tất cả dữ liệu gói tin?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.packets = []
                self.packet_table.setRowCount(0)
                self.packet_tree.clear()
                self.packet_hex.clear()
                self.status_label.setText("Đã xóa dữ liệu")
    
    def save_packets(self):
        """Lưu gói tin ra file pcap"""
        if not self.packets:
            QMessageBox.warning(self, "Cảnh báo", "Không có gói tin nào để lưu")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu gói tin", "", "PCAP Files (*.pcap);;All Files (*)"
        )
        
        if file_path:
            try:
                scapy.wrpcap(file_path, self.packets)
                QMessageBox.information(
                    self, "Thành công", f"Đã lưu {len(self.packets)} gói tin vào {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {str(e)}")
    
    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ"""
        if self.packet_capture and self.packet_capture.isRunning():
            self.packet_capture.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PacketAnalyzerApp()
    window.show()
    sys.exit(app.exec_())
