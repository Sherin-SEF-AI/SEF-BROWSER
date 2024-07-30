import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QLineEdit, QPushButton, QHBoxLayout, QAction, 
                             QMenu, QTabWidget, QFileDialog, QMessageBox, 
                             QInputDialog, QDialog, QListWidget)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QClipboard


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the main components
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.update_current_tab)

        self.url_bars = {}  # Dictionary to map browsers to their URL bars
        self.search_bars = {}
        self.history = {}
        self.bookmarks = {}
        self.incognito_mode = {}
        self.custom_home_page = 'https://www.google.com'

        self.url_bar = QLineEdit()  # Initialize a single URL bar for the main window
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setPlaceholderText('Enter URL and press Enter')

        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.perform_search)
        self.search_bar.setPlaceholderText('Search...')

        self.home_button = QPushButton('Home')
        self.home_button.clicked.connect(self.navigate_home)
        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.current_tab_back)
        self.forward_button = QPushButton('Forward')
        self.forward_button.clicked.connect(self.current_tab_forward)
        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.current_tab_refresh)
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.current_tab_stop)
        self.zoom_in_button = QPushButton('Zoom In')
        self.zoom_in_button.clicked.connect(self.current_tab_zoom_in)
        self.zoom_out_button = QPushButton('Zoom Out')
        self.zoom_out_button.clicked.connect(self.current_tab_zoom_out)
        self.inspect_button = QPushButton('Inspect')
        self.inspect_button.clicked.connect(self.inspect_page)
        self.add_tab_button = QPushButton('+')
        self.add_tab_button.clicked.connect(self.init_tab)
        self.copy_url_button = QPushButton('Copy URL')
        self.copy_url_button.clicked.connect(self.copy_url)

        # Layout setup
        nav_bar = QHBoxLayout()
        nav_bar.addWidget(self.back_button)
        nav_bar.addWidget(self.forward_button)
        nav_bar.addWidget(self.refresh_button)
        nav_bar.addWidget(self.stop_button)
        nav_bar.addWidget(self.home_button)
        nav_bar.addWidget(self.zoom_in_button)
        nav_bar.addWidget(self.zoom_out_button)
        nav_bar.addWidget(self.inspect_button)
        nav_bar.addWidget(self.add_tab_button)
        nav_bar.addWidget(self.url_bar)
        nav_bar.addWidget(self.copy_url_button)
        nav_bar.addStretch()  # Add stretchable space to center the search bar
        nav_bar.addWidget(self.search_bar)

        layout = QVBoxLayout()
        layout.addLayout(nav_bar)
        layout.addWidget(self.tab_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set up menu bar
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu('File')

        new_tab_action = QAction('New Tab', self)
        new_tab_action.triggered.connect(self.init_tab)
        file_menu.addAction(new_tab_action)

        bookmarks_menu = self.menu_bar.addMenu('Bookmarks')
        add_bookmark_action = QAction('Add Bookmark', self)
        add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(add_bookmark_action)
        view_bookmarks_action = QAction('View Bookmarks', self)
        view_bookmarks_action.triggered.connect(self.view_bookmarks)
        bookmarks_menu.addAction(view_bookmarks_action)

        history_menu = self.menu_bar.addMenu('History')
        view_history_action = QAction('View History', self)
        view_history_action.triggered.connect(self.view_history)
        history_menu.addAction(view_history_action)
        clear_history_action = QAction('Clear History', self)
        clear_history_action.triggered.connect(self.clear_history)
        history_menu.addAction(clear_history_action)

        settings_menu = self.menu_bar.addMenu('Settings')
        incognito_mode_action = QAction('Toggle Incognito Mode', self)
        incognito_mode_action.triggered.connect(self.toggle_incognito_mode)
        settings_menu.addAction(incognito_mode_action)
        custom_home_action = QAction('Set Custom Home Page', self)
        custom_home_action.triggered.connect(self.set_custom_home_page)
        settings_menu.addAction(custom_home_action)

        view_menu = self.menu_bar.addMenu('View')
        clear_cache_action = QAction('Clear Cache and Cookies', self)
        clear_cache_action.triggered.connect(self.clear_cache_and_cookies)
        view_menu.addAction(clear_cache_action)

        # Window settings
        self.setWindowTitle('SEF-BROWSER')
        self.setWindowIcon(QIcon('browser_icon.png'))
        self.showMaximized()

        self.init_tab()  # Initialize with one tab

    def init_tab(self):
        new_browser = QWebEngineView()
        new_browser.setUrl(QUrl(self.custom_home_page))
        new_browser.urlChanged.connect(lambda qurl, nb=new_browser: self.update_url_bar(nb, qurl))
        new_browser.loadFinished.connect(self.handle_load_finished)

        tab_index = self.tab_widget.addTab(new_browser, f"Tab {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(tab_index)

        self.url_bars[new_browser] = self.url_bar  # Map the new browser to the URL bar

        # Initialize other mappings
        self.search_bars[new_browser] = self.search_bar
        self.history[new_browser] = []
        self.bookmarks[new_browser] = []
        self.incognito_mode[new_browser] = False

    def handle_load_finished(self, ok):
        if ok:
            browser = self.tab_widget.currentWidget()
            if browser:
                url = browser.url().toString()
                # Update the history with the new URL
                self.history[browser].append(url)
                # Update the URL bar
                self.update_url_bar(browser, browser.url())
            else:
                QMessageBox.warning(self, 'Load Error', 'Failed to load the page.')
        else:
            QMessageBox.warning(self, 'Load Error', 'Page failed to load.')

    def update_url_bar(self, browser, qurl):
        if browser in self.url_bars:
            self.url_bars[browser].setText(qurl.toString())

    def navigate_to_url(self):
        browser = self.tab_widget.currentWidget()
        url = self.url_bar.text()
        browser.setUrl(QUrl(url))

    def perform_search(self):
        browser = self.tab_widget.currentWidget()
        query = self.search_bar.text()
        search_url = f'https://www.google.com/search?q={query}'
        browser.setUrl(QUrl(search_url))

    def navigate_home(self):
        for browser in self.tab_widget.findChildren(QWebEngineView):
            if not self.incognito_mode[browser]:
                browser.setUrl(QUrl(self.custom_home_page))

    def current_tab_back(self):
        self.tab_widget.currentWidget().back()

    def current_tab_forward(self):
        self.tab_widget.currentWidget().forward()

    def current_tab_refresh(self):
        self.tab_widget.currentWidget().reload()

    def current_tab_stop(self):
        self.tab_widget.currentWidget().stop()

    def current_tab_zoom_in(self):
        self.tab_widget.currentWidget().setZoomFactor(self.tab_widget.currentWidget().zoomFactor() + 0.1)

    def current_tab_zoom_out(self):
        self.tab_widget.currentWidget().setZoomFactor(self.tab_widget.currentWidget().zoomFactor() - 0.1)

    def inspect_page(self):
        browser = self.tab_widget.currentWidget()
        if browser:
            inspector = browser.page().webInspector()
            inspector.show()
        else:
            QMessageBox.warning(self, 'Inspect Error', 'No page to inspect.')

    def add_bookmark(self):
        browser = self.tab_widget.currentWidget()
        if browser:
            url = browser.url().toString()
            title = browser.page().title()
            self.bookmarks[browser].append((title, url))
            QMessageBox.information(self, 'Bookmark Added', f'Bookmark added: {title}')

    def view_bookmarks(self):
        browser = self.tab_widget.currentWidget()
        if browser and self.bookmarks[browser]:
            bookmarks = [f"{title} ({url})" for title, url in self.bookmarks[browser]]
            bookmark_dialog = QDialog(self)
            bookmark_list = QListWidget()
            bookmark_list.addItems(bookmarks)
            layout = QVBoxLayout()
            layout.addWidget(bookmark_list)
            bookmark_dialog.setLayout(layout)
            bookmark_dialog.setWindowTitle('Bookmarks')
            bookmark_dialog.exec_()
        else:
            QMessageBox.information(self, 'No Bookmarks', 'No bookmarks to display.')

    def view_history(self):
        browser = self.tab_widget.currentWidget()
        if browser and self.history[browser]:
            history = self.history[browser]
            history_dialog = QDialog(self)
            history_list = QListWidget()
            history_list.addItems(history)
            layout = QVBoxLayout()
            layout.addWidget(history_list)
            history_dialog.setLayout(layout)
            history_dialog.setWindowTitle('History')
            history_dialog.exec_()
        else:
            QMessageBox.information(self, 'No History', 'No history to display.')

    def clear_history(self):
        browser = self.tab_widget.currentWidget()
        self.history[browser].clear()
        QMessageBox.information(self, 'History Cleared', 'Browsing history has been cleared.')

    def toggle_incognito_mode(self):
        browser = self.tab_widget.currentWidget()
        if browser:
            if not self.incognito_mode[browser]:
                # Switch to incognito mode
                new_profile = QWebEngineProfile('IncognitoProfile', browser.page().profile().parent())
                browser.setPage(QWebEnginePage(new_profile, browser))
                self.incognito_mode[browser] = True
                QMessageBox.information(self, 'Incognito Mode', 'Incognito mode enabled.')
            else:
                # Switch back to regular mode
                default_profile = QWebEngineProfile.defaultProfile()
                browser.setPage(QWebEnginePage(default_profile, browser))
                self.incognito_mode[browser] = False
                QMessageBox.information(self, 'Incognito Mode', 'Incognito mode disabled.')

    def set_custom_home_page(self):
        url, ok = QInputDialog.getText(self, 'Set Home Page', 'Enter the URL for the custom home page:')
        if ok and url:
            self.custom_home_page = url
            QMessageBox.information(self, 'Home Page Set', f'Custom home page set to {url}')

    def clear_cache_and_cookies(self):
        for browser in self.tab_widget.findChildren(QWebEngineView):
            browser.page().profile().clearHttpCache()
            browser.page().profile().clearAllVisitedLinks()
        QMessageBox.information(self, 'Cache Cleared', 'Cache and cookies have been cleared')

    def copy_url(self):
        browser = self.tab_widget.currentWidget()
        if browser:
            clipboard = QApplication.clipboard()
            clipboard.setText(browser.url().toString())
            QMessageBox.information(self, 'URL Copied', 'URL copied to clipboard.')

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            tab = self.tab_widget.widget(index)
            self.tab_widget.removeTab(index)
            tab.deleteLater()
        else:
            QMessageBox.warning(self, 'No Tabs', 'Cannot close the last tab.')

    def update_current_tab(self):
        browser = self.tab_widget.currentWidget()
        if browser:
            self.update_url_bar(browser, browser.url())
        else:
            self.url_bar.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())

