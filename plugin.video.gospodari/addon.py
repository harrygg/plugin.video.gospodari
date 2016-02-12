# -*- coding: utf-8 -*-
import re, sys, urllib, os.path
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from resources.lib.helper import Helper

reload(sys)  
sys.setdefaultencoding('utf8')
	
_addon = xbmcaddon.Addon(id='plugin.video.gospodari')

class Mode:
    Categories = 0
    Subcategories = 1
    Videos = 2
    Play = 3
    FullShows = 4

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
	addDir('Цели предавания', -5)
	
def SUBCATEGORIES(cat_id):
	if cat_id == -5: #if we are looking for full seasons
		seasons = helper.get_seasons()
		for s in seasons:
			addDir(s['title'].encode('utf-8'), s['id'], Mode.FullShows)		
	else:
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
	
def FULLSHOWS(show_id, page):
	videos = helper.get_full_shows(show_id, page)
	for v in videos:
		icon = v['_links']['image']['href'].replace('{size}', '768x432')
		addLink(v['title'].encode('utf-8'), v['id'], icon, True)
	
	if helper.has_more_videos:
		page = page + 1
		addDir('Следваща страница >>>', show_id, Mode.FullShows, page)
	
def PLAY(id, name, img, isFullShow):
	url = helper.get_video_stream(id, isFullShow)
	xbmc.log('Gospodari | play() | Will try to play item: ' + url)
	li = xbmcgui.ListItem(iconImage = img, thumbnailImage = img, path =  url)
	li.setInfo('video', { 'title': name })
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = url))

def addLink(name, id, img, isfullshow = False):
	u = sys.argv[0] + "?id=" + str(id) + "&mode=3&name=" + urllib.quote_plus(name) + "&isfullshow=" + str(isfullshow)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage = img, thumbnailImage = img)
	liz.setInfo( type = "Video", infoLabels = { "Title": name } )
	liz.setProperty("IsPlayable" , "true")
	ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = False)
	return ok

def addDir(name, id, mode = Mode.Subcategories, page = 1):
	u = sys.argv[0] + "?name=" + urllib.quote_plus(name) + "&mode=" + str(mode) + "&id=" + str(id) + "&page=" + str(page)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
	liz.setInfo( type = "Video", infoLabels = { "Title": name } )
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

icon = xbmc.translatePath(os.path.join(_addon.getAddonInfo('path'), "icon.png"))
try: icon = urllib.unquote_plus(params["icon"])
except: pass

mode = None
try: mode = int(params["mode"])
except: pass

page = 1
try: page = int(params["page"])
except: pass

isfullshow = False
try: isfullshow = params["isfullshow"] == 'True'
except: pass

if mode == None:
	CATEGORIES()
    
elif mode == Mode.Subcategories:
	SUBCATEGORIES(id)

elif mode == Mode.Videos:
	VIDEOS(id, page)

elif mode == Mode.Play:
	PLAY(id, name, icon, isfullshow)

elif mode == Mode.FullShows:
	FULLSHOWS(id, page)

xbmcplugin.endOfDirectory(int(sys.argv[1]))