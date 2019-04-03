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

		def set_desktop_user(self):
			self.desktoppath="%s/.local/share/applications"%os.getenv("HOME")

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

		def get_desktop_info(self,desktop):
			pass

		def set_desktop_info(self,name,icon,comment,categories,exe=None):
			if exe==None:
				exe=name
			(tmp_obj,tmpfile)=tempfile.mkstemp(suffix='.desktop')
			tmp=open(tmpfile,'w+')
			tmp.write("[Desktop Entry]\n")
			tmp.write("Version=1.0\n")
			tmp.write("Type=Application\n")
			tmp.write("Name=%s\n"%name)
			tmp.write("Icon=%s\n"%icon)
			tmp.write("Comment=%s\n"%comment)
			tmp.write("Categories=%s;\n"%';'.join(categories))
			tmp.write("Exec=%s\n"%exe)
			val=True
			tmp.close()
			try:
				desk=xdg.DesktopEntry.DesktopEntry(tmpfile)
			except Exception as e:
				val=False
				self._debug("Desktop could not be loaded: %s"%e)
			if val:
				try:
					desk.validate()
				except Exception as e:
					val=False
					self._debug("Desktop could not be validated: %s"%e)
			if val:
				desk_name="%s.desktop"%name
				shutil.copy2(tmpfile,"%s/%s"%(self.desktoppath,desk_name))

app=app2menu()
app.set_desktop_user()
app.set_desktop_info("prueba","firefox","esto es una prueba",["GTK","Audio"])
