#!/usr/bin/env python3
import sys
import subprocess
from app2menu import App2Menu

#Generate desktop
menu=App2Menu.app2menu()
desktop_name=sys.argv[1]
desktop_icon=sys.argv[2]
desktop_comment=sys.argv[3]
desktop_categories=sys.argv[4]
desktop_exe=sys.argv[5]
filename=sys.argv[6]

menu.set_desktop_info(desktop_name,desktop_icon,desktop_comment,desktop_categories,desktop_exe,False,filename)
subprocess.run(["/usr/bin/update-desktop-database","/usr/share/applications"])
