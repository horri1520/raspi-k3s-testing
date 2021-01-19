import sys

import gi
from gi.repository import GLib, Gst, GstVideo, Tcam

gi.require_version("Tcam", "0.1")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")


CAM_ADDRESS = '192.168.1.59'


def main():
    try:
        Gst.init(sys.argv)
        source = Gst.ElementFactory.make("tcambin")
        serials = source.get_device_serials()

        print(serials)


if __name__ == "__main__":
    main()
