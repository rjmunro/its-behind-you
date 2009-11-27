#!/usr/bin/env python
from BeautifulSoup import BeautifulSoup

YAML = False

def extractText(soup):
  try:
    return ' '.join(' '.join(soup(text=True)).replace('&amp;','&').replace('&nbsp;',' ').split())
  except:
    return soup

plays = []
#for year in range(2000,2010):
for year in range(2002,2005):
  soup = BeautifulSoup(open("diary"+str(year)+str(year+1)+".html"))
  for table in soup.findAll('table'):
    keys = []
    for col in table.tr('td'):
      keys.append(extractText(col).replace('Venue','Theatre'))
    print year,keys
    if 'Dates' not in keys:
      continue # Skip this table - it will be decorative
    for row in table.findAll('tr')[1:]:
      rawCols = dict(zip(keys,row.findAll('td')))

      theatre = extractText(rawCols['Theatre']).split(" Box Office")[0]

      rawDates = extractText(rawCols['Dates']).replace(" '"," 20")
      dates = [rawDates,""]
      if " to " in rawDates:
        dates = rawDates.split(" to ")
      if " - " in rawDates:
        dates = rawDates.split(" - ")

      if not dates[0].endswith(str(year)):
        dates[0]+=str(year)
      if not dates[1].endswith(str(year+1)):
        dates[0]+=str(year+1)

      titleTag = rawCols.get('Pantomime',rawCols.get('Production',''))
      if titleTag:
        title = titleTag.findAll(text=True)[0]
        if len(titleTag)>1:
          print titleTag
      else:
        title = ""
      if title.endswith(' handbill') or title.endswith(' Handbill'):
        title = title[:-9]

      castText = extractText(rawCols.get('Starring',rawCols.get('Cast Details','')))
      if castText.endswith(' handbill') or castText.endswith(' Handbill'):
        castText = castText[:-9]
      if "; " in castText:
        cast = castText.split("; ")
      elif ", " in castText:
        cast = castText.split(", ")
      else:
        cast = [castText]

      if ' and ' in cast[-1]:
        cast[-1],extra = cast[-1].rsplit(' and ',1)
        cast.append(extra)

      plays.append({'theatre':theatre,'dates':dates,'title':title,'cast':cast, 'year':year})

if not YAML:
  from pprint import pprint
  pprint(plays)
else:
  import yaml
  # this is the magic that treats all strings as unicode<br>
  def represent_unicode(dumper, data):

      return dumper.represent_scalar("tag:yaml.org,2002:str", data)
  def construct_unicode(loader, node):
      return unicode(loader.construct_scalar(node))
  yaml.add_representer(unicode, represent_unicode)
  yaml.add_constructor("tag:yaml.org,2002:str", construct_unicode)

  print yaml.dump(plays,allow_unicode=True)

print str(len(plays)) + " plays dumped"
