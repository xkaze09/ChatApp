''' 
Authors: Kristina Celis & Christian Salinas
Description: dialog.py module provides a dialog box
to enter IP address and port number 
'''

import tkinter as tk
from tkinter import ttk

DEFAULT_PORT = "5000"
INSTRUCTION = '''
Server IP Address: 
  Enter the IP Address of the server you want to connect to.
Server PORT Number: 
  Enter the PORT number to use:
  5000 is default port. if you want to change, check configurations settings.  
'''

def address_dialog(ip, port):
    # Create a top-level window
    dialog = tk.Toplevel()
    dialog.title("Enter IP Address")
    dialog.resizable(False,False)
    dialog.transient()
    dialog.focus_force()

    # Main frame for padding and structure
    main_frame = ttk.Frame(dialog, padding="10 10 10 10")
    main_frame.grid(row=0,column=0, sticky="NSEW")

    # Set port
    port.set(DEFAULT_PORT)

    # Labels and entries for IP and Port
    ttk.Label(main_frame, text="Server IP Address: ", width=25).grid(row=0, column=0, sticky="W")
    ip_entry = ttk.Entry(main_frame, textvariable=ip, width=25)
    ip_entry.grid(row=0, column=1, sticky="W")
    ip_entry.focus()

    ttk.Label(main_frame, text="Server PORT Number:", width=25).grid(row=1, column=0, sticky="W")
    ttk.Entry(main_frame, textvariable=port, width=25, state='disabled').grid(row=1, column=1, sticky="W")

    # Label for Instructions
    instruction_label = tk.Text(main_frame, width=60, height=4, font=('Arial', 8, 'italic'))
    instruction_label.insert('1.0', INSTRUCTION)
    instruction_label.config(state='disabled', wrap="word")
    instruction_label.grid(row=2, column=0, columnspan=2, pady=(10, 10))

    # Button
    ttk.Button(main_frame, text="Next", command=dialog.destroy, width=25).grid(row=3, column=1, pady=(10, 0))

    # Run the dialog window
    dialog.mainloop()

if __name__ == '__main__':
    root = tk.Tk()  # Temporary root to test the dialog
    root.withdraw()  # Hide the root window

    ip = tk.StringVar()
    port = tk.StringVar()
    address_dialog(ip, port)

    # Print values after dialog closes
    print("IP Address:", ip.get())
    print("Port:", port.get())

    root.destroy()  # Destroy the root window after use
