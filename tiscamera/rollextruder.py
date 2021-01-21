from gi.repository import Gst, GLib, Tcam, GstVideo
import datetime
import argparse
import sys
import os
import numpy as np
import cv2
import gi
import socket
gi.require_version("Tcam", "0.1")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")


def callback(appsink, save_dir):
    sample = appsink.emit("pull-sample")

    if sample:
        caps = sample.get_caps()
        gst_buffer = sample.get_buffer()

        try:
            (ret, buffer_map) = gst_buffer.map(Gst.MapFlags.READ)

            video_info = GstVideo.VideoInfo()
            video_info.from_caps(caps)
            height = video_info.height
            width = video_info.width

            img_array = np.asarray(bytearray(buffer_map.data), dtype=np.uint8)
            img = img_array.reshape((height, width, 4))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            dt_now = datetime.datetime.now()
            dt_str = dt_now.strftime('%Y-%m-%d_%H-%M-%S-%f')
            save_name = "%s.jpg" % (dt_str)
            save_path = os.path.join(save_dir, save_name)
            cv2.imwrite(save_path, img_rgb)
        finally:
            gst_buffer.unmap(buffer_map)

    return Gst.FlowReturn.OK


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


def get_args():
    parse = argparse.ArgumentParser(description="Capture process")
    parse.add_argument("--camera", "-c", type=int, default=-1,
                       help="Camera id for trimer.")
    parse.add_argument("--width", "-w", default="",
                       help="Board width for trimer.")
    parse.add_argument("--savedir", "-s", default="",
                       help="Path to directory of saveing images")
    parse.add_argument("--port", "-p", type=int, default=0,
                       help="Socket connect port for tiscamera.")
    return parse.parse_args()


def main():
    try:
        Gst.init(sys.argv)
        args = get_args()
        source = Gst.ElementFactory.make("tcambin")
        serials = source.get_device_serials()
        serial = serials[args.camera]
        port = args.port
        print(serial)
        # rggb 1280 * 1024
        format_number = 10
        pipeline = Gst.parse_launch("tcambin name=bin"
                                    " ! capsfilter name=filter"
                                    " ! videoconvert"
                                    " ! appsink name=sink"
                                    )

        if serial is not None:
            # retrieve the bin element from the pipeline
            camera = pipeline.get_by_name("bin")
            camera.set_property("serial", serial)

        camera.set_state(Gst.State.READY)
        caps = Gst.Caps.new_empty()

        structure = Gst.Structure.new_from_string("video/x-raw")

        frame_rates = get_frame_rate_list(camera, format_number)
        rate = frame_rates[0]
        if type(rate) == Gst.Fraction:
            structure.set_value("framerate", rate)
        else:
            numerator, denominator = rate.split("/")
            try:
                fraction = Gst.Fraction(int(numerator), int(denominator))
                structure.set_value("framerate", fraction)
            except TypeError:
                struc_string = structure.to_string()

                struc_string += ",framerate={}/{}".format(
                    int(numerator), int(denominator))
                structure.free()
                structure, end = structure.from_string(struc_string)

        caps.append_structure(structure)

        structure.free()
        # structure is not useable from here on

        capsfilter = pipeline.get_by_name("filter")

        if not capsfilter:
            print("Could not retrieve capsfilter from pipeline.")
            return 1

        capsfilter.set_property("caps", caps)

        cam_dir = "roll-cam-%d" % args.camera
        save_dir = os.path.join(args.savedir, cam_dir)
        os.makedirs(save_dir, exist_ok=True)

        output = pipeline.get_by_name("sink")
        output.set_property("emit-signals", True)
        output.connect("new-sample", callback, save_dir)

        pipeline.set_state(Gst.State.PLAYING)

        loop = GLib.MainLoop()
        print("start capturing roll-cam-%d" % args.camera)
        loop.run()
        pipeline.set_state(Gst.State.NULL)
    except KeyboardInterrupt:
        pipeline.set_state(Gst.State.NULL)
        print("terminate capturing roll-cam-%d" % args.camera)
    except Exception as e:
        print(str(e))
        pipeline.set_state(Gst.State.NULL)
        sys.exit()


if __name__ == "__main__":
    main()
