# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

def html_header() :
    print ("Content-Type: text/html; charset=utf-8\n\n")
    print ("""
        <html>
        <head>
        <title>Docutone</title>
        <meta http-equiv='content-type' content='text/html;charset=utf-8'/>
        </head>
        <body>
    """)

def html_footer():
    print ("</body></html>")