import tkinter as tk
from tkinter import Menu
import serial
import serial.tools.list_ports
import threading  # For background serial reading
from tkinter import messagebox

# Arduino Commands (button name, serial command to send)
commands = {
    ("Argon", "Argon"),
    ("Hydrogen", "Hydrogen"),
    ("Nitrogen", "Nitrogen"),
    ("No gas", "none")
}

# Function to read serial data in the background
def read_serial():
    global ser
    while True:
        try:
            # Check if ser is not None and if it's open
            if ser and (hasattr(ser, 'isOpen') and ser.isOpen() or hasattr(ser, 'is_open') and ser.is_open):  # Check for both versions
                try:
                    line = ser.readline().decode().strip()
                    if line:
                        response_text.insert(tk.END, line + "\n")  # Append to textbox
                except serial.SerialException as e:
                    print(f"Serial read error: {e}")
        except (AttributeError, serial.SerialException) as e:
            print(f"Error in read_serial: {e}")


# Function to update the port dropdown menu
def update_port_menu():
    global port_menu, port_var
    port_menu.delete(0, "end")  # Clear existing menu items

    available_ports = []
    for port in serial.tools.list_ports.comports():
        description = port.description if hasattr(port, 'description') else "Unknown device"
        available_ports.append((port.device, description))

    for port, desc in available_ports:
        port_menu.add_radiobutton(label=f"{port} - {desc}", variable=port_var, value=port)

def show_about():
    messagebox.showinfo("About Gas Switcher", "This is a gas switcher application designed to work with the PPFE gas switcher \nVersion 1.0\nCreated by Kenneth")
def show_help():
    messagebox.showinfo("Help",
                        "Just click the buttons with the gas names and it should change, make sure you have the right COM port selected. Otherwise something is probably broken or turned off. \nGood luck.")
# Create main window
window = tk.Tk()
window.title("Gas switcher")
window.iconbitmap("fire.ico")
# --- Menu Bar ---
menubar = Menu(window)
window.config(menu=menubar)

# Create 'Serial' menu
serial_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Serial", menu=serial_menu)

# Create 'Port' submenu
port_var = tk.StringVar(window)
port_menu = Menu(serial_menu, tearoff=0)
serial_menu.add_cascade(label="Port", menu=port_menu)
update_port_menu()  # Populate the port menu initially

# Add 'Refresh Ports' to the 'Serial' menu
serial_menu.add_command(label="Refresh Ports", command=update_port_menu)

# Create "Help" menu
helpmenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=helpmenu)

# Add "About" command to "Help" menu
helpmenu.add_command(label="About", command=show_about)
# Add "Help" command to "Help" menu
helpmenu.add_command(label="Help me", command=show_help)

# --- Status Bar ---
status_var = tk.StringVar(window)  # Variable to hold the status message
status_label = tk.Label(window, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X)
# Function to update status bar
def update_status_bar():
    if ser and ser.is_open:  # Use is_open for older versions
        port = ser.port
        status_var.set(f"Connected to {port}")
    else:
        status_var.set("Disconnected")
    #window.after(1000, update_status_bar)  # Update every 1 second
# Function to send commands over serial
def send_command(command):
    global ser
    selected_port = port_var.get()
    baud_rate = 115200 # As defined on the Arduino
    command = command+"\n" # We always end up with a newline to indicate the command is finished
    try:
        # Check if the port is already open and valid
        if ser is not None and ser.is_open:  # Use is_open for older versions
            ser.write(command.encode())
            status_var.set(f"Sent command {command.encode()} to device on port {selected_port}")
        else:
            # Attempt to open the port
            ser = serial.Serial(selected_port, baud_rate, timeout=1)
            if ser.is_open:  # Use is_open for older versions
                ser.write(command.encode())
                status_var.set(f"Sent command {command.encode()} to device on port {selected_port}")
            else:
                # Handle the case where the port could not be opened
                response_text.insert(tk.END, "Error: Unable to open serial port.\n")
    except serial.SerialException as e:
        response_text.insert(tk.END, f"Error: {e}\n")  # Display error in the textbox

    #update_status_bar()

w = tk.Label(window, text="Select gas:")
w.pack()
# Create a frame for the button grid
button_frame = tk.Frame(window)
button_frame.pack(pady=10,fill=tk.BOTH, expand=True)  # Add some padding around the frame

# Create buttons dynamically in a grid
row, col = 0, 0  # Start at the top-left corner
for button_label, command in commands:
    button = tk.Button(button_frame, text=button_label, command=lambda cmd=command: send_command(cmd))
    button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")  # Place in grid with padding
    col += 1  # Move to the next column
    if col >= 2:  # Create a new row after 3 columns
        col = 0
        row += 1

# Configure button frame to give equal weight to all columns and rows
for i in range(2):  # Assuming 2 columns in your grid
    button_frame.columnconfigure(i, weight=1)
for i in range(row + 1):  # Configure rows up to the last used row
    button_frame.rowconfigure(i, weight=1)

# --- Response Textbox ---
response_text = tk.Text(window, width=60, height=10, wrap=tk.WORD)
response_text.pack(pady=2,padx=2)

ser = None
update_status_bar()  # Start updating the status bar
threading.Thread(target=read_serial, daemon=True).start() # Start serial thread to read in background

window.mainloop()