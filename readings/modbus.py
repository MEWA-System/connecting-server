import pymodbus
import yaml

global data
global electric_meter


def load_register_reference():
    with open("modbus_registers.yaml", "r") as stream:
        try:
            global data, electric_meter
            data = yaml.safe_load(stream)
            electric_meter = data["electric_meter"]
        except yaml.YAMLError as ex:
            print(ex)


if __name__ == "__main__":
    load_register_reference()
    print(electric_meter)
    print(electric_meter["registers"]["phases"][1]["voltage"])
