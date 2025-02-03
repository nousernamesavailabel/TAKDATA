import math
import csv
import os
import tkinter as tk
from tkinter import filedialog, ttk
from datetime import datetime, timedelta, timezone
import http.client
from mgrsconv import *

global button_width
global entry_width
button_width = 20
entry_width = 20

# Function to send CoT Message
def send_cot_message(callsign, lat, long, type, tak_server_address, tak_server_port):
    try:
        print(f"Attempting to send CoT for {callsign} to {tak_server_address}:{tak_server_port}...")  # Debugging

        #icontype = "a-n-g" if type == "F" else "a-h-g"
        if type == "F":
            icontype = "a-n-g"
        elif type == "E":
            icontype = "a-h-g"
        elif type == "C":
            icontype = "a-f-g"
        else:
            icontype = "a-n-g"
            print(f"Icon Type could not be parsed.")

        iconsetpath = "COT_MAPPING_2525B/a-n/a-n-G" if type == "F" else "COT_MAPPING_2525B/a-h/a-h-G"

        current_time = datetime.now(timezone.utc)
        current_time_str = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        stale_time_str = (current_time + timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')

        cot_xml = f"""<?xml version="1.0" encoding="utf-16"?>
        <COT>
          <event version="2.0" uid="{callsign}" type="{icontype}" how="h-g-i-g-o" time="{current_time_str}" start="{current_time_str}" stale="{stale_time_str}">
            <point lat="{lat}" lon="{long}" hae="0" le="9999999" ce="9999999" />
            <detail>
              <contact callsign="{callsign}" />
              <usericon iconsetpath="{iconsetpath}" />
            </detail>
          </event>
        </COT>"""

        print("Connecting to TAK server...")  # Debugging
        print(f"TAK Server Address (raw): [{tak_server_address.encode()}]")  # Show raw bytes
        print(f"TAK Server Port (raw): [{tak_server_port.encode()}]")  # Show raw bytes

        try:
            conn = http.client.HTTPConnection(tak_server_address.strip(), int(tak_server_port.strip()), timeout=3)

            headers = {"Content-type": "application/xml"}
            conn.request("POST", "/", body=cot_xml, headers=headers)

            #response = conn.getresponse()
            #print(f"CoT sent: {response.status}, {response.reason}")
            return 200

        except Exception as e:
            print(f"Error sending CoT: {e}")
            return 500

        finally:
            try:
                conn.close()  # Force close after each request
                print("Connection closed.")
            except Exception:
                pass

        #headers = {"Content-type": "application/xml"}

        #print("Sending HTTP request...")  # Debugging
        #conn.request("POST", "/", body=cot_xml, headers=headers)

        #print("Waiting for response...")  # Debugging
        #response = conn.getresponse()

        #print(f"CoT sent: {response.status}, {response.reason}")  # Response Debugging

    except Exception as e:
        print(f"Error sending CoT: {e}")

    finally:
        if conn:
            print("Closing connection...")  # Debugging
            conn.close()


# Function to process CSV
def prepare_message(file_var, address_entry, port_entry):
    csv_file = file_var.get().strip()  # Get selected CSV file path
    tak_server_address = address_entry.get().strip()  # Get user-input address
    tak_server_port = port_entry.get().strip()  # Get user-input port

    # Debugging print statements to verify extracted values
    print(f"Extracted TAK Server Address: {tak_server_address}")
    print(f"Extracted TAK Server Port: {tak_server_port}")

    if not csv_file:
        print("No file selected!")
        return

    if not tak_server_address or not tak_server_port:
        print("Error: Server address or port is missing or invalid!")
        return

    try:
        with open(csv_file, newline='') as file:
            importedfile = csv.DictReader(file)
            for row in importedfile:
                callsign = row["callsign"]
                MGRS_String = row["MGRS_String"]
                type = row["type"]
                success, lat, long = mgrs2dd(MGRS_String)

                if success:
                    print(f"Successfully converted {MGRS_String} -> Lat: {lat}, Long: {long}")
                    send_cot_message(callsign, lat, long, type, tak_server_address, tak_server_port)
                else:
                    print(f"Failed to convert {MGRS_String} for {callsign}")

    except Exception as e:
        print(f"Error reading file: {e}")



# Function to select file
def import_file(button, file_var):
    file_path = filedialog.askopenfilename(title="Select a file:",
                                           filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if file_path:
        filename = os.path.basename(file_path)  # Extract only the filename
        button.config(text=filename)  # Update button text
        file_var.set(file_path)  # Store file path


# Main GUI function
def main():
    ################################## Functions ##################################################
    # Function to add stages
    def update_stages(number_of_stages_entry):
        window.geometry("350x150") #Reset window size
        csv_file_selector_label_ = {}  # define the label dictionary
        csv_file_selector_button_ = {}  # define the label dictionary
        send_button_ = {} # define send button dictionary
        file_var_ = {} # empty file_var

        int_stages = int(number_of_stages_entry.get())
        print(f"Stages: {int_stages}")

        for stage in range(int_stages):

            print(f"INT Stage: ", stage, "Type: ", type(stage))
            str_stage = str(stage)
            print(f"STR Stage: ", str_stage, "Type: ", type(str_stage))

            file_var_[stage] = tk.StringVar()

            csv_file_selector_label_[stage] = tk.Label(tab2, text=(f"CSV File Phase: {str_stage}"))
            csv_file_selector_label_[stage].grid(row=(8+stage), column=0)

            csv_file_selector_button_[stage] = tk.Button(tab2, text=f"Phase {str_stage}", command=lambda s=stage: import_file(csv_file_selector_button_[s], file_var_[s]))
            csv_file_selector_button_[stage].grid(row=(8+stage), column=1)

            send_button_[stage] = tk.Button(tab2, text=f"Send Phase {str_stage}", command=lambda s=stage: prepare_message(file_var_[s], tak_server_address_entry_tab2, tak_server_port_entry_tab2))
            send_button_[stage].grid(row=(8+stage), column=2)

            window.update_idletasks()
            width = window.winfo_width()
            height = window.winfo_height() + 25
            window.geometry(f"{width}x{height}")

    ################################## Window ##################################################

    window = tk.Tk()
    window.title("CoT Message Sender")
    window.geometry("350x150")

    notebook = ttk.Notebook(window)
    notebook.pack(expand=True, fill="both")

    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="CSV To TAK")
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="CSV Scenario to TAK")

    ################################## TAB 1 ##################################################

    file_var = tk.StringVar()  # Store file path

    # TAK Server Address
    tak_server_address_label = tk.Label(tab1, text="TAK Server Address: ")
    tak_server_address_label.grid(row=0, column=0)
    tak_server_address_entry = tk.Entry(tab1)
    tak_server_address_entry.grid(row=0, column=1)
    tak_server_address_entry.insert(0, "192.168.5.14")  #default IP address

    # TAK Server Port
    tak_server_port_label = tk.Label(tab1, text="TAK Server Port: ")
    tak_server_port_label.grid(row=2, column=0)
    tak_server_port_entry = tk.Entry(tab1)
    tak_server_port_entry.grid(row=2, column=1)
    tak_server_port_entry.insert(0, "8087") #default port

    # CSV File Selection
    csv_file_selector_label = tk.Label(tab1, text="CSV File: ")
    csv_file_selector_label.grid(row=4, column=0)

    csv_file_selector_button = tk.Button(tab1, text="Select File",
                                         command=lambda: import_file(csv_file_selector_button, file_var))
    csv_file_selector_button.grid(row=4, column=1)

    # Send Button
    send_button = tk.Button(
        tab1,
        width = 40,
        text="Send",
        command=lambda: prepare_message(file_var, tak_server_address_entry, tak_server_port_entry)
    )
    send_button.grid(row=6, column=0, columnspan=2)



    ################################## TAB 2 ##################################################

    tak_server_address_label_tab2 = tk.Label(tab2, text="TAK Server Address:")
    tak_server_address_label_tab2.grid(row=0, column=0)
    tak_server_address_entry_tab2 = tk.Entry(tab2)
    tak_server_address_entry_tab2.grid(row=0, column=1)
    tak_server_address_entry_tab2.insert(0, "192.168.5.14")  # default IP address

    tak_server_port_label_tab2 = tk.Label(tab2, text="TAK Server Port:")
    tak_server_port_label_tab2.grid(row=2, column=0)
    tak_server_port_entry_tab2 = tk.Entry(tab2)
    tak_server_port_entry_tab2.grid(row=2, column=1)
    tak_server_port_entry_tab2.insert(0, "8087")

    number_of_stages_label = tk.Label(tab2, text="Number of Stages:")
    number_of_stages_label.grid(row=4, column=0)
    number_of_stages_entry = tk.Entry(tab2)
    number_of_stages_entry.grid(row=4, column=1)

    number_of_stages_button = tk.Button(tab2, text="Update Stages", command=lambda: update_stages(number_of_stages_entry))
    number_of_stages_button.grid(row=6, column=0, columnspan=2)

    #mgrs = "17R LL 12345 54321"
    #ll = mgrs2dd(mgrs)
    #print(ll)





    window.mainloop()




if __name__ == "__main__":
    main()