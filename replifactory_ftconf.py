import os
import sys
bin_dir = os.path.dirname(sys.executable)
sys.path.insert(0, bin_dir)
import replifactory.drivers.ftdi
sys.modules["pyftdi.ftdi"] = replifactory.drivers.ftdi
import ftconf

if __name__ == '__main__':
    ftconf.main()
