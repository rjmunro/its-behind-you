#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :
from imageList import imageList,getTitleOfImage
from operator import itemgetter
from plays import plays
print """<html>
<head>
  <title>Image title test</title>
  <style>
    div { height: 200px; width: 290px; text-align: center; float: left }
  </style>
</head>
<body>
"""

uniquePlays = list(set([(play['title'],play['titleImg']) for play in plays if play['titleImg']]))
uniquePlays.sort()

#for url,title in imageList.items():
for title,url in uniquePlays:
  print '<div><img src="http://www.its-behind-you.com/%s" /><br />%s<br />%s</div>' % (url,url,getTitleOfImage(url))

print """</body>
</html>"""
