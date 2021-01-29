# -*- coding: utf-8 -*-


from PySide2 import QtCore, QtGui, QtWidgets
from qt_material import apply_stylesheet
import requests
import shutil
import sqlite3
import os
from res.logic.waitingspinnerwidget import QtWaitingSpinner
from res.ui.py import beepdl_ui
from res.logic import messages


def init(app, dialog, self):
    connect_to_db(dialog, self)
    load_settings(app, dialog, self)
    self.spinner = QtWaitingSpinner(dialog)
    self.stackedWidget.setCurrentIndex(0)
    self.download_pushButton.setEnabled(False)
    self.select_all_checkBox.setEnabled(False)
    self.artists_tableWidget.setColumnHidden(2, True)
    self.artists_tableWidget.setColumnWidth(0, 200)
    self.files_tableWidget.setColumnHidden(3, True)
    self.files_tableWidget.setColumnHidden(4, True)
    self.songs_pushButton.clicked.connect(
        lambda: goto_songs(dialog, self)
        )
    self.artist_search_pushButton.clicked.connect(
        lambda: fetch_artists(dialog, self)
        )
    self.download_pushButton.clicked.connect(
        lambda: download(dialog, self)
        )
    self.cancel_pushButton.clicked.connect(
        lambda: stop_download(dialog, self)
        )
    self.about_pushButton.clicked.connect(
        lambda: messages.about(dialog)
        )
    self.select_all_checkBox.clicked.connect(
        lambda: select_all(dialog, self)
        )
    self.filter_lineEdit.textChanged.connect(
        lambda: search(dialog, self)
        )
    self.search_pushButton.clicked.connect(
        lambda: goto_search(dialog, self)
        )
    self.settings_pushButton.clicked.connect(
        lambda: goto_settings(dialog, self)
        )
    self.theme_comboBox.currentTextChanged.connect(
        lambda: change_theme(app, dialog, self)
        )
    self.ok_pushButton.clicked.connect(
        lambda: save_settings(dialog, self)
        )
    self.goto_songs_pushButton.clicked.connect(
        lambda: goto_songs(dialog, self, True)
        )
    self.goto_search_pushButton.clicked.connect(
        lambda: goto_search(dialog, self)
        )
    self.persian_checkBox.clicked.connect(
        lambda: show_hide_columns(dialog, self)
        )
    self.english_checkBox.clicked.connect(
        lambda: show_hide_columns(dialog, self)
        )
    self.duration_checkBox.clicked.connect(
        lambda: show_hide_columns(dialog, self)
        )
    self.artists_persian_checkBox.clicked.connect(
        lambda: show_hide_columns(dialog, self)
        )
    self.artists_english_checkBox.clicked.connect(
        lambda: show_hide_columns(dialog, self)
        )
    self.settings_pushButton_1.clicked.connect(
        lambda: goto_settings(dialog, self)
        )
    self.artists_tableWidget.doubleClicked.connect(
        lambda: goto_songs(dialog, self)
        )


def load_settings(app, dialog, self):
    theme = fetch_settings(self, 'theme')
    self.theme_comboBox.setCurrentText(theme)
    apply_stylesheet(app, theme='{}.xml'.format(theme))
    quality = fetch_settings(self, 'quality')
    self.quality_comboBox.setCurrentText(quality)
    artists_table = fetch_settings(self, 'artists_table').split(',')
    if '0' in artists_table:
        self.artists_persian_checkBox.setChecked(True)
    if '1' in artists_table:
        self.artists_english_checkBox.setChecked(True)
    songs_table = fetch_settings(self, 'songs_table').split(',')
    if '0' in songs_table:
        self.persian_checkBox.setChecked(True)
    if '1' in songs_table:
        self.english_checkBox.setChecked(True)
    if '2' in songs_table:
        self.duration_checkBox.setChecked(True)
    show_hide_columns(dialog, self)


def show_hide_columns(dialog, self):
    if self.persian_checkBox.isChecked():
        self.files_tableWidget.setColumnHidden(0, False)
    else:
        self.files_tableWidget.setColumnHidden(0, True)
    if self.english_checkBox.isChecked():
        self.files_tableWidget.setColumnHidden(1, False)
    else:
        self.files_tableWidget.setColumnHidden(1, True)
    if self.duration_checkBox.isChecked():
        self.files_tableWidget.setColumnHidden(2, False)
    else:
        self.files_tableWidget.setColumnHidden(2, True)
    if self.artists_persian_checkBox.isChecked():
        self.artists_tableWidget.setColumnHidden(0, False)
    else:
        self.artists_tableWidget.setColumnHidden(0, True)
    if self.artists_english_checkBox.isChecked():
        self.artists_tableWidget.setColumnHidden(1, False)
    else:
        self.artists_tableWidget.setColumnHidden(1, True)


def save_settings(dialog, self):
    quality = self.quality_comboBox.currentText()
    theme = self.theme_comboBox.currentText()
    artists_flags = []
    songs_flags = []
    if self.persian_checkBox.isChecked():
        songs_flags.append('0')
    if self.english_checkBox.isChecked():
        songs_flags.append('1')
    if self.duration_checkBox.isChecked():
        songs_flags.append('2')
    if self.artists_persian_checkBox.isChecked():
        artists_flags.append('0')
    if self.artists_english_checkBox.isChecked():
        artists_flags.append('1')
    artists_flags = ','.join(artists_flags)
    songs_flags = ','.join(songs_flags)
    update_settings(self, 'quality', quality)
    update_settings(self, 'theme', theme)
    update_settings(self, 'artists_table', artists_flags)
    update_settings(self, 'songs_table', songs_flags)
    messages.info(
        dialog,
        'Info',
        'Your settings have been saved.'
        )


def goto_search(dialog, self):
    self.stackedWidget.setCurrentIndex(0)


def goto_settings(dialog, self):
    self.stackedWidget.setCurrentIndex(2)


def goto_songs(dialog, self, from_settings=False):
    if from_settings:
        self.stackedWidget.setCurrentIndex(1)
    else:
        current_row = self.artists_tableWidget.currentRow()
        if current_row != -1:
            self.artist_id = self.artists_tableWidget.item(
                current_row, 2
                ).text()
            fetch_songs(dialog, self)
        else:
            messages.warning(
                dialog,
                'Warning',
                'Please choose an artist.'
            )


def change_theme(app, dialog, self):
    current_theme = self.theme_comboBox.currentText()
    apply_stylesheet(app, theme='{}.xml'.format(current_theme))


def connect_to_db(dialog, self):
    self.conn = sqlite3.connect('res/database')
    self.cur = self.conn.cursor()


def fetch_artists(dialog, self):
    name = self.search_lineEdit.text().strip()
    if name != '':
        self.spinner.start()
        self.artist_search_pushButton.setEnabled(False)
        url = 'https://newapi.beeptunes.com/public/search'
        json = {
            'albumCount': '6',
            'text': name,
            'artistCount': '1000',
            'trackCount': '8'
            }
        self.artists_thread = Response(url, json)
        self.artists_thread.start()
        self.artists_thread.res.connect(
            lambda response: load_artists(dialog, self, response)
            )


def load_artists(dialog, self, response):
    self.spinner.stop()
    self.artist_search_pushButton.setEnabled(True)
    self.artists_tableWidget.setRowCount(0)
    if response != {} and 'artists' in response.keys():
        for artist in response['artists']:
            try:
                if 'english_full_name' not in artist.keys():
                    english = 'Not Provided.'
                else:
                    english = artist['english_full_name']
                if 'full_name_auxiliary' not in artist.keys():
                    persian = 'نا مشخص.'
                else:
                    persian = artist['full_name_auxiliary']
                name_id = [
                    persian,
                    english,
                    artist['id']
                    ]
                row_count = self.artists_tableWidget.rowCount()
                self.artists_tableWidget.insertRow(row_count)
                item = QtWidgets.QTableWidgetItem(name_id[0])
                self.artists_tableWidget.setItem(row_count, 0, item)
                item = QtWidgets.QTableWidgetItem(name_id[1])
                self.artists_tableWidget.setItem(row_count, 1, item)
                item = QtWidgets.QTableWidgetItem(str(name_id[2]))
                self.artists_tableWidget.setItem(row_count, 2, item)
            except Exception as e:
                print('Warning: def load_artists > ', str(e))


def fetch_songs(dialog, self):
    self.spinner.start()
    url = 'https://newapi.beeptunes.com/public/artist/single-tracks'
    json = {
        'artistId': self.artist_id,
        'begin': '0',
        'size': '1000'
        }
    self.songs_res_thread = Response(url, json)
    self.songs_res_thread.start()
    self.songs_res_thread.res.connect(
        lambda response: load_songs(dialog, self, response)
    )


def load_songs(dialog, self, response):
    self.spinner.stop()
    list_of_songs = []
    if response != []:
        c = 1
        for single_track in response:
            if 'durationMinutes' in single_track.keys():
                try:
                    if 'name' not in single_track.keys():
                        persian_name = 'آهنگ شماره {}'.format(c)
                    else:
                        persian_name = single_track['name']
                    if 'englishName' not in single_track.keys():
                        english_name = 'Track Number {}'.format(c)
                    else:
                        english_name = single_track['englishName']
                    c = c + 1
                    minutes = single_track['durationMinutes']
                    seconds = single_track['durationSeconds']
                    high_quality_link = single_track['hqHttpPath']
                    low_quality_link = single_track['lqHttpPath']
                    list_of_songs.append(
                        [
                            persian_name,
                            english_name,
                            '{}:{}'.format(minutes, seconds),
                            high_quality_link,
                            low_quality_link
                        ]
                        )
                except Exception as e:
                    print('Warning: def load_songs > ', str(e))
        row_count = len(list_of_songs)
        if row_count > 0:
            self.download_pushButton.setEnabled(True)
            self.select_all_checkBox.setEnabled(True)
        self.total_num_of_songs_label.setText(str(row_count))
        self.files_tableWidget.setRowCount(row_count)
        for row in range(row_count):
            for column in range(5):
                item = QtWidgets.QTableWidgetItem(
                    list_of_songs[row][column]
                    )
                self.files_tableWidget.setItem(row, column, item)
                self.files_tableWidget.item(row, 0).setCheckState(
                    QtCore.Qt.Checked
                    )
        self.stackedWidget.setCurrentIndex(1)
    else:
        messages.warning(
            dialog,
            'Warning',
            'This artist does not have any single tracks'
            )


def download(dialog, self):
    files = {}
    row_count = self.files_tableWidget.rowCount()
    quality = self.quality_comboBox.currentText()
    if quality == 'High':
        link_column = 3
    else:
        link_column = 4
    c = 1
    for row in range(row_count):
        url = self.files_tableWidget.item(row, link_column).text()
        english_name = self.files_tableWidget.item(row, 1).text()
        english_name = english_name.replace(' ', '_')
        checked = self.files_tableWidget.item(row, 0).checkState()
        if checked == QtCore.Qt.Checked:
            if english_name in files.keys():
                english_name = '{}. {}'.format(c, english_name)
                c = c + 1
            files[english_name] = url
    self.total_files_to_download = len(files)
    if self.total_files_to_download > 0:
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(
            dialog,
            caption='Save files...',
            )
        if dir_ != '':
            self.download_pushButton.setEnabled(False)
            self.search_pushButton.setEnabled(False)
            self.goto_search_pushButton.setEnabled(False)
            self.download_thread = Download(files, dir_)
            self.download_thread.start()
            self.download_thread.progress.connect(
                lambda val: progress(dialog, self, val)
                )
            self.download_thread.failed.connect(
                lambda files: show_failed_files(
                    dialog,
                    self,
                    files
                    )
                )
    else:
        message = 'Select at least one track!'
        messages.warning(dialog, 'Warning', message)


def show_failed_files(dialog, self, files):
    files = '\n'.join(files)
    message = 'Failed to download the below files: \n\n{}'.format(files)
    messages.error(dialog, 'Error', message)
    self.download_pushButton.setEnabled(True)
    self.search_pushButton.setEnabled(True)
    self.goto_search_pushButton.setEnabled(True)


def progress(dialog, self, val):
    self.progressBar.setFormat('{} of {}'.format(
        val,
        self.total_files_to_download
        ))
    percent = (val/self.total_files_to_download) * 100
    self.progressBar.setValue(int(percent))
    if percent == 100:
        messages.info(
            dialog,
            'Info',
            'Downloading has been finished!'
            )
        self.download_pushButton.setEnabled(True)
        self.search_pushButton.setEnabled(True)
        self.goto_search_pushButton.setEnabled(True)
        self.progressBar.setValue(0)


def stop_download(dialog, self):
    try:
        self.download_thread.stop()
    except Exception as e:
        print('Warning: def stop_download > ', str(e))
    message = 'Do you want to close the windows?'
    close = messages.question(dialog, 'Confirmation', message)
    if close:
        dialog.close()


def select_all(dialog, self):
    row_count = self.files_tableWidget.rowCount()
    select_all = self.select_all_checkBox.isChecked()
    if select_all:
        state = QtCore.Qt.Checked
    else:
        state = QtCore.Qt.Unchecked
    for row in range(row_count):
        self.files_tableWidget.item(row, 0).setCheckState(state)


def search(dialog, self):
    num_of_rows = self.artists_tableWidget.rowCount()
    for row in range(num_of_rows):
        persian = self.artists_tableWidget.item(row, 0).text().lower()
        english = self.artists_tableWidget.item(row, 1).text().lower()
        name = '{} {}'.format(persian, english)
        keyword = self.filter_lineEdit.text().lower()
        if keyword != '':
            if keyword not in name:
                self.artists_tableWidget.setRowHidden(row, True)
            else:
                self.artists_tableWidget.setRowHidden(row, False)
        elif keyword == '':
            self.artists_tableWidget.setRowHidden(row, False)


def fetch_settings(self, option):
    sql = '''SELECT value FROM settings
        WHERE option="{}";'''.format(option)
    self.cur.execute(sql)
    option = self.cur.fetchall()[0][0]
    return option


def update_settings(self, option, value):
    sql = '''UPDATE settings
        set value="{}"
        WHERE option="{}"'''.format(value, option)
    self.cur.execute(sql)
    self.conn.commit()


class Download(QtCore.QThread):

    progress = QtCore.Signal(int)
    failed = QtCore.Signal(list)

    def __init__(self, files, dir_):
        super().__init__()
        self.files = files
        self.dir_ = dir_
        self.stop_ = False
        self.escape_not_complete = False

    def stop(self):
        try:
            self.response.close()
            self.file_.close()
            self.stop_ = True
            self.escape_not_complete = True
        except Exception as error:
            print('Warning: class Download, def stop > ', str(error))

    def run(self):
        successfully_downloaded = []
        num_of_downloaded_files = 0
        for english_name, url in self.files.items():
            if not self.stop_:
                try:
                    self.progress.emit(num_of_downloaded_files)
                    self.response = requests.get(
                        url,
                        allow_redirects=True,
                        stream=True
                        )
                    pot = '{}/{}.mp3'.format(self.dir_, english_name)
                    if os.path.isfile(pot):
                        pot = '{}/duplicated_{}.mp3'.format(
                            self.dir_,
                            english_name
                            )
                    with open(pot, 'wb') as self.file_:
                        shutil.copyfileobj(
                            self.response.raw,
                            self.file_
                            )
                    if not self.escape_not_complete:
                        num_of_downloaded_files += 1
                        self.progress.emit(num_of_downloaded_files)
                        successfully_downloaded.append(english_name)
                except Exception as error:
                    print('Warning: class Download, def run > ', str(error))
                    if english_name in successfully_downloaded:
                        successfully_downloaded.remove(english_name)
        if not len(successfully_downloaded) == len(self.files):
            failed_files = [
                track for track in self.files.keys()
                if track not in successfully_downloaded
                ]
            self.failed.emit(failed_files)


class Response(QtCore.QThread):
    res = QtCore.Signal(dict)

    def __init__(self, url, json):
        super().__init__()
        self.url = url
        self.json = json

    def run(self):
        try:
            self.response = requests.get(self.url, params=self.json)
            response = self.response.json()
            self.res.emit(response)
        except Exception as e:
            print('Warning: class Response, def run > ', str(e))
            self.res.emit({})


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_amber.xml')
    dialog = QtWidgets.QDialog()
    ui = beepdl_ui.Ui_dialog()
    ui.setupUi(dialog)
    init(app, dialog, ui)
    dialog.show()
    sys.exit(app.exec_())
