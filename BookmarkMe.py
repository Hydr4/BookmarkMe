#!/usr/bin/env python
'''
@Author: Abdelrahman Moez -aka Hydra
@Script: BookmarkMe.py
'''
import sys
reload(sys)
sys.path.append('modules')
sys.setdefaultencoding('utf-8')
#
from PyQt4 import QtCore, QtGui
import threading
import urllib2
from BeautifulSoup import BeautifulSoup as bs
from functools import partial
import os
import sqlite3
import re
import webbrowser
import database
import functions
import time
# -----------------------------------------------------------------

db_handler = database.DatabaseWork()
PROGRAM_BANNER = os.path.join('datafiles', 'header')
APP_ICON = os.path.join('datafiles', 'bme')
def busy_mouse():
	# Make mouse busy
	QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
	return
def reset_mouse():
	# Restore mouse shape
	QtGui.QApplication.restoreOverrideCursor()
	return
class UI(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.resize(800,500) # resize the window
		self.setWindowTitle('BookmarkMe!')
		self.setWindowIcon(QtGui.QIcon(APP_ICON))        
		self.statusBar().showMessage('Status: Ready ')
		self.statusBar().setStyleSheet('font: bold; color: green;')
		self.move(QtGui.QApplication.desktop().screen().rect().center()- self.rect().center()) # set position to center of screen
		# Application Banner
		self.banner = QtGui.QLabel(self)
		self.banner.setPixmap(QtGui.QPixmap(PROGRAM_BANNER))
		self.banner.resize(500, 113)
		self.banner.move(165,10)
		self.banner.setStyleSheet('border-bottom: 2px solid black;')
		#
		self.all_results = []
		self.folders_names = db_handler.folders_names()
		self.draw_bookmark_ui = self.bookmark_ui()
		self.draw_controls = self.controls()
	def bookmark_ui(self):
		# -------------- Main inputs ------------------ #
		self.bm_cont = QtGui.QGroupBox('Bookmark Link', self)
		self.bm_cont.setStyleSheet('QGroupBox {font-weight: bold; font-size: 15px; font-family: Verdana}')
		self.bm_cont.resize(370,210)
		self.bm_cont.move(20,140)
		
		self.link_label = QtGui.QLabel('Link:', self.bm_cont)
		self.link_label.move(20,40)
		self.link_input = QtGui.QLineEdit(self.bm_cont)
		self.link_input.move(90,40)
		self.link_input.resize(180,20)
		self.link_input.setDragEnabled(True) # To enable darg/drop feature
		
		self.paste_cb = QtGui.QPushButton('Paste link', self.bm_cont)
		self.paste_cb.move(280,40)
		self.paste_cb.clicked.connect(self.paste_from_clipboard)
		
		self.title_label = QtGui.QLabel('Title:', self.bm_cont)
		self.title_label.move(20,70)
		self.title_input = QtGui.QLineEdit(self.bm_cont)
		self.title_input.move(90,70)
		self.title_input.resize(260,20)

		self.description_label = QtGui.QLabel('Description:', self.bm_cont)
		self.description_label.move(20, 100)
		self.description_input = QtGui.QLineEdit(self.bm_cont)
		self.description_input.move(90,100)
		self.description_input.resize(260,20)

		self.folder_label = QtGui.QLabel('Pick a folder:', self.bm_cont)
		self.folder_label.move(20,130)
		self.folder_input = QtGui.QComboBox(self.bm_cont)
		self.folder_input.move(90,130)
		self.folder_input.resize(180,20)	
		self.set_folders_list()

		self.newfolder_button = QtGui.QPushButton('New Folder', self.bm_cont)
		self.newfolder_button.move(280,130)
		self.newfolder_button.clicked.connect(self.initNewFolder)

		self.bookmark_button = QtGui.QPushButton('Bookmark!',self.bm_cont)
		self.bookmark_button.move(170,165)
		self.bookmark_button.resize(80,30)
		self.bookmark_button.setStyleSheet('font-weight: bold; color: #FF5400; border: 2px solid black; border-radius: 13px')
		self.bookmark_button.clicked.connect(self.initBookmarking)
		self.draw_search = self.Search()

	def set_folders_list(self):
		# Clear list
		self.folder_input.clear()
		# Add folders to list
		for folder in db_handler.folders_names():
			self.folder_input.addItem(unicode(folder.replace('_', ' ')))

	def Search(self):
		self.search = QtGui.QGroupBox('Quick Search', self)
		self.search.setStyleSheet('QGroupBox {font-weight: bold; font-size: 15px; font-family: Verdana}')
		self.search.move(410,140)
		self.search.resize(370,210)

		self.search_input = QtGui.QLineEdit(self.search)
		self.search_input.setPlaceholderText('Type title or URL ...')
		self.search_input.textChanged.connect(self.performSearch)
		self.search_input.move(20,30)
		self.search_input.resize(330,20)

		self.results = QtGui.QListWidget(self.search)
		self.results.activated.connect(self.OpenLink)
		self.results.resize(330,120)
		self.results.move(20,60)
		self.results.setStyleSheet('border: 1px solid darkgrey; border-radius: 3px')
	def performSearch(self):
		all_bookmarks = db_handler.all_urls()
		title_url_pair = db_handler.title_url_pair()
		keyword = str(self.search_input.text().toUtf8()).lower()
		pattern = re.compile(unicode(keyword))
		# ----------------------------
		if keyword == '':
			for each in xrange(self.results.count()):
				self.results.takeItem(each)
				self.results.clear()
			return
		# ----------------------------
		for each in xrange(self.results.count()):
			self.results.takeItem(each)
			self.results.clear()
		# ----------------------------
		self.all_results = []

		for record in all_bookmarks:
				r1 = re.search(pattern, record.lower())
				if r1:
					if record not in self.all_results:
						self.all_results.append(record)
						list_item = self.results.addItem(record)
		for title, url in title_url_pair.items():
			r2 = re.search(pattern, title.lower())
			if r2:
				if url not in self.all_results:
					self.all_results.append(url)
					self.results.addItem(url)
	def OpenLink(self):
		current_item = str(self.results.currentItem().text())
		webbrowser.open_new_tab(current_item)

	def controls(self):
		self.controls_cont = QtGui.QGroupBox('Controls', self)
		self.controls_cont.resize(650,80)
		self.controls_cont.setStyleSheet('QGroupBox {font: bold}')
		self.controls_cont.move(80,380)

		self.view_bookmarks = QtGui.QPushButton('Bookmarks list', self.controls_cont)
		self.view_bookmarks.move(20,30)
		self.view_bookmarks.resize(100,30)
		self.view_bookmarks.clicked.connect(self.initViewBookmarks)

		self.export_bookmarks = QtGui.QPushButton('Export Bookmarks', self.controls_cont)
		self.export_bookmarks.move(150,30)
		self.export_bookmarks.resize(100,30)
		self.export_bookmarks.clicked.connect(self.initExporting)
		
		self.import_bookmarks = QtGui.QPushButton('Import Bookmarks', self.controls_cont)
		self.import_bookmarks.move(280,30)
		self.import_bookmarks.resize(100,30)
		self.import_bookmarks.clicked.connect(self.initImporting)
		

		self.send_systray = QtGui.QPushButton('Send to Systray', self.controls_cont)
		self.send_systray.move(410,30)
		self.send_systray.resize(100,30)
		self.send_systray.clicked.connect(self.sendToSysTray)

		self.contact_btn = QtGui.QPushButton('About', self.controls_cont)
		self.contact_btn.move(540,30)
		self.contact_btn.resize(100,30)
		self.contact_btn.clicked.connect(self.initAbout)
	def initImporting(self):
		self.importing = Importing()
		self.importing.show()
	def initExporting(self):
		self.exporting = Exporting()
		self.exporting.show()
	def sendToSysTray(self):
		self.systray = QtGui.QSystemTrayIcon(QtGui.QIcon(APP_ICON), self)
		#
		systray_menu = QtGui.QMenu()
		showAction = systray_menu.addAction('Show')
		showAction.triggered.connect(self.appear)
		#
		systray_menu.addSeparator()
		#
		exitAction = systray_menu.addAction('Exit')
		exitAction.triggered.connect(self.exitApp)
		#
		self.systray.setContextMenu(systray_menu)
		self.systray.show()
		self.hide()
	def appear(self):
		self.show()
		self.systray.hide()
	def exitApp(self):
		sys.exit()
	def initBookmarking(self):
		link = unicode(self.link_input.text()).encode('utf-8')
		# Making sure that input is not blank
		if link == '':
			msg_box = QtGui.QMessageBox.critical(self,  'Error',  'You did not enter a link to bookmark!',  QtGui.QMessageBox.Ok)
			return
		# Getting the abs http
		link = functions.abs_http(link)
		# Check if link is already exist
		if link in db_handler.all_urls():
				msg_box = QtGui.QMessageBox.critical(self,  'Error',  'Link already exists and bookmarked.',  QtGui.QMessageBox.Ok)
				return
		# Adding bookmark
		title = unicode(self.title_input.text()).encode('utf-8')
		description = unicode(self.description_input.text()).encode('utf-8')
		folder = unicode(self.folder_input.currentText()).encode('utf-8')
		preview = None
		date_time = time.strftime("%A, %d/%m/%Y %H:%M %p")
		if title == '':
			# Make mouse busy
			busy_mouse()
			self.statusBar().setStyleSheet('font: bold; color: red;')
			self.statusBar().showMessage('Status: Extracing title from link ...')	
			#
			try:				
				title = functions.extract_title(link)
				self.title_input.setText(title)
			except:
				# Restore mouse shape
				reset_mouse()
				self.statusBar().showMessage('Status: Ready')
				self.statusBar().setStyleSheet('font: bold; color: green;')
				self.link_input.setText('')
				msg_box = QtGui.QMessageBox.critical(self,  'Error',  'Error while opening the link. Make sure you entered a correct link.',  QtGui.QMessageBox.Ok)	
				QtGui.QApplication.restoreOverrideCursor()
				self.statusBar().showMessage('Status: Ready')
				self.statusBar().setStyleSheet('font: bold; color: green;')
				return
		bookmark_process = db_handler.add_bookmark(link, title, description, folder, preview, date_time)
		# Restore mouse shape
		QtGui.QApplication.restoreOverrideCursor()
		self.statusBar().showMessage('Status: Ready')
		self.statusBar().setStyleSheet('font: bold; color: green;')
		# -----------------------------
		if bookmark_process == True:
				msg_box = QtGui.QMessageBox.information(self,  'Notification',  'Link bookmarked successfully.',  QtGui.QMessageBox.Ok)
				self.reset_inputs()
		return
	def reset_inputs(self):
		self.link_input.setText('')
		self.title_input.setText('')
		self.description_input.setText('')
		self.folder_input.setCurrentIndex(0)
	def initViewBookmarks(self):
		self.view_list = ViewBookmarks()
		self.view_list.show()
		# For updating folders list if user deleted one
		self.connect(self.view_list, QtCore.SIGNAL('ReListFolders'), partial(self.set_folders_list))
	def paste_from_clipboard(self):
		clipboard = QtGui.QApplication.clipboard()
		clipboard_text = clipboard.text()
		self.link_input.setText(clipboard_text)
	def initNewFolder(self):
		self.newfolder = NewFolder()
		self.newfolder.show()
		self.connect(self.newfolder, QtCore.SIGNAL('FolderName'), partial(self.CreateNewFolder))
	def initAbout(self):
		self.handle_about = About()
		self.handle_about.show()
	def CreateNewFolder(self, folder_name):
		if db_handler.add_folder(folder_name) == True: # add folder to the database
			try:
				self.folder_input.addItem(unicode(folder_name)) # add folder to input list

			except Exception, e:
				print e
			self.folders_names = db_handler.folders_names()
class ViewBookmarks(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		self.resize(660,380)
		self.setWindowTitle('Bookmarks List')
		self.move(QtGui.QApplication.desktop().screen().rect().center()- self.rect().center()) # set position to center of screen
		self.bookmarks_info = {}
		self.bookmarks_viewer()
	def bookmarks_viewer(self):
		#
		self.viewer_cont = QtGui.QTreeWidget(self)
		self.viewer_cont.resize(450,300)
		self.viewer_cont.move(20,40)
		self.viewer_cont.setHeaderLabels(['Bookmarks Folders'])
		self.viewer_cont.setAlternatingRowColors(True)
		self.viewer_cont.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		#
		self.viewer_cont.header().setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerItem)
		self.viewer_cont.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.viewer_cont.header().setStretchLastSection(False)
		self.viewer_cont.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.viewer_cont.header().setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		#
		self.viewer_cont.setCursor(QtCore.Qt.BusyCursor)
		#
		self.viewer_cont.unsetCursor()
		self.viewer_cont.expandAll()
		self.viewer_cont.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.connect(self.viewer_cont, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menu)
		# Statistics 
		self.stat = QtGui.QGroupBox('Statistics', self)
		self.stat.setStyleSheet('QGroupBox{font: bold}')
		self.stat.move(480,60)
		self.stat.resize(150,90)

		self.folders_num = QtGui.QLabel('Folders count: \t%d'%(len(db_handler.list_all_bookmarks())), self.stat)
		self.folders_num.move(20,30)
		self.bookmarks_num = QtGui.QLabel('Bookmarks count: \t%d'%(len(db_handler.all_urls())), self.stat)
		self.bookmarks_num.move(20,50)

		# Expand & Collapse Buttons
		self.expand_btn = QtGui.QPushButton('Expand Bookmarks ', self)
		self.expand_btn.setStyleSheet('padding: 5px 10px;')
		self.expand_btn.move(500,260)
		self.expand_btn.clicked.connect(self.viewer_cont.expandAll)
		#
		self.collapse_btn = QtGui.QPushButton('Collapse Bookmarks', self)
		self.collapse_btn.move(500,300)
		self.collapse_btn.setStyleSheet('padding: 5px 10px;')
		self.collapse_btn.clicked.connect(self.viewer_cont.collapseAll)
		#
		self.viewer_cont.itemDoubleClicked.connect(self.OpenLink)
		#
		self.setbookmarks = self.set_bookmarks()

	def set_bookmarks(self):
		# Separating this in a function for using it to refresh the list
		self.viewer_cont.clear()
		all_bookmarks = db_handler.list_all_bookmarks()
		#
		for folder, bookmark_info in all_bookmarks.items():
			# Get folder name
			folder_header = QtGui.QTreeWidgetItem(self.viewer_cont,[folder.replace('_', ' ')])
			for each in bookmark_info:
				link = QtGui.QTreeWidgetItem(folder_header, [each[0]])
				link.setTextColor(0, QtGui.QColor(54,54,54))
				link.setToolTip(0, u'<font color=red><b>Title:</b><br></font> {0}<br> <font color=red><b>Description:</b><br></font>{1}<br> <font color=red><b>Date/Time:</b><br></font>{2}<br>'.format(unicode(each[1]), unicode(each[2]), unicode(each[4])))
				link.setExpanded(True)
				self.bookmarks_info[each[0]] = (each[0], each[1], each[2], each[3], each[4])
				QtGui.QTreeWidgetItem.parent(link).text(0)
		self.viewer_cont.expandAll() # For expanding all the bookmarks in QTreeWidget
		self.viewer_cont.setStyleSheet('QTreeWidget{font-size: 13px;}')
		self.folders_num.setText('Folders count: \t%d'%(len(db_handler.list_all_bookmarks())))
		self.bookmarks_num.setText('Bookmarks count: \t%d'%(len(db_handler.all_urls())))

	def on_context_menu(self, point):
		clicked_item = unicode(self.viewer_cont.currentItem().text(0))
		clicked_item = clicked_item.replace(' ', '_')
		self.menu = QtGui.QMenu(self)
		#
		self.selected_items = self.viewer_cont.selectedItems()

		if len(self.selected_items) > 1:
			# Delete Links
			delete_links = QtGui.QAction('Delete Links', self.menu)
			self.menu.addAction(delete_links)
			delete_links.triggered.connect(self.deleteLinks)
			# Move to Sub-menu
			self.move_menu = QtGui.QMenu(self.menu)
			self.move_menu.setTitle("Move to")
			self.menu.addMenu(self.move_menu)

			for each in db_handler.folders_names():
				each = each.replace('_', ' ')
				move_action = QtGui.QAction(each, self.move_menu)
				self.move_menu.addAction(move_action)
			self.move_menu.triggered.connect(self.moveLinks)
		####################################
		elif clicked_item in db_handler.folders_names():
			# Rename Folder
			rename_folder = QtGui.QAction('Rename Folder', self.menu)
			self.menu.addAction(rename_folder)
			rename_folder.triggered.connect(self.renameFolder)
			# Delete Folder
			delete_folder = QtGui.QAction('Delete Folder', self.menu)
			self.menu.addAction(delete_folder)
			delete_folder.triggered.connect(self.deleteFolder)
		else:
			# Open Link
			open_link = QtGui.QAction('Open Link', self.menu)
			self.menu.addAction(open_link)
			open_link.triggered.connect(self.OpenLink)
			# Copy Link
			copy_link = QtGui.QAction('Copy Link', self.menu)
			self.menu.addAction(copy_link)
			copy_link.triggered.connect(self.copy)
			# Delete Link
			delete_link = QtGui.QAction('Delete Link', self.menu)
			self.menu.addAction(delete_link)
			delete_link.triggered.connect(self.delete)
			# Update Info
			update_info = QtGui.QAction('Update Bookmark', self.menu)
			self.menu.addAction(update_info)
			update_info.triggered.connect(self.update)
			# Move to Sub-menu
			self.move_menu = QtGui.QMenu(self.menu)
			self.move_menu.setTitle("Move to")
			self.menu.addMenu(self.move_menu)

			for each in db_handler.folders_names():
				each = each.replace('_', ' ')
				move_action = QtGui.QAction(each, self.move_menu)
				self.move_menu.addAction(move_action)
			self.move_menu.triggered.connect(self.moveTo)
		# Execution of context menu
		self.menu.exec_(self.viewer_cont.mapToGlobal(point))
	def renameFolder(self):
		folder_name = str(self.viewer_cont.currentItem().text(0))
		if folder_name == 'General':
			msg_box = QtGui.QMessageBox.critical(self,  'Error',  'General folder can not be renamed.',  QtGui.QMessageBox.Ok)
			return
		self.renaming = RenameFolder(folder_name)
		self.renaming.show()
		self.connect(self.renaming, QtCore.SIGNAL('NewName'), partial(self.RenameFolderName))
	def RenameFolderName(self, names):
		old_name = unicode(names[0]).encode('utf-8').replace(' ', '_')
		new_name = unicode(names[1]).encode('utf-8').replace(' ', '_')
		set_new_name = db_handler.rename_folder(old_name, new_name)
		if set_new_name == True:
			self.set_bookmarks()
			self.emit(QtCore.SIGNAL('ReListFolders'), '')
		else:
			msg_box = QtGui.QMessageBox.critical(self,  'Error',  'Error has been occured.',  QtGui.QMessageBox.Ok)
		return

	def deleteFolder(self):
		current_item = self.viewer_cont.currentItem()
		folder_name = unicode(current_item.text(0)).encode('utf-8')
		# ----------------------------------------
		if folder_name == 'General':
			msg_box = QtGui.QMessageBox.critical(self,  'Error',  'General folder can not be deleted.',  QtGui.QMessageBox.Ok)
			return
		# ----------------------------------------
		ask_msg_box = QtGui.QMessageBox.question(self,  'Delete Folder',  u'Are you sure you want to delete folder \" %s \" ?' %unicode(folder_name),  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		if ask_msg_box == QtGui.QMessageBox.Yes:
			folder_name = folder_name.replace(' ', '_')
			deleting_process = db_handler.delete_folder(folder_name)
			if deleting_process == True:
				self.set_bookmarks() # refresh view list
				self.emit(QtCore.SIGNAL('ReListFolders'))
			else:
				msg_box = QtGui.QMessageBox.critical(self,  'Error', str(deleting_process) ,  QtGui.QMessageBox.Ok)
		else:
			return
	def moveTo(self):
		link = str(self.viewer_cont.currentItem().text(0))
		src_folder = self.viewer_cont.currentItem().parent().text(0)
		dst_fodler = self.move_menu.sender().text()
		if src_folder == dst_fodler:
			msg_box = QtGui.QMessageBox.critical(self,  'Error', u'Bookmark is already in "%s" folder.' %unicode(dst_fodler),  QtGui.QMessageBox.Ok)
			return
		# MOVE TO
		moving_process = db_handler.move_to_folder(link, src_folder, dst_fodler)
		if moving_process == True:
			self.set_bookmarks()
			return
		else:
			msg_box = QtGui.QMessageBox.critical(self,  'Error', str(moving_process) ,  QtGui.QMessageBox.Ok)
	def update(self):
		link = str(self.viewer_cont.currentItem().text(0))
		self.old_url = unicode(link).encode('utf-8')
		title = self.bookmarks_info[link][1]
		description = self.bookmarks_info[link][2]
		self.folder = unicode(self.viewer_cont.currentItem().parent().text(0)).encode('utf-8')
		date_time = self.bookmarks_info[link][4]
		self.showUpdateInfo = UpdateInfo(link, title, description, self.folder, date_time)
		self.showUpdateInfo.show()
		self.connect(self.showUpdateInfo, QtCore.SIGNAL('UpdateInfo'), partial(self.updating))
	def updating(self, info):
		deleting_process = db_handler.delete_bookmark(unicode(self.folder), self.old_url)
		adding_bookmark = db_handler.update_bookmark(*info)
		self.set_bookmarks()
	def copy(self):
		current_item = unicode(self.viewer_cont.currentItem().text(0))
		clipboard = QtGui.QApplication.clipboard()
		clipboard_text = clipboard.setText(current_item)
	
	def deleteLinks(self):
		busy_mouse()
		for each in self.selected_items:
			link = unicode(each.text(0)).encode('utf-8')
			folder = each.parent().text(0)
			deleting_process = db_handler.delete_bookmark(unicode(folder), str(link))	
		reset_mouse()
		self.set_bookmarks()
	def delete(self):
		current_item = self.viewer_cont.currentItem()
		link = unicode(current_item.text(0)).encode('utf-8')
		folder = self.viewer_cont.currentItem().parent().text(0)
		deleting_process = db_handler.delete_bookmark(unicode(folder), str(link))
		if deleting_process == True:
			self.set_bookmarks()
		else:
			msg_box = QtGui.QMessageBox.critical(self,  'Error', deleting_process ,  QtGui.QMessageBox.Ok)
		return
	def moveLinks(self):
		#---------------------------------------
		conflict_list = []
		busy_mouse()
		for each in self.selected_items:
			link = unicode(each.text(0))
			src_folder = self.viewer_cont.currentItem().parent().text(0)
			dst_fodler = self.move_menu.sender().text()

			if src_folder == dst_fodler:
				reset_mouse()
				conflict_list.append(link)
			else:
				# Moving process
				moving_process = db_handler.move_to_folder(link, src_folder, dst_fodler)
		#
		if conflict_list != []:
			msg_box = QtGui.QMessageBox.critical(self,  'Error', u'Faild to move: <br>%s' %unicode("<br>".join(conflict_list)),  QtGui.QMessageBox.Ok)
		reset_mouse()
		self.set_bookmarks()
		return
	def OpenLink(self):
		clicked_item = self.viewer_cont.currentItem().text(0)
		# I don't know how the couple of lines are working,
		# but they do exactly what I want, so deal with it :D
		if self.viewer_cont.currentItem().parent():
			#print self.viewer_cont.currentItem().parent().type()
			webbrowser.open_new_tab(clicked_item)

class Exporting(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		self.choose = QtGui.QGroupBox('Choose', self)
		self.choose.move(20,20)
		self.choose.resize(200,100)
		self.all_bookmarks_rbtn = QtGui.QRadioButton('All Bookmarks', self.choose)
		self.all_bookmarks_rbtn.move(20,30)
		#
		self.one_folder_rbtn = QtGui.QRadioButton('Folder:', self.choose)
		self.one_folder_rbtn.move(20,60)
		#
		self.folders_list = QtGui.QComboBox(self.choose)
		self.folders_list.move(80,60)
		self.folders_list.setStyleSheet('border: 1px none black')
		self.folders_list.resize(100,20)
		folders_names = db_handler.folders_names()
		for each in folders_names:
			self.folders_list.addItem(each)
		self.folders_list.activated.connect(self.changeRB)
		#
		self.export_btn = QtGui.QPushButton('Export', self)
		self.export_btn.move(80,130)
		self.export_btn.clicked.connect(self.exporting)
		#
		self.resize(240,170)
		self.setWindowTitle('Export Bookmarks')
	def changeRB(self):
		self.one_folder_rbtn.setChecked(True)
	def exporting(self):
		if self.all_bookmarks_rbtn.isChecked() == True:
			export_all_bookmarks = functions.export_all_folders()
			if export_all_bookmarks == True:
				msg_box = QtGui.QMessageBox.information(self,  'Notification',  'All bookmarks are exported successfully.\nCheck file: \"All Bookmarks.html\".',  QtGui.QMessageBox.Ok)
			else:
				msg_box = QtGui.QMessageBox.critical(self,  'Error',  'Error has been occured. Try again!',  QtGui.QMessageBox.Ok)	
				return
		elif self.one_folder_rbtn.isChecked() == True:
			current_item = unicode(self.folders_list.currentText()).encode('utf-8')
			# One argument is to define that we are gonna import one FOLDER
			export_folder = functions.export_folder(current_item, 'one')
			if export_folder == True:
				msg_box = QtGui.QMessageBox.information(self,  'Notification',  u'All bookmarks are exported successfully.\nCheck file: \"%s.html\".' %unicode(current_item),  QtGui.QMessageBox.Ok)
		else:
			msg_box = QtGui.QMessageBox.critical(self,  'Error',  'You have to choose what to import.',  QtGui.QMessageBox.Ok)	
		self.close()
class NewFolder(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		self.newfolder_name_label = QtGui.QLabel('Folder name:', self)
		self.newfolder_name_label.move(20,20)
		self.newfolder_name_input = QtGui.QLineEdit(self)
		self.newfolder_name_input.move(100,20)
		self.create_button = QtGui.QPushButton('Create', self)
		self.create_button.move(250,20)
		self.create_button.clicked.connect(self.createFolder)
		self.resize(350,60)
		self.setWindowTitle('New Folder')
	def createFolder(self):
		foldername = self.newfolder_name_input.text()
		#print foldername
		self.hide()
		self.emit(QtCore.SIGNAL('FolderName'), foldername)
		return foldername

class RenameFolder(QtGui.QDialog):
	def __init__(self, folder_name):
		QtGui.QDialog.__init__(self)
		self.old_name = folder_name
		#
		self.new_name_label = QtGui.QLabel('New name:', self)
		self.new_name_label.move(20,20)
		self.new_name_input = QtGui.QLineEdit(self)
		self.new_name_input.move(100,20)
		self.rename_button = QtGui.QPushButton('Rename', self)
		self.rename_button.move(250,20)
		self.rename_button.clicked.connect(self.renameFolder)
		self.resize(350,60)
		self.setWindowTitle('Rename Folder')
	def renameFolder(self):
		new_name = unicode(self.new_name_input.text())
		self.hide()
		self.emit(QtCore.SIGNAL('NewName'), (self.old_name, new_name))

class UpdateInfo(QtGui.QDialog):
	def __init__(self, link, title, description, folder, date_time):
		QtGui.QDialog.__init__(self)
		self.resize(400,180)
		self.setWindowTitle('Update Bookmark')
		self.folder = folder
		self.date_time = date_time
		#
		self.link_label = QtGui.QLabel('Link:', self)
		self.link_label.move(20,40)
		self.link_input = QtGui.QLineEdit(link ,self)
		self.link_input.move(90,40)
		self.link_input.resize(280,20)


		self.title_label = QtGui.QLabel('Title:', self)
		self.title_label.move(20,70)
		self.title_input = QtGui.QLineEdit(title ,self)
		self.title_input.move(90,70)
		self.title_input.resize(280,20)


		self.description_label = QtGui.QLabel('Description:', self)
		self.description_label.move(20,100)
		self.description_input = QtGui.QLineEdit(description ,self)
		self.description_input.move(90,100)
		self.description_input.resize(280,20)

		self.update_button = QtGui.QPushButton('Update',self)
		self.update_button.move(270,140)
		self.update_button.clicked.connect(self.update_info)
	def update_info(self):
		link = unicode(self.link_input.text()).encode('utf-8')
		title = unicode(self.title_input.text()).encode('utf-8')
		description = unicode(self.description_input.text()).encode('utf-8')
		folder = unicode(self.folder).encode('utf-8')
		date_time = unicode(self.date_time).encode('utf-8')
		preview = None
		self.emit(QtCore.SIGNAL('UpdateInfo'), (folder, link, title, description, preview, date_time ))
		self.hide()

class Importing(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		self.setWindowTitle('Importing')
		self.setFixedSize(260,180)
		#
		self.checks = QtGui.QGroupBox('Import from', self)
		self.checks.move(20,20)
		self.checks.resize(220,110)
		self.chrome = QtGui.QCheckBox('Google Chrome',self.checks)
		self.chrome.move(20,30)

		self.firefox = QtGui.QCheckBox('Mozilla Firefox', self.checks)
		self.firefox.move(20,50)

		self.ie = QtGui.QCheckBox('Internet Explorer? \t\t- No man! :/', self.checks)
		self.ie.move(20,70)
		self.ie.setEnabled(False)

		self.import_btn = QtGui.QPushButton('Import', self)
		self.import_btn.move(100,145)
		self.import_btn.clicked.connect(self.importing)
	def importing(self):
		if self.chrome.isChecked() | self.firefox.isChecked() | self.ie.isChecked() == False:
			msg_box = QtGui.QMessageBox.critical(self,  'Error', 'You have to choose what browser to import from' ,  QtGui.QMessageBox.Ok)
			return
		# ------------------------------------
		if self.chrome.isChecked():
			chrome_bookmarks = functions.chrome_bookmarks()
			busy_mouse()
			if type(chrome_bookmarks) == list:
				for each in chrome_bookmarks:
					url = each[0]
					title = each[1]
					date_time = each[2]
					if url not in db_handler.all_urls():
						adding_bookmark = db_handler.add_bookmark(url, title, '', 'General', None, date_time)
				reset_mouse()
			else:
				reset_mouse()
				msg_box = QtGui.QMessageBox.critical(self,  'Error', '%s'%chrome_bookmarks ,  QtGui.QMessageBox.Ok)
				return
		# ------------------------------------ 
		if self.firefox.isChecked():
			firefox_bookmarks = functions.firefox_bookmarks()
			busy_mouse()
			if type(firefox_bookmarks) == list:
				for each in firefox_bookmarks:
					url = each[0]
					title = each[1]
					date_time = each[2]
					if url not in db_handler.all_urls():
						adding_bookmark = db_handler.add_bookmark(url, title, '', 'General', None, date_time)
				reset_mouse()
			else:
				reset_mouse()
				msg_box = QtGui.QMessageBox.critical(self,  'Error', '%s'%firefox_bookmarks ,  QtGui.QMessageBox.Ok)
				return
		# Job is finished 
		msg_box = QtGui.QMessageBox.information(self,  'Notification', 'All bookmarks are imported successfully.',  QtGui.QMessageBox.Ok)
		self.close()
			
			
class About(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		self.resize(300,460)
		self.setWindowTitle('About')
		#
		self.about_container = QtGui.QGroupBox('About', self)
		self.about_container.setStyleSheet('QGroupBox{font-weight: bold; color: red}')
		self.about_container.move(20,20)
		self.about_container.resize(260,300)

		self.about_data = """ <b>BookmarkMe</b><br> <font color="red">version:</font> 1.0 <br><br>
BookmarkMe is an application which gives you<br>
the ability to bookmark and organize all your<br>
favorite links in separated folders according<br>
to your desires. In addition, it has a quick<br>
search feature, so you can search for a certain<br>
bookmarked link by its title or the url itself<br><br>
You can also export your bookmarks to a nice<br>
formatted html file, so you can share them with<br>
your friends.<br><br>
And you can import links from browser either,<br>
(Google Chrome & Mozilla Firefox are the only<br>
supported for now)<br><br>
If you have any feedback you want to give us,<br>
or you want to contact, feel free to do so.
		"""
		self.about_label = QtGui.QLabel(self.about_data, self.about_container)
		self.about_label.move(20,20)
		#
		self.contact_container = QtGui.QGroupBox('Contact',self)
		self.contact_container.setStyleSheet('QGroupBox{font-weight: bold; color: red}')
		self.contact_container.move(20,330)
		self.contact_container.resize(260,110)
	
		#
		self.twitter = QtGui.QLabel('<b>Follow: <a style="text-decoration: none" href="http://twitter.com/abdelrahmanmoez">Twitter</a>', self.contact_container)
		self.twitter.move(20,20)
		self.twitter.linkActivated.connect(self.twitterOpener)
		#
		self.facebook = QtGui.QLabel('<b>Like:   <a style="text-decoration: none" href="https://www.facebook.com/abdelrahman.moez"> Facebook </a>', self.contact_container)
		self.facebook.move(20,40)
		self.facebook.linkActivated.connect(self.facebookOpener)
		#
		self.github = QtGui.QLabel('<b> Follow: <a style="text-decoration: none" href="https://github.com/Hydr4/"> Github </a>', self.contact_container)
		self.github.move(20,60)
		self.github.linkActivated.connect(self.githubOpener)
		#
		self.mail = QtGui.QLabel('<b> Email: <a style="text-decoration: none" href="mailto:abdelrahman.moez@gmail.com"> abdelrahman.moez@gmail.com </a><b>', self.contact_container)
		self.mail.move(20,80)
		self.mail.linkActivated.connect(self.mailOpener)
	def twitterOpener(self):
		webbrowser.open('http://twitter.com/abdelrahmanmoez')
	def facebookOpener(self):
		webbrowser.open('https://www.facebook.com/abdelrahman.moez')
	def githubOpener(self):
		webbrowser.open('https://github.com/Hydr4/')
	def mailOpener(self):
		webbrowser.open('mailto:abdelrahman.moez@gmail.com')
	#

def main():
	app = QtGui.QApplication(sys.argv)
	foo = UI()
	foo.show()
	sys.exit(app.exec_())
if __name__ == '__main__':
	main()

