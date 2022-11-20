# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:54:33 2015

@author: georg
"""
import sys, os
import scipy as sp
import numpy as np
from scipy import ndimage
from PyQt5.QtGui import QColor
import pyqtgraph as pg


class Processing_Object(object):
    def __init__(self,Main):
        self.Main = Main
        self.Data = None
        pass

    def calc_gaussian_smooth(self):
        """ apply gaussian """
        xy,z = sp.float32(self.Main.Options.preprocessing['filter_size'])
        filter_size = (xy,xy,z)

        for n in range(self.Main.Data.nTrials):
            self.Main.MainWindow.statusBar().showMessage("calculating gaussian smooth on Dataset " + str(n))
            if self.Main.Options.preprocessing['filter_target'] == 'raw':
                self.Main.Data.raw[:,:,:,n] = ndimage.gaussian_filter(self.Main.Data.raw[:,:,:,n],filter_size)
            if self.Main.Options.preprocessing['filter_target'] == 'dFF':
                self.Main.Data.dFF[:,:,:,n] = ndimage.gaussian_filter(self.Main.Data.dFF[:,:,:,n],filter_size)
        self.Main.MainWindow.statusBar().clearMessage()

        self.Main.Signals.updateDisplaySettingsSignal.emit()
        self.Main.MainWindow.Data_Display.Traces_Visualizer.update_traces()
        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update_traces()
        pass

    def first_time_dFF(self):
        """ is connected to ... and executed upon dFF toggle. If dFF is zeros,
        then calc it now. """
        ## from dFF toggler
        if self.Main.Options.view['show_dFF'] == True:
            # if no dFF has been calculated, do so now.
            if not(self.Main.Options.flags['dFF_was_calc']):

                self.calc_dFF()
                self.Main.Options.flags['dFF_was_calc'] = True
                self.Main.Data_Display.LUT_Controlers.reset_levels()


    def calc_dFF(self):
        """ calculates:
        data = x,y,t
        frames = (f1,f2) frames to consider, background is calculated avg(f1:f2)

        deltaF / F = (F - F_background) / F_background
        works on 3d version for memory efficiency. When this function is called,
        it has to be explicitly iterated over the datasets
        """

        f_start,f_stop = self.Main.Options.preprocessing['dFF_frames']

        if sp.any(self.Main.Data.raw == 0): # add offset if 0 intensity pixels exist
            data_tmp = self.Main.Data.raw + 100
        else:
            data_tmp = self.Main.Data.raw

        bck = sp.average(data_tmp[:,:,f_start:f_stop,:],axis=2)[:,:,sp.newaxis,:]
        self.Main.Data.dFF = (data_tmp - bck) / bck
        self.Main.Options.flags['dFF_was_calc'] = True

    def calc_avg(self):
        f_start,f_stop = self.Main.Options.preprocessing['avg_frames']
        sp.average(self.Main.Data.raw[:,:,f_start:f_stop,:],axis=2)

#==============================================================================
    ### dataset extraction related
#==============================================================================

    def calc_tvec(self,t0=None):
        """ calculates a time vector based on dt. if t0 is not given, the
        start of the first stimulus is t0 """

        # get
        dt = self.Main.Options.preprocessing['dt']
        nFrames = self.Main.Data.nFrames
        if t0 == None:
            t0 = self.Main.Options.preprocessing['stimuli'][0,0] * dt

        # calc
        tvec = sp.arange(0,nFrames*dt,dt)
        tvec = tvec - t0

        # store
        self.Main.Data.Metadata.dt = dt
        self.Main.Data.Metadata.tvec = tvec
        return tvec


    def calc_extraction_mask(self):
        """ calculates boolean extraction mask based on current ROIs
        extraction mask as the shape of (x,y,nROIs), True if pixel is inside
        ROI """

        extraction_mask = sp.zeros((self.Main.Data.raw.shape[0],self.Main.Data.raw.shape[1],len(self.Main.ROIs.ROI_list)),dtype='bool')

        for i,ROI in enumerate(self.Main.ROIs.ROI_list):
            mask, inds = self.Main.ROIs.get_ROI_mask(ROI)
            extraction_mask[mask,i] = 1
            pass

        self.Main.Data.extraction_mask = extraction_mask

    def calc_traces(self,extraction_mask):
        """ calculates traces based on the extraction_mask
        definition: Traces is of shape (t,ID,stim),
        t,ID,stim,rep is Traces_sorted """
        if extraction_mask is None:
            extraction_mask = self.Main.Data.extraction_mask

        self.Main.Data.Traces = sp.zeros((self.Main.Data.nFrames,extraction_mask.shape[2],self.Main.Data.nTrials))

        for stim_id in range(self.Main.Data.nTrials): # iterate over trials
            for ROI_id in range(extraction_mask.shape[2]): # iterate over ROIs
                if self.Main.Options.export['data'] == 'raw':
                    sliced = self.Main.Data.raw[extraction_mask[:,:,ROI_id],:,stim_id]
                if self.Main.Options.export['data'] == 'dFF':
                    sliced = self.Main.Data.dFF[extraction_mask[:,:,ROI_id],:,stim_id]

                self.Main.Data.Traces[:,ROI_id,stim_id] = sp.average(sliced,axis=0)


    def sort_traces(self):
        """ creates a (t,ID,stim,rep) np.array of the Traces """

        labels = sp.array(self.Main.Data.Metadata.trial_labels)

        # inferrence
        stim_unique = sp.unique(labels)
        nStims = stim_unique.shape[0]
        nReps = len(labels) / nStims

        nFrames = self.Main.Data.nFrames
        nROIs = len(self.Main.ROIs.ROI_list)

        # dims are t, cell, odor, rep
        self.Main.Data.Traces_sorted = sp.zeros((nFrames,nROIs,nStims,nReps))

        for n in range(self.Main.Data.nTrials):
            # get the correct indices
            stim_index = sp.where(stim_unique == labels[n])[0][0] # this finds the index in stim_unique of the corresponding stim of the trial
            rep_index = sp.where(sp.where(labels == labels[n])[0] == n)[0][0] # das wievielte mal kommt n in stim_order[n] vor? -> rep index

            # get the traces and put it in the data structure at the correct place
            try:
                self.Main.Data.Traces_sorted[:,:,stim_index,rep_index] = self.Main.Data.Traces[:,:,n]
            except IndexError:
                sys.exit()
                pass
        pass

#==============================================================================
    ### color calculations
#==============================================================================
    def calc_colormaps(self,nColors,HSVsubset=(0,270),HSVoffset=0):
        colors = self.calc_colors(nColors,HSVsubset,HSVoffset)
        color_maps = [self.calc_colormap(color) for color in colors]
        return colors, color_maps

    def calc_colors(self,nColors,HSVsubset=(0,360),HSVoffset=0):
        h = sp.linspace(HSVsubset[0],HSVsubset[1],nColors,endpoint=False).astype('int')
        h = self.add_circular_offset(h,HSVoffset,HSVsubset[1]).tolist()
        s = [255] * nColors
        v = [255] * nColors
        colors = []
        for n in range(nColors):
            Color = QColor()
            Color.setHsv(h[n],s[n],v[n])
            colors.append(Color.getRgb())
        return colors

    def calc_colormap(self,rgba):
        """ input is a rgb(a) tuple returns PGColorMap """
        pos = sp.array([1,0])
        cols = sp.array([rgba,[0,0,0,0]],dtype=sp.ubyte)
        cmap = pg.ColorMap(pos,cols)
        return cmap

    def calc_preset_colormaps(self):
        pos = sp.array([1,0.66,0.33,0])
        cols = sp.array([[255,255,255,255],[255,220,0,255],[185,0,0,255],[0,0,0,0]],dtype=sp.ubyte)
        heatmap = pg.ColorMap(pos,cols)

        pos = sp.array([1,0])
        cols = sp.array([[255,255,255,255],[0,0,0,255]],dtype=sp.ubyte)
        graymap = pg.ColorMap(pos,cols)

        return heatmap, graymap

    def calc_levels(self,data,fraction=(0.1,0.9),nbins=500,samples=None):
        """ fraction is a tuple with (low, high) in the range of 0 to 1
        nbins is the number of bins for the histogram resolution

        if samples: draw this number of samples (random inds) for faster
        calculation
        """
        if samples:
            data = data.flatten()[np.random.randint(sp.prod(data.shape),size=samples)]
        else:
            data = data.flatten()
        y,x = sp.histogram(data,bins=nbins)
        cy = sp.cumsum(y).astype('float32')
        cy = cy / cy.max()
        minInd = sp.argmin(sp.absolute(cy - fraction[0]))
        maxInd = sp.argmin(sp.absolute(cy - fraction[1]))
        levels = (x[minInd],x[maxInd])
        return levels

    def add_circular_offset(self,array,offset,bound):
        """ helper function to rotate the color wheel"""
        rotated = sp.array([val % bound if val > bound else val for val in (array + offset)])
        return rotated
    pass

#==============================================================================
    ### parametric / nonparametric mask conversions
#==============================================================================

    def find_contour(self,mask,level=0.5):
        """ returns a list of segments """
        import matplotlib._cntr as cntr
        X,Y = sp.meshgrid(sp.arange(mask.shape[0]),sp.arange(mask.shape[1]))
        c = cntr.Cntr(X, Y, mask.T)
        nlist = c.trace(level, level, 0)
        segs = nlist[:len(nlist)//2]
        return segs

    def calc_segment_area(self,seg):
        """ calculates the area inside a segment (defined as [[x1,y1], ... ,[xn,yn]]) """
        centroid = sp.average(seg,axis=0)
        tri = []
        for i in range(1,seg.shape[0]):
            g = np.linalg.norm(seg[i-1,:] - centroid)
            h = np.linalg.norm(seg[i-1,:] - seg[i,:])
            tri.append(g*h/2.0)
        area = sp.sum(sp.array(tri))
        return area

#    def find_submasks(self,mask,level=0.5):
#        """ return a list of submasks"""
#
#        return submasks

if __name__ == '__main__':
    from . import Main
    Main.main()
    pass
