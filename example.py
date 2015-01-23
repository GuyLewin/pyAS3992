import as3992_api

def main():
    ann = as3992_api.AntennaDevice()
    
    print "Firmware info: %s\nHardware info: %s" % ann.get_system_info()

    print "Activating antenna"
    ann.set_antenna_state(True)

    print "Tags:"
    for epc, rssi in ann.iter_epc_rssi():
        print epc.encode("HEX"), rssi

    ann.set_antenna_state(False)

if __name__ == "__main__":
    main()
