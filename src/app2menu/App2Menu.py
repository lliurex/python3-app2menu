#!/usr/bin/env python3
import os,sys,subprocess
import json
import xdg.Menu
import xdg.Mime as mime
import xdg.DesktopEntry
import xdg.BaseDirectory as xdgdir
import tempfile
import shutil

class app2menu():
		def __init__(self):
			self.dbg=False
			self.desktoppath="/usr/share/applications"
		#def __init__

		def _debug(self,msg):
			if self.dbg:
				print("app2menu: {}".format(msg))
		#def _debug

		def set_desktop_user(self):
			self._debug("Set path to user")
			self.desktoppath=os.path.join(os.getenve("HOME"),".local","share","applications")
		#def set_desktop_user
		
		def set_desktop_system(self):
			self._debug("Set path to system")
			self.desktoppath="/usr/share/applications"
		#def set_desktop_user

		def _get_basedirs(self):
			menu_path=[]
			for path in xdgdir.xdg_config_dirs:
				if os.path.isdir(path):
					for subdirpath in os.listdir(path):
						if "menus" in subdirpath:
							menu_path.append(os.path.join(path,subdirpath))
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
					fpath=os.path.join(path,file_item)
					if os.path.isdir(fpath):
						_walking_path(fpath)
					elif file_item.endswith(".menu"):
						menufiles.append(fpath)

			def _walking_menu(menu,depth=0):
				if str(menu).lower() not in categories:
					categories.append(str(menu).lower())
				for cat in menu.getEntries():
					if isinstance(cat,xdg.Menu.Menu):
						_walking_menu(cat,depth)

			for xdgdir in xdgdirs:
				_walking_path(xdgdir)
			for menufile in menufiles:
				try:
					menu=xdg.Menu.parse(menufile)
					_walking_menu(menu)
				except Exception as e:
					self._debug("Error parsing {0}: {1}".format(menufile,e))
			return(categories)
		#def get_categories

		def get_categories_tree(self):
			xdgdirs=self._get_basedirs()
			menufiles=[]
			menuentries=[]
			categories=[]
			categories_tree={}
			def _walking_path(path):
				file_list=os.listdir(path)
				for file_item in file_list:
					fpath=os.path.join(path,file_item)
					if os.path.isdir(fpath):
						_walking_path(fpath)
					elif file_item.endswith(".menu"):
						menufiles.append(fpath)

			def _walking_menu(menu,depth=0,mainCat=''):
				if str(menu).lower() not in categories:
					categories.append(str(menu).lower())
				if "lliurex" in str(menu).lower():
				#Lliurex xdg own menus for any reason don't load entries...
					categories_tree[str(menu)]=self.get_apps_from_category(str(menu).lower())
				else:
					for cat in menu.getEntries():
						if isinstance(cat,xdg.Menu.Menu):
							if depth==0:
								mainCat=str(cat)
								categories_tree[mainCat]=[]
								_walking_menu(cat,depth+1,mainCat)
							else:
								newCat=str(cat)
								categories_tree[newCat]=[]
								_walking_menu(cat,depth+1,newCat)
						elif mainCat!='':
							if str(cat).endswith(".desktop"):
								categories_tree[mainCat].append(str(cat))

			for xdgdir in xdgdirs:
				_walking_path(xdgdir)
			for menufile in menufiles:
				mainCat=''
				try:
					menu=xdg.Menu.parse(menufile)
					_walking_menu(menu)
				except Exception as e:
					self._debug("Error parsing {0}: {1}".format(menufile,e))
			populated_categories={}
			for cat,tree in categories_tree.items():
				if len(tree)>1:
					populated_categories[cat]=tree
			return(populated_categories)
		#def get_categories_tree

		def get_apps_from_category(self,category):
			desktops={}
			if os.path.isdir(self.desktoppath):
				for deskFile in os.listdir(self.desktoppath):
					if deskFile.endswith(".desktop"):
						dpath=os.path.join(self.desktoppath,deskFile)
						try:
							desk=xdg.DesktopEntry.DesktopEntry(dpath)
						except:
							self._debug("Rejecting {}".format(deskFile))
							continue
						exe=desk.getExec().split()
						if self._validate_exe(exe)==False:
							continue
						for cat in desk.getCategories():
							catlow=cat.lower()
							if category == catlow or category.replace(" ","-") == catlow:
								desktops[deskFile]={'icon':desk.getIcon(),'exe':desk.getExec(),'name':desk.getName(),"path":dpath}
								break
							elif "{}s".format(catlow)==category:
								desktops[deskFile]={'icon':desk.getIcon(),'exe':desk.getExec(),'name':desk.getName(),"path":dpath}
								break
			return desktops
		#def get_apps_from_category

		def get_apps_from_menuentry(self,entry):
			desktops={}
			categories=self.get_categories_tree()
			entries=categories.get(entry,[])
			if os.path.isdir(self.desktoppath):
				for deskFile in entries:
					if deskFile.endswith(".desktop"):
						try:
							desk=xdg.DesktopEntry.DesktopEntry(os.path.join(self.desktoppath,deskFile))
						except Exception as e:
							self._debug("Rejecting {}".format(deskFile))
							print(e)
							continue
						exe=desk.getExec().split()
						if self._validate_exe(exe)==False:
							continue
						desktops[deskFile]={'icon':desk.getIcon(),'exe':desk.getExec(),'name':desk.getName()}
			return desktops
		#def get_apps_from_menuentry

		def _validate_exe(self,exe):
			sw=False
			blacklist=["/bin/bash","env","/bin/sh"]
			for component in exe:
				if "%" in component or component in blacklist:
					continue
				if os.path.isfile(component)==True:
					sw=True
					break
				else:
					which=shutil.which(component)
					if which!="" and which!=None:
						sw=True
						break
			return(sw)
		#def _validate_exe

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
			self._debug("Parsing {}".format(desktop_file))
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

		def write_custom_desktop(self, desktop,path):
			destPath=path
			(tmp_obj,tmpfile)=tempfile.mkstemp(suffix='.desktop')
			tmp=open(tmpfile,'w+')
			tmp.write("[Desktop Entry]\n")
			tmp.write("Version=1.0\n")
			tmp.write("Type=Application\n")
			for key,data in desktop.items():
				tmp.write("{0}={1}\n".format(key.capitalize(),data))
			tmp.close()
			sw_ok=True
			try:
				desk=xdg.DesktopEntry.DesktopEntry(tmpfile)
			except Exception as e:
				sw_ok=False
				self._debug("Desktop could not be loaded: {}".format(e))
			if sw_ok:
				os.chmod(tmpfile,0o644)
				if path.endswith(".desktop")==False:
					deskName=desktop['Name'].replace(" ","_").replace(",","_")
					if not deskName.endswith('.desktop'):
						deskName="{}.desktop".format(deskName)
					destPath=os.path.join(path,deskName)
				self._debug("Copying {} to {}".format(tmpfile,destPath))
				shutil.copy2(tmpfile,"{}".format(destPath))
				self._debug("Created {}".format(tmpfile,destPath))
			#os.remove(tmpfile)
			return(destPath)


		def set_desktop_info(self,name,icon,comment,categories,exe=None,validate=False,fname=None):
			if exe==None:
				exe=name
			(tmp_obj,tmpfile)=tempfile.mkstemp(suffix='.desktop')
			tmp=open(tmpfile,'w+')
			tmp.write("[Desktop Entry]\n")
			tmp.write("Version=1.0\n")
			tmp.write("Type=Application\n")
			tmp.write("Name={}\n".format(name))
			tmp.write("GenericName={}\n".format(name))
			tmp.write("Icon={}\n".format(icon))
			tmp.write("Comment={}\n".format(comment))
			tmp.write("Categories={};\n".format(categories))
			tmp.write("Exec={}\n".format(exe))
			tmp.write('StartupNotify=true\n')
			val=True
			tmp.close()
			try:
				desk=xdg.DesktopEntry.DesktopEntry(tmpfile)
			except Exception as e:
				val=False
				self._debug("Desktop could not be loaded: {}".format(e))
			if val and validate:
				try:
					desk.validate()
				except Exception as e:
					val=False
					self._debug("Desktop could not be validated: {}".format(e))
			if val:
				if fname:
					desk_name=os.path.basename(fname)
					if not desk_name.endswith('.desktop'):
						desk_name="{}.desktop".format(desk_name)
				else:
					desk_name=os.path.basename(name)
					desk_name="{}.desktop".format(desk_name.replace(' ','_'))
				os.chmod(tmpfile,0o644)
				if not os.path.isdir(self.desktoppath):
					try:
						os.makedirs(self.desktoppath)
					except Exception as e:
						print("Couldn't create {0}: {1}".format(self.desktoppath,e))
				shutil.copy2(tmpfile,os.path.join(self.desktoppath,desk_name))
			os.remove(tmpfile)
			return(desk_name)
		#def set_desktop_info

		def get_default_app_for_file(self,filename):
			app=""
			mimetype=mime.get_type(filename)
			prc=subprocess.run(["xdg-mime","query","default","{0}/{1}".format(mimetype.media,mimetype.subtype)],stdout=subprocess.PIPE)
			deskFile=prc.stdout.decode().rstrip("\n")
			if deskFile:
				info=self.get_desktop_info("/usr/share/applications/{}".format(deskFile))
				self._debug(info)
				if info['Exec']:
					self._debug("Find {}".format(info['Exec']))
					if ("%" in info['Exec']):
						app=" ".join(info['Exec'].split(" ")[:-1])
					else:
						app=info['Exec']
			self._debug("Default app for {0}: {1}".format(filename,app))
			return(app)
#class app2menu
