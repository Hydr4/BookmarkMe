#!/usr/bin/env python
'''
@Author: Abdelrahman Moez -aka Hydra
@Script: database.py
'''
import sqlite3
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
class DatabaseWork:
	def __init__(self):
		self.dbPath = os.path.join('datafiles','bookmarks.db')
		self.init_con = sqlite3.connect(self.dbPath)
		self.curs = self.init_con.cursor()
		self.generate_general = self.general_bookmarks()
		self.init_con.commit()
	def general_bookmarks(self):
		try:
			self.curs.execute(''' CREATE TABLE General (id INTEGER PRIMARY KEY, URL TEXT, TITLE TEXT, DESCRIPTION TEXT,  PREVIEW TEXT, DATE_TIME TEXT)''')
			self.init_con.commit()
			return True
		except Exception, e:
			return e

	def add_folder(self, folder_name):
		folder_name = unicode(folder_name)
		folder_name = folder_name.replace(' ', '_')
		try:
			self.curs.execute(''' CREATE TABLE '''+folder_name+''' (id INTEGER PRIMARY KEY, URL TEXT, TITLE TEXT, DESCRIPTION TEXT,  PREVIEW TEXT, DATE_TIME TEXT)''')
			self.init_con.commit()
			return True
		except Exception, e:
			print e
			return False
	def add_bookmark(self, url, title, description, folder, preview, date_time):
		try:
			self.curs.execute(''' INSERT INTO '''+ folder +'''(URL, TITLE, DESCRIPTION, PREVIEW, DATE_TIME) VALUES (?,?,?,?,?)''',  (unicode(url), unicode(title), unicode(description), unicode(preview), unicode(date_time)))
			self.init_con.commit()
			return True
		except Exception, e:
			print '[Add Bookmark]',e
			return False
	def table_exist(self, table_name):
		tables_names = self.curs.execute(''' SELECT name FROM sqlite_master WHERE type = 'table' ''').fetchall()
		for each in tables_names:
			if table_name in tables_names:
				return True
			else:
				return False
	'''
	def url_exist(self, url):
		all_bookmarks = self.list_all_bookmarks()
		for x, y in all_bookmarks.items():
			if url in y:
				print 'URL EXISTS!'
			print y
	'''
	def folders_names(self):
		folders_names = []
		tables_names = self.curs.execute(''' SELECT name FROM sqlite_master WHERE type = 'table' ''').fetchall()
		for each in tables_names:
			name = unicode(each[0])
			folders_names.append(unicode(name))
		return folders_names
	def urls_of_folder(self, folder_name):
		folder_bookmarks = []
		for bookmark in self.curs.execute(''' SELECT * FROM '''+folder_name):
			folder_bookmarks.append((bookmark[2], bookmark[1], bookmark[3], bookmark[5]))
		return folder_bookmarks

	def urls_of_folders(self):
		folder_bookmarks = {}
		folders_names = self.folders_names()
		for folder in folders_names:
			folder_bookmarks[folder] = []
			for bookmark in self.curs.execute(''' SELECT * FROM '''+folder):
				folder_bookmarks[folder] = (bookmark[2], bookmark[1], bookmark[3], bookmark[5])
		return folder_bookmarks

	def all_urls(self):
		urls = []
		tables_names = self.curs.execute(''' SELECT name FROM sqlite_master WHERE type = 'table' ''').fetchall()
		for each in tables_names:
			for url in self.curs.execute(''' SELECT * FROM '''+unicode(each[0])):
				urls.append(url[1])
		return urls

	def delete_bookmark(self, folder, link):
		try:
			query = " ".join(('''DELETE FROM''', folder,''' WHERE URL = (?)'''))
			self.curs.execute(query, (link,))
			self.init_con.commit()
			return True
		except Exception, e:
			return e

	def title_url_pair(self):
		paires = {}
		tables_names = self.curs.execute(''' SELECT name FROM sqlite_master WHERE type = 'table' ''').fetchall()
		for each in tables_names:
			for url in self.curs.execute(''' SELECT * FROM '''+unicode(each[0])):
				paires[url[2]] = url[1]
		return paires

	def list_all_bookmarks(self):
		all_bookmarks = {}
		folders_names = self.folders_names()
		for each in folders_names:
			folder = unicode(each)
			all_bookmarks[folder] = []
			for record in self.curs.execute(''' SELECT * FROM '''+folder):
				#print record
				url = record[1] or ''
				title = record[2] or ''
				description = record[3] or ''
				date_time = record[5] or ''
				if folder in all_bookmarks.keys():
					all_bookmarks[folder].append([url, title, description, folder, date_time])

		return all_bookmarks
	def delete_folder(self, folder_name):
		try:
			self.curs.execute(''' drop table '''+folder_name)
			self.init_con.commit()
			return True
		except Exception, e:
			return e
	def get_url_info(self, link):
		info = None
		# Get all tables names
		tables_names = self.curs.execute(''' SELECT name FROM sqlite_master WHERE type = 'table' ''').fetchall()
		# Grab each bookmark from each folder
		for each in tables_names:
			table_name = unicode(each[0]).encode('utf-8')
			for url in self.curs.execute(''' SELECT * FROM '''+table_name):
				if url[1] == link:
					info = [url[1], url[2], url[3], url[4], url[5]]
					return info
		return False
	def move_to_folder(self, link, src_folder, dst_folder):
		try:
			dst_folder = unicode(dst_folder).replace(' ', '_')
			src_folder = unicode(src_folder).replace(' ', '_')
			# Get link info
			info = self.get_url_info(link)
			update_info = info.insert(3, dst_folder)
			info = tuple(info)
			# Bookmark a new link with the info		
			self.add_bookmark(*info)
			# Delete the old record
			self.delete_bookmark(src_folder, link)
			return True
		except Exception, e:
			return e
	def rename_folder(self, old_name, new_name):
		query = " ".join((''' ALTER TABLE ''', old_name, ''' RENAME TO''', new_name))
		try:
			self.curs.execute(query)
			self.init_con.commit()
			return True
		except Exception, e:
			print e
			return e
	def update_bookmark(self, folder, link, title, description, preview, date_time):
		# MAKE SURE THERE IS NO DUPLICATE URL
		self.add_bookmark(link, title, description, folder, preview, date_time)
		#self.delete_bookmark()
		##query = " ".join(('''UPDATE''', folder, ''' SET URL=? and TITLE=? '''))
		
