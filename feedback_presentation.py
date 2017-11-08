#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# feedback_presentation.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Module that receives reports from Kano Feedback inspectors, and presents them
# in a HTML document for making life easier, we are generating the HTML
# document using the compact versatile "markup.py" module
#
# http://markup.sourceforge.net/
#

import feedback_inspectors  # TODO: is this used?
import markup
import base64
import time
import cgi


#
# Class that implements the HTML document for DrFeeback complete report
#
class FeedbackPresentation:
    def __init__(self, filename, title=None, css=None, header=None, footer=None, h1_title=None):
        '''
        Build and html document called "page" where we can build up html information areas
        '''
        self.info = []
        self.warn = []
        self.error = []
        self.logs = []
        jquery_code = ('<script>'
                       '$(".expand_click").click(function(){'
                       'if ( $(this).children(".expand").is( ":hidden" ) ) {'
                       '$(this).children(".expand").slideDown( "slow" );'
                       '} else {'
                       '$(this).children(".expand").slideUp( "slow" );'
                       '};'
                       '});'
                       '</script>')

        css_code = ('<script src="http://code.jquery.com/jquery-2.1.3.min.js"></script>'
                    '<style>'
                    '.expand'
                    '{'
                    'display:none;'
                    '}'
                    '</style>')

        self.page = markup.page()
        self.page.init(title=title, css=css, header='{}{}'.format(css, css_code), footer='{}{}'.format(footer, jquery_code))
        if h1_title:
            self.page.h1(h1_title)

        self.page.h3('Generated %s' % (time.ctime()))

    def add_report(self, inspector, logdata):
        '''
        Collect information and logfile sections from this inspector
        '''
        if len(inspector.get_info()):
            self.info.append(inspector.get_info())
        if len(inspector.get_warn()):
            self.warn.append(inspector.get_warn())
        if len(inspector.get_error()):
            self.error.append(inspector.get_error())

        if logdata:
            format = inspector.get_format(logdata[0])

            self.logs.append({'logfile': inspector.logfile, 'logdata': logdata,
                              'format': format})

    def wrap_it_up(self):
        '''
        Uniformly join all the information and logfiles in a single document in 2 sections
        '''
        self.page.h2('Summary section')
        self.page.h3('Information')

        for entry in self.info:
            self.page.ul(class_='inspector-information')
            self.page.li(entry, class_='info-entry')
            self.page.ul.close()

        self.page.h3('Warning')
        for entry in self.warn:
            self.page.ul(class_='inspector-warning')
            self.page.li(entry, class_='warn-entry')
            self.page.ul.close()

        self.page.h3('Error')
        for entry in self.error:
            self.page.ul(class_='inspector-error')
            self.page.li(entry, class_='error-entry')
            self.page.ul.close()

        self.page.h2('Logfile section')
        for log in self.logs:

            self.page.div(class_='expand_click')
            self.page.h3('Dump logfile: %s' % log['logfile'])
            self.page.div(class_='expand')

            if log['format'] == 'image':
                img64 = base64.b64encode(''.join(log['logdata']))
                self.page.img(src='data:image/png;base64,%s' % img64)
                pass
            elif log['format'] == 'binary':
                if len(log['logdata']) < 1024 * 1024:
                    b64 = base64.b64encode(''.join(log['logdata']))
                    self.page.a(href='data:application/octet-stream;base64,%s' % b64, download=log['logfile'])
                    self.page.h3('Download: %s' % log['logfile'])
                    self.page.a.close()
                else:
                    self.page.h4("data too big; extract from original tar file")
            else:
                # Insert log lines, escaping non-ascii characters to HTML encoding
                lines = []
                for line in log['logdata']:
                    lines.append (cgi.escape(unicode(line, errors='ignore')).encode('ascii', 'xmlcharrefreplace'))

                self.page.pre(lines, class_='logfile')

            self.page.div.close()
            self.page.div.close()

    def get_html(self):
        return self.page
