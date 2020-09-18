# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:57:18 2015

@author: georg
"""
from PyQt5 import QtWidgets, QtGui
import scipy as sp


class Data_Selector_Widget(QtWidgets.QTableWidget):
    def __init__(self,Main,parent):
        super(Data_Selector_Widget, self).__init__()

        self.Main = Main
#        self.Main.Data_Selector = self
        self.Front_Control_Panel = parent
        self.init_UI()
        
    def init_UI(self):
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(['select data'])
        self.horizontalHeader().setStretchLastSection(True)

    def init_data(self):
                
        self.Main.Data.Metadata.paths = self.Main.Data.Metadata.paths
        self.setRowCount(len(self.Main.Data.Metadata.paths))
        
        # table entries
        for n, path in enumerate(self.Main.Data.Metadata.paths):
            self.setItem(n, 0, QtWidgets.QTableWidgetItem(self.Main.Data.Metadata.trial_labels[n]))
            
            color = self.Main.Options.view['colors'][n]
            QColor = QtGui.QColor(*color)
            QColor.setAlpha(100)
            self.item(n, 0).setBackground(QtGui.QBrush(QColor))  # FIXME find color solution

            verticalHeader = QtWidgets.QTableWidgetItem(str(n))
            verticalHeader.setBackground(QtGui.QBrush(QColor))
            
            QColor.setAlpha(255)
            verticalHeader.setForeground(QColor)
            
            self.setVerticalHeaderItem(n, verticalHeader)

        # connect
        self.itemSelectionChanged.connect(self.selection_changed)
        self.itemChanged.connect(self.labels_changed)
        
        # select all on startup
        selection = QtWidgets.QTableWidgetSelectionRange(0,0,len(self.Main.Data.Metadata.paths) - 1, 0)
        self.setRangeSelected(selection, True)
        
        self.verticalHeader().setStyle(QtWidgets.QStyleFactory.create('Cleanlooks')) # check on windows machines
        pass
    
    def update(self):
        pass
    
    def update_selection(self):
        # from monochrome toggler
        if self.Main.Options.view['show_monochrome'] is True:
            # disable all except the last selected dataset
            self.clearSelection()
            self.selectRow(self.Main.Options.view['last_selected']) # this should emit a selectionChanged
            self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        if self.Main.Options.view['show_monochrome'] is False:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    
    def reset(self):
        """ emtpy table """
        try:
            self.itemChanged.disconnect()
        except:
            pass
        if self.rowCount():
            self.setRowCount(0)

#        
#        for i in range(self.rowCount()):
#            item = self.takeItem(i,0)
#            pass

    def selection_changed(self):     
        selection = [item.row() for item in self.selectedItems()]
        if len(selection) > 0:
            last_selected = selection[-1] # FIXME this sometimes throws errors
            show_flags_updated = sp.zeros(len(self.Main.Data.Metadata.paths),dtype='bool')
            show_flags_updated[selection] = 1
            self.Main.Options.view['show_flags'] = show_flags_updated
            self.Main.Options.view['last_selected'] = last_selected
            
            self.Main.MainWindow.Data_Display.Traces_Visualizer.init_traces()
            self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.init_traces()
            self.Main.Signals.updateDisplaySettingsSignal.emit()

        pass


    def labels_changed(self):
        """ entry point for manual label change """
        current_labels = self.get_current_labels()
        self.update_labels(current_labels)
        
    def get_current_labels(self):
        """ reads the labels that are currently displayed """
        labels = [str(self.item(row,0).text()) for row in range(self.rowCount())]
        return labels
    
    def set_current_labels(self,labels):
        """ writes the labels currently displayed """
        self.blockSignals(True)
        for row in range(self.rowCount()):
            self.item(row,0).setText(labels[row])
        self.blockSignals(False)
        self.labels_changed()
    
    def update_labels(self,labels):
        """ update the trial_labels of the Metadata object, reinitialize
        Stimsorted """
        self.Main.Data.Metadata.trial_labels = labels
        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.init_data()
        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.init_traces()
        pass
        

if __name__ == '__main__':
    from .. import Main
    Main.main()
    pass