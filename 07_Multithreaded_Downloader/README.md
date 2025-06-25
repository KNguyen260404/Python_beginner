# Multithreaded Downloader

A Python application with a graphical user interface that allows downloading files from the internet using multiple threads to increase download speed.

## Features

- **Multithreaded Downloads**: Split downloads into multiple chunks to download in parallel
- **Progress Tracking**: Real-time progress tracking for each thread and overall download
- **Resumable Downloads**: Ability to pause and resume downloads (future feature)
- **Error Handling**: Robust error handling for network issues
- **User-friendly Interface**: Clean PyQt5 GUI with progress visualization

## Requirements

- Python 3.6+
- PyQt5
- Requests

## Installation

1. Install the required packages:

```bash
pip install PyQt5 requests
```

2. Run the application:

```bash
python multithreaded_downloader.py
```

## Usage

1. Enter the URL of the file you want to download
2. Select a save location by clicking the "Browse" button
3. Choose the number of threads (1-32) to use for downloading
4. Click "Start Download" to begin
5. Monitor the progress of each thread and the overall download
6. Cancel the download at any time by clicking "Cancel"

## How It Works

The application works by:

1. Sending a HEAD request to get file size and other metadata
2. Dividing the file into equal chunks based on the number of threads
3. Creating a separate thread for each chunk to download its portion
4. Using HTTP Range headers to request specific byte ranges
5. Saving each chunk to a temporary file
6. Combining all chunks into the final file when download completes

## Limitations

- Some servers don't support range requests, in which case the download will fall back to single-threaded mode
- Very small files will automatically use single-threaded download
- The pause/resume functionality is not yet implemented

## Future Improvements

- Implement pause/resume functionality
- Add download queue for multiple files
- Support for authentication
- Download speed limiting
- Download scheduling
- Integration with browser extensions 