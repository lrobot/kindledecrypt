#!/usr/bin/python

"""
    Kindle Book Decrypter
    =====================
    Simple GUI for MobiDeDRM code written with wxWidgets. This GUI takes a 
    serial number and encrypted book file and outputs an unencrypted book
    that can be used to backup your data or legally remove audio and other
    restrictions by allowing you to convert to other formats.
    
    License
    -------
    Copyright (C) 2010 Daniel G. Taylor <dan@programmer-art.org>
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

__author__ = "Daniel G. Taylor"
__version__ = 1.0

import ConfigParser
import mobidedrm
import optparse
import os
import sys
import wx

import process

CONFIG = os.path.expanduser("~/.mobidedrmwx.cfg")

class MobiDeDrmApp(wx.App):
    """
        The main application holding all windows, controls, etc.
    """
    def __init__(self, redir=False):
        super(MobiDeDrmApp, self).__init__(redir)
        
        self.config = ConfigParser.SafeConfigParser()
        if os.path.exists(CONFIG):
            self.config.read(CONFIG)
        
        if not self.config.has_section("General"):
            self.config.add_section("General")
        
        if self.config.has_option("General", "Serial"):
            default_serial = self.config.get("General", "Serial")
        else:
            # This is just a random example serial
            default_serial = "B002A1C457493453"
        
        self.frame = wx.Frame(None, wx.ID_ANY, "Kindle Book Decrypter", size=(400, 130))
        
        self.panel = wx.Panel(self.frame)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.grid = wx.GridBagSizer(3, 3)
        self.serial_label = wx.StaticText(self.panel, label="Serial:")
        self.serial = wx.TextCtrl(self.panel, value=default_serial)
        self.serial_help = wx.StaticText(self.panel, label="Kindle or Kindle for iPhone serial number")
        font = self.serial_help.GetFont()
        font.SetPointSize(8)
        self.serial_help.SetFont(font)
        self.input_label = wx.StaticText(self.panel, label="Book:")
        self.input = wx.FilePickerCtrl(self.panel, wildcard="Kindle Books|*.azw;*.mobi|All Files|*.*")
        self.button = wx.Button(self.panel, label="Decrypt")
        
        self.grid.Add(self.serial_label, (0, 0), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        self.grid.Add(self.serial, (0, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        self.grid.Add(self.serial_help, (1, 1))
        self.grid.Add(self.input_label, (2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.grid.Add(self.input, (2, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        self.grid.Add(self.button, (3, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        
        self.grid.AddGrowableCol(1, 1)
        
        self.vbox.Add(self.grid, 1, wx.ALL | wx.EXPAND, border=5)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self.frame)
        
        self.frame.Bind(wx.EVT_BUTTON, self.on_process, self.button)
        self.frame.Bind(wx.EVT_TEXT, self.on_serial_changed, self.serial)
        
        self.frame.Centre()
        self.frame.Show(True)
    
    def on_serial_changed(self, event):
        """
            The serial number has changed. If it is the correct number of
            characters then enable the decrypt button, otherwise disable it
            until a valid serial is entered.
        """
        serial = self.serial.GetValue()
        if len(serial) in [16, 40]:
            self.button.Enable()
            self.config.set("General", "Serial", self.serial.GetValue())
            self.config.write(open(CONFIG, "w"))
        else:
            self.button.Disable()
    
    def on_process(self, event):
        """
            The decrypt button was clicked, so start the decrypting process.
            This shows a pulsing progress dialog while the book is decrypted,
            displaying a dialog for any errors that are encountered.
        """
        infile = self.input.GetPath()
        
        if not os.path.exists(infile):
            error_dialog = wx.MessageDialog(self.panel, "Error: Input file doesn't exist!", "Error procesesing file!", wx.OK | wx.ICON_ERROR)
            error_dialog.ShowModal()
            error_dialog.Destroy()
            return
        
        outfile = os.path.splitext(infile)[0] + ".mobi"
        pid = mobidedrm.getPid(self.serial.GetValue())
        dialog = wx.ProgressDialog("Progress", "Decrypting...")
        dialog.Pulse()
        dialog.Show()
        for error in process.decrypt(infile, outfile, pid):
            dialog.Pulse()
            wx.Yield()
        
        if error:
            error_dialog = wx.MessageDialog(self.panel, "Error: %s" % error, "Error processing file!", wx.OK | wx.ICON_ERROR)
            error_dialog.ShowModal()
            error_dialog.Destroy()
        
        dialog.Destroy()

if __name__ == "__main__":
    parser = optparse.OptionParser("%prog [options]", version="Kindle Book Decrypter %s" % __version__)
    
    options, args = parser.parse_args()    
    
    app = MobiDeDrmApp()
    app.MainLoop()

