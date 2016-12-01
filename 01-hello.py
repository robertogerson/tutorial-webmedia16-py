import sys, gi
gi.require_version ('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

playbin = Gst.ElementFactory.make("playbin", None)
assert (playbin)

playbin.set_property("uri", "file://" + sys.argv[1])

ret = playbin.set_state(Gst.State.PLAYING)
assert (ret != Gst.StateChangeReturn.FAILURE)

bus = playbin.get_bus()
msg = bus.timed_pop_filtered (
    Gst.CLOCK_TIME_NONE,
    Gst.MessageType.ERROR | Gst.MessageType.EOS )

playbin.set_state(Gst.State.NULL)

