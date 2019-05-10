#!/usr/bin/env python3
import os,sys,subprocess
import json
import xdg.Menu
import xdg.DesktopEntry
import xdg.BaseDirectory as xdgdir
import tempfile
import shutil

class app2menu():
		def __init__(self):
			self.dbg=True
			self.desktoppath="/usr/share/applications"
		#def __init__

		def _debug(self,msg):
			if self.dbg:
				print("%s"%msg)
		#def _debug

		def set_desktop_user(self):
			self.desktoppath="%s/.local/share/applications"%os.getenv("HOME")
		#def set_desktop_user

		def _get_basedirs(self):
			menu_path=[]
			for path in xdgdir.xdg_config_dirs:
				if os.path.isdir(path):
					for subdirpath in os.listdir(path):
						if "menus" in subdirpath:
							menu_path.append("%s/%s"%(path,subdirpath))
			return (menu_path)
		#def _get_basedirs

		def get_categories(self):
			xdgdirs=self._get_basedirs()
			menufiles=[]
			menuentries=[]
			categories=[]
			def _walking_path(path):
				file_list=os.listdir(path)
				for file_item in file_list:
					if os.path.isdir("%s/%s"%(path,file_item)):
						_walking_path("%s/%s"%(path,file_item))				
					elif file_item.endswith(".menu"):
						menufiles.append("%s/%s"%(path,file_item))

			def _walking_menu(menu,depth=0):
				if str(menu).lower() not in categories:
					categories.append(str(menu).lower())
				for cat in menu.getEntries():
					if isinstance(cat,xdg.Menu.Menu):
						_walking_menu(cat,depth)

			for xdgdir in xdgdirs:
				_walking_path(xdgdir)
			for menufile in menufiles:
				menu=xdg.Menu.parse(menufile)
				_walking_menu(menu)
			return(categories)
		#def get_categories

		def init_desktop_file(self):
			desktop={}
			desktop['Categories']=[]
			desktop['Comment']=''
			desktop['Exec']=''
			desktop['GenericName']=''
			desktop['Icon']=''
			desktop['Mimetypes']=''
			desktop['MiniIcon']=''
			desktop['Name']=''
			desktop['NoDisplay']=''
			desktop['NotShowIn']=''
			desktop['OnlyShowIn']=''
			desktop['Path']=''
			desktop['Protocols']=[]
			desktop['StartupNotify']=''
			desktop['StartupWMClass']=''
			desktop['Terminal']=''
			desktop['TerminalOptions']=[]
			desktop['TryExec']=''
			desktop['Type']=''
			desktop['URL']=''
			desktop['VersionString']=''
			return desktop

		def get_desktop_info(self,desktop_file):
			self._debug("Parsing %s"%desktop_file)
			desktop=self.init_desktop_file()
			try:
				deskInfo=xdg.DesktopEntry.DesktopEntry(desktop_file)
				desktop['Categories']=deskInfo.getCategories()
				desktop['Comment']=deskInfo.getComment()
				desktop['Exec']=deskInfo.getExec()
				desktop['GenericName']=deskInfo.getGenericName()
				desktop['Icon']=deskInfo.getIcon()
				desktop['Mimetypes']=deskInfo.getMimeTypes()
				desktop['MiniIcon']=deskInfo.getMiniIcon()
				desktop['Name']=deskInfo.getName()
				desktop['NoDisplay']=deskInfo.getNoDisplay()
				desktop['NotShowIn']=deskInfo.getNotShowIn()
				desktop['OnlyShowIn']=deskInfo.getOnlyShowIn()
				desktop['Path']=deskInfo.getPath()
				desktop['Protocols']=deskInfo.getProtocols()
				desktop['StartupNotify']=deskInfo.getStartupNotify()
				desktop['StartupWMClass']=deskInfo.getStartupWMClass()
				desktop['Terminal']=deskInfo.getTerminal()
				desktop['TerminalOptions']=deskInfo.getTerminalOptions()
				desktop['TryExec']=deskInfo.getTryExec()
				desktop['Type']=deskInfo.getType()
				desktop['URL']=deskInfo.getURL()
				desktop['VersionString']=deskInfo.getVersionString()
			except Exception as e:
				self._debug(e)
			return desktop
		#def get_desktop_info

		def set_desktop_info(self,name,icon,comment,categories,exe=None,validate=False,fname=None):
			if exe==None:
				exe=name
			(tmp_obj,tmpfile)=tempfile.mkstemp(suffix='.desktop')
			tmp=open(tmpfile,'w+')
			tmp.write("[Desktop Entry]\n")
			tmp.write("Version=1.0\n")
			tmp.write("Type=Application\n")
			tmp.write("Name=%s\n"%name)
			tmp.write("GenericName=%s\n"%name)
			tmp.write("Icon=%s\n"%icon)
			tmp.write("Comment=%s\n"%comment)
			tmp.write("Categories=Qt;KDE;%s;\n"%categories)
			tmp.write("Exec=%s\n"%exe)
			tmp.write('StartupNotify=true\n')
			val=True
			tmp.close()
			try:
				desk=xdg.DesktopEntry.DesktopEntry(tmpfile)
			except Exception as e:
				val=False
				self._debug("Desktop could not be loaded: %s"%e)
			if val and validate:
				try:
					desk.validate()
				except Exception as e:
					val=False
					self._debug("Desktop could not be validated: %s"%e)
			if val:
				if fname:
					desk_name=os.path.basename(fname)
				else:
					desk_name="%s.desktop"%name.replace(' ','_')
				os.chmod(tmpfile,0o644)
				shutil.copy2(tmpfile,"%s/%s"%(self.desktoppath,desk_name))
			os.remove(tmpfile)
			return(desk_name)
		#def set_desktop_info

#class app2menu
