# Replifactory

### New device initialization
#### Write USB String Descriptor
For PCBv5:
1. Plug only one instance of replifactory machine to USB port.
2. Run `poetry run python replifactory_ftconf.py` to get list of devices urls. Output should looks like:
   ```
   Available interfaces:
   ftdi://ftdi:2232:1:e/1   (Dual RS232-HS)
   ftdi://ftdi:2232:1:e/2   (Dual RS232-HS)

   Please specify the USB device
   ```
   Copy address interface address that ends with 2. E.g.: `ftdi://ftdi:2232:1:e/2`
3. Now write new machine serial number to selected interface:
   ```
   poetry run python replifactory_ftconf.py -i data.ini -s FT050000 -u ftdi://ftdi:2232:1:e/2
   ```
4. Check the result. Read configuration from EEPROM:
   ```
   poetry run python replifactory_ftconf.py -o - ftdi://ftdi:2232:1:e/2 
   ```
   Output should look like:
   ```
   [values]
   chip = 0xff
   vendor_id = 0x0403
   product_id = 0x6010
   type = 0x0700
   self_powered = true
   remote_wakeup = true
   power_max = 0
   has_serial = true
   suspend_pull_down = true
   out_isochronous = true
   in_isochronous = true
   manufacturer = OIST_ESB
   product = Replifactory
   serial = FT050005
   channel_a_driver = VCP
   channel_b_driver = VCP
   group_0_drive = 16
   group_0_schmitt = true
   group_0_slow_slew = true
   group_1_drive = 16
   group_1_schmitt = true
   group_1_slow_slew = true
   group_2_drive = 16
   group_2_schmitt = true
   group_2_slow_slew = true
   group_3_drive = 16
   group_3_schmitt = true
   group_3_slow_slew = true
   channel_a_type = UART
   channel_b_type = UART
   suspend_dbus7 = true

   [raw]
   @00 = ffff030410600007ff00ffffffff9a12
   @10 = ac1ac612ffffffffffffffffffffffff
   @20 = ffffffffffffffffffffffffffffffff
   @30 = ffffffffffffffffffffffffffffffff
   @40 = ffffffffffffffffffffffffffffffff
   @50 = ffffffffffffffffffffffffffffffff
   @60 = ffffffffffffffffffffffffffffffff
   @70 = ffffffffffffffffffffffffffffffff
   @80 = ffffffffffffffffffffffffffffffff
   @90 = ffffffffffffffffffff12034f004900
   @a0 = 530054005f004500530042001a035200
   @b0 = 650070006c0069006600610063007400
   @c0 = 6f007200790012034600540030003500
   @d0 = 30003000300035000000000000000000
   @e0 = 00000000000000000000000000000000
   @f0 = 0000000000000000000000000000c2d4
   ```
   Check that parameter serial equals to your value from step 3.