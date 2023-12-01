# G-Codes for replifactory v5
## Experiment commands
* Stirrer V<vial> S<speed>
* Stop stirring V<vial>
* Measure optical density V<vial> [L<laser>]
* Measure temperature T<thermometer>
* Pump P<pump> S<speed> [V<volume>] V<vial>
* Stop pumping P<pump>

## Devices
M101 P1 S<speed> [V<volume>]  ; pump liquid from Pump 1, where <speed> is the desired flow rate in milliliters per minute and <volume> is desired volume in milliliters
M102 P1  ; stop pumping
M103 V1  ; open valve 1
M104 V1  ; close valve 1
M105 S1 R<speed>  ; stir with stirrer 1 where <speed> is desired rotation speed in revolution per minute
M106 S1  ; stop stirring with stirrer 1
M107 O1  ; measure optical density with sensor 1 and read the value from the serial output
M108 T1  ; measure temperature with thermometer 1 and read the value from the serial output

