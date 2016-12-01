import sys, gi
gi.require_version ('Gst', '1.0')
from gi.repository import Gst

Gst.init(sys.argv)

pipeline = Gst.ElementFactory.make("pipeline", "mp3")

src = Gst.ElementFactory.make ("filesrc", "src")
dec = Gst.ElementFactory.make ("mad", "dec")
sink = Gst.ElementFactory.make ("alsasink", "sink")
assert (pipeline and src and dec and sink)

pipeline.add(src)
pipeline.add(dec)
pipeline.add(sink)

src.link(dec)
dec.link(sink)

src.set_property ("location", sys.argv[1])

ret = pipeline.set_state (Gst.State.PLAYING)
assert (ret != Gst.StateChangeReturn.FAILURE)

bus = pipeline.get_bus()
msg = bus.timed_pop_filtered (
    Gst.CLOCK_TIME_NONE,
    Gst.MessageType.ERROR | Gst.MessageType.EOS)

pipeline.set_state(Gst.State.NULL)

