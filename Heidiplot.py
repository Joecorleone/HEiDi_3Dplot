#!/usr/bin/emv python

import math as math
import string as string
import random as random
import os as os
import csv as csv
import re as re
import xmlrpclib
import wx
import Heidilib as Hl
import numpy as np

HeidiMeasurementDicALL={}





#initialisierstructur
CurrentCrysStruc=Hl.crystalStructure(None,0,0,0,0,0,0,np.mat(np.identity(3)))

class MainFrame(wx.Frame):
	filename="Heidiplot"
	APP_SIZE_X=450
	APP_SIZE_Y=461
	loadedFiles=[]
	
	def __init__(self):
		wx.Frame.__init__(self, parent=None, title="Neue Datei", pos=(100,100), size=(self.APP_SIZE_X,self.APP_SIZE_Y))
		self.panel = wx.Panel(self)
		

		boxFeld = wx.BoxSizer(wx.VERTICAL)
		menuBar = wx.MenuBar()
		self.SetMenuBar(menuBar)
		menuFile = wx.Menu()
		menuBar.Append(menuFile,"&File")
		m_new = menuFile.Append(-1, "&New\tCtrl+N","New Plot")
		m_load = menuFile.Append(-1, "&Load\tCtrl+L","Load plotting config") #es waere sinnvoller wenn load, einfach eine komplette konfiguration mit allem drum und dran laden wuerde
		m_save = menuFile.Append(-1, "&Save\tCtrl+S","Save plotting config")
		menuFile.AppendSeparator()
		m_quit = menuFile.Append(-1, "&Quit\tCtrl+Q","Quit")
		
		menuHelp = wx.Menu()
		menuBar.Append(menuHelp, "&Help")
		m_manual = menuHelp.Append(-1, "Manual","Short Manual to Heidiplot")
		m_about = menuHelp.Append(-1, "About","Info about Heidiplot")
		
		
		
		self.Bind(wx.EVT_MENU, self.on_new, m_new)
		self.Bind(wx.EVT_MENU, self.on_loadAll, m_load)
		self.Bind(wx.EVT_MENU, self.on_saveAll, m_save)
		self.Bind(wx.EVT_MENU, self.on_quit, m_quit)
		self.Bind(wx.EVT_MENU, self.on_manual, m_manual)
		self.Bind(wx.EVT_MENU, self.on_about, m_about)
		
		wx.StaticText(self, -1, 'Step 1: define crystal structure:', (20, 20))
		bt_insertCrysManual=wx.Button(self, -1, "manual/edit", (246,15))
		bt_insertCrysFromFile=wx.Button(self, -1, "from file", (350,15))
		
		self.Bind(wx.EVT_BUTTON, self.on_StrucManual, bt_insertCrysManual)
		self.Bind(wx.EVT_BUTTON, self.on_StrucFromFile, bt_insertCrysFromFile)
		
		#load heidi measurements
		wx.StaticText(self, -1, 'Step 2: load Heidi Measurements:', (20, 70))
		bt_loadHeidiMeas=wx.Button(self, -1, "load", (255,65))
		bt_unloadHeidiMeas=wx.Button(self, -1, "unload", (350,65))
		self.Bind(wx.EVT_BUTTON, self.on_load, bt_loadHeidiMeas)
		

		self.Bind(wx.EVT_BUTTON, self.on_unload, bt_unloadHeidiMeas)
		
		#boundary conditions
		wx.StaticText(self, -1, 'Step 3: select boundaries:', (20, 120))
		wx.StaticText(self, -1, 'hmin:', (205, 120))
		self.hmin=wx.TextCtrl(self,-1, value="", pos=(245,120), size=(40,20),style=wx.TE_LEFT)
		wx.StaticText(self, -1, ',   hmax:', (287, 120))
		self.hmax=wx.TextCtrl(self,-1, value="", pos=(345,120), size=(40,20),style=wx.TE_LEFT)
		wx.StaticText(self, -1, 'kmin:', (205, 145))
		self.kmin=wx.TextCtrl(self,-1, value="", pos=(245,145), size=(40,20),style=wx.TE_LEFT)
		wx.StaticText(self, -1, ',   kmax:', (287, 145))
		self.kmax=wx.TextCtrl(self,-1, value="", pos=(345,145), size=(40,20),style=wx.TE_LEFT)
		wx.StaticText(self, -1, 'lmin:', (205, 170))
		self.lmin=wx.TextCtrl(self,-1, value="", pos=(245,170), size=(40,20),style=wx.TE_LEFT)
		wx.StaticText(self, -1, ',   lmax:', (287, 170))
		self.lmax=wx.TextCtrl(self,-1, value="", pos=(345,170), size=(40,20),style=wx.TE_LEFT)
		wx.StaticText(self, -1, 'Tmin:', (205, 195))
		self.Tmin=wx.TextCtrl(self,-1, value="", pos=(245,195), size=(40,20),style=wx.TE_LEFT)
		wx.StaticText(self, -1, ',   Tmax:', (287, 195))
		self.Tmax=wx.TextCtrl(self,-1, value="", pos=(345,195), size=(40,20),style=wx.TE_LEFT)
		
		
		wx.StaticBox(self, -1, 'additional options', (12, 250), size=(263, 130))
		self.showNucPeaks=wx.CheckBox(self, -1 ,'show nuclear peaks',(20, 270))
		self.showMagPeaks=wx.CheckBox(self, -1 ,'show magnetic peaks',(20, 295))
		self.showBZ=wx.CheckBox(self, -1 ,'show Brillouinzone boundary',(20, 320))
		wx.StaticText(self, -1, 'Scale points:', (20, 348))
		self.scalePoints = wx.Slider(self, -1, 100, 1, 500, (110,345), (100, -1),wx.SL_AUTOTICKS | wx.SL_HORIZONTAL)
		self.scalePointsValue=wx.TextCtrl(self, -1, '%i %%' %self.scalePoints.GetValue(), (215, 345),style=wx.TE_READONLY, size=(50,25))
		self.showNucPeaks.SetValue(True)
		self.showMagPeaks.SetValue(True)
		self.showBZ.SetValue(True)
		
		self.Bind(wx.EVT_SLIDER, self.sliderUpdate)
		#self.Bind(wx.EVT_CHECKBOX, self.ch_showNucPeaks, self.showNucPeaks)
		
		
		bt_generatePlot=wx.Button(self, -1, "generate plot", (335,350))
		self.Bind(wx.EVT_BUTTON, self.on_generatePlot, bt_generatePlot)
		
		wx.StaticLine(self, -1, (5, 390), (440,1))
		wx.StaticText(self, -1, 'Gnuplotscript for intensity against |Q|: ', (20, 405))
		bt_writeGnuplot=wx.Button(self, -1, "write", (290,400))
		self.Bind(wx.EVT_BUTTON, self.on_writeGnuplot, bt_writeGnuplot)
		
		self.CreateStatusBar()
		self.SetStatusText("")
		self.Centre()
		#self.ShowModal()
		#self.Destroy()
		self.Show(True)
	
	
	
 
	def sliderUpdate(self, event):
		self.pos1 = self.scalePoints.GetValue()
		self.scalePointsValue.SetValue('%i %%' %self.pos1)
		
		
	def on_new(self,evt):
		#hier muss noch einiges rein
		clearReply=wx.MessageBox('Clear current plot?', 'Question', wx.YES_NO | wx.ICON_QUESTION)
		if clearReply==wx.YES:
			CurrentCrysStruc.reset()
			MeasurementsKeyList=[]
			for key,measurement in HeidiMeasurementDicALL.iteritems():
				MeasurementsKeyList.append(key)
			for key in MeasurementsKeyList:
				del HeidiMeasurementDicALL[key]
			self.hmin.SetValue('')
			self.hmax.SetValue('')
			self.kmin.SetValue('')
			self.kmax.SetValue('')
			self.lmin.SetValue('')
			self.lmax.SetValue('')
			self.Tmin.SetValue('')
			self.Tmax.SetValue('')
			self.showNucPeaks.SetValue(True)
			self.showMagPeaks.SetValue(True)
			self.showBZ.SetValue(True)
			self.scalePoints.SetValue(100)
				#print self.scalePoints.GetValue()#wird nicht geupdated
			self.pos1 = self.scalePoints.GetValue()
			self.scalePointsValue.SetValue('%i %%' %self.pos1)
			self.SetStatusText('Plot reset')
			clearall()
		
		
	def on_loadAll(self,evt):#load from file: configfile, datafiles, boundaries and optional options
		
		#clearall, but ask before
		clearReply=wx.MessageBox('Clear current plot?', 'Question', wx.YES_NO | wx.ICON_QUESTION)
		if clearReply==wx.YES:
			dlg= wx.FileDialog(parent=self.panel, message="Choose a file", wildcard="PlotConfig|*.pcfg|All|*", style=wx.OPEN)
			value = dlg.ShowModal()
			filename = dlg.GetPath()
			if value == wx.ID_OK and not filename.endswith('/'):
				self.SetStatusText('processing...')
				datei=open(filename,"r")
				Zeilen=datei.readlines()
				DataLines=[]
				for Zeile in Zeilen:
					if not Zeile.startswith('#'):
						DataLines.append(Zeile)
				structype=DataLines[0].strip()
				#print structype
				a=DataLines[1].split()[0]
				b=DataLines[1].split()[1]
				c=DataLines[1].split()[2]
				alpha=float(DataLines[2].split()[0])/180*math.pi
				beta=float(DataLines[2].split()[1])/180*math.pi
				gamma=float(DataLines[2].split()[2])/180*math.pi
				Matrix=[]
				Matrix.append(DataLines[3].split())
				Matrix.append(DataLines[4].split())
				Matrix.append(DataLines[5].split())
				Matrix=np.mat(Matrix,dtype=float)
				datei.close()
				
				#self.SetStatusText('Crystal structure loaded from file')
				for datafile in DataLines[6].split():
					self.loadedFiles.append(datafile)
				hmin,hmax=DataLines[7].split()
				kmin,kmax=DataLines[8].split()
				lmin,lmax=DataLines[9].split()
				Tmin,Tmax=DataLines[10].split()
				Nuc,Mag,BZ,sP=DataLines[11].split()
				#loaded the plot
				#now change current work
				CurrentCrysStruc.setValues(structype,a,b,c,alpha,beta,gamma,Matrix)#.transpose())
				for datafile in self.loadedFiles:
					HeidiMeasurementDicALL.update(Hl.readHeidiGnuplotFile(datafile,CurrentCrysStruc))
				#convert None to ''
				if hmin=='None':
					self.hmin.SetValue('')
				else:
					self.hmin.SetValue(str(hmin))
				if hmax=='None':
					self.hmax.SetValue('')
				else:
					self.hmax.SetValue(str(hmax))
				if kmin=='None':
					self.kmin.SetValue('')
				else:
					self.kmin.SetValue(str(kmin))
				if kmax=='None':
					self.kmax.SetValue('')
				else:
					self.kmax.SetValue(str(kmax))
				if lmin=='None':
					self.lmin.SetValue('')
				else:
					self.lmin.SetValue(str(lmin))
				if lmax=='None':
					self.lmax.SetValue('')
				else:
					self.lmax.SetValue(str(lmax))
				if Tmin=='None':
					self.Tmin.SetValue('')
				else:
					self.Tmin.SetValue(str(Tmin))
				if Tmax=='None':
					self.Tmax.SetValue('')
				else:
					self.Tmax.SetValue(str(Tmax))
				#if Nuc=='True':
				self.showNucPeaks.SetValue(Nuc=='True')
				self.showMagPeaks.SetValue(Mag=='True')
				self.showBZ.SetValue(BZ=='True')
				self.scalePoints.SetValue(int(sP))
				#print self.scalePoints.GetValue()#wird nicht geupdated
				self.pos1 = self.scalePoints.GetValue()
				self.scalePointsValue.SetValue('%i %%' %self.pos1)
				self.SetStatusText('Plot loaded from %s' %filename)
	  
	def on_saveAll(self,evt):#save to file: configfile, datafiles, boundaries and optional options
		#maybe not: just do#before saving, working of Plot should be ensured, therefore check if plot 
		#config has to be saved, not the file
		#class unneeded
		#savePlot=Hl.completePlot(configFile, self.loadedFiles, boundaries, options)
		#print CurrentCrysStruc.omat
		#print np.array(CurrentCrysStruc.omat)[0][2]
		dlg= wx.FileDialog(parent=self.panel, message="Choose a file", wildcard="PlotConfig|*.pcfg|All|*", style=wx.SAVE)
		value = dlg.ShowModal()
		filename = dlg.GetPath()
		if value == wx.ID_OK and not filename.endswith('/'):
			CurrentCrysStruc
			datei=open(filename,"w")
			datei.write('#changes can be done within the textfile too, but proper functionality cannot be assured\n#structuretype:\n')
			datei.write('%s\n' %CurrentCrysStruc.structype)
			datei.write('#from left to right: a b c in reciprocal Angstroem\n')
			datei.write('%s\t%s\t%s\n' %(CurrentCrysStruc.a,CurrentCrysStruc.b,CurrentCrysStruc.c))
			datei.write('#from left to right: alpha beta gamma in degree\n')
			datei.write('%s\t%s\t%s\n' %(CurrentCrysStruc.alpha*180/math.pi,CurrentCrysStruc.beta*180/math.pi,CurrentCrysStruc.gamma*180/math.pi))
			datei.write('#Orientationmatrix: a* b* c*\n')
			arrayOmat=np.array(CurrentCrysStruc.omat.transpose())
			datei.write('%f\t%f\t%f\n' %(arrayOmat[0][0],arrayOmat[0][1],arrayOmat[0][2]))
			datei.write('%f\t%f\t%f\n' %(arrayOmat[1][0],arrayOmat[1][1],arrayOmat[1][2]))
			datei.write('%f\t%f\t%f\n' %(arrayOmat[2][0],arrayOmat[2][1],arrayOmat[2][2]))
			datei.write('#loaded measurement files:\n')
			fileline=''
			for datafile in self.loadedFiles:
				 fileline+=datafile + ' '
			datei.write('%s\n' %fileline)
			datei.write('#plotting boundaries (h,k,l,T):\n')
			boundaryDic=self.check_boundaries()
			datei.write('%s %s\n' %(boundaryDic['hmin'],boundaryDic['hmax']))
			datei.write('%s %s\n' %(boundaryDic['kmin'],boundaryDic['kmax']))
			datei.write('%s %s\n' %(boundaryDic['lmin'],boundaryDic['lmax']))
			datei.write('%s %s\n' %(boundaryDic['Tmin'],boundaryDic['Tmax']))
			datei.write('#plotting options:\n')
			datei.write('%s %s %s %i' %(self.showNucPeaks.GetValue(), self.showMagPeaks.GetValue(), self.showBZ.GetValue(),self.scalePoints.GetValue()))
			self.SetStatusText('Plot saved to %s' %filename)
			
	      
	#def on_manual(self,evt):
		#pass
	      
	#def on_info(self,evt):
		#pass
		
	def on_load(self,evt):
		if CurrentCrysStruc==Hl.crystalStructure(None,0,0,0,0,0,0,np.mat(np.identity(3))):
			wx.MessageBox('Crystal structure has not been defined yet!', 'Warning', wx.OK | wx.ICON_WARNING)
		else:
			dlg= wx.FileDialog(parent=self.panel, message="Choose a file", wildcard="Gnuplot|*.gpl|All|*", style=wx.OPEN)
			
			value = dlg.ShowModal()
			filename=dlg.GetPath()
			if value == wx.ID_OK and not filename.endswith('/'):
				self.SetStatusText('processing...')
				#filename=dlg.GetPath().split('/')[-1]
				HeidiMeasurementDicALL.update(Hl.readHeidiGnuplotFile(dlg.GetPath(),CurrentCrysStruc))#[0:-len(filename)],filename)
				self.loadedFiles.append(dlg.GetPath())
			#print HeidiMeasurementDicALL
			self.SetStatusText('%i measurements loaded' %len(HeidiMeasurementDicALL))
		
	def on_unload(self,evt):
		if CurrentCrysStruc==Hl.crystalStructure(None,0,0,0,0,0,0,np.mat(np.identity(3))):
			wx.MessageBox('Crystal structure has not been defined yet!', 'Warning', wx.OK | wx.ICON_WARNING)
		elif len(self.loadedFiles)==0:
			wx.MessageBox('No measurements have been loaded yet!', 'Warning', wx.OK | wx.ICON_WARNING)
		else:
			dlg= wx.FileDialog(parent=self.panel, message="Choose a file", wildcard="Gnuplot|*.gpl|All|*", style=wx.OPEN)
			value = dlg.ShowModal()
			if value == wx.ID_OK and self.loadedFiles.count(dlg.GetPath())>0:
				self.SetStatusText('processing...')
				#filename=dlg.GetPath().split('/')[-1]
				removeDic=Hl.readHeidiGnuplotFile(dlg.GetPath(),CurrentCrysStruc)
				Hl.unloadHeidiGnuplotFile(HeidiMeasurementDicALL,removeDic)#[0:-len(filename)],filename)
				self.loadedFiles.remove(dlg.GetPath())
				self.SetStatusText('%i measurements unloaded, %i remaining' %(len(removeDic),len(HeidiMeasurementDicALL)))
			elif self.loadedFiles.count(dlg.GetPath())==0:
				wx.MessageBox('This datafile has not been loaded, therefore cannot be unloaded!', 'Warning', wx.OK | wx.ICON_WARNING)
			#print HeidiMeasurementDicALL
			
	
	def on_quit(self,evt):
		self.Close(True)
	
	def on_StrucManual(self,evt):
		insStruc = InsertStrucDialog(None, title='Crystal Structure')
		insStruc.ShowModal()
		insStruc.Destroy()   
		return
		
	def check_boundaries(self):
		boundaryDic={}
		if self.hmin.GetValue()=='':
			boundaryDic['hmin']=None
		else:
			boundaryDic['hmin']=float(self.hmin.GetValue())
			
		if self.hmax.GetValue()=='':
			boundaryDic['hmax']=None
		else:
			boundaryDic['hmax']=float(self.hmax.GetValue())
			
		if self.kmin.GetValue()=='':
			boundaryDic['kmin']=None
		else:
			boundaryDic['kmin']=float(self.kmin.GetValue())
			
		if self.kmax.GetValue()=='':
			boundaryDic['kmax']=None
		else:
			boundaryDic['kmax']=float(self.kmax.GetValue())
			
		if self.lmin.GetValue()=='':
			boundaryDic['lmin']=None
		else:
			boundaryDic['lmin']=float(self.lmin.GetValue())
			
		if self.lmax.GetValue()=='':
			boundaryDic['lmax']=None
		else:
			boundaryDic['lmax']=float(self.lmax.GetValue())
		
		if self.Tmin.GetValue()=='':
			boundaryDic['Tmin']=None
		else:
			boundaryDic['Tmin']=float(self.Tmin.GetValue())
		
		if self.Tmax.GetValue()=='':
			boundaryDic['Tmax']=None
		else:
			boundaryDic['Tmax']=float(self.Tmax.GetValue())
		return boundaryDic
		
	def on_generatePlot(self,evt):
		if len(HeidiMeasurementDicALL)==0:
			wx.MessageBox('No measurements have been loaded yet!', 'Warning', wx.OK | wx.ICON_WARNING)
		else:
			if not self.checkBoundaries:
				wx.MessageBox('Please insert only decimal values for all boundaries!', 'Warning', wx.OK | wx.ICON_WARNING)
			else:
				boundaryDic=self.check_boundaries()
				
				self.SetStatusText('processing...')
				#die ganzen Variabeln muessen hier uebergeben werden, gefaellt mir nicht so richtig aber mir faellt nichts besseres ein
				#und ausserdem ist mir nicht klar was alles benoetigt wird -> morgen frueh
				Success=Hl.plotteMessung3D(HeidiMeasurementDicALL,CurrentCrysStruc,boundaryDic['hmin'],boundaryDic['hmax'],boundaryDic['kmin'],boundaryDic['kmax'],boundaryDic['lmin'],boundaryDic['lmax'],boundaryDic['Tmin'],boundaryDic['Tmax'],self.showNucPeaks.GetValue(),self.showMagPeaks.GetValue(),self.showBZ.GetValue(),self.scalePoints.GetValue())
				self.SetStatusText('')
				if Success==False:
					wx.MessageBox('Due to the selected boundaries or options, there is no data to plot!', 'Warning', wx.OK | wx.ICON_WARNING)
	#def ch_showNucPeaks(self,evt):
	#  print self.showNucPeaks.GetValue()
	
	def on_StrucFromFile(self,evt):
		dlg= wx.FileDialog(parent=self.panel, message="Choose a file", wildcard="StructureConfig|*.scfg|All|*", style=wx.OPEN)
		value = dlg.ShowModal()
		filename = dlg.GetPath()
		if value == wx.ID_OK and not filename.endswith('/'):
			datei=open(filename,"r")
			Zeilen=datei.readlines()
			DataLines=[]
			for Zeile in Zeilen:
				if not Zeile.startswith('#'):
					DataLines.append(Zeile)
			structype=DataLines[0].strip()
			#print structype
			a=DataLines[1].split()[0]
			b=DataLines[1].split()[1]
			c=DataLines[1].split()[2]
			alpha=float(DataLines[2].split()[0])/180*math.pi
			beta=float(DataLines[2].split()[1])/180*math.pi
			gamma=float(DataLines[2].split()[2])/180*math.pi
			Matrix=[]
			Matrix.append(DataLines[3].split())
			Matrix.append(DataLines[4].split())
			Matrix.append(DataLines[5].split())
			Matrix=np.mat(Matrix,dtype=float)
			datei.close()
			CurrentCrysStruc.setValues(structype,a,b,c,alpha,beta,gamma,Matrix)
			#print CurrentCrysStruc.omat
			self.SetStatusText('Crystal structure loaded from file')
			
	def on_writeGnuplot(self,evt):
		if len(HeidiMeasurementDicALL)==0:
			wx.MessageBox('No measurements have been loaded yet!', 'Warning', wx.OK | wx.ICON_WARNING)
		else:
			dlg= wx.FileDialog(parent=self.panel, message="Choose a file", wildcard="Gnuplot|*.gpl|All|*", style=wx.SAVE)
			value = dlg.ShowModal()
			if value == wx.ID_OK and not filename.endswith('/'):
				self.SetStatusText('processing...')
				Hl.schreibeGnuplotSkript(HeidiMeasurementDicALL,dlg.GetPath())
				self.SetStatusText('')
	
	def checkBoundaries(self):
		try:
			if self.hmin.GetValue()!='':
				test=float(self.hmin.GetValue())
			if self.hmax.GetValue()!='':
				test=float(self.hmax.GetValue())
			if self.kmin.GetValue()!='':
				test=float(self.kmin.GetValue())
			if self.kmax.GetValue()!='':
				test=float(self.kmax.GetValue())
			if self.lmin.GetValue()!='':
				test=float(self.lmin.GetValue())
			if self.lmax.GetValue()!='':
				test=float(self.lmax.GetValue())
			if self.Tmin.GetValue()!='':
				test=float(self.Tmin.GetValue())
			if self.Tmax.GetValue()!='':
				test=float(self.Tmax.GetValue())
		except ValueError:
			return False
		else:
			return True
	
	
	
	def on_about(self, evt):
		readme=open('readme.txt','r')
		readmeLines=readme.readlines()
		
		about=False
		description=''
		for i,line in enumerate(readmeLines):
			#print i,line
			if line.startswith('about'):
				about=True
				
			elif about:
				if line.startswith('manual')>0:
					about=False
				elif len(line)<4:
					pass
				else:
					 description+=line + '\n'
				    
			
		

		#licence = """File Hunter is free software; you can redistribute 
	#it and/or modify it under the terms of the GNU General Public License as 
	#published by the Free Software Foundation; either version 2 of the License, 
	#or (at your option) any later version.

	#File Hunter is distributed in the hope that it will be useful, 
	#but WITHOUT ANY WARRANTY; without even the implied warranty of 
	#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
	#See the GNU General Public License for more details. You should have 
	#received a copy of the GNU General Public License along with File Hunter; 
	#if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
	#Suite 330, Boston, MA  02111-1307  USA"""
    

		info = wx.AboutDialogInfo()

		info.SetIcon(wx.Icon('Heidiplot_logo.png', wx.BITMAP_TYPE_PNG))
		info.SetName('HEiDiplot')
		info.SetVersion(readmeLines[0].split('v')[-1])
		info.SetDescription(description)
		info.SetCopyright('(C) 2012 Johannes Reim')
		info.SetWebSite('http://www.notyet.de')
		#info.SetLicence(licence)
		#info.AddDeveloper('Johannes Reim')
		#info.AddDocWriter('Johannes Reim')
		#info.AddArtist('Johannes Reim')
		#info.AddTranslator('Johannes Reim')
		readme.close()
		wx.AboutBox(info)
	 
	 
	def on_manual(self, evt):
		insStruc = ManualDialog(None, title='Manual')
		insStruc.ShowModal()
		insStruc.Destroy()

class ManualDialog(wx.Dialog):
	def __init__(self, parent, title):
		super(ManualDialog, self).__init__(parent=parent, title=title, size=(550, 400))
		
		self.panel = wx.Panel(parent=self)
		
		
		readme=open('readme.txt','r')
		readmeLines=readme.readlines()
		
		manual=False
		description='Short introduction to the usage of HEiDiplot:\n\n'
		for i,line in enumerate(readmeLines):
			#print i,line
			if line.startswith('manual'):
				manual=True
				
			elif manual:
				if line.startswith('Example data')>0:
					manual=False
				elif len(line)<4:
					pass
				else:
					 description+=line + '\n'
					 
		readme.close()
		
		self.txt=wx.TextCtrl(self.panel, value=description, style=wx.TE_MULTILINE|wx.TE_LEFT|wx.TE_READONLY)
		
		boxFeld = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(boxFeld)
		boxFeld.Add(self.txt, proportion=20, flag=wx.EXPAND)
		
		#vbox = wx.BoxSizer(wx.VERTICAL)
		#hbox = wx.BoxSizer(wx.HORIZONTAL)
		#hboxPanel = wx.Panel(self)
		#self.txt_manual=wx.TextCtrl(hboxPanel, -1, description, style=wx.TE_READONLY )
		#hbox.Add(self.txt_manual,flag=wx.ALL|wx.EXPAND, border=5)
		
		#vbox.Add(self.panel, flag=wx.ALL|wx.EXPAND, border=5)
		#vbox.Add(hbox, flag=wx.ALL|wx.EXPAND, border=5)
		#self.panel.SetSizer(hboxPanel)
		#self.SetSizer(vbox)
		
class InsertStrucDialog(wx.Dialog):
    
	def __init__(self, parent, title):
		super(InsertStrucDialog, self).__init__(parent=parent, title=title, size=(250, 520))

		self.panel = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)

		sb = wx.StaticBox(self.panel, label='types')
		sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
		
		self.rbt_sc=wx.RadioButton(self.panel, label='cubic', style=wx.RB_GROUP)
		self.rbt_bcc=wx.RadioButton(self.panel, label='bodycentered cubic')
		self.rbt_fcc=wx.RadioButton(self.panel, label='facecentered cubic')
		self.rbt_hex=wx.RadioButton(self.panel, label='hexagonal')
		sbs.Add(self.rbt_sc)
		sbs.Add(self.rbt_bcc)
		sbs.Add(self.rbt_fcc)
		sbs.Add(self.rbt_hex)
		
		#hbox1 = wx.BoxSizer(wx.HORIZONTAL)        
		#hbox1.Add(wx.RadioButton(panel, label='Custom'))
		#hbox1.Add(wx.TextCtrl(panel), flag=wx.LEFT, border=5)
		#sbs.Add(hbox1)
		
		self.panel.SetSizer(sbs)
		
		
		#values
		hboxvaluesPanel = wx.Panel(self)
		hboxvaluesStatic = wx.StaticBox(hboxvaluesPanel, label='values')
		hboxvaluesSizer = wx.StaticBoxSizer(hboxvaluesStatic, orient=wx.HORIZONTAL)
				
		vboxvariable=wx.BoxSizer(wx.VERTICAL)
		vboxvalues=wx.BoxSizer(wx.VERTICAL)
		
		vboxvariable.AddStretchSpacer(prop=0.5)
		vboxvariable.Add(wx.StaticText(hboxvaluesPanel, -1, 'a:'))
		vboxvariable.AddStretchSpacer(prop=1)
		vboxvariable.Add(wx.StaticText(hboxvaluesPanel, -1, 'b:'))
		vboxvariable.AddStretchSpacer(prop=1)
		vboxvariable.Add(wx.StaticText(hboxvaluesPanel, -1, 'c:'))
		vboxvariable.AddStretchSpacer(prop=1)
		vboxvariable.Add(wx.StaticText(hboxvaluesPanel, -1, 'alpha:'))
		vboxvariable.AddStretchSpacer(prop=1)
		vboxvariable.Add(wx.StaticText(hboxvaluesPanel, -1, 'beta:'))
		vboxvariable.AddStretchSpacer(prop=1)
		vboxvariable.Add(wx.StaticText(hboxvaluesPanel, -1, 'gamma:'))
		vboxvariable.AddStretchSpacer(prop=1)
				
		self.txt_a=wx.TextCtrl(hboxvaluesPanel, value="",style=wx.TE_LEFT)
		self.txt_b=wx.TextCtrl(hboxvaluesPanel, value="",style=wx.TE_LEFT)
		self.txt_c=wx.TextCtrl(hboxvaluesPanel, value="",style=wx.TE_LEFT)
		self.txt_alpha=wx.TextCtrl(hboxvaluesPanel, value="",style=wx.TE_LEFT)
		self.txt_beta=wx.TextCtrl(hboxvaluesPanel, value="",style=wx.TE_LEFT)
		self.txt_gamma=wx.TextCtrl(hboxvaluesPanel, value="",style=wx.TE_LEFT)
		vboxvalues.Add(self.txt_a)
		vboxvalues.Add(self.txt_b)
		vboxvalues.Add(self.txt_c)
		vboxvalues.Add(self.txt_alpha)
		vboxvalues.Add(self.txt_beta)
		vboxvalues.Add(self.txt_gamma)
		
		hboxvaluesSizer.Add(vboxvariable, flag=wx.ALL|wx.EXPAND, border=5)
		hboxvaluesSizer.Add(vboxvalues, flag=wx.ALL|wx.EXPAND, border=5)
		hboxvaluesPanel.SetSizer(hboxvaluesSizer)
		
		#Orientation Matrix
		hboxOmatPanel = wx.Panel(self)
		hboxOmatStatic = wx.StaticBox(hboxOmatPanel, label='Orientation Matrix: a* b* c*')
		hboxOmatSizer = wx.StaticBoxSizer(hboxOmatStatic, orient=wx.HORIZONTAL)
		
		vboxColumn1=wx.BoxSizer(wx.VERTICAL)
		vboxColumn2=wx.BoxSizer(wx.VERTICAL)
		vboxColumn3=wx.BoxSizer(wx.VERTICAL)
		
		OmatItemList=[]		
		#column1
		self.txt_omat11=wx.TextCtrl(hboxOmatPanel, value="",style=wx.TE_LEFT)
		self.txt_omat21=wx.TextCtrl(hboxOmatPanel, value="",style=wx.TE_LEFT)
		self.txt_omat31=wx.TextCtrl(hboxOmatPanel, value="",style=wx.TE_LEFT)
		OmatItemList.append(self.txt_omat11)
		OmatItemList.append(self.txt_omat21)
		OmatItemList.append(self.txt_omat31)
		vboxColumn1.Add(self.txt_omat11,1,wx.EXPAND)
		vboxColumn1.Add(self.txt_omat21,1,wx.EXPAND)
		vboxColumn1.Add(self.txt_omat31,1,wx.EXPAND)
		#column2
		self.txt_omat12=wx.TextCtrl(hboxOmatPanel, value="",style=wx.TE_LEFT)
		self.txt_omat22=wx.TextCtrl(hboxOmatPanel, value="",style=wx.TE_LEFT)
		self.txt_omat32=wx.TextCtrl(hboxOmatPanel, value="",style=wx.TE_LEFT)
		OmatItemList.append(self.txt_omat12)
		OmatItemList.append(self.txt_omat22)
		OmatItemList.append(self.txt_omat32)
		vboxColumn2.Add(self.txt_omat12,1,wx.EXPAND)
		vboxColumn2.Add(self.txt_omat22,1,wx.EXPAND)
		vboxColumn2.Add(self.txt_omat32,1,wx.EXPAND)
		#column3
		self.txt_omat13=wx.TextCtrl(hboxOmatPanel, value="",style=wx.TE_LEFT)
		self.txt_omat23=wx.TextCtrl(hboxOmatPanel, value="",style=wx.TE_LEFT)
		self.txt_omat33=wx.TextCtrl(hboxOmatPanel, value="",style=wx.TE_LEFT)
		OmatItemList.append(self.txt_omat13)
		OmatItemList.append(self.txt_omat23)
		OmatItemList.append(self.txt_omat33)
		vboxColumn3.Add(self.txt_omat13,1,wx.EXPAND)
		vboxColumn3.Add(self.txt_omat23,1,wx.EXPAND)
		vboxColumn3.Add(self.txt_omat33,1,wx.EXPAND)
		#zusammensetzen der Spalten
		hboxOmatSizer.Add(vboxColumn1,1, flag=wx.ALL|wx.EXPAND, border=1)
		hboxOmatSizer.Add(vboxColumn2,1, flag=wx.ALL|wx.EXPAND, border=1)
		hboxOmatSizer.Add(vboxColumn3,1, flag=wx.ALL|wx.EXPAND, border=1)
		hboxOmatPanel.SetSizer(hboxOmatSizer)
		
		#hboxSave = wx.BoxSizer(wx.HORIZONTAL)
		saveButton = wx.Button(self, label='        Save config to file        ')
		saveButton.Bind(wx.EVT_BUTTON, self.on_saveConfig)
		
		
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		okButton = wx.Button(self, label='Ok')
		closeButton = wx.Button(self, label='Close')
		hbox2.Add(okButton)
		hbox2.Add(closeButton, flag=wx.LEFT, border=5)

		vbox.Add(self.panel, flag=wx.ALL|wx.EXPAND, border=5)
		vbox.Add(hboxvaluesPanel, flag=wx.ALL|wx.EXPAND, border=5)
		vbox.Add(hboxOmatPanel, flag=wx.ALL|wx.EXPAND, border=5)		
		vbox.Add(saveButton, flag= wx.ALIGN_CENTER, border=10)
		vbox.Add(hbox2, flag= wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)
		
		self.SetSizer(vbox)
		
		okButton.Bind(wx.EVT_BUTTON, self.on_Okay)
		closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
		#self.rbt_sc.SetValue(False)
		#self.rbt_bcc.SetValue(False)
		#self.rbt_fcc.SetValue(False)
		#self.rbt_hex.SetValue(False)
		if CurrentCrysStruc.structype=='sc':
			self.rbt_sc.SetValue(True)
			#self.rbt_bcc.SetValue(False)
			#self.rbt_fcc.SetValue(False)
			#self.rbt_hex.SetValue(False)
		elif CurrentCrysStruc.structype=='bcc':
			self.rbt_bcc.SetValue(True)
		elif CurrentCrysStruc.structype=='fcc':
			self.rbt_fcc.SetValue(True)
		elif CurrentCrysStruc.structype=='hexagonal':
			self.rbt_hex.SetValue(True)
			
		self.txt_a.SetValue(str(CurrentCrysStruc.a))
		self.txt_b.SetValue(str(CurrentCrysStruc.b))
		self.txt_c.SetValue(str(CurrentCrysStruc.c))
		self.txt_alpha.SetValue(str(round(CurrentCrysStruc.alpha*180.0/math.pi,4)))
		self.txt_beta.SetValue(str(round(CurrentCrysStruc.beta*180.0/math.pi,4)))
		self.txt_gamma.SetValue(str(round(CurrentCrysStruc.gamma*180.0/math.pi,4)))
		
		#lese omat aus
		#print CurrentCrysStruc.omat.item((0,2))
		j=0
		i=0
		for Eintrag in OmatItemList:
			if i==3:
				j+=1
				i=0
			#print 'i: %i, j: %i' %(i,j)
			Eintrag.SetValue(str(CurrentCrysStruc.omat.item((i,j))))
			i+=1
			
		#print CurrentCrysStruc.omat
		
		
		
	def OnClose(self, evt):
	    
		self.Destroy()

	def on_saveConfig(self,evt):
		if not self.checkEntries():
			wx.MessageBox('Please insert only decimal values for all entries and only non-zero values for all length and angles!', 'Warning', wx.OK | wx.ICON_WARNING)
			
		elif not self.checkConsistency():
			wx.MessageBox('The orientationmatrix is not consistent with the lengths you inserted!', 'Warning', wx.OK | wx.ICON_WARNING)
			
		else:
			dlg= wx.FileDialog(parent=self.panel, message="Choose a file", wildcard="StructureConfig|*.scfg|All|*", style=wx.SAVE)
			value = dlg.ShowModal()
			filename = dlg.GetPath()
			if value == wx.ID_OK and not filename.endswith('/'):
				datei=open(filename,"w")
				datei.write('#changes can be done within the textfile too, but proper functionality cannot be assured\n#structuretype:\n')
				if self.rbt_sc.GetValue() == True:
					datei.write('sc\n')
				elif self.rbt_bcc.GetValue() == True:
					datei.write('bcc\n')
				elif self.rbt_fcc.GetValue() == True:
					datei.write('fcc\n')
				elif self.rbt_hex.GetValue() == True:
					datei.write('hexagonal\n')
				datei.write('#from left to right: a b c in reciprocal Angstroem\n')
				datei.write('%s\t%s\t%s\n' %(self.txt_a.GetValue(),self.txt_b.GetValue(),self.txt_c.GetValue()))
				datei.write('#from left to right: alpha beta gamma in degree\n')
				datei.write('%s\t%s\t%s\n' %(self.txt_alpha.GetValue(),self.txt_beta.GetValue(),self.txt_gamma.GetValue()))
				self.omat=[[float(self.txt_omat11.GetValue()),float(self.txt_omat12.GetValue()),float(self.txt_omat13.GetValue())],[float(self.txt_omat21.GetValue()),float(self.txt_omat22.GetValue()),float(self.txt_omat23.GetValue())],[float(self.txt_omat31.GetValue()),float(self.txt_omat32.GetValue()),float(self.txt_omat33.GetValue())]]
				datei.write('#Orientationmatrix: a* b* c*\n')
				
				datei.write('%f\t%f\t%f\n' %(self.omat[0][0],self.omat[0][1],self.omat[0][2]))
				datei.write('%f\t%f\t%f\n' %(self.omat[1][0],self.omat[1][1],self.omat[1][2]))
				datei.write('%f\t%f\t%f\n' %(self.omat[2][0],self.omat[2][1],self.omat[2][2]))
				self.omat=np.mat(self.omat)
				#datei.write(str(self.omat))
				#print self.omat
				#np.savetxt(filename,self.omat, fmt="%12.6G")
				datei.close()
				
			
			
	def on_Okay(self,evt):
		if not self.checkEntries():
			wx.MessageBox('Please insert only decimal values for all entries and only non-zero values for all length and angles!', 'Warning', wx.OK | wx.ICON_WARNING)
			
		elif not self.checkConsistency():
			wx.MessageBox('The orientationmatrix is not consistent with the lengths you inserted!', 'Warning', wx.OK | wx.ICON_WARNING)
		else:
			self.omat=np.mat([[float(self.txt_omat11.GetValue()),float(self.txt_omat12.GetValue()),float(self.txt_omat13.GetValue())],[float(self.txt_omat21.GetValue()),float(self.txt_omat22.GetValue()),float(self.txt_omat23.GetValue())],[float(self.txt_omat31.GetValue()),float(self.txt_omat32.GetValue()),float(self.txt_omat33.GetValue())]])
			if self.rbt_sc.GetValue() == True:
				CurrentCrysStruc.setValues('sc',self.txt_a.GetValue(),self.txt_b.GetValue(),self.txt_c.GetValue(),float(self.txt_alpha.GetValue())/180*math.pi,float(self.txt_beta.GetValue())/180*math.pi,float(self.txt_gamma.GetValue())/180*math.pi,self.omat)
			elif self.rbt_bcc.GetValue() == True:
				CurrentCrysStruc.setValues('bcc',self.txt_a.GetValue(),self.txt_b.GetValue(),self.txt_c.GetValue(),float(self.txt_alpha.GetValue())/180*math.pi,float(self.txt_beta.GetValue())/180*math.pi,float(self.txt_gamma.GetValue())/180*math.pi,self.omat)
			elif self.rbt_fcc.GetValue() == True:
				CurrentCrysStruc.setValues('fcc',self.txt_a.GetValue(),self.txt_b.GetValue(),self.txt_c.GetValue(),float(self.txt_alpha.GetValue())/180*math.pi,float(self.txt_beta.GetValue())/180*math.pi,float(self.txt_gamma.GetValue())/180*math.pi,self.omat)
			elif self.rbt_hex.GetValue() == True:
				CurrentCrysStruc.setValues('hexagonal',self.txt_a.GetValue(),self.txt_b.GetValue(),self.txt_c.GetValue(),float(self.txt_alpha.GetValue())/180*math.pi,float(self.txt_beta.GetValue())/180*math.pi,float(self.txt_gamma.GetValue())/180*math.pi,self.omat)
			self.Destroy()
	
	def checkEntries(self): #check values for to float convertable non-zero entries for length and angles
		try:
			test=float(self.txt_a.GetValue())+float(self.txt_b.GetValue())+float(self.txt_c.GetValue())+float(self.txt_alpha.GetValue())+float(self.txt_beta.GetValue())+float(self.txt_gamma.GetValue())+float(self.txt_omat11.GetValue())+float(self.txt_omat12.GetValue())+float(self.txt_omat13.GetValue())+float(self.txt_omat21.GetValue())+float(self.txt_omat22.GetValue())+float(self.txt_omat23.GetValue())+float(self.txt_omat31.GetValue())+float(self.txt_omat32.GetValue())+float(self.txt_omat33.GetValue())
		except ValueError:
			#print 'not convertable to float'
			return False
		else:
			if float(self.txt_a.GetValue())==0 or float(self.txt_b.GetValue())==0 or float(self.txt_c.GetValue())==0 or float(self.txt_alpha.GetValue())==0 or float(self.txt_beta.GetValue())==0 or float(self.txt_gamma.GetValue())==0:
				return False
			else:
				return True
				
	def checkConsistency(self):
		self.omat=np.mat([[float(self.txt_omat11.GetValue()),float(self.txt_omat12.GetValue()),float(self.txt_omat13.GetValue())],[float(self.txt_omat21.GetValue()),float(self.txt_omat22.GetValue()),float(self.txt_omat23.GetValue())],[float(self.txt_omat31.GetValue()),float(self.txt_omat32.GetValue()),float(self.txt_omat33.GetValue())]])
		if self.rbt_sc.GetValue() == True:
			tempCrysStruc=Hl.crystalStructure('sc',self.txt_a.GetValue(),self.txt_b.GetValue(),self.txt_c.GetValue(),float(self.txt_alpha.GetValue())/180*math.pi,float(self.txt_beta.GetValue())/180*math.pi,float(self.txt_gamma.GetValue())/180*math.pi,self.omat)
		elif self.rbt_bcc.GetValue() == True:
			tempCrysStruc=Hl.crystalStructure('bcc',self.txt_a.GetValue(),self.txt_b.GetValue(),self.txt_c.GetValue(),float(self.txt_alpha.GetValue())/180*math.pi,float(self.txt_beta.GetValue())/180*math.pi,float(self.txt_gamma.GetValue())/180*math.pi,self.omat)
		elif self.rbt_fcc.GetValue() == True:
			tempCrysStruc=Hl.crystalStructure('fcc',self.txt_a.GetValue(),self.txt_b.GetValue(),self.txt_c.GetValue(),float(self.txt_alpha.GetValue())/180*math.pi,float(self.txt_beta.GetValue())/180*math.pi,float(self.txt_gamma.GetValue())/180*math.pi,self.omat)
		elif self.rbt_hex.GetValue() == True:
			tempCrysStruc=Hl.crystalStructure('hexagonal',self.txt_a.GetValue(),self.txt_b.GetValue(),self.txt_c.GetValue(),float(self.txt_alpha.GetValue())/180*math.pi,float(self.txt_beta.GetValue())/180*math.pi,float(self.txt_gamma.GetValue())/180*math.pi,self.omat)
		#tempCrysStruc
		#print 'aStar: %f, bStar: %f, cStar: %f' %(tempCrysStruc.aStar,tempCrysStruc.bStar,tempCrysStruc.cStar)
		#print tempCrysStruc.omat
		test=np.sqrt(np.sum(np.power(tempCrysStruc.omat.transpose(),2),axis=1))
		#print np.power(tempCrysStruc.omat,2)
		#print test
		sigNu=2
		#print 'from Omat: aStar: %f, bStar: %f, cStar: %f' %(test[0],test[1],test[2])
		#print 'rounded:  aStar: %f, bStar: %f, cStar: %f' %(round(tempCrysStruc.aStar,sigNu),round(tempCrysStruc.bStar,sigNu),round(tempCrysStruc.cStar,sigNu))
		#print 'rounded from Omat: aStar: %f, bStar: %f, cStar: %f' %(round(test[0],sigNu),round(test[1],sigNu),round(test[2],sigNu))
		if round(tempCrysStruc.aStar,sigNu)==round(test[0],sigNu) and round(tempCrysStruc.bStar,sigNu)==round(test[1],sigNu) and round(tempCrysStruc.cStar,sigNu)==round(test[2],sigNu):
			return True
		else:
			return False
	
def clearall():
	return

#def loadHeidiMeasurement(filepath):
  ##print path
  ##print filename
  
  #HeidiMeasurementDic=Hl.readHeidiGnuplotFile(filepath)
  #return HeidiMeasurementDic
  
  
app=wx.PySimpleApp()
frame = MainFrame()
frame.SetTitle(frame.filename)
app.MainLoop()
