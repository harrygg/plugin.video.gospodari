# -*- coding: utf-8 -*-
import re, sys, urllib
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.helper import Helper

# append pydev remote debugger
REMOTE_DBG = False
if REMOTE_DBG:
	try:
		sys.path.append("C:\\Software\\Java\\eclipse-luna\\plugins\\org.python.pydev_4.4.0.201510052309\\pysrc")
		import pydevd
		xbmc.log("After import pydevd")
		#import pysrc.pydevd as pydevd # with the addon script.module.pydevd, only use `import pydevd`
		# stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
		pydevd.settrace('localhost', stdoutToServer=False, stderrToServer=False, suspend=False)
	except ImportError:
		xbmc.log("Error: You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
		sys.exit(1)
	except:
		xbmc.log("Unexpected error:", sys.exc_info()[0]) 
		sys.exit(1)
		
reload(sys)  
sys.setdefaultencoding('utf8')

class Mode:
    Categories = 0
    Subcategories = 1
    Videos = 2
    Play = 3

helper = Helper()
   
def CATEGORIES():
	addDir('Гафове', 0)
	addDir('Репоражи', 1)
	addDir('Скечове', 2)
	addDir('Класации', 3)
	addDir('Топ 20 най-гледаните днес', -1, Mode.Videos)
	addDir('Топ 20 най-гледаните тази седмица', -2, Mode.Videos)
	addDir('Топ 20 най-гледаните тази месец', -3, Mode.Videos)
	addDir('Зоополиция', -4, Mode.Videos)
	#addDir('Цели предавания', -5, Mode.Videos)
	
def SUBCATEGORIES(cat_id):
	data = helper.get_categories(cat_id)
	for s in data['categories']:
		addDir(s['name'].encode('utf-8'), s['id'], Mode.Videos)
	
def VIDEOS(cat_id, page):
	videos = helper.get_videos(cat_id, page)
	for v in videos:
		addLink(v['title'].encode('utf-8'), v['id'], v['icon'])
	
	if helper.has_more_videos:
		page = page + 1
		addDir('Следваща страница >>>', cat_id, Mode.Videos, page)
	
def PLAY(id, name, icon):
	url = helper.get_video_stream(id)
	li = xbmcgui.ListItem(iconImage = icon, thumbnailImage = icon, path =  url)
	li.setInfo('video', { 'title': name })
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = url))

def addLink(name, id, iconimage):
	u = sys.argv[0] + "?id=" + str(id) + "&mode=3&name=" + urllib.quote_plus(name)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage = iconimage, thumbnailImage = iconimage)
	liz.setInfo( type = "Video", infoLabels = { "Title": name } )
	liz.setProperty("IsPlayable" , "true")
	ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = False)
	return ok

def addDir(name, id, mode = Mode.Subcategories, page = 1):
	u = sys.argv[0] + "?name=" + urllib.quote_plus(name) + "&mode=" + str(mode) + "&id=" + str(id) + "&page=" + str(page)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = True)
	return ok

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

params = get_params()

id = None
try: id = int(params["id"])
except: pass

name = None
try: name = urllib.unquote_plus(params["name"])
except: pass

url = None
try: url = urllib.unquote_plus(params["url"])
except: pass

iconimage = None
try: iconimage = urllib.unquote_plus(params["iconimage"])
except: pass

mode = None
try: mode = int(params["mode"])
except: pass

page = 1
try: page = int(params["page"])
except: pass

if mode == None:
	CATEGORIES()
    
elif mode == Mode.Subcategories:
	SUBCATEGORIES(id)

elif mode == Mode.Videos:
	VIDEOS(id, page)

elif mode == Mode.Play:
	PLAY(id, name, iconimage)

xbmcplugin.endOfDirectory(int(sys.argv[1]))