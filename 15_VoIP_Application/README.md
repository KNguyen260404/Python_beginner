# Simple VoIP Application

This is a simple Voice over IP (VoIP) application built with Python. It allows users to make voice calls over a network.

## Features

- Real-time voice communication
- Simple user interface
- Support for multiple clients
- Audio quality settings

## Requirements

- Python 3.8+
- PyAudio
- Socket
- Threading
- Tkinter (for GUI)

## Installation

1. Install the required packages:
```
pip install pyaudio
```

2. Run the server:
```
python server.py
```

3. Run the client:
```
python client.py
```

## Usage

1. Start the server on one machine
2. Connect from clients by entering the server IP address
3. Start a conversation

## Project Structure

- `server.py`: The VoIP server that handles connections
- `client.py`: The client application with GUI
- `audio_handler.py`: Handles audio recording and playback
- `common.py`: Common utilities and settings

## License

MIT 