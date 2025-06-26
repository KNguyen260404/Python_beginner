"""
Audio handler for the VoIP application.
Handles recording and playback of audio.
"""
import pyaudio
import numpy as np
import threading
import queue
import time
from common import CHUNK, RATE, CHANNELS, FORMAT

class AudioHandler:
    def __init__(self):
        """Initialize the audio handler."""
        self.pyaudio = pyaudio.PyAudio()
        self.recording = False
        self.playing = False
        self.input_stream = None
        self.output_stream = None
        self.audio_queue = queue.Queue(maxsize=100)
        self.format_map = {
            'int16': pyaudio.paInt16,
            'int24': pyaudio.paInt24,
            'int32': pyaudio.paInt32,
            'float32': pyaudio.paFloat32
        }
        self.format = self.format_map.get(FORMAT, pyaudio.paInt16)
        
    def start_recording(self, callback):
        """
        Start recording audio from the microphone.
        
        Args:
            callback: Function to call with recorded audio data
        """
        if self.recording:
            return
            
        self.recording = True
        
        # Create and start the input stream
        self.input_stream = self.pyaudio.open(
            format=self.format,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self._recording_callback(callback)
        )
        
        self.input_stream.start_stream()
        
    def _recording_callback(self, user_callback):
        """
        Callback function for the input stream.
        
        Args:
            user_callback: Function to call with recorded audio data
            
        Returns:
            Callback function for the input stream
        """
        def callback(in_data, frame_count, time_info, status):
            if self.recording:
                user_callback(in_data)
                return (None, pyaudio.paContinue)
            else:
                return (None, pyaudio.paComplete)
        return callback
        
    def stop_recording(self):
        """Stop recording audio."""
        if not self.recording:
            return
            
        self.recording = False
        
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
    
    def start_playback(self):
        """Start playing audio from the queue."""
        if self.playing:
            return
            
        self.playing = True
        
        # Create and start the output stream
        self.output_stream = self.pyaudio.open(
            format=self.format,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK,
            stream_callback=self._playback_callback()
        )
        
        self.output_stream.start_stream()
    
    def _playback_callback(self):
        """
        Callback function for the output stream.
        
        Returns:
            Callback function for the output stream
        """
        def callback(in_data, frame_count, time_info, status):
            try:
                data = self.audio_queue.get(block=False)
                return (data, pyaudio.paContinue)
            except queue.Empty:
                # Return silence if the queue is empty
                return (bytes(CHUNK * CHANNELS * 2), pyaudio.paContinue)
        return callback
    
    def stop_playback(self):
        """Stop playing audio."""
        if not self.playing:
            return
            
        self.playing = False
        
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
    
    def add_audio_data(self, data):
        """
        Add audio data to the playback queue.
        
        Args:
            data: Audio data to add to the queue
        """
        try:
            # Add to queue, but don't block if full (discard oldest data)
            if self.audio_queue.full():
                self.audio_queue.get_nowait()  # Remove oldest item
            self.audio_queue.put_nowait(data)
        except queue.Full:
            pass  # Queue is full, discard data
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_recording()
        self.stop_playback()
        self.pyaudio.terminate()
        
    def get_input_devices(self):
        """
        Get a list of available input devices.
        
        Returns:
            List of input devices as (index, name) tuples
        """
        devices = []
        for i in range(self.pyaudio.get_device_count()):
            device_info = self.pyaudio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append((i, device_info['name']))
        return devices
        
    def get_output_devices(self):
        """
        Get a list of available output devices.
        
        Returns:
            List of output devices as (index, name) tuples
        """
        devices = []
        for i in range(self.pyaudio.get_device_count()):
            device_info = self.pyaudio.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                devices.append((i, device_info['name']))
        return devices
        
    def set_input_device(self, device_index):
        """
        Set the input device.
        
        Args:
            device_index: Index of the input device to use
        """
        was_recording = self.recording
        
        if was_recording:
            self.stop_recording()
            
        self.input_device_index = device_index
        
        if was_recording:
            self.start_recording()
            
    def set_output_device(self, device_index):
        """
        Set the output device.
        
        Args:
            device_index: Index of the output device to use
        """
        was_playing = self.playing
        
        if was_playing:
            self.stop_playback()
            
        self.output_device_index = device_index
        
        if was_playing:
            self.start_playback() 