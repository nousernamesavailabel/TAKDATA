# CoT Message Sender

This Python application facilitates sending Cursor on Target (CoT) messages to a TAK (Tactical Assault Kit) server. It provides a GUI to process CSV files containing coordinates, convert them from MGRS to decimal degrees, and send CoT messages to the specified TAK server.

## Features

- **CoT Message Generation**: Sends CoT messages in XML format.
- **MGRS to Decimal Conversion**: Converts MGRS coordinates to latitude and longitude.
- **TAK Server Integration**: Connects to a TAK server via HTTP.
- **CSV Processing**: Reads CSV files containing callsigns, MGRS coordinates, and types.
- **GUI Interface**: User-friendly interface to configure server settings and send messages.
- **Multi-Phase CSV Support**: Load coordinate files for multiple phases to present/update the COP at the press of a button.

## Requirements

Ensure you have the following dependencies installed:

- Python 3.x
- `tkinter` (GUI)
- `mgrsconv` (MGRS conversion library)
- `http.client` (for sending messages)
- `csv`, `os`, `datetime`, `math` (standard libraries)

You can install dependencies via:

```sh
pip install mgrsconv
```

Additionally, you need a TAK server available with an unencrypted input port.

## How to Use

1. **Run the Application**  
   Open a terminal and execute:
   ```sh
   python main.py
   ```

2. **Select CSV File**  
   - Navigate to the "CSV To TAK" tab.
   - Click "Select File" and choose a CSV file.
   - The CSV file must have the following columns:
     - `callsign`
     - `MGRS_String`
     - `type` (F, E, C, etc.)

3. **Enter TAK Server Details**  
   - Provide the TAK server's IP address and port (unecrypted input, as mentioned above).

4. **Send CoT Messages**  
   - Click "Send" to process the CSV and transmit CoT messages.

5. **Batch Processing (Scenarios)**  
   - Use the "CSV Scenario to TAK" tab to process multiple phases.
   - Set the number of stages and import CSV files accordingly.

## CSV Format

Ensure your CSV file is formatted correctly:

```csv
callsign,MGRS_String,type
Alpha,17R LL 12345 54321,F
Bravo,17S MM 67890 12345,E
Charlie,18T PK 13579 24680,C
```

## Troubleshooting

- **No File Selected**: Ensure you select a CSV file before sending.
- **Server Connection Issues**: Verify the TAK server address and port.
- **MGRS Conversion Errors**: Ensure MGRS coordinates are formatted correctly.

## License

This project is licensed under the MIT License.


