# Remote Control System in Python

A remote control system implemented in Python using TCP sockets.
The client streams the screen, while the server sends input commands (mouse and keyboard) for remote control.

## Usage

Run the project on two separate machines: one as the **client** and the other as the **server**.
In `Client.py`, update the `SERVER_IP` variable inside the `main` function to match the IP address of the server machine (around line 63).
Start the server first, then the client. A window should open on the server showing the client's screen — remote control begins from there.
## warning
USE ONLY ON TWO DIFFERENT COMPUTERS. DO NOT USE IT ON THE SAME COMPUTER

## Features

- Real-time screen streaming from client to server
- Remote mouse movement, clicking, and scrolling
- Remote keyboard key press and release
- Custom binary/text protocol over separate sockets

## Components

- **Client**: Captures and streams screen frames to the server
- **Server**: Sends mouse and keyboard input commands to the client

