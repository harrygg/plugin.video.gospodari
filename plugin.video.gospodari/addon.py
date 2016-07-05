# -*- coding: utf-8 -*-
import re, sys, urllib, os.path, time
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.helper import Mode, Helper


reload(sys)  
sys.setdefaultencoding('utf8')
	

def Categories():
	addDir('Гафове', 1)
	addDir('Репоражи', 2)
	addDir('Скечове', 3)
	addDir('Класации', 4)
	addDir('Топ 20', 6)
	addDir('Зоополиция', 7, Mode.Videos, 'http://gospodari.com/mobile/zoopolice')
	addDir('Цели предавания', 0)
	helper.update('browse', 'Categories')
	
def Subcategories(cat_id):
	if cat_id == 0: #if we are looking for full seasons
		seasons = helper.get_seasons()
		for s in seasons:
			addDir(s['title'].encode('utf-8'), s['id'], Mode.FullShows)		
	else:
		data = helper.get_categories(cat_id)
		for s in data:
			addDir(s.get_text().encode('utf-8'), cat_id, Mode.Videos, s['href'])
	
def Videos(cat_id, url, page):
	videos = helper.get_videos(cat_id, url, page)
	for v in videos:
		addLink(v['title'].encode('utf-8'), v['url'], v['icon'])
	
	if helper.has_more_videos:
		page = page + 1
		addDir('Следваща страница >>>', helper.cat_id, Mode.Videos, '', page)
	
def FullShows(show_id, page):
	videos = helper.get_full_shows(show_id, page)
	for v in videos:
		icon = v['_links']['image']['href'].replace('{size}', '768x432')
		addLink(v['title'].encode('utf-8'), v['id'], icon, True)
	
	if helper.has_more_videos:
		page = page + 1
		addDir('Следваща страница >>>', show_id, Mode.FullShows, '', page)
	
def Play(url, name, img, isFullShow):
	video = helper.get_video_info(url, isFullShow)
	xbmc.log('Gospodari | play() | Will try to play item: ' + video['url'])
	li = xbmcgui.ListItem(iconImage = img, thumbnailImage = img, path = video['url'])
	li.setInfo('video', { 'title': name + ' ' + video['date'] })
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = video['url']))

def addLink(name, url, img, isfullshow = False):
	u = "%s?url=%s&mode=3&name=%s&isfullshow=%s" % (sys.argv[0], url, urllib.quote_plus(name), isfullshow)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage = img, thumbnailImage = img)
	liz.setInfo( type = "Video", infoLabels = { "Title": name } )
	liz.setProperty("IsPlayable" , "true")
	ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = False)
	return ok

def addDir(name, id, mode = Mode.Subcategories, url = '', page = 1):
	u = "%s?name=%s&mode=%s&id=%s&page=%s&url=%s" % (sys.argv[0], urllib.quote_plus(name), mode, id, page, urllib.quote_plus(url))
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

try:
	addon = xbmcaddon.Addon(id='plugin.video.gospodari')
	helper = Helper(addon)

	params = get_params()

	try: id = int(params["id"])
	except: id = None

	try: name = urllib.unquote_plus(params["name"])
	except: name = None

	try: url = urllib.unquote_plus(params["url"])
	except: url = None

	try: icon = urllib.unquote_plus(params["icon"])
	except: icon = xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), "icon.png"))

	try: mode = int(params["mode"])
	except: mode = None

	try: page = int(params["page"])
	except: page = 1

	try: isfullshow = params["isfullshow"] == 'True'
	except: isfullshow = False

	if mode == None:
		Categories()
			
	elif mode == Mode.Subcategories:
		Subcategories(id)

	elif mode == Mode.Videos:
		Videos(id, url, page)

	elif mode == Mode.Play:
		Play(url, name, icon, isfullshow)

	elif mode == Mode.FullShows:
		FullShows(id, page)
	
except Exception, e:
  helper.update('exception', str(e.args[0]), sys.exc_info())
	
xbmcplugin.endOfDirectory(int(sys.argv[1]))