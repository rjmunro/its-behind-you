#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :
from imageList import imageList,getTitleOfImage
print """<html>
<head>
  <title>Image title test</title>
  <style>
    div { height: 200px; width: 290px; text-align: center; float: left }
  </style>
</head>
<body>
"""

for url,title in imageList.items():
  print '<div><img src="http://www.its-behind-you.com/%s" /><br />%s<br />%s</div>' % (url,url,getTitleOfImage(url))

print """</body>
</html>"""
