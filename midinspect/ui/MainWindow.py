from typing import Optional

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import rtmidi

STATUS_NOTE_OFF = 0x80
STATUS_NOTE_ON = 0x90
STATUS_POLYPHONIC_AFTERTOUCH = 0xA0
STATUS_CONTROL_CHANGE = 0xB0
STATUS_PROGRAM_CHANGE = 0xC0
STATUS_MONOPHONIC = 0xD0
STATUS_PITCH_BENDING = 0xE0
STATUS_SYSTEM = 0xF0


class InputEventHandler(object):
    def __init__(self, messageFunction):
        self.messageFunction = messageFunction

    def __call__(self, event, data=None):
        message, deltatime = event
        print("Got MIDI Event !")
        self.messageFunction(message, deltatime)


class MainWindow(QMainWindow):

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

        self.CONTROL_LUT = {
            STATUS_NOTE_OFF: "NOTE OFF",
            STATUS_NOTE_ON: "NOTE ON",
            STATUS_POLYPHONIC_AFTERTOUCH: "POLYPHONIC AFTERTOUCH",
            STATUS_CONTROL_CHANGE: "CONTROL CHANGE",
            STATUS_PROGRAM_CHANGE: "PROGRAM CHANGE",
            STATUS_MONOPHONIC: "MONOPHONIC",
            STATUS_PITCH_BENDING: "PITCH BENDING",
            STATUS_SYSTEM: "SYSTEM"
        }

        self.edit_incoming: Optional[QTextEdit]
        self.edit_outgoing: Optional[QTextEdit]

        self.combo_control: Optional[QComboBox]
        self.spin_channel: Optional[QSpinBox]
        self.spin_data1: Optional[QSpinBox]
        self.spin_data2: Optional[QSpinBox]
        self.btn_send: Optional[QToolButton]

        self.midiIn = None
        self.midiOut = None

        self.isOpen = False

        self.html_head = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd\">\n<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\np, li { white-space: pre-wrap; }\n</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
        self.html_paraStart = "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">"
        self.html_paraEnd = "</p>\n"
        self.html_foot = "</body></html>"

        self.incoming: str = ""
        self.outgoing: str = ""

        uic.loadUi('GUI/Windows/mainwindow.ui', self)

        self.loadControls()

        self.openMIDI()

    def loadControls(self):
        for k in self.CONTROL_LUT:
            self.combo_control.addItem(self.CONTROL_LUT[k], k)

        self.btn_send.clicked.connect(self.onSend)

    def openMIDI(self):
        self.midiOut = rtmidi.MidiOut()
        self.midiOut.open_port(1)

        self.midiIn = rtmidi.MidiIn()
        self.midiIn.open_port(0)

        self.midiIn.set_callback(InputEventHandler(self.appendMessage))
        self.isOpen = True

    def closeMIDI(self):
        self.isOpen = False

        self.midiIn.close_port()
        del self.midiIn
        self.midiIn = None

        self.midiOut.close_port()
        del self.midiOut
        self.midiOut = None

    def cleanup(self):
        self.closeMIDI()

    def onSend(self, triggered=False):
        self.combo_control: Optional[QComboBox]
        self.spin_channel: Optional[QSpinBox]
        self.spin_data1: Optional[QSpinBox]
        self.spin_data2: Optional[QSpinBox]

        control = self.combo_control.currentData()
        ctrl = control + self.spin_channel.value()
        data1 = self.spin_data1.value()
        data2 = self.spin_data2.value()

        msg = [ctrl, data1]

        if (control != 0xC0) and (control != 0xD0):
            msg.append(data2)

        self.midiOut.send_message(msg)
        self.appendMessage(msg, 0, isIncoming=False)

    #region Message Generation

    def appendMessage(self, message, deltaTime, isIncoming=True):
        print("Got Message:", message)

        if len(message) < 3:
            message.append(0x00)
            message.append(0x00)
            message.append(0x00)

        #txt = "[{delta:.6F}] {control:>32} channel={channel:02X} data={data1:02X}{data2:02X}"
        msg = "[{delta:.6F}] {control:>16} channel={channel:02d} data={data1:03d} {data2:03d}".format(delta=deltaTime, control=self.CONTROL_LUT[message[0] & 0xF0], channel=(message[0] & 0x0F),
                         data1=message[1]&0xff, data2=message[2]&0xff)

        self.addMessageToWidget(msg, isIncoming)

    def addMessageToWidget(self, message, isIncoming: bool):
        msg = message

        if isIncoming:
            self.edit_incoming.append(self.writeLine(msg, "#008800"))
            self.edit_outgoing.append(self.writeLine(msg, "#888888"))
        else:
            self.edit_incoming.append(self.writeLine(msg, "#888888"))
            self.edit_outgoing.append(self.writeLine(msg, "#880000"))

        self.edit_incoming.verticalScrollBar().setValue(self.edit_incoming.verticalScrollBar().maximum())
        self.edit_outgoing.verticalScrollBar().setValue(self.edit_outgoing.verticalScrollBar().maximum())

    def writeLine(self, message, color):
        return "<pre><span style=\" color:" + color + ";\">" + message + "</span></pre>"

    #endregion
