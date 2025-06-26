"""
VoIP Client
Provides a GUI for connecting to the VoIP server and making calls.
"""
import socket
import threading
import time
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from audio_handler import AudioHandler
from common import (
    DEFAULT_PORT, send_msg, recv_msg,
    CONNECT, DISCONNECT, AUDIO_DATA, TEXT_MESSAGE, USER_LIST
)

class VoIPClient:
    def __init__(self, root):
        """
        Initialize the VoIP client.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("VoIP Client")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Set up variables
        self.username = tk.StringVar(value=f"User_{os.getpid()}")
        self.server_address = tk.StringVar(value="localhost")
        self.server_port = tk.IntVar(value=DEFAULT_PORT)
        self.room = tk.StringVar(value="default")
        self.connected = False
        self.socket = None
        self.receive_thread = None
        self.audio_handler = AudioHandler()
        self.users = []
        
        # Create the UI
        self._create_ui()
        
        # Set up protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _create_ui(self):
        """Create the user interface."""
        # Create a notebook (tabbed interface)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        connection_tab = ttk.Frame(notebook)
        call_tab = ttk.Frame(notebook)
        settings_tab = ttk.Frame(notebook)
        
        notebook.add(connection_tab, text="Connection")
        notebook.add(call_tab, text="Call")
        notebook.add(settings_tab, text="Settings")
        
        # Set up the connection tab
        self._setup_connection_tab(connection_tab)
        
        # Set up the call tab
        self._setup_call_tab(call_tab)
        
        # Set up the settings tab
        self._setup_settings_tab(settings_tab)
        
        # Status bar
        self.status_var = tk.StringVar(value="Not connected")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def _setup_connection_tab(self, parent):
        """
        Set up the connection tab.
        
        Args:
            parent: Parent widget
        """
        # Create a frame for the connection form
        form_frame = ttk.LabelFrame(parent, text="Server Connection")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Username
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.username).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Server address
        ttk.Label(form_frame, text="Server:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.server_address).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Server port
        ttk.Label(form_frame, text="Port:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.server_port).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Room
        ttk.Label(form_frame, text="Room:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.room).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Connect button
        self.connect_button = ttk.Button(form_frame, text="Connect", command=self._toggle_connection)
        self.connect_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
    def _setup_call_tab(self, parent):
        """
        Set up the call tab.
        
        Args:
            parent: Parent widget
        """
        # Create frames
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # User list (left frame)
        user_frame = ttk.LabelFrame(left_frame, text="Users in Room")
        user_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.user_list = tk.Listbox(user_frame)
        self.user_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Call controls (left frame)
        control_frame = ttk.LabelFrame(left_frame, text="Call Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.talk_button = ttk.Button(control_frame, text="Push to Talk", command=self._toggle_talk)
        self.talk_button.pack(fill=tk.X, padx=5, pady=5)
        self.talk_button.state(['disabled'])
        
        # Chat (right frame)
        chat_frame = ttk.LabelFrame(right_frame, text="Chat")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state='disabled')
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chat input
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.message_input = ttk.Entry(input_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_input.bind("<Return>", self._send_message)
        
        send_button = ttk.Button(input_frame, text="Send", command=self._send_message)
        send_button.pack(side=tk.RIGHT)
        
    def _setup_settings_tab(self, parent):
        """
        Set up the settings tab.
        
        Args:
            parent: Parent widget
        """
        # Audio devices frame
        audio_frame = ttk.LabelFrame(parent, text="Audio Devices")
        audio_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input devices
        ttk.Label(audio_frame, text="Input Device:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_device_var = tk.StringVar()
        self.input_device_combo = ttk.Combobox(audio_frame, textvariable=self.input_device_var, state="readonly")
        self.input_device_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.input_device_combo.bind("<<ComboboxSelected>>", self._on_input_device_change)
        
        # Output devices
        ttk.Label(audio_frame, text="Output Device:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_device_var = tk.StringVar()
        self.output_device_combo = ttk.Combobox(audio_frame, textvariable=self.output_device_var, state="readonly")
        self.output_device_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.output_device_combo.bind("<<ComboboxSelected>>", self._on_output_device_change)
        
        # Refresh button
        refresh_button = ttk.Button(audio_frame, text="Refresh Devices", command=self._refresh_devices)
        refresh_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Configure grid
        audio_frame.columnconfigure(1, weight=1)
        
        # Load devices
        self._refresh_devices()
        
    def _refresh_devices(self):
        """Refresh the list of audio devices."""
        # Get input devices
        input_devices = self.audio_handler.get_input_devices()
        self.input_device_combo['values'] = [device[1] for device in input_devices]
        if input_devices:
            self.input_device_combo.current(0)
            
        # Get output devices
        output_devices = self.audio_handler.get_output_devices()
        self.output_device_combo['values'] = [device[1] for device in output_devices]
        if output_devices:
            self.output_device_combo.current(0)
            
    def _on_input_device_change(self, event):
        """
        Handle input device change.
        
        Args:
            event: Event data
        """
        selected = self.input_device_combo.current()
        if selected >= 0:
            input_devices = self.audio_handler.get_input_devices()
            if selected < len(input_devices):
                self.audio_handler.set_input_device(input_devices[selected][0])
                
    def _on_output_device_change(self, event):
        """
        Handle output device change.
        
        Args:
            event: Event data
        """
        selected = self.output_device_combo.current()
        if selected >= 0:
            output_devices = self.audio_handler.get_output_devices()
            if selected < len(output_devices):
                self.audio_handler.set_output_device(output_devices[selected][0])
                
    def _toggle_connection(self):
        """Toggle the connection state."""
        if not self.connected:
            self._connect()
        else:
            self._disconnect()
            
    def _connect(self):
        """Connect to the server."""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_address.get(), self.server_port.get()))
            
            # Send connect message
            send_msg(self.socket, CONNECT, {
                'username': self.username.get(),
                'room': self.room.get()
            })
            
            # Wait for response
            response = recv_msg(self.socket)
            if not response or response[0] != CONNECT:
                messagebox.showerror("Connection Error", "Invalid response from server")
                self.socket.close()
                return
                
            # Update UI
            self.connected = True
            self.connect_button.config(text="Disconnect")
            self.status_var.set(f"Connected to {self.server_address.get()}:{self.server_port.get()}")
            self.talk_button.state(['!disabled'])
            
            # Start audio playback
            self.audio_handler.start_playback()
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_data)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            # Add system message
            self._add_chat_message("System", f"Connected to room: {self.room.get()}")
            
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            if self.socket:
                self.socket.close()
                
    def _disconnect(self):
        """Disconnect from the server."""
        if self.connected and self.socket:
            # Send disconnect message
            try:
                send_msg(self.socket, DISCONNECT, {})
            except:
                pass
                
            # Close socket
            self.socket.close()
            self.socket = None
            
            # Update UI
            self.connected = False
            self.connect_button.config(text="Connect")
            self.status_var.set("Not connected")
            self.talk_button.state(['disabled'])
            self.talk_button.config(text="Push to Talk")
            
            # Stop audio
            self.audio_handler.stop_recording()
            self.audio_handler.stop_playback()
            
            # Clear user list
            self.user_list.delete(0, tk.END)
            
            # Add system message
            self._add_chat_message("System", "Disconnected from server")
            
    def _receive_data(self):
        """Receive data from the server."""
        while self.connected and self.socket:
            try:
                # Receive message
                msg = recv_msg(self.socket)
                if not msg:
                    break
                    
                msg_type, data = msg
                
                if msg_type == AUDIO_DATA:
                    # Add audio data to the playback queue
                    self.audio_handler.add_audio_data(data)
                    
                elif msg_type == TEXT_MESSAGE:
                    # Add message to chat
                    self._add_chat_message(data['sender'], data['message'])
                    
                elif msg_type == USER_LIST:
                    # Update user list
                    self._update_user_list(data['users'])
                    
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
                
        # If we get here, the connection is closed
        if self.connected:
            self.root.after(0, self._disconnect)
            
    def _toggle_talk(self):
        """Toggle the talk state."""
        if not self.audio_handler.recording:
            # Start recording
            self.audio_handler.start_recording(self._on_audio_data)
            self.talk_button.config(text="Release to Stop")
        else:
            # Stop recording
            self.audio_handler.stop_recording()
            self.talk_button.config(text="Push to Talk")
            
    def _on_audio_data(self, data):
        """
        Handle recorded audio data.
        
        Args:
            data: Audio data
        """
        if self.connected and self.socket:
            send_msg(self.socket, AUDIO_DATA, data)
            
    def _send_message(self, event=None):
        """
        Send a chat message.
        
        Args:
            event: Event data (optional)
        """
        message = self.message_input.get().strip()
        if message and self.connected and self.socket:
            # Send message
            send_msg(self.socket, TEXT_MESSAGE, message)
            
            # Clear input
            self.message_input.delete(0, tk.END)
            
    def _add_chat_message(self, sender, message):
        """
        Add a message to the chat display.
        
        Args:
            sender: Sender of the message
            message: Message text
        """
        # Enable editing
        self.chat_display.config(state='normal')
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        
        # Add message
        self.chat_display.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        
        # Scroll to bottom
        self.chat_display.see(tk.END)
        
        # Disable editing
        self.chat_display.config(state='disabled')
        
    def _update_user_list(self, users):
        """
        Update the user list.
        
        Args:
            users: List of users
        """
        self.users = users
        
        # Clear list
        self.user_list.delete(0, tk.END)
        
        # Add users
        for user in users:
            self.user_list.insert(tk.END, user['username'])
            
    def _on_close(self):
        """Handle window close."""
        if self.connected:
            self._disconnect()
            
        self.audio_handler.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VoIPClient(root)
    root.mainloop() 