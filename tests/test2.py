import bluetooth

services = bluetooth.find_service(
    uuid=bluetooth.SERIAL_PORT_CLASS,
    address="34:09:C9:2F:1A:98",
)

print(services)