#!/usr/bin/env python
'''
@Author: Abdelrahman Moez -aka Hydra
@Script: functions.py
'''
from BeautifulSoup import BeautifulSoup as bs
import urllib2
from PyQt4 import QtGui
import datetime
import time
import sys
import os
import re
import database
import json
#
style = """
<style>
* {
	font-family: tahoma;
	font-size: 16px;
	font-weight: normal;
}
th {
	width: 10%;
	padding: 5px;
	color: #DD0000;
	font-weight: bold;
}
td {
	width: 80%;
	padding: 5px 20px;
}
table {
	background-color: #FFFDCB;
	margin: 35px 0px;
	margin-left: 50px;
	width: 90%;
}
h1 {
	background-color: #ccc;
	padding: 20px;
	font-weight: bold;

}
</style>
	"""
def abs_http(link):
    http_link = str(link)
    if http_link.startswith('https://'):
    	http_link = http_link[8:]
    	http_link = "".join(("http://",http_link))
    if http_link.startswith("www."):
        http_link = http_link[4:]
        http_link = "".join(("http://",http_link))
    if http_link.startswith("http://www."):
        http_link = http_link[11:]
        http_link = "".join(("http://",http_link))
    if not http_link.startswith("http://"):
        http_link = "".join(("http://",http_link))
    return http_link

def page_source(link):
	link = abs_http(link)
	opener = urllib2.urlopen(link)
	html = opener.read()
	return html

def isurl(url):
	domain_suffix = ['.com','.net','.org', '.tv', '']
	for each in domain_suffix:
		if each in url:
			return True
		else:
			return False

def extract_title(link):
	get_page_source = page_source(link)
	soup = bs(get_page_source)
	title =  soup.find('title').text
	return title
# ---------------------------------------------------- #
def export_folder(folder_name, status):
	bookmarks = database.DatabaseWork().urls_of_folder(folder_name)
	if status == 'one':
		filename = "".join((unicode(folder_name), '.html'))
	elif status == 'all':
		filename = "".join(('All Bookmarks', '.html'))
	if os.path.exists(filename):
		os.remove(filename)
	f = open(unicode(filename),'a')
	f.write(style)
	# Write folder name as Header
	header = "".join(("<h1>",folder_name,"</h1>"))
	f.write(header)
	# 
	for each in bookmarks:
		to_add = u"""
		 <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
		<table border="1">
		<tr>
		<th>Title</th>
		<td>{0}</td>
		</tr>
		<tr>

		<th>Link</th>
		<td><a href="{1}" target="_blank">{1} </a></td>
		</tr>
		<tr>

		<th>Description</th>
		<td>{2}</td>
		</tr>

		<th>Date/Time</th>
		<td>{3}</td>
		</tr>
		</table>""".format(unicode(each[0]), unicode(each[1]), unicode(each[2]), unicode(each[3]))
		f.write(to_add)
	f.close()
	return True

def export_all_folders():
	if os.path.exists('All Bookmarks.html'):
		os.remove('All Bookmarks.html')
	all_bookmarks = database.DatabaseWork().list_all_bookmarks()
	for each in all_bookmarks:
		export_folder(each, 'all')
	return True
def chrome_bookmarks():
	bookmarks = []
	userprofile = os.environ['USERPROFILE']
	rest_of_path = r'AppData\\Local\\Google\\Chrome\\User Data\\Default'
	bookmark_file = 'Bookmarks'

	bookmarks_path = os.path.join(userprofile, rest_of_path,bookmark_file)
	if os.path.exists(bookmarks_path) == False:
		msg_box = QtGui.QMessageBox.critical(QtGui.QWidget(),  'Error', 'Can not locate the following bookmark file.\n"%s\n\nPress Ok and locate the file manually."'%bookmarks_path ,  QtGui.QMessageBox.Ok)
		bookmarks_path = QtGui.QFileDialog.getOpenFileName(QtGui.QWidget(), 'Locate Bookmarks File', userprofile, '*.*')
		if not bookmarks_path:
			return

	f = open(bookmarks_path, 'r').readlines()
	
	for line in f:
		# Just in case we miss something
		#date_result = title_result = url_result = None
		#
		if "date_added" in line:
			date_pattern = re.compile('\"[0123456789].*\"')
			date_result = re.search(date_pattern, line)
			if date_result:
				pass
		if "name" in line:
			title_pattern = re.compile('[\".*\""].*')
			title_result = re.search(title_pattern, line)
			if title_result:
				pass
				#print title_result.group()[9:-2]
		if "url" in line:
			url_pattern = re.compile('http://.*')
			url_result = re.search(url_pattern, line)
			if url_result:
				url = url_result.group()[:-1]
				title = title_result.group()[9:-2]
				date = date_result.group().strip("\"")
				date_time = format(getFiletime(hex(int(date)*10)[2:17]), '%a, %d %B %Y %H:%M:%S %Z')
				bookmarks.append((url, title, date_time))
	return bookmarks
	#
def getFiletime(dt):
    microseconds = int(dt, 16) / 10
    seconds, microseconds = divmod(microseconds, 1000000)
    days, seconds = divmod(seconds, 86400)
    return datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, microseconds)
def firefox_bookmarks():
	bookmarks = []
	target_folder = None
	# Grab bookmarks file
	app_data = os.environ['APPDATA']
	rest_of_path = '\Mozilla\Firefox\Profiles'
	full_path = r"".join((app_data, rest_of_path,"\\"))
	
	for folder in os.listdir(full_path):
		folder2check = "\\".join((full_path,folder))
		for subfolder in os.listdir(folder2check):
			if subfolder == 'bookmarkbackups':
				target_folder = "\\".join((full_path,folder, 'bookmarkbackups'))
	# Grab the bookmarks
	for bk_file in os.listdir(target_folder):
		json_file = "\\".join((target_folder, bk_file))
		f = open(json_file)
		data = json.load(f)

		for each in data['children'][0]['children']:
			try:
				bookmark = each['uri']
				title = each['title'] or None
				date = each['dateAdded']
				date = float(date)/1000000
				date = time.ctime(int(date))
				if bookmark.startswith('http'):
					bookmarks.append((bookmark, title, date))
			except Exception, e:
				pass
	return bookmarks
