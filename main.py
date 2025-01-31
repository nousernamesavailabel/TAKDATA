import math
import csv
from datetime import datetime, timedelta
import http.client

# Function to convert MGRS to Latitude and Longitude
def LatLongFromMGRSstring(a):
    try:
        b = a.strip().split()
        if not b or len(b) != 4:
            return False, None, None

        c = b[0][0] if len(b[0]) < 3 else b[0][:2]
        d = b[0][1] if len(b[0]) < 3 else b[0][2]
        e = (int(c) * 6 - 183) * math.pi / 180

        f = ["ABCDEFGH", "JKLMNPQR", "STUVWXYZ"][(int(c) - 1) % 3].find(b[1][0]) + 1
        g = "CDEFGHJKLMNPQRSTUVWXX".find(d)

        h = ["ABCDEFGHJKLMNPQRSTUV", "FGHJKLMNPQRSTUVABCDE"][(int(c) - 1) % 2].find(b[1][1])
        i = [1.1, 2.0, 2.8, 3.7, 4.6, 5.5, 6.4, 7.3, 8.2, 9.1, 0, 0.8, 1.7, 2.6, 3.5, 4.4, 5.3, 6.2, 7.0, 7.9]
        j = [0, 2, 2, 2, 4, 4, 6, 6, 8, 8, 0, 0, 0, 2, 2, 4, 4, 6, 6, 6]
        k = i[g]
        l = j[g] + h / 10

        if l < k:
            l += 2

        m = f * 100000.0 + int(b[2])
        n = l * 1000000 + int(b[3])
        m -= 500000.0

        if d < 'N':
            n -= 10000000.0

        m /= 0.9996
        n /= 0.9996

        o = n / 6367449.14570093
        p = o + (0.0025188266133249035 * math.sin(2.0 * o)) + (0.0000037009491206268 * math.sin(4.0 * o)) + (
                    0.0000000074477705265 * math.sin(6.0 * o)) + (0.0000000000170359940 * math.sin(8.0 * o))
        q = math.tan(p)
        r = q * q
        s = r * r
        t = math.cos(p)
        u = 0.006739496819936062 * t ** 2
        v = 40680631590769 / (6356752.314 * math.sqrt(1 + u))
        w = v
        x = 1.0 / (w * t)
        w *= v
        y = q / (2.0 * w)
        w *= v
        z = 1.0 / (6.0 * w * t)
        w *= v
        aa = q / (24.0 * w)
        w *= v
        ab = 1.0 / (120.0 * w * t)
        w *= v
        ac = q / (720.0 * w)
        w *= v
        ad = 1.0 / (5040.0 * w * t)
        w *= v
        ae = q / (40320.0 * w)

        lat = p + y * (-1.0 - u) * (m ** 2) + aa * (5.0 + 3.0 * r + 6.0 * u - 6.0 * r * u - 3.0 * (u * u) - 9.0 * r * (u * u)) * (m ** 4) + ac * (-61.0 - 90.0 * r - 45.0 * s - 107.0 * u + 162.0 * r * u) * (m ** 6) + ae * (1385.0 + 3633.0 * r + 4095.0 * s + 1575 * (s * r)) * (m ** 8)
        lng = e + x * m + z * (-1.0 - 2 * r - u) * (m ** 3) + ab * (5.0 + 28.0 * r + 24.0 * s + 6.0 * u + 8.0 * r * u) * (m ** 5) + ad * (-61.0 - 662.0 * r - 1320.0 * s - 720.0 * (s * r)) * (m ** 7)

        return True, lat * 180 / math.pi, lng * 180 / math.pi

    except Exception as e:
        print(f"Error converting MGRS: {e}")
        return False, None, None


# Function to send CoT Message
def send_cot_message(callsign, lat, long, type, tak_server_address, tak_server_port):
    try:
        icontype = "a-n-g" if type == "F" else "a-h-g"
        iconsetpath = "COT_MAPPING_2525B/a-n/a-n-G" if type == "F" else "COT_MAPPING_2525B/a-h/a-h-G"

        current_time = datetime.utcnow()
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

        conn = http.client.HTTPConnection(tak_server_address, tak_server_port)
        headers = {"Content-type": "application/xml"}
        conn.request("POST", "/", body=cot_xml, headers=headers)

        return 200

    except Exception as e:
        print(f"Error sending CoT: {e}")
        return 500

    finally:
        if conn:
            conn.close()


# Read CSV and process entries
csv_file = "callsigns.csv"
tak_server_address = "192.168.5.14"
tak_server_port = 8087
#type = "F"

with open(csv_file, newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        callsign = row["callsign"]
        MGRS_String = row["MGRS_String"]
        type = row["type"]
        success, lat, long = LatLongFromMGRSstring(MGRS_String)

        if success:
            print(f"Successfully converted {MGRS_String} -> Lat: {lat}, Long: {long}")
            send_cot_message(callsign, lat, long, type, tak_server_address, tak_server_port)
        else:
            print(f"Failed to convert {MGRS_String} for {callsign}")
