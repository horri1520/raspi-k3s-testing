import sys

import gi
from gi.repository import GLib, Gst, GstVideo, Tcam

gi.require_version("Tcam", "0.1")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")


CAM_ADDRESS = '192.168.1.59'


def get_frame_rate_list(source, format_number):

    caps = source.get_static_pad("src").query_caps()
    ret = [caps.get_structure(i) for i in range(caps.get_size())]
    structure = ret[format_number]

    try:
        rates = structure.get_value("framerate")
    except TypeError:
        import re
        substr = structure.to_string(
        )[structure.to_string().find("framerate="):]
        field, values, remain = re.split("{|}", substr, maxsplit=3)
        rates = [x.strip() for x in values.split(",")]
    return rates


def main():
    Gst.init(sys.argv)
    source = Gst.ElementFactory.make("tcambin")
    serials = source.get_device_serials()
    for serial in serials:
        print(serial)

    format_number = 10
    pipeline = Gst.parse_launch("tcambin name=bin"
                                " ! capsfilter name=filter"
                                " ! videoconvert"
                                " ! appsink name=sink"
                                )

    if len(serials) != 0:
        camera = pipeline.get_by_name("bin")
        camera.set_property("serial", serials[0])
    else:
        print('ERROR: Cannot detect tiscamera.')
        sys.exit()

    # camera.set_state(Gst.State.READY)
    # caps = Gst.Caps.new_empty()

    # structure = Gst.Structure.new_from_string("video/x-raw")

    # frame_rates = get_frame_rate_list(camera, format_number)
    # print(frame_rates)
    # rate = frame_rates[0]


if __name__ == "__main__":
    main()
