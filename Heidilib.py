# -*- coding: utf-8 -*-
import math
import numpy as np
import fractions as fr
from matplotlib import pyplot as plt
import time
from mpl_toolkits.mplot3d import Axes3D
#from decimal import Decimal
HeidiTemperatures={}
Background=[]

#class completePlot(object):#
	#def __init__(self,CurrentCrysStruc, measurementFiles, boundaries, options): #boundaries,options should be dictionaries
		##self.CurrentCrysStruc=CurrentCrysStruc
		#self.measurementFiles=measurementFiles
		#self.boundaries=boundaries
		#self.option=options

class crystalStructure(object):
	"""Class for crystal structures configurations.	
	"""
	def __init__(self,structype=None,a=0.0,b=0.0,c=0.0,alpha=0.0,beta=0.0,gamma=0.0,omat=np.mat(np.identity(3))):
		"""initialize a crystal structure configuration 
		
		Keyword arguments:
		structype -- structure type (default 0.0)
		a -- real cell length (default 0.0)
		b -- real cell length (default 0.0)
		c -- real cell length (default 0.0)
		alpha -- real cell angle (default 0.0)
		beta -- real cell angle (default 0.0)
		gamma -- real cell angle (default 0.0)
		omat -- orientation matrix for the defined cell in the form a* b* c*
		"""
		self.structype=structype
		self.a=float(a)
		self.b=float(b)
		self.c=float(c)
		self.alpha=float(alpha)  #internal in rad
		self.beta=float(beta)
		self.gamma=float(gamma)
		self.omat=omat#.transpose()  #internal is the correct orienting matrix, not a* b* c*
		self.omatinv=np.array(np.linalg.inv(self.omat))
		if self.a!=0 and self.b!=0 and self.c!=0 and self.alpha!=0 and self.beta!=0 and self.gamma!=0:
			self.alphaStar=math.acos((math.cos(self.beta)*math.cos(self.gamma)-math.cos(self.alpha))/(math.sin(self.beta)*math.sin(self.gamma)))
			self.betaStar=math.acos((math.cos(self.gamma)*math.cos(self.alpha)-math.cos(self.beta))/(math.sin(self.gamma)*math.sin(self.alpha)))
			self.gammaStar=math.acos((math.cos(self.alpha)*math.cos(self.beta)-math.cos(self.gamma))/(math.sin(self.alpha)*math.sin(self.beta)))
			if self.structype=='sc':
				self.aStar=1/self.a
				self.bStar=1/self.b
				self.cStar=1/self.c
			elif self.structype=='bcc':
				self.aStar=2/self.a
				self.bStar=2/self.b
				self.cStar=2/self.c
			elif self.structype=='fcc':
				self.aStar=2/self.a
				self.bStar=2/self.b
				self.cStar=2/self.c
			elif self.structype=='hexagonal':
				self.aStar=2/(math.sqrt(3)*self.a)#0.103738
				self.bStar=2/(math.sqrt(3)*self.b)#0.104386
				self.cStar=1/self.c#0.097037
			
	
	def __eq__(self,other):
		"""returns if two crystal structure configurations are equal
		
		Keyword arguments:
		other - another crystal structure configuration		
		"""
		return self.structype==other.structype and self.a==other.a and self.b==other.b and self.c==other.c and self.alpha==other.alpha and self.beta==other.beta and self.gamma==other.gamma and self.omat.all()==other.omat.all()
	
	def setValues(self,structype=None,a=0.0,b=0.0,c=0.0,alpha=0.0,beta=0.0,gamma=0.0,omat=np.mat(np.identity(3))):
		"""set Values for a crystal structure configuration 
		
		Keyword arguments:
		structype -- structure type (default 0.0)
		a -- real cell length (default 0.0)
		b -- real cell length (default 0.0)
		c -- real cell length (default 0.0)
		alpha -- real cell angle (default 0.0)
		beta -- real cell angle (default 0.0)
		gamma -- real cell angle (default 0.0)
		omat -- orientation matrix for the defined cell in the form a* b* c*
		"""
		self.structype=structype
		self.a=float(a)
		self.b=float(b)
		self.c=float(c)
		self.alpha=float(alpha)#/180.0*math.pi
		self.beta=float(beta)#/180.0*math.pi
		self.gamma=float(gamma)#/180.0*math.pi
		self.omat=omat#.transpose()
		#calculate matrixinvers
		self.omatinv=np.array(np.linalg.inv(self.omat))
		#calculate values for reciprocal cell
		self.alphaStar=math.acos((math.cos(self.beta)*math.cos(self.gamma)-math.cos(self.alpha))/(math.sin(self.beta)*math.sin(self.gamma)))
		self.betaStar=math.acos((math.cos(self.gamma)*math.cos(self.alpha)-math.cos(self.beta))/(math.sin(self.gamma)*math.sin(self.alpha)))
		self.gammaStar=math.acos((math.cos(self.alpha)*math.cos(self.beta)-math.cos(self.gamma))/(math.sin(self.alpha)*math.sin(self.beta)))
		#berechne reziproke Zellparameter in kristallographischer Notation
		#depending on the structype
		if self.structype=='sc':
			self.aStar=1/self.a
			self.bStar=1/self.b
			self.cStar=1/self.c
		elif self.structype=='bcc':
			self.aStar=2/self.a
			self.bStar=2/self.b
			self.cStar=2/self.c
		elif self.structype=='fcc':
			self.aStar=2/self.a
			self.bStar=2/self.b
			self.cStar=2/self.c
		elif self.structype=='hexagonal':
			self.aStar=2/(math.sqrt(3)*self.a)#0.103738
			self.bStar=2/(math.sqrt(3)*self.b)#0.104386
			self.cStar=1/self.c#0.097037
			
			
	def reset(self):
		self.structype=None
		self.a=0.0
		self.b=0.0
		self.c=0.0
		self.alpha=0.0
		self.beta=0.0
		self.gamma=0.0
		self.omat=np.mat(np.identity(3))  #internal is the correct orienting matrix, not a* b* c*
		self.omatinv=np.array(np.linalg.inv(self.omat))
		
		
		

class HeidiMeasurement(object):
  """A data set from a specific measurement  taken at Heidi
  """
  def __init__(self,InfoBlock,DatenBlock,Peak,CurrentCrysStruc):
    """initialize a data set
    
    Keyword arguments:
    InfoBlock -- Lineblock within gnuplot file, which holds Infodata
    DatenBlock -- Lineblock within gnuplot file, which holds the measured data
    Peak -- Peak in hkl around which have been measured 
    CurrentCrysStruc -- the crystal structure of the crystal, which has been measured
    """
    self.PeakWinkel=np.array(InfoBlock[0].split('(')[2].split(')')[0].split()).astype(float)
    self.theta=self.PeakWinkel[0]
    self.omega=self.PeakWinkel[1]
    self.chi=self.PeakWinkel[2]
    self.phi=self.PeakWinkel[3]
    self.Temperatur=float(InfoBlock[0].split('T=')[1].split('K')[0])
    self.Peak=Peak
    self.time=float(InfoBlock[0].split('t=')[1].split('s')[0])
    self.numberOfPoints=int(InfoBlock[0].split('n=')[1].split()[0])
    self.domg=float(InfoBlock[0].split('domg=')[1].split()[0])
    self.CurrentCrysStruc=CurrentCrysStruc 
     
     
    if InfoBlock[1].find('omega scan')==-1:
      print 'Die Messung an %s bei %f K ist kein omega scan' %(self.Peak, self.Temperatur)
    #DatenBlock aufteilen
    Block=[]
    BlockCounter=0
    for Zeile in DatenBlock:
      #print Zeile
      if Zeile.startswith('e'):
	if BlockCounter==0:
	  self.Detector=Block
	  BlockCounter+=1
	elif BlockCounter==1:
	  self.LRBackground=Block
	  BlockCounter+=1
	elif BlockCounter==2:
	  self.BackgroundFit=Block
	  BlockCounter+=1
	elif BlockCounter==3:
	  self.Monitor=Block  
	  BlockCounter+=1
	Block=[]
      else:
	if Zeile.startswith('#'):
	  Block.append(Zeile)
	else:
	  Block.append(Zeile.split())
	  
    #Detectorblock auslesen
    self.xomg=[]
    self.I=[]
    self.Ierr=[]
    for Zeile in self.Detector[1:]:
      self.xomg.append(float(Zeile[0]))
      self.I.append(float(Zeile[1]))
      self.Ierr.append(float(Zeile[2]))
    self.I=np.array(self.I)
    self.Ierr=np.array(self.Ierr)
      
    #LRBackgroundblock auslesen
    self.BackgroundPoints=[]
    for Zeile in self.LRBackground[1:]:
      self.BackgroundPoints.append([float(Zeile[0]),float(Zeile[1])])
      
    #BackgroundFit auslesen
    self.BackgroundFitI=[]
    for Zeile in self.BackgroundFit[1:]:
      self.BackgroundFitI.append(float(Zeile[1]))
    self.BackgroundFitI=np.array(self.BackgroundFitI)
      
    #Monitorcounts auslesen
    self.MonitorCts=[]
    self.MonitorCtserr=[]
    for Zeile in self.Monitor[1:]:
      self.MonitorCts.append(float(Zeile[1]))
      self.MonitorCtserr.append(float(Zeile[2]))
    
    
    #Berechne aus omg qx,qy,qz
    self.q=[]
    self.hkl=[]
    self.qBetrag=[]
    for omgSet in self.xomg:
      #print omgSet+self.omega
      self.q.append(calcAngles2Koord(self.theta,omgSet+self.omega,self.chi,self.phi,self.CurrentCrysStruc))
      #self.hkl.append(calcAngles2Koord(omgSet+self.omega,self.chi,self.phi))
      self.qBetrag.append(Betrag(self.q[-1]))
    self.qBetrag=np.array(self.qBetrag)
  #   v   Koordinaten des Peaks   v   #
  def get_koord(self):
    """get coordinates of the peak belonging to the measurement
    """
    return self._koord
    
  def set_koord(self, Koord):
    """set coordinates of the peak belonging to the measurement
    
    Keyword arguments:
    koord -- coordinations in hkl
    """
    self._koord=np.array(Koord)
    self._qBetrag = BetragInStruk(Koord)
    return
    
  def del_koord(self):
    """delete coordinates of the peak belonging to the measurement
    """
    del self._koord
    return
    
  koord = property(get_koord, set_koord, del_koord, "Koordinaten des Peaks")    
  #   ^   Koordinaten des Peaks   ^   #


      

     



  
def Betrag(Vektor):
  """calculate absolute of a vector [Q]
    
  Keyword arguments:
  Vektor -- vector defined in Qx,Qy,Qz
  """
  return math.sqrt(Vektor[0]**2+Vektor[1]**2+Vektor[2]**2)


def umrechMag2c(Vektor,CurrentCrysStruc):
  """calculate Q from hkl defined by the magnetical structure
    
  Keyword arguments:
  Vektor -- vector defined in hkl
  CurrentCrysStruc -- the crystal structure of the crystal, which has been measured
  """  

  #Vektor in magnetischer Zelle definiert in kartesische Koordinaten umrechnen
  #Zellparameter

  return np.array([CurrentCrysStruc.aStar*Vektor[0]+math.cos(CurrentCrysStruc.gammaStar)*CurrentCrysStruc.bStar*Vektor[1]+CurrentCrysStruc.cStar*Vektor[2]*math.cos(CurrentCrysStruc.alphaStar),CurrentCrysStruc.bStar*math.sin(CurrentCrysStruc.gammaStar)*Vektor[1]+CurrentCrysStruc.cStar*Vektor[2]*math.cos(CurrentCrysStruc.betaStar), CurrentCrysStruc.cStar*Vektor[2]])*2*math.pi



  
def readHeidiGnuplotFile(filename,CurrentCrysStruc):
  """read a set of measurmeents taken at HEiDi from a gnuplot file and svae them into a dictionary
    
  Keyword arguments:
  filename -- filename and path of the gnuplot file to read
  CurrentCrysStruc -- the crystal structure of the crystal, which has been measured
  """ 
  file=open(filename,'r')
  Zeilen=file.readlines()
  HeidiMeasurementDic={}
  #Blöcke sind durch leerzeilen getrennt, und infoblock wird vom Datenblock durch '# Detector count rate' getrennt
  Zeilen.pop(0)#remove('set terminal postscript color')
  Zeilen.pop(0)#remove('set output "' + filename + '"')
  InfoBlock=[]
  DataBlock=[]
  Measurement=[]
  for Zeile in Zeilen:
    #print len(Zeile)
    if Zeile.startswith('set') or Zeile.startswith('plot'):
      InfoBlock.append(Zeile)
    elif len(Zeile)>1:
      DataBlock.append(Zeile)
    else:
      Peakstring=InfoBlock[0].split('(')[1].split(')')[0]
      #print Peakstring
      if Peakstring.count('-')==0:
	Peak=Peakstring.split()
	if len(Peak)==2:
	  if Peak[0].count('.')>1:
	      #lpindex=Peakstring.find('.')
	      rpIndex=Peak[0].rfind('.')
	      Peakstring=Peak[0][0:rpIndex-2]+ ' ' + Peak[0][rpIndex-2:] + ' ' + Peak[1]
	  if Peak[1].count('.')>1:
	      rpIndex=Peak[1].rfind('.')
	      Peakstring=Peak[0]  + ' ' +  Peak[1][0:rpIndex-2]+ ' ' + Peak[1][rpIndex-2:]
	  #print Peakstring
	  Peak=Peakstring.split()
	    
      elif Peakstring.count('-')==1:
	index=Peakstring.find('-')
	Peakstring=Peakstring[0:index] + ' ' + Peakstring[index:]
	#print Peakstring
	Peak=Peakstring.split()
	if len(Peak)==2:
	  if Peak[0].count('.')>1:
	      #lpindex=Peakstring.find('.')
	      rpIndex=Peak[0].rfind('.')
	      Peakstring=Peak[0][0:rpIndex-2]+ ' ' + Peak[0][rpIndex-2:] + ' ' + Peak[1]
	  if Peak[1].count('.')>1:
	      rpIndex=Peak[1].rfind('.')
	      Peakstring=Peak[0]  + ' ' +  Peak[1][0:rpIndex-2]+ ' ' + Peak[1][rpIndex-2:]	      
	  #print Peakstring
	  Peak=Peakstring.split()
	
      elif Peakstring.count('-')==2:
	lIndex=Peakstring.find('-')
	rIndex=Peakstring.rfind('-')
	
	
	#print lIndex
	#print rIndex
	Peakstring=Peakstring[0:lIndex] + ' ' + Peakstring[lIndex:rIndex] + ' ' + Peakstring[rIndex:]
	#print Peakstring
	Peak=Peakstring.split()
	if len(Peak)==2:
	  if Peak[0].count('.')>1:
	      #lpindex=Peakstring.find('.')
	      rpIndex=Peak[0].rfind('.')
	      Peakstring=Peak[0][0:rpIndex-2]+ ' ' + Peak[0][rpIndex-2:] + ' ' + Peak[1]
	  if Peak[1].count('.')>1:
	      rpIndex=Peak[1].rfind('.')
	      Peakstring=Peak[0]  + ' ' +  Peak[1][0:rpIndex-2]+ ' ' + Peak[1][rpIndex-2:]	      
	  #print Peakstring
	  Peak=Peakstring.split()
	
      elif Peakstring.count('-')==3:
	Peak=Peakstring.split('-')[1:]
	Peak=[-float(Peak[0]),-float(Peak[1]),-float(Peak[2])]
	
      Peak=[float(Peak[0]),float(Peak[1]),float(Peak[2])]
      #print Peak
      Temperatur=InfoBlock[0].split('T= ')[1].split('K')[0]
      HeidiMeasurementDic[str(Peak)+ '@' +Temperatur]=HeidiMeasurement(InfoBlock, DataBlock, Peak,CurrentCrysStruc)
      InfoBlock=[]
      DataBlock=[]
     
  return HeidiMeasurementDic #array mit N Zeilen und 2 Spalten, erster Eintrag InfoBlock, zweiter Eintrag DatenBlock
  

def unloadHeidiGnuplotFile(HeidiMeasurementDic,unloadDic):
  """remove specific entries from a dictionary
    
  Keyword arguments:
  HeidiMeasurementDic -- dictionary conatining measurements form HEiDi
  unloadDic -- dictionary containing measurements, which shall be removed from the first one
  """ 
  try:
      for key,measurement in unloadDic.iteritems():
          del HeidiMeasurementDic[key]
  except KeyError:
      return False#print 'MeasurementDictionary does not 
  else:
      return True
  

def calcAngles2Koord(twotheta,omega,chi,phi,CurrentCrysStruc):
  """calculate Q coordinates from the angles of the 4 circle instrument
    
  Keyword arguments:
  omega -- omega angle
  chi -- chi angle
  phi -- phi angle
  CurrentCrysStruc -- the crystal structure of the crystal, which has been measured
  """ 
  ca=[0,0,0,0,0]
  sa=[0,0,0,0,0]
  xyz=[0,0,0,0]

  wl=0.87300 #heidi spezifisch
  rad=math.pi/180.0
  angle=[0,twotheta,omega,chi,phi]
  
  for i in range(1,5):
    x=angle[i]*rad
    # change 2theta --> theta
    if i==1:
      x=abs(0.5*x)
    sa[i]=math.sin(x)
    ca[i]=math.cos(x)
   
    
  if angle[1]<0:
    ca[1]=-ca[1]

  x=ca[2]*ca[3];
  y=sa[2]*ca[3];
  xyz[1]= (ca[1]*(x*ca[4]-sa[2]*sa[4])+sa[1]*(y*ca[4]+ca[2]*sa[4]))#*(-2*math.pi)
  xyz[2]=(-ca[1]*(x*sa[4]+sa[2]*ca[4])+sa[1]*(ca[2]*ca[4]-y*sa[4]))#*(-2*math.pi)
  xyz[3]= sa[3]*(ca[1]*ca[2]+sa[1]*sa[2])#*2*math.pi
  vl=2.0*sa[1]/wl
  for i in range(1,4):
    xyz[i]*=vl;
  
  
  oinv=CurrentCrysStruc.omatinv
  
  val=[0,0,0,0]
   
  for i in range(1,4):
    val[i]=oinv[i-1][0]*xyz[1]+oinv[i-1][1]*xyz[2]+oinv[i-1][2]*xyz[3]
  
  
  return umrechMag2c([val[1],val[2],val[3]],CurrentCrysStruc)
  
  


def plotteMessung3D(Dictionary,CurrentCrysStruc,hmin=None, hmax=None, kmin=None, kmax=None, lmin=None, lmax=None,Tmin=None,Tmax=None,showNuk=True,showMag=True,showBZ=True,scalePoints=1):#nur Messpunkte unterhalb der angebenen Temperatur plotten
  """plot the measurment data as points within a 3D space
    
  Keyword arguments:
  Dictionary -- dictionary conatining measurements form HEiDi, which shall be plotted
  CurrentCrysStruc -- the crystal structure of the crystal, which has been measured
  hmin -- lower limit for h (default None)
  hmax -- upper limit for h (default None)
  kmin -- lower limit for k (default None)
  kmax -- upper limit for k (default None)
  lmin -- lower limit for l (default None)
  lmax -- upper limit for l (default None)
  Tmin -- lower limit for T (default None)
  Tmax -- upper limit for T (default None)
  showNuk -- defines if nuclear Peak shall be plotted
  showMag -- defines if magnetic Peak shall be plotted
  showBZ -- defines if the Brillouinzone shall be plotted
  scalePoints -- factor how much the plotted points shall be scaled
  """
  import locale
  locale.setlocale(locale.LC_NUMERIC, 'C')
  
  #if some of the boundaries were not defined, they are defined as None, then the regarding maximum/minimum shall be selected
  
  
	
  if hmin is None:
	hmin=1000
	for key,Messung in Dictionary.iteritems():
		if hmin > Messung.Peak[0]:
			hmin=Messung.Peak[0]

  if hmax is None:
	hmax=-1000
	for key,Messung in Dictionary.iteritems():
		if hmax < Messung.Peak[0]:
			hmax=Messung.Peak[0]
    
  if kmin is None:
	kmin=1000
	for key,Messung in Dictionary.iteritems():
		if kmin > Messung.Peak[1]:
			kmin=Messung.Peak[1]
    
  if kmax is None:
	kmax=-1000
	for key,Messung in Dictionary.iteritems():
		if kmax < Messung.Peak[1]:
			kmax=Messung.Peak[1]
    
  if lmin is None:
	lmin=1000
	for key,Messung in Dictionary.iteritems():
		if lmin > Messung.Peak[2]:
			lmin=Messung.Peak[2]
    
  if lmax is None:
	lmax=-1000
	for key,Messung in Dictionary.iteritems():
		if lmax < Messung.Peak[2]:
			lmax=Messung.Peak[2]
    
  if Tmin is None:
	Tmin=1000
	for key,Messung in Dictionary.iteritems():
		if Tmin > Messung.Temperatur:
			Tmin=Messung.Temperatur
    
  if Tmax is None:
	Tmax=-10000
	for key,Messung in Dictionary.iteritems():
		if Tmax < Messung.Temperatur:
			Tmax=Messung.Temperatur
	  
  
  #print 'h: %i to %i, k: %i to %i, l: %i to %i, T: %f to %f' %(hmin,hmax,kmin,kmax,lmin,lmax,Tmin,Tmax)
  fig = plt.figure()
  fig.facecolor=1.0
  ax = fig.gca(projection='3d')
  #ax.set_title('lmin=%s, lmax=%s, showNuk=%s, showMag=%s' %(float('%.1g' % lmin),float('%.1g' % lmax),showNuk,showMag), ha='right')
  
  
  
  x=[]
  y=[]
  z=[]
  I=[]
  
  StrukturelleZelleQx=[]
  StrukturelleZelleQy=[]
  StrukturelleZelleQz=[]
  MagReflexe=[]
  for l in range(int(math.ceil(lmin)),int(math.floor(lmax+1))):
    EckpunktListe=[[0,1,l],[0,2,l],[-1,3,l],[-2,3,l],[-3,4,l],[-3,5,l],[-2,5,l],[-1,4,l],[-1,3,l],[0,2,l],[1,2,l],[1,3,l],[0,4,l],[-1,4,l],[0,4,l],[0,5,l],[1,5,l],[2,4,l],[3,4,l],[4,3,l],[4,2,l],
		 [3,2,l],[2,3,l],[2,4,l],[2,3,l],[1,3,l],[1,2,l],[2,1,l],[3,1,l],[3,2,l],[4,2,l],[5,1,l],[5,0,l],[6,-1,l],[6,-2,l],[5,-2,l],[6,-2,l],[7,-3,l],[7,-4,l],[6,-4,l],[5,-3,l],[6,-4,l],
		 [6,-5,l],[5,-5,l],[4,-4,l],[5,-5,l],[5,-6,l],[4,-6,l],[3,-5,l],[3,-4,l],[4,-4,l],[4,-3,l],[5,-3,l],[5,-2,l],[4,-1,l],[4,0,l],[5,0,l],
		 [4,0,l],[3,1,l],[2,1,l],[2,0,l],[3,-1,l],[4,-1,l],[4,0,l],[4,-1,l],[5,-2,l],[5,-3,l],
		 [4,-3,l],[4,-4,l],[3,-4,l],[3,-5,l],[2,-5,l],[2,-6,l],[1,-6,l],[0,-5,l],[0,-4,l],[1,-4,l],[2,-5,l],[1,-4,l],[1,-3,l],[2,-3,l],[3,-4,l],[4,-4,l],[4,-3,l],[3,-2,l],[3,-1,l],[3,-2,l],
		 [2,-2,l],[2,-3,l],[1,-3,l],[0,-2,l],[0,-1,l],[1,-1,l],[2,-2,l],[1,-1,l],[0,-1,l],[-1,0,l],[-1,1,l],[0,1,l],[1,0,l],[1,-1,l],[1,0,l],[2,0,l],[1,0,l],[0,1,l]]
    for Eckpunkt in EckpunktListe:
      MagReflexe.append(Eckpunkt)
      temp=umrechMag2c(Eckpunkt,CurrentCrysStruc)
      StrukturelleZelleQx.append(temp[0])
      StrukturelleZelleQy.append(temp[1])
      StrukturelleZelleQz.append(temp[2])
  if showBZ:
    ax.plot(StrukturelleZelleQx,StrukturelleZelleQy,StrukturelleZelleQz, label='Bzg der strukturellen Zelle')
  
  
  #ursprung als rote linie plotten
  UrsprungLinie=[[0,0,0],[0,0,lmax]]
  UrsprungLinieQx=[]
  UrsprungLinieQy=[]
  UrsprungLinieQz=[]
  for Punkt in UrsprungLinie:
    temp=umrechMag2c(Punkt,CurrentCrysStruc)
    UrsprungLinieQx.append(temp[0])
    UrsprungLinieQy.append(temp[1])
    UrsprungLinieQz.append(temp[2])
  if showBZ:
    ax.plot(UrsprungLinieQx,UrsprungLinieQy,UrsprungLinieQz, label='Normalenvektor der hk0-Ebene', c='r')
  
  NuklearePeaks=[[]]
  
  for key,Messung in Dictionary.iteritems():
    if Messung.Peak[0]>=hmin and Messung.Peak[0]<=hmax and Messung.Peak[1]>=kmin and Messung.Peak[1]<=kmax and Messung.Peak[2]>=lmin and Messung.Peak[2]<=lmax and Tmin<Messung.Temperatur and Messung.Temperatur<Tmax:
      if Messung.Peak[2]>=lmin and Messung.Peak[2]<=lmax:

	if showNuk:
	  if showMag:
	    for Punkt,Intens in zip(Messung.q,(Messung.I-Messung.BackgroundFitI)):
	      x.append(Punkt[0])
	      y.append(Punkt[1])
	      z.append(Punkt[2])
	      I.append(Intens)
	  elif not showMag:
	    if MagReflexe.count(Messung.Peak)==0:
	      for Punkt,Intens in zip(Messung.q,(Messung.I-Messung.BackgroundFitI)):
		x.append(Punkt[0])
		y.append(Punkt[1])
		z.append(Punkt[2])
		I.append(Intens)
	    
	elif not showNuk:
	  if showMag:
	    if MagReflexe.count(Messung.Peak)>0:
	      for Punkt,Intens in zip(Messung.q,(Messung.I-Messung.BackgroundFitI)):
		x.append(Punkt[0])
		y.append(Punkt[1])
		z.append(Punkt[2])
		I.append(Intens)
	  elif not showMag:
	    break

  if (showNuk or showMag) and len(I)>0:    
    I=np.array(I)
    x=np.array(x)
    y=np.array(y)
    z=np.array(z)
    size=I/I.max()*150*scalePoints/100

    color=I/I.max()

    idx=np.where(I>0)
    ax.scatter(x[idx],y[idx],z[idx], zdir='z', label='zs=0, zdir=z', marker='o', s=size[idx], c=color[idx], edgecolors=None)
    
    #plotte strukturelle Brillouinzone
    #dazu Liste der Eckpunkte
    ax.legend()
    ax.facecolor='white'
    
    ax.set_xlim3d(-0.5, 1.5)
    ax.set_ylim3d(-1, 1)
    ax.set_zlim3d((lmin-1)*CurrentCrysStruc.cStar*2*math.pi, (lmax+1)*CurrentCrysStruc.cStar*2*math.pi)

    plt.show()
    return True
  else:
    return False


   

  

def schreibeGnuplotSkript(Dictionary,filename): 
  """write a gnuplot script which plots intensity vs. the calculated |Q|
  
  Keyword arguments:
  Dictionary -- dictionary conaitning measurements form HEiDi, which shall be plotted
  filename -- the file the gnuplotscript shall be written into, and also how the ps -file, from the gnuplot script shall be named like 
  """ 
  Datei=open(filename + '.gpl','w')
  Datei.write('set terminal postscript color\nset output "%s.ps"\n' %filename)
  i=1
  for key,Messung in Dictionary.iteritems():
    Datei.write('set title " #%i: ( %s ) at ( %s ), t=%fs n=%i domg=%f T=%fK"\n' %(i,Messung.Peak,Messung.PeakWinkel,Messung.time,Messung.numberOfPoints,Messung.domg,Messung.Temperatur))
    Datei.write('set xlabel "omega scan, Q [A-1]"\nset ylabel "I [cps]"\n')
    Datei.write('set xrange [%f:%f]\n' %(np.min(Messung.qBetrag),np.max(Messung.qBetrag)))
    Datei.write('set yrange [%f:%f]\n' %(np.min(Messung.I),np.max(Messung.I)))
    Datei.write('plot "-" using 1:($2/  1.00):($3/  1.00) with errorbars pt 16 notitle\n')
    Datei.write('#Detector count rate - qBetrag - I - Ierr\n')
    for Q,I,Ierr in zip(Messung.qBetrag,Messung.I,Messung.Ierr):
      Datei.write('\t%f\t%f\t%f\n' %(Q,I,Ierr))
    Datei.write('e\n\n')
    i+=1
  return
  
  
