import xbmc, os.path, json, urllib, urllib2, re, base64

class Helper():
    has_more_videos = False
    host = base64.b64decode('aHR0cDovL2dvc3BvZGFyaS5jb20v')
    
    def get_categories(self, id):
        try:
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'categories.json')
            with open(filename) as data_file: 
                data = json.load(data_file)
            return data["categories"][id]
        except Exception, er:
            xbmc.log("Error:" + str(er))
            return json.load("{}")
    
    def get_videos(self, id, page):
        if page == 1:
            response = Request(self.get_url(id))
            if id < 0 and id > -4: #top20 videos
                videos = self.get_top20_videos(response)
            elif id == -4:
                videos = self.get_zoo_videos(response)
            else:
                videos = self.extract_videos(response)
        else:
            if id == -4:
                response = self.load_more_zoo_videos(page)
                videos = self.get_zoo_videos(response, True)
            else:
                response = self.load_more_videos(id, page)
                videos = self.extract_videos(response, True)
        return videos
    
    def get_url(self, id):
        
        if id > 0:
            u = self.host + 'mobile/index/' + str(id)
        elif id == -1: #top20-dnes
            u = self.host + 'mobile/top20-dnes'
        elif id == -2: #top20
            u = self.host + 'mobile/sedmichen-top'
        elif id == -3: #top20
            u = self.host + 'mobile/mesechen-top'
        elif id == -4: #top20
            u = self.host + 'mobile/zoopolice'
        return u
        
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
            matches = re.compile('(onclick[=\'"]+loadMore)').findall(response)
            self.has_more_videos = True if len(matches) > 0 else False
            
            if load_more == False:
                body = re.compile('class="scroll_down"(.*)load_ajax_up', re.DOTALL).findall(response)
                html = body[0] if len(body) > 0 else ''
                
            xbmc.log("HTML: " + html)
            regex = 'gospodari\.com/mobile/view/([0-9]+)'
            ids = re.compile(regex).findall(html)
            icons = re.compile('i\.gospodari\.com/(.+)\.jpg').findall(html)
            titles = re.compile('class[="\'\s]+title["\s\']+>(.+?)</div').findall(html)
            if len(ids) == len(icons) and len(icons) == len(titles):
                for i in range(0, len(ids)):
                    video = {}
                    video['id'] = ids[i]
                    video['icon'] = 'http://i.gospodari.com/%s.jpg' % icons[i]
                    video['title'] = titles[i]
                    videos.append(video) 
        except Exception, er:
            xbmc.log("Error:" + str(er))
        return videos
    
    def get_top20_videos(self, html):
        videos = []
        regex = 'class="[a-zA-Z0-9\s]+big-video-holder(.*?)</div'
        divs = re.compile(regex, re.DOTALL).findall(html)
        if len(divs) > 0:
            for i in range (0, len(divs)):
                ids = re.compile('video([0-9]+).html').findall(divs[i])
                icons_titles = re.compile('img.*src="(.*?)".+alt="(.*?)"').findall(divs[i])
                #titles = re.compile('title=["\s\']+(.+?)["\s\']+').findall(divs[i])
                if ids > 0 and icons_titles > 0:
                    video = {}
                    video['id'] = ids[0]
                    video['icon'] = icons_titles[0][0]
                    video['title'] = icons_titles[0][1]
                    videos.append(video)
        else: 
            xbmc.log("Unable to find matching regex for rule: " + regex)
            xbmc.log("Html: " + html)
        return videos        
    
    def get_zoo_videos(self, html, loading_more = False):
        videos = []
        if loading_more == False:
            regex = 'about-box-icon2(.*)load_more_wrap'
            divs = re.compile(regex, re.DOTALL).findall(html)
            source = divs[0]
        else:
            source = html
            
        #set has_more
        matches = re.compile('(onclick[=\'"]+loadMore)').findall(html)
        self.has_more_videos = True if len(matches) > 0 else False
        
        ids = re.compile('view/([0-9]+?)"').findall(source)
        icons_titles = re.compile('img.*src="(.+?)".+alt="(.+?)"').findall(source)
        if len(ids) > 0:
            for i in range (0, len(ids)):
                video = {}
                video['id'] = ids[i]
                video['icon'] = icons_titles[i][0]
                video['title'] = icons_titles[i][1]
                videos.append(video)
        else: 
            xbmc.log("Html: " + html)
        return videos    
        
        
    def get_video_stream(self, id):
        try:
            url = 'http://gospodari.com/mobile/view/' + str(id)
            html = Request(url)
            #file:"http://v.gospodari.com/f/videos/80/d93e8b96e484babd7ad35bee7e09847f.mp4"
            url = re.compile('file[:"\']+(.*?\.[a-zA-Z0-9]+)["\'\s]{0,1}\}').findall(html)
            if len(url) > 0:
                return url[0]
        except Exception, er:
            xbmc.log("Error in get_video_stream(id = %s): " % id + str(er))
            return ''
    
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
