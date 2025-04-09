import time
import pickle
from pathlib import Path
from MiniCmdUtil import MiniCmdUtil

ROOTDIR = Path(__file__).resolve().parent
quick_def_file = ROOTDIR / 'quick-buttons.txt'
parameter_dir = ROOTDIR / 'ParameterFiles'

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

# Helper: Check if a command requires parameters
def has_params(param_filename):
    if not param_filename.strip():
        return False
    try:
        with open(parameter_dir / param_filename.strip(), 'rb') as pf:
            _, param_names = pickle.load(pf)
        return len(param_names) > 0
    except Exception:
        return False

# Loop through and send only parameterless commands
for i in range(len(quick_cmd)):
    if not has_params(quick_param[i]):
        print(f"[AUTO COMMAND] Sending '{quick_cmd[i]}' to {quick_address[i]}:{quick_port[i]}")
        mcu = MiniCmdUtil(
            host=quick_address[i],
            port=quick_port[i],
            endian=quick_endian[i],
            pkt_id=quick_pkt_id[i],
            cmd_code=quick_code[i]
        )
        success = mcu.send_packet()
        print(f"[AUTO COMMAND] Success: {success}\n")
        time.sleep(1)
    else:
        print(f"[AUTO COMMAND] Skipped '{quick_cmd[i]}' (needs parameters)")
