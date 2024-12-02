from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import argparse
import csv
import os
import datetime
# Assuming the data is stored in a list of tuples or similar structure

output_filepath = os.path.join(os.getcwd(), 'data.csv')
# print(output_filepath)

VOI = [
    # ("first_run", "%QX0.7"),
    ("flow_set", "%MW1"),
    ("a_setpoint", "%MW2"),
    ("pressure_sp", "%MW3"),
    ("override_sp", "%MW4"),
    ("level_sp", "%MW5"),
    ("f1_valve_pos", "%IW100"),
    ("f1_flow", "%IW101"),
    ("f2_valve_pos", "%IW102"),
    ("f2_flow", "%IW103"),
    ("purge_valve_pos", "%IW104"),
    ("purge_flow", "%IW105"),
    ("product_valve_pos", "%IW106"),
    ("product_flow", "%IW107"),
    ("pressure", "%IW108"),
    ("level", "%IW109"),
    ("a_in_purge", "%IW110"),
    ("b_in_purge", "%IW111"),
    ("c_in_purge", "%IW112"),
    ("f1_valve_sp", "%QW100"),
    ("f2_valve_sp", "%QW101"),
    ("purge_valve_sp", "%QW102"),
    ("product_valve_sp", "%QW103"),
    # ("hmi_pressure", "%MW20"),
    # ("hmi_level", "%MW21"),
    # ("hmi_f1_valve_pos", "%MW22"),
    # ("hmi_f1_flow", "%MW23"),
    # ("hmi_f2_valve_pos", "%MW24"),
    # ("hmi_f2_flow", "%MW25"),
    # ("hmi_purge_valve_pos", "%MW26"),
    # ("hmi_purge_flow", "%MW27"),
    # ("hmi_product_valve_pos", "%MW28"),
    # ("hmi_product_flow", "%MW29"),
    # ("scan_count", "%MW30"),
    # ("run_bit", "%QX0.5"),
    # ("attack", "%QX0.6"),
]

for i, (name, addr) in enumerate(VOI):
    if addr.startswith("%QX"):
        # print("COIL")
        VOI[i] = (name, addr, int(addr[5:]))
    elif addr.startswith("%QW"):
        # print("HOLDING REGISTER")
        VOI[i] = (name, addr, int(addr[3:]))
    elif addr.startswith("%MW"):
        # print("CONTROL REGISTER")
        VOI[i] = (name, addr, int(addr[3:]))
    elif addr.startswith("%IW"):
        # print("INPUT REGISTER")
        VOI[i] = (name, addr, int(addr[3:]))
        
# print(VOI)

variable_values = {}
fieldnames = [name for name, addr, tag in VOI] + ['timestamp']

def main(vector):
    with open(output_filepath, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        client = ModbusTcpClient("129.59.234.182")
        status = client.connect()
        print(f"Client connection status is {status}")

        try:
            while True:
                try:
                    read_input_registers = client.read_input_registers(address=100, count=13, slave=1)
                    # read_holding_registers = client.read_holding_registers(address=0,count=4,slave=1)
                    read_holding_registers_slaves = client.read_holding_registers(address=100,count=4,slave=1)
                    read_holding_registers_master = client.read_holding_registers(address=1025,count=30,slave=1)
                    read_coils = client.read_coils(0,7)
                    # discrete_inputs = client.read_discrete_inputs(0,1)
                    

                    for i, (name, addr, tag) in enumerate(VOI):
                        if addr.startswith("%QX"):
                            # print("COIL")
                            # tag = int(addr[5:])
                            variable_values[name] = read_coils.bits[tag]
                        elif addr.startswith("%QW"):
                            # print("HOLDING REGISTER")
                            # tag = int(addr[3:])
                            variable_values[name] = read_holding_registers_slaves.registers[tag-100]
                        elif addr.startswith("%MW"):
                            # print("CONTROL REGISTER")
                            # tag = int(addr[3:])
                            variable_values[name] = read_holding_registers_master.registers[tag-1]
                        elif addr.startswith("%IW"):
                            # print("INPUT REGISTER")
                            # tag = int(addr[3:])
                            variable_values[name] = read_input_registers.registers[tag-100]
                    
                    
                    print(variable_values)
                    
                    # Create a filtered dictionary to match fieldnames
                    filtered_values = {name: variable_values.get(name, '') for name in fieldnames}
                    filtered_values['timestamp'] = datetime.datetime.now().timestamp()
                    csv_writer.writerow(filtered_values)
                    csv_file.flush()

                    if 'vector' in locals() and vector:
                        client.write_registers(100, vector, slave=1)

                    # print(read_input_registers.registers)
                    # # print(read_holding_registers.registers)
                    # print(read_holding_registers_master.registers)
                    # print("----",read_holding_registers_slaves.registers)
                    
                    if not read_coils.isError():
                        print(read_coils.bits)

                except ModbusIOException as e:
                    print(f"Modbus error: {e}")
                except KeyboardInterrupt:
                    print("Keyboard interrupt received. Closing client.")
                    break

        finally:
            client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Modbus TCP Client')
    parser.add_argument('vector', type=int, nargs='*', default=[], help='List of integers to write to registers')
    args = parser.parse_args()
    main(args.vector)