'''

Python class for RapidShare

Uses RapidShare API - http://images.rapidshare.com/apidoc.txt

'''

import re
import urllib2
            
class rapidshare:
    def __init__(self):
        self.class_name='rapidshare'
        
        self.accountdetails = 'http://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=getaccountdetails&withcookie=1&type=prem&login=%s&password=%s'
        self.checkfile = 'http://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=checkfiles&files=%s&filenames=%s'
        self.downloadfile = 'http://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=download&fileid=%s&filename=%s'
        self.downloadfile_cookie = 'http://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=download&fileid=%s&filename=%s&cookie=%s'
        self.download_link = 'http://%s/cgi-bin/rsapi.cgi?sub=download&fileid=%s&filename=%s&dlauth=%s'
        self.download_link_cookie = 'http://%s/cgi-bin/rsapi.cgi?sub=download&fileid=%s&filename=%s&dlauth=%s&cookie=%s'


    def check_account(self, login, password):
        
        html = self.get_url(self.accountdetails % (login, password))
        
        #Check for error
        if html.startswith('ERROR:'):
            return None
        elif html:
            cookie = re.search('cookie=(.+)', html).group(1)
            rapids = re.search('rapids=([0-9]+)', html).group(1)
            
            #Only return and use cookie if account has Rapids (rapidshare currency)
            if int(rapids) > 0:
                #Return login cookie
                return cookie
            else:
                return None
        else:
            return None


    def resolve_link(self, url, login, password):
        
        download_details = []

        cookie = self.check_account(login, password)
        
        file_details = self.validate_file(url)

        if file_details:
            download_details = self.get_download_link(file_details['file_id'], file_details['file_name'], cookie)
            file_details.update(download_details)
            print 'RapidRoutines returning:', file_details            
            return file_details
        else:
            return None


    def validate_file(self, url):
        #A valid file link will have a 1 after the 5th comma
        
        file_details = self.parse_filelink(url)
        
        if file_details:
            #File link is valid url - now grab details from RapidShare to ensure file exists there
            file_check_url = self.checkfile % (file_details['file_id'], file_details['file_name'])

            html = self.get_url(file_check_url)          

            #If file is available, RapidShare will return a '1' in 5th comma position of returned data         
            file_details['file_name'] = html.split(',')[1]
            file_details['file_size'] = html.split(',')[2]
            file_details['server_id'] = html.split(',')[3]
            file_details['status'] = html.split(',')[4]
            file_details['short_host'] = html.split(',')[5]
            
            if file_details['status'] == '1':
                return file_details
            else:
                #File is unavailable for download
                return None           
        else:
            #Invalid file link
            return None

        
    def parse_filelink(self, url):
        r = re.search('https://rapidshare.com/files/([0-9]+)/(.+)', url)
        if r:
            file_details = {}
            file_details['file_id'] = r.group(1)
            file_details['file_name'] = r.group(2)
            return file_details
        else:
            return None


    def get_download_link(self, file_id, file_name, cookie):
        
        download_details = {}
        if cookie:
            rapid_download = self.downloadfile_cookie % (file_id, file_name, cookie)
        else:
            rapid_download = self.downloadfile % (file_id, file_name)
        
        html = self.get_url(rapid_download)
        
        if html.startswith("ERROR:"):
            return None
        else:
            host = html.split(",")[0].split(":")[1]
            authkey = html.split(",")[1]
            
            if cookie:
                download_details['download_link'] = self.download_link_cookie % (host, file_id, file_name, authkey, cookie)
            else:
                download_details['download_link'] = self.download_link % (host, file_id, file_name, authkey)
            download_details['wait_time'] = html.split(",")[2]
            return download_details

    
    def get_url(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        html=response.read()
        response.close()
        return html