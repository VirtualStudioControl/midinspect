import rtmidi

midiout = rtmidi.MidiOut()
available_ports_out = midiout.get_ports()

midiin = rtmidi.MidiIn()
available_ports_in = midiin.get_ports()

print("Input Ports:", available_ports_in)
print("Output Ports:", available_ports_out)