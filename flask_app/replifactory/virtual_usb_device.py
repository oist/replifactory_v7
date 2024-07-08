from usb.core import Device as UsbDevice, Configuration as UsbConfiguration


class VirtualUsbDevice(UsbDevice):
    class Device:
        pass

    class DeviceDescriptor:
        bLength = 0
        bDescriptorType = 0
        bcdUSB = 0
        bDeviceClass = 0
        bDeviceSubClass = 0
        bDeviceProtocol = 0
        bMaxPacketSize0 = 0
        idVendor = 0
        idProduct = 0
        bcdDevice = 0
        iManufacturer = 0
        iProduct = 0
        iSerialNumber = 0
        bNumConfigurations = 0
        address = 0
        bus = 0
        port_number = 0
        port_numbers = 0
        speed = 0

    class ConfigurationDescriptor(UsbConfiguration):
        bLength = 0
        bDescriptorType = 0
        wTotalLength = 0
        bNumInterfaces = 2
        bConfigurationValue = 0
        iConfiguration = 0
        bmAttributes = 0
        bMaxPower = 0
        extra_descriptors = 0

        def __init__(self, device, configuration=0):
            self.device = device
            self.index = configuration

    class InterfaceDescriptor:
        bLength = 0
        bDescriptorType = 0
        bInterfaceNumber = 0
        bAlternateSetting = 0
        bNumEndpoints = 2
        bInterfaceClass = 0
        bInterfaceSubClass = 0
        bInterfaceProtocol = 0
        iInterface = 0
        extra_descriptors = 0

    class EndpointDescriptor:
        bLength = 0
        bDescriptorType = 0
        bEndpointAddress = 0
        bmAttributes = 0
        wMaxPacketSize = 0
        bInterval = 0
        bRefresh = 0
        bSynchAddress = 0
        extra_descriptors = 0

    class Backend:
        def get_device_descriptor(self, dev):
            return VirtualUsbDevice.DeviceDescriptor()

        def open_device(self, dev):
            return self

        def close_device(self, dev):
            return self

        def get_configuration_descriptor(self, device, configuration=0):
            return VirtualUsbDevice.ConfigurationDescriptor(
                device=device, configuration=configuration
            )

        def set_configuration(self, *args, **kwargs):
            pass

        def get_interface_descriptor(self, *args, **kwargs):
            return VirtualUsbDevice.InterfaceDescriptor()

        def get_endpoint_descriptor(self, *args, **kwargs):
            return VirtualUsbDevice.EndpointDescriptor()

        def is_kernel_driver_active(self, *args, **kwargs):
            return False

        def ctrl_transfer(
            self, handle, bmRequestType, bRequest, wValue, wIndex, buff, timeout
        ):
            return len(buff) * buff.itemsize

        def attach_kernel_driver(self, *args, **kwargs):
            pass

    def __init__(self):
        super().__init__(VirtualUsbDevice.Device(), VirtualUsbDevice.Backend())
        self._manufacturer = "OIST"
        self._product = "Virtual Replifactory"
        self._serial_number = "VIRTUAL"
        self.id = f"/dev/bus/usb/{self.bus:03}/{self.address:03}"
        self._langids = (0x0409,)
        self._has_parent = False
