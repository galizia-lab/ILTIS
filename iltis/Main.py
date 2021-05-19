# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:29:30 2015

@author: georg
"""
import sys
import os
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg


from iltis.Objects.Options_Object import Options_Object
from iltis.Objects.Processing_Object import Processing_Object
from iltis.Objects.ROIs_Object import ROIs_Object
from iltis.Objects.IO_Object import IO_Object
from iltis.Widgets.MainWindow_Widget import MainWindow_Widget
from iltis.Signals import Signals

# pg.setConfigOption("useOpenGL", True)
pg.setConfigOptions(antialias=True)


class Main(QtCore.QObject):

    def __init__(self, verbose=False):
        super(Main, self).__init__()

        # fields
        self.cwd = None
        self.program_dir = None
        self.graphics_path = None  # move to MainWindow
        self.tmp_path = None
        self.data_path = None
        self.roi_path = None
        self.Data = None
        self.verbose = verbose

        self.initialize_paths()
        self.print_startup_msg()

        # ini
        self.IO = IO_Object(self)
        self.Options = Options_Object(self)
        self.Processing = Processing_Object(self)
        self.ROIs = ROIs_Object(self)

        self.MainWindow = MainWindow_Widget(self)

        # centrally managed signals
        self.Signals = Signals(self)

    # initializers
    def initialize_paths(self):
        """ initializes current working directory, path of the program
        path to the graphics files, path to tmp """

        self.cwd = os.getcwd()
        self.data_path = self.cwd
        self.roi_path = self.cwd
        self.program_dir = os.path.split(os.path.realpath(__file__))[0] # of the dir where this code is executed from!
        self.graphics_path = self.program_dir + os.path.sep + 'graphics'
        if os.name == 'posix':
            self.tmp_path = '/tmp'
        else:
            self.tmp_path = 'C:\\Windows\\temp'

    # messages
    def print_startup_msg(self):

        print("no startup msg set")
#        print "this is ILTIS version" + self.version
#        print "os type: ", os.name
#        print "Process ID: ", os.getpid()


#    def cleanup(self):
#        """ remove tmp files """
#        for dirpath, dirnames, filenames in os.walk(self.tmp_path):
#            for filename in [f for f in filenames if f.endswith('.npa')]:
#                filepath = os.path.join(dirpath, filename)
#                if self.Options.general['verbose']:
#                    print "removing file: ",filepath
#                os.remove(filepath)

def main():

    # run application
    app = QtWidgets.QApplication(sys.argv)
    Iltis = Main(verbose=True)
    return_code = app.exec_()

    if return_code != 0:
        print(("exiting with return code: ", return_code))

    # after closing MainWindow, do cleanup and exit
    pg.exit()  # the exit hammer
    pass


if __name__ == '__main__':
    main()
