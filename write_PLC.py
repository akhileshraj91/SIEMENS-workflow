from pymodbus.client import ModbusTcpClient
import argparse

def main(vector):
    client = ModbusTcpClient("129.59.234.182")
    status = client.connect()
    print(f"Client connection status is {status}")


    if vector != []:
        client.write_registers(1025, vector, slave=1)
        
    client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Modbus TCP Client')
    parser.add_argument('vector', type=int, nargs='*', default=[], help='List of integers to write to registers')
    args = parser.parse_args()
    main(args.vector)