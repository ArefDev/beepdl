from PySide2 import QtCore, QtGui, QtWidgets


def warning(widget, title, message):
    "shows a warning"
    button = QtWidgets.QMessageBox.Ok
    QtWidgets.QMessageBox.warning(widget, title, message, button)


def error(widget, title, message):
    "shows an error"
    button = QtWidgets.QMessageBox.Ok
    QtWidgets.QMessageBox.critical(widget, title, message, button)


def question(widget, title, message):
    '''
    ask a question and returns true or false
    true  -> yes
    false -> no
    '''
    button = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    answer = QtWidgets.QMessageBox.question(widget, title, message, button)
    if answer == QtWidgets.QMessageBox.No:
        return False
    elif answer == QtWidgets.QMessageBox.Yes:
        return True


def info(widget, title, message):
    "shows an info message"
    button = QtWidgets.QMessageBox.Ok
    QtWidgets.QMessageBox.question(widget, title, message, button)


def about(widget):
    message = """
<b>beepdl</b> is a GUI application to download<br>
free single tracks from beeptunes.com<br><br>
Developed by Aref Alikhani (@ArefDev)<br><br>
“beepdl” is distributed under the GPLv2 license.
"""
    info(widget, 'About...', message)
