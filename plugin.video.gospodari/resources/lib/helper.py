import sys, xbmc, os.path, json, urllib, urllib2, re, base64
from bs4 import BeautifulSoup
from ga import ga

class Mode:
	Categories = 0
	Subcategories = 1
	Videos = 2
	Play = 3
	FullShows = 4
	
	def __getattr__(self, name):
		return str(name)

class Helper:

	has_more_videos = False
	host = base64.b64decode('aHR0cDovL2dvc3BvZGFyaS5jb20v')

	def __init__(self, addon):
		self._addon = addon

	def get_categories(self, id):
		cats = []
		#if user wants to watch seasons, get them from REST API:
		if id == -4:
			cats = self.get_seasons()
		else: #Otherwise get them from mobile page
			try:
				res = Request(base64.b64decode('aHR0cDovL2dvc3BvZGFyaS5jb20vbW9iaWxl'))
				soup = BeautifulSoup(res, 'html5lib')
				submenu = soup.find('div', class_='num_%s' % id)
				return submenu.find_all('a')
			except Exception, er:
				xbmc.log("Gospodari | get_categories(" + str(id) + ") | Error: " + str(er))
		return cats
	
	def get_seasons(self):
		seasons = []
		try:
			url = base64.b64decode('aHR0cDovL3BsYXlhcGkubXRneC50di92My9zZWFzb25zL3ZpZGVvbGlzdD9mb3JtYXQ9NDY5NA==')
			res = Request(url)
			data = json.loads(res)
			seasons = data['_embedded']['seasons']
		except Exception, er:
			xbmc.log("Gospodari | Error:" + str(er))
		return seasons
	
	def get_full_shows(self, id, page):
		videos = []
		try:
			url = base64.b64decode('aHR0cDovL3BsYXlhcGkubXRneC50di92My92aWRlb3M/c2Vhc29uPSVzJnBhZ2U9JXMmb3JkZXI9LXZpc2libGVfZnJvbQ==') % (id, page)
			res = Request(url)
			data = json.loads(res)
			videos = data['_embedded']['videos']
			
			#check if there are more videos
			if page != data['count']['total_pages']:
				self.has_more_videos = True
			
		except Exception, er:
			xbmc.log("Gospodari | Error:" + str(er))
		return videos
	
	def get_videos(self, id, url, page):
		if page == 1:
			response = Request(urllib.unquote_plus(url))
			if id == 6: #top20 videos
				videos = self.get_top20_videos(response)
			else:
				videos = self.extract_videos(response)
		else:
			if id == 7: #Zoo videos are loaded from a different source
				response = self.load_more_zoo_videos(page)
			else:
				response = self.load_more_videos(id, page)
			videos = self.extract_videos(response, True)
		return videos
			
	def load_more_videos(self, id, page):
			url = base64.b64decode('aHR0cDovL2dvc3BvZGFyaS5jb20vbW9iaWxlL2xvYWRfbW9yZQ==')
			post_data = 'cat_id=%s&page=%s&order=1' % (id, page)
			return Request(url, post_data)
			
	def load_more_zoo_videos(self, page):
			url = self.host + 'mobile/load_more_zoovideos'
			post_data = 'page=%s&type=1' % page
			return Request(url, post_data)
	
	def extract_videos(self, response, load_more = False):
		videos = []
		html = response
		try:
			#set has_more
			matches = re.compile('(onclick[=\'"]+loadMore.*?)\((.+?)\)').findall(response)
			self.has_more_videos = True if len(matches) > 0 else False
			try :
				params = matches[0][1].split(',')
				if len(params) > 2: #If we are in the zoopolice page there will be 2 params only
					try: self.cat_id = params[0]
					except: self.cat_id = 0
				else:
					self.cat_id = 7
			except: pass
					
			soup = BeautifulSoup(html.decode('utf-8', 'ignore'), 'html5lib')
			items = soup.find_all('a', {'class':['video_box_wrap', 'article_box']})
			xbmc.log("Gospodari found %s items: " % len(items))
			if len(items) == 0:
				xbmc.log("HTML: " + html)
			
			for i in range(0, len(items)):
				video = {}
				url = items[i]['href'].encode('utf-8')
				video['url'] = urllib.quote_plus(url)
				video['icon'] = items[i].img['src']
				video['title'] = items[i]['title'].encode('utf-8')
				videos.append(video)
		except Exception, er:
			xbmc.log("Gospodari | extract_videos() %s" % er)
		return videos
	
	def get_top20_videos(self, html):
		videos = []
		soup = BeautifulSoup(html.decode('utf-8', 'ignore'), 'html5lib')
		items = soup.find_all('div', class_='big-video-holder')
		#regex = 'class="[a-zA-Z0-9\s]+big-video-holder(.*?)</div'
		#divs = re.compile(regex, re.DOTALL).findall(html)
		if len(items) > 0:
			for i in range (0, len(items)):
				video = {}
				a = items[i].find('a')
				video['url'] = a['href']
				video['icon'] = a.img['src']
				video['title'] = a['title'].encode('utf-8')
				videos.append(video)
		else: 
			xbmc.log("Unable to find matching regex for rule: " + regex)
			xbmc.log("Html: " + html)
		return videos				
			
	def get_video_info(self, url, isFullShow):
		stream = {}
		try:
			if isFullShow:
				url = base64.b64decode('aHR0cDovL3BsYXlhcGkubXRneC50di92My92aWRlb3Mvc3RyZWFtLyVz') % url 
				res = Request(url)
				data = json.loads(res)
				medium = data['streams']['medium']
				high = data['streams']['high']
				hls = data['streams']['hls']
				
				if high != None:
					stream['url'] = high
				elif medium != 'video://vod/':
					if 'stream.novatv.bg' in medium:
						stream['url'] = medium.replace(base64.b64decode('cnRtcDovL3N0cmVhbS5ub3ZhdHYuYmcvbWVkaWFjYWNoZS9tcDQ6aHR0cC8='), base64.b64decode('aHR0cDovL3ZpZGVvYmcubm92YXR2LmJnLw=='))
					elif 'host.bg' in medium:
						stream['url'] = medium.replace(base64.b64decode('cnRtcDovL3N0cmVhbS5ieS5ob3N0LmJnL21lZGlhY2FjaGUvZmx2Omh0dHAv'), base64.b64decode('aHR0cDovL3ZpZGVvYmcubm92YXR2LmJnLw=='))
				elif hls != None:
					stream['url'] = hls
				stream['date'] = ''
			else:
				if not url.startswith('http'): 
					url = 'http://gospodari.com/%s' % url
				html = Request(url)
				stream['url'] = re.compile('file[:"\'\s]+(http.+?mp4)').findall(html)[0]
				try:
					stream['date'] = re.compile('ubuntubold">(.+?)<').findall(html)[0]
				except: stream['date'] = ''
		except Exception, er:
			xbmc.log("Error in get_video_stream(id = %s): " % id + str(er))
		return stream

	def update(self, name, location, crash=None):
		p = {}
		p['an'] = self._addon.getAddonInfo('name')
		p['av'] = self._addon.getAddonInfo('version')
		p['ec'] = 'Addon actions'
		p['ea'] = name
		p['ev'] = '1'
		p['ul'] = xbmc.getLanguage()
		p['cd'] = location
		ga('UA-79422131-2').update(p, crash)
		
def Request(url, data = ''):
		xbmc.log("Gospodari | Sending request to: " + url)
		try:
				req = urllib2.Request(url) if data == '' else urllib2.Request(url, data) 
				req.add_header('User-Agent', MUA)
				res = urllib2.urlopen(req)
				response = res.read()
				res.close()
				#xbmc.log("Response: " + response)
				return response
		except Exception, er:
				xbmc.log("Gospodari | Request error: " + str(er))
				return ""

MUA = 'Mozilla/5.0 (Linux; Android 5.0.2; bg-bg; SAMSUNG GT-I9195 Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Version/1.0 Chrome/18.0.1025.308 Mobile Safari/535.19' 
