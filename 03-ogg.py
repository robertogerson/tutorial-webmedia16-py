import sys, gi
gi.require_version ('Gst', '1.0')
from gi.repository import Gst

def pad_added_cb(demux, srcpad):
  pipeline = demux.get_parent()
  caps = srcpad.query_caps()
  name = caps.get_structure(0).get_name()

  if name == "audio/x-vorbis":
    dec = Gst.ElementFactory.make ("vorbisdec")
    conv = Gst.ElementFactory.make ("audioconvert")
    sink = Gst.ElementFactory.make ("alsasink")
    assert (dec and conv and sink)

    pipeline.add(dec); dec.sync_state_with_parent()
    pipeline.add(conv); conv.sync_state_with_parent()
    pipeline.add(sink); sink.sync_state_with_parent()

    srcpad.link(dec.get_static_pad("sink"))
    dec.link(conv)
    conv.link(sink)

  elif name ==  "video/x-theora":
    queue = Gst.ElementFactory.make ("queue")
    dec = Gst.ElementFactory.make ("theoradec")
    sink = Gst.ElementFactory.make ("xvimagesink")
    assert (queue and dec and sink)

    pipeline.add(queue); queue.sync_state_with_parent()
    pipeline.add(dec); dec.sync_state_with_parent()
    pipeline.add(sink); sink.sync_state_with_parent()

    srcpad.link(queue.get_static_pad("sink"))
    queue.link(dec)
    dec.link(sink)

# Main
Gst.init(sys.argv)

pipeline = Gst.ElementFactory.make("pipeline", "ogg")
src = Gst.ElementFactory.make ("filesrc", "src")
demux = Gst.ElementFactory.make ("oggdemux", "demux")
sink = Gst.ElementFactory.make ("alsasink", "sink")
assert (pipeline and src and demux and sink)

src.set_property ("location", sys.argv[1])

pipeline.add(src)
pipeline.add(demux)
pipeline.add(sink)

src.link(demux)
demux.connect("pad-added", pad_added_cb)

ret = pipeline.set_state (Gst.State.PLAYING)
assert (ret != Gst.StateChangeReturn.FAILURE)

bus = pipeline.get_bus()
msg = bus.timed_pop_filtered (
    Gst.CLOCK_TIME_NONE,
    Gst.MessageType.ERROR | Gst.MessageType.EOS)

pipeline.set_state(Gst.State.NULL)

