import time
import pickle
from pathlib import Path
from MiniCmdUtil import MiniCmdUtil

ROOTDIR = Path(__file__).resolve().parent
quick_def_file = ROOTDIR / 'quick-buttons.txt'
parameter_dir = ROOTDIR / 'ParameterFiles'

# Ask the user for the number of commands to send
try:
    total_commands = int(input("Enter the number of automated commands to send: ").strip())
    if total_commands <= 0:
        raise ValueError
except ValueError:
    print("Please enter a valid positive integer.")
    exit(1)

# Read quick-button command definitions
subsys, quick_cmd, quick_code, quick_pkt_id, quick_endian, quick_address, quick_port, quick_param = ([] for _ in range(8))

with open(quick_def_file) as f:
    for row in f:
        row = row.strip()
        if not row or row.startswith('#'):
            continue
        parts = row.split(',')
        subsys.append(parts[0])
        quick_cmd.append(parts[2].strip())
        quick_code.append(parts[3].strip())
        quick_pkt_id.append(parts[4].strip())
        quick_endian.append(parts[5].strip())
        quick_address.append(parts[6].strip())
        quick_port.append(parts[7].strip())
        quick_param.append(parts[8].strip())

# Filter out parameterless commands
valid_indices = []
for i in range(len(quick_cmd)):
    param = quick_param[i]
    if not param.strip():
        valid_indices.append(i)
    else:
        try:
            with open(parameter_dir / param.strip(), 'rb') as pf:
                _, param_names = pickle.load(pf)
            if len(param_names) == 0:
                valid_indices.append(i)
            else:
                print(f"[AUTO COMMAND] Skipped '{quick_cmd[i]}' (needs parameters)")
        except Exception:
            valid_indices.append(i)  # If file is missing or unreadable, treat as no params

# Repeat the loop until total_commands have been sent
if not valid_indices:
    print("[ERROR] No parameterless quick commands found.")
    exit(1)

print(f"[INFO] Sending {total_commands} automated commands...")

sent_count = 0
while sent_count < total_commands:
    for i in valid_indices:
        if sent_count >= total_commands:
            break
        print(f"[AUTO COMMAND] ({sent_count + 1}/{total_commands}) Sending '{quick_cmd[i]}' to {quick_address[i]}:{quick_port[i]}")
        mcu = MiniCmdUtil(
            host=quick_address[i],
            port=quick_port[i],
            endian=quick_endian[i],
            pkt_id=quick_pkt_id[i],
            cmd_code=quick_code[i]
        )
        success = mcu.send_packet()
        print(f"[AUTO COMMAND] Success: {success}\n")
        sent_count += 1
        time.sleep(1)
