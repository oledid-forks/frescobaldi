# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2014 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
The Manuscript viewer panel widget.
"""

from __future__ import unicode_literals

import os
import weakref

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import app
import sessions
import userguide.util
import icons
try:
    import popplerqt4
except ImportError:
    pass

import viewers
from viewers import documents
from . import contextmenu

class Widget(viewers.popplerwidget.AbstractPopplerView):
    def __init__(self, dockwidget):

        self.use_layout = layout = QVBoxLayout()
        super(Widget, self).__init__(dockwidget)

        self._ctxMenuClass = contextmenu.ManuscriptViewerContextMenu

        hor = QHBoxLayout()

        self.helpButton = QToolButton(
            icon = icons.get("help-contents"),
            autoRaise = True,
            clicked = lambda: userguide.show("manuscript"))

        ac = self.actionCollection = self.parent().actionCollection
        ac.manuscript_open.triggered.connect(self.openManuscripts)
        ac.manuscript_close.triggered.connect(self.closeManuscript)
        ac.manuscript_close_other.triggered.connect(self.closeOtherManuscripts)
        ac.manuscript_close_all.triggered.connect(self.closeAllManuscripts)


        t = self.parent().mainwindow().addToolBar("manuscriptview")

        t.addWidget(self.helpButton)
        t.addAction(ac.manuscript_open)
        t.addAction(ac.manuscript_close)
        t.addAction(ac.music_document_select)
        t.addAction(ac.music_reload)
        t.addAction(ac.music_print)
        t.addSeparator()
        t.addAction(ac.music_zoom_in)
        t.addAction(ac.music_zoom_combo)
        t.addAction(ac.music_zoom_out)
        t.addSeparator()
        t.addAction(ac.music_prev_page)
        t.addAction(ac.music_pager)
        t.addAction(ac.music_next_page)

        hor.addWidget(t)

        hor.addStretch(1)

        layout.addLayout(hor)

        app.translateUI(self)
        userguide.openWhatsThis(self)

        app.sessionChanged.connect(self.slotSessionChanged)

    def translateUI(self):
        self.setWhatsThis(_(
            "<p>The Manuscript Viewer displays an original manuscript " +
            "one is copying from.</p>\n"
            "<p>See {link} for more information.</p>").format(link=
                userguide.util.format_link("manuscript")))

    def slotSessionChanged(self, name):
        if name:
            self.closeAllManuscripts()
            session = sessions.sessionGroup(name)
            manuscripts = session.value("manuscripts", "")
            active_manuscript = session.value("active-manuscript", "")
            if manuscripts:
                ds = self.actionCollection.music_document_select
                ds.loadManuscripts(manuscripts, active_manuscript, True)

    def closeManuscript(self):
        """ Close current manuscript. """
        mds = self.parent().actionCollection.music_document_select
        mds.removeManuscript(self._currentDocument)
        if len(mds._documents) == 0:
            self.view.clear()

    def closeOtherManuscripts(self):
        """Close all manuscripts except the one currently opened"""
        mds = self.parent().actionCollection.music_document_select
        mds.removeOtherManuscripts(self._currentDocument)

    def closeAllManuscripts(self):
        """Close all opened manuscripts"""
        mds = self.parent().actionCollection.music_document_select
        mds.removeAllManuscripts()
        self.view.clear()

    def openManuscripts(self):
        """ Displays an open dialog to open a manuscript PDF. """
        caption = app.caption(_("dialog title", "Open Manuscript(s)"))
        directory = app.basedir()

        current_ms = self._currentDocument
        current_manuscript_document = current_ms.filename() if current_ms else None
        current_editor_document = self.parent().mainwindow().currentDocument().url().toLocalFile()
        directory = os.path.dirname(current_manuscript_document or current_editor_document or app.basedir())
        filenames = QFileDialog().getOpenFileNames(self, caption, directory, '*.pdf',)
        self.actionCollection.music_document_select.loadManuscripts(filenames, filenames[-1])