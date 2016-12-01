import sys
import gi
gi.require_version ('Gst', '1.0')
from gi.repository import Gst

videofilters = {
  "coloreffects": {"preset": 1},
  "dicetv": None,
  "shagadelictv": None,
  "edgetv": None,
  "revtv": None
}

audiofilters = {
  "volume": {"volume": 2.0},
  "pitch": {"pitch": 0.5},
  "audioecho": {"delay": Gst.SECOND, "intensity": 1.0},
  "feeverb": {"room-size": 1.0, "level": 1.0},
  "equalizer-3bands": {"band0": 12.0, "band1": -24.0}
}

def pad_added_cb(demux, srcpad):
  pipeline = demux.get_parent()
  caps = srcpad.query_caps()
  name = caps.get_structure(0).get_name()
  pre = newfilter = pos = sink = filter_name = filter_params = None
  if name == "audio/x-raw":
    filter_name = sys.argv[2]
    filter_params = audiofilters[filter_name]

    pre = Gst.ElementFactory.make ("audioconvert")
    newfilter = Gst.ElementFactory.make (filter_name)
    pos = Gst.ElementFactory.make ("audioconvert")
    sink = Gst.ElementFactory.make ("autoaudiosink")

  elif name ==  "video/x-raw":
    filter_name = sys.argv[3]
    filter_params = videofilters[filter_name]

    pre = Gst.ElementFactory.make ("videoconvert")
    newfilter = Gst.ElementFactory.make(filter_name)
    pos = Gst.ElementFactory.make ("videoconvert")
    sink = Gst.ElementFactory.make ("autovideosink")

  assert ( pre and newfilter and pos and sink )
  pipeline.add(pre); pre.sync_state_with_parent()
  pipeline.add(newfilter); newfilter.sync_state_with_parent()
  pipeline.add(pos); pos.sync_state_with_parent()
  pipeline.add(sink); sink.sync_state_with_parent()

  # set filter properties
  if filter_params:
    for k, v in filter_params.items():
      newfilter.set_property(k, v)

  srcpad.link(pre.get_static_pad("sink"))
  pre.link (newfilter)
  newfilter.link(pos)
  pos.link (sink)

# Main
Gst.init(sys.argv)

pipeline = Gst.ElementFactory.make("pipeline", "filter")
src = Gst.ElementFactory.make ("uridecodebin", "src")
assert (pipeline and src)

pipeline.add (src)
src.set_property ("uri", "file://" + sys.argv[1]) 
src.connect ("pad-added", pad_added_cb) 

ret = pipeline.set_state (Gst.State.PLAYING)
assert (ret != Gst.StateChangeReturn.FAILURE)

bus = pipeline.get_bus()
msg = bus.timed_pop_filtered (
    Gst.CLOCK_TIME_NONE,
    Gst.MessageType.ERROR | Gst.MessageType.EOS)

pipeline.set_state(Gst.State.NULL)

