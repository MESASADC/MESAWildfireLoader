# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MESAWildfireLoader
                                 A QGIS plugin
 This plugin loads Active Wildfire text files to the Layers Panel
                              -------------------
        begin                : 2016-11-24
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Thembani Moitlhobogi, MESA SADC THEMA
        email                : taxmanyana@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from mesa_wildfire_loader_dialog import MESAWildfireLoaderDialog
import os.path
import os, glob
import os.path
import tempfile
import re 

class MESAWildfireLoader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MESAWildfireLoader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = MESAWildfireLoaderDialog()				

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&MESA Wildfire Loader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'MESAWildfireLoader')
        self.toolbar.setObjectName(u'MESAWildfireLoader')
        # clear the listWidget when the selectdirectory is selected
        self.dlg.selectdirectory.clicked.connect(self.cleartext)
        # clear the listWidget when the selectfile is selected
        self.dlg.selectfile.clicked.connect(self.cleartext)
        # open the system navigator dialog when the browsebutton is clicked
        self.dlg.browsebutton.clicked.connect(self.select_input)
        # clear the listWidget at the start of this plugin
        self.dlg.listWidget.clear()
		
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MESAWildfireLoader', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        #self.dlg = MESAWildfireLoaderDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/MESAWildfireLoader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'MESA Import Active WIldfires'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&MESA Wildfire Loader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # routine to clear the listWidget		
    def cleartext(self):
        wdir = ""	
        if self.dlg.listWidget.count() >= 1:
            if os.path.isdir(self.dlg.listWidget.item(0).text()):
                wdir =  self.dlg.listWidget.item(0).text()
            else:
                wdir =  os.path.dirname(self.dlg.listWidget.item(0).text())
                self.dlg.listWidget.clear()
                self.dlg.listWidget.addItem(wdir)
        else:		
            self.dlg.listWidget.clear()
		
    # routine to load the system navigator dialog		
    def select_input(self):
        wdir = ""	
        # remember last directory "wdir" that was loaded on the listWidget (use directory of first item on the listWidget)
        if self.dlg.listWidget.count() >= 1:
            if os.path.isdir(self.dlg.listWidget.item(0).text()):
                wdir =  self.dlg.listWidget.item(0).text()
            else:
                wdir =  os.path.dirname(self.dlg.listWidget.item(0).text())

        if self.dlg.selectfile.isChecked():
            filenames = []
            # open filedialog and set working directory to last open directory "wdir", only text files considered
            filenames = QFileDialog.getOpenFileNames(self.dlg, "Select input file(s) ",wdir, '*.txt')
            self.dlg.listWidget.clear()
            self.dlg.listWidget.addItems(filenames)
        if self.dlg.selectdirectory.isChecked():
            # open filedialog and set working directory to last open directory "wdir"
            dir = str(QFileDialog.getExistingDirectory(self.dlg, "Select Directory", wdir))
            self.dlg.listWidget.clear()
            self.dlg.listWidget.addItem(dir)
	
    def add_modis_layers(self, *inputs): 
        # the plugin instance and MODIS files are passed to the function
        # we only consider inputs from second element since first element is plugin instance
        if len(inputs[1:]) <= 0:
    	   return None
        elif len(inputs[1:]) == 1:
    	   # if only one file is selected then use it filename as the name of the layer
    	   filename = os.path.basename(inputs[1]) 	
        else:
           # if more thank one file is selected then name the layer Combined_MODIS_FIRE
           filename = 'Combined_MODIS_FIRE'
        # we create a temporary file for storing the output
        f = tempfile.NamedTemporaryFile(delete=False)
        tmpf = str(f.name)
        # write the header to the temporary file
        f.write(b'Lat,Lon,BT,FRP,Ver,Date,Time,Sat,Conf\n')
        # loop through all lines in the file 
        for file in inputs[1:]:
           # open input file for reading
           g = open(file,'r')
           # loop through all lines in the file 
           for line in g:
              # append data lines to output files
              f.write(line)
           # close the input/output files			  
           g.close()
        f.close()
        # generate the uniform resource identifier for importing temporary file, specifying the projection and columns containing coordinates
        uri = 'file:///%s?crs=%s&delimiter=%s&xField=%s&yField=%s&decimal=%s' % (tmpf, 'EPSG:4326', ',', 'Lon', 'Lat', '.')
        # add vector layer to the Layer Panel
        layer = self.iface.addVectorLayer(uri, filename, "delimitedtext")

    def add_msg_layers(self, *inputs): 
        # the plugin instance and MSG files are passed to the function
        # we only consider inputs from second element since first element is plugin instance
        if len(inputs[1:]) <= 0:
    	   return None
        elif len(inputs[1:]) == 1:
    	   # if only one file is selected then use it filename as the name of the layer
    	   filename = os.path.basename(inputs[1]) 	
        else:
           # if more thank one file is selected then name the layer Combined_MSG_ABBA
           filename = 'Combined_MSG_ABBA'
        # we create a temporary file for storing the output
        f = tempfile.NamedTemporaryFile(delete=False)
        tmpf = str(f.name)
        # write the header to the temporary file
        f.write(b'Longitude,Latitude,Satzen,Pix Size,T4(K),T11(K),Fire Size,Temp(K),FRP(MW),Ecosystem,Fire Flag,Date,Time(UTC)\n')
        # loop through the files		
        for file in inputs[1:]:
           # extract filename, then date and time from the filename
           fname = os.path.basename(file)
           fdate = fname[22:29]
           ftime = fname[29:33]
           # open input file for reading
           g = open(file,'r') 	   
           # loop through all lines in the file 
           for line in g:
              # replace all white spaces with a comma ','
              fdata = ','.join(line.split()) + ',' + fdate + ',' + ftime + '\n'
              # consider only lines where there are 12 columns and no alphabetic characters (to eliminate non-data lines)
              if fdata.count(',') == 12 and not re.search('[a-zA-Z]+',fdata):
                 # append data lines to output files
                 f.write(fdata)
           # close the input/output files
           g.close()
        f.close()
        # generate the uniform resource identifier for importing temporary file, specifying the projection and columns containing coordinates
        uri = 'file:///%s?crs=%s&delimiter=%s&xField=%s&yField=%s&decimal=%s' % (tmpf, 'EPSG:4326', ',', 'Longitude', 'Latitude', '.')
        # add vector layer to the Layer Panel
        layer = self.iface.addVectorLayer(uri, filename, "delimitedtext")
	
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # list to contain MODIS wildfire files
        af_modis = []
        # list to contain MSG WF ABBA wildfire files
        af_msg = []
		# 
        if result:		
            # if the selectfile option is selected then run the following procedure
            if self.dlg.selectfile.isChecked():			
				# loop through all the items on the listWidget
				for i in range(self.dlg.listWidget.count()):
					# get corresponding line from listWidget				
					file = self.dlg.listWidget.item(i).text()
					# get file name from the line (remove path)					
					filename = os.path.basename(file)
					# check if filename matches either MODIS or MSG and populate corresponding list					
					if re.match('MODIS[AT]_FIRE.[0-9]{7}.[0-9]{4}.txt' , filename):					
						af_modis.append(file)
					elif re.match('AMESD_SADC_MSG_W_ABBA_[0-9]{11}_Afri_v[1-9]{1}.txt' , filename):
					    af_msg.append(file)
            else:
				if self.dlg.listWidget.count() == 1:
					# get folder name from listWidget					
					cdir = self.dlg.listWidget.item(0).text()
					# recurse into the folder and loop through all files
					for root, dirs, files in os.walk(cdir):
					   for file in files:
					      if file.endswith(".txt"):
					         # get filename from the file
					         filename = os.path.basename(os.path.join(root, file))
					         # check if filename matches either MODIS or MSG and populate corresponding list
					         if re.match('MODIS[AT]_FIRE.[0-9]{7}.[0-9]{4}.txt' , filename):					
					            af_modis.append(os.path.join(root, file))
					         elif re.match('AMESD_SADC_MSG_W_ABBA_[0-9]{11}_Afri_v[1-9]{1}.txt' , filename):
					            af_msg.append(os.path.join(root, file))

            # if the data lists are not empty then call relevant routine to process the list								
            if len(af_modis) != 0:
            	self.add_modis_layers(self, *af_modis)
            if len(af_msg) != 0:
            	self.add_msg_layers(self, *af_msg)
