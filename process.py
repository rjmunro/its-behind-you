#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :
import BeautifulSoup
from imageList import getTitleOfImage
import sys
YAML = False

def extractText(soup):
  """ Pull out just the text, with whitespace trimmed and normalised from a
      BeautifulSoup tag. I'm amazed Beautiful soup doesn't have something
      like this built in."""
  try:
    return ' '.join(' '.join(soup(text=True)).replace('&amp;','&').replace('&nbsp;',' ').replace('&rsquo;',"'").replace('&lsquo;',"'").split())
  except:
    return soup

def fixLinks(link):
  if not link:
    return ""
  elif link.startswith('http://'):
    return link
  elif link.startswith('/'):
    return 'http://www.its-behind-you.com'+link
  else:
    return 'http://www.its-behind-you.com/'+link

missingImgs = set()
plays = []
castLinks = {}
for year in range(2000,2010):
  soup = BeautifulSoup.BeautifulSoup(open("diary"+str(year)+str(year+1)+".html"))
  for table in soup.findAll('table'):
    producer = ""
    producerImg = ""
    # Pull out the first row of the table as keys
    keys = []
    for col in table.tr('td'):
      keys.append(extractText(col).lower())
    if 'dates' not in keys:
      continue # Skip this table - it's not a normal list of productions
    for row in table.findAll('tr')[1:]:
      theatreImg = ''
      theatre = ''
      rawdates =''
      dates = ['','']
      titleImg = ''
      title = ''
      cast = []

      for colname,colsoup in zip(keys,row.findAll('td')):


        if colname in ('venue','theatre'):
          # Get theatre logo if present
          if colsoup.img:
            theatreImg = fixLinks(colsoup.img['src'])
          # Get theatre name, cutting off text after "Box Office" if present
          theatre = extractText(colsoup).split(" Box Office",1)[0]

        elif colname == "dates":
          rawDates = extractText(colsoup).replace(" '"," 20")

          # Split into start and end date
          if " to " in rawDates:
            dates = rawDates.split(" to ",1)
          elif " - " in rawDates:
            dates = rawDates.split(" - ",1)
          elif " -" in rawDates:
            dates = rawDates.split(" -",1)
          elif rawDates.lower().startswith("until "):
            dates = ['',rawDates[6:]]
          elif rawDates.lower().startswith("from "):
            dates = [rawDates[5:],'']
          elif not rawDates:
            dates = ['','']
          else:
            dates = [rawDates,"!!ERROR!!"]

          # Fix dates with month but no year
          for i in 0,1:
            if dates[i][-3:].lower() in ("nov","dec"):
              dates[i]+=' ' + str(year)
            if dates[i][-3:].lower() in ("jan","feb"):
              dates[i]+=' ' + str(year+1)

        elif colname in ('pantomime','production'):
          # If part of it is bold, that's the title.
          if colsoup.b:
            title = extractText(colsoup.b)
          # If there is an image, that's the title.
          elif colsoup.img:
            titleImg = colsoup.img['src']
            title = getTitleOfImage(titleImg)
            titleImg = fixLinks(titleImg)
            if not title:
              title = "!!ERROR !! %s" % titleImg
              missingImgs.add(titleImg)
          else:
            title = extractText(colsoup)
          # Strip the link to the handbill if present
          if title.lower().endswith(' handbill'):
            title = title[:-9]

        elif colname in ('starring','cast details'):
          # Get text from cast column and strip the word "Handbill" from the end of it (if present)
          castText = extractText(colsoup)
          if castText.lower().endswith(' handbill'):
            castText = castText[:-9]

          # Split the cast into a list of people
          if "; " in castText:
            cast = castText.split("; ")
          elif ", " in castText:
            cast = castText.split(", ")
          elif castText:
            cast = [castText]

          # Split the last cast member into 2 people if the list ends with " and "
          if cast and ' and ' in cast[-1]:
            cast[-1],extra = cast[-1].rsplit(' and ',1)
            cast.append(extra)


        # Producers
        elif colname == "producer":
          producer = extractText(colsoup)
          producerImg = colsoup.img and fixLinks(colsoup.img['src']) or ''

      # Add link to page sourced from
      source = "http://www.its-behind-you.com/diary%s%s.html" % (year,year+1)

      # Find any other images
      pictures = [fixLinks(i['src']) for i in row.findAll('img') if fixLinks(i['src']) not in (theatreImg, producerImg, titleImg)]

      # Find any links
      links = set()
      for href,text in [(fixLinks(i['href']),extractText(i)) for i in row.findAll('a') if i.has_key('href')]:
        if text in cast:
          if text in castLinks:
            castLinks[text].add(href)
          else:
            castLinks[text] = set([href])
        elif href.endswith('.jpg'):
          pictures.append(href)
        else:
            links.add((text,href))

      plays.append({'theatre':theatre,'theatreImg':theatreImg,'dates':dates,'title':title,'cast':cast, 'year':year, 'source':source,
        "pictures": pictures, "producer":producer, "producerImg":producerImg, "titleImg":titleImg, "links": list(links)})

# Sort plays
plays.sort(lambda x,y: cmp(x['year'],y['year']) or cmp(x['title'],y['title']) or cmp(x['theatre'],y['theatre']))

# Search consecutive pairs for duplicate data
dupes1 = []
dupes2 = []
dupeIds = []
playId = 1
removedDupes = 0
while playId < len(plays):
  matchingKeys = set()
  nonMatchingKeys = set()
  for key in plays[playId].keys():
    if plays[playId-1].has_key(key):
      if plays[playId][key] and plays[playId-1][key]: # Check both keys have data
        if plays[playId][key]==plays[playId-1][key]: # See if it's the same data
          matchingKeys.add(key)
        else:
          nonMatchingKeys.add(key)

  if nonMatchingKeys.issubset(set(['links','images'])): # Certainly a dupe - nothing disagrees. There may data missing from one or other.
    # Mash data together & remove it.
    for key in plays[playId].keys():
      if key in ('links','images'):
        plays[playId-1][key] = plays[playId-1][key] + plays[playId][key]
      else:
        plays[playId-1][key] = plays[playId-1][key] or plays[playId][key]
    plays.pop(playId)
    removedDupes += 1
    continue # don't increment playId

  elif len(matchingKeys) > 3 and len(nonMatchingKeys) < 4 and 'dates' in nonMatchingKeys and 'theatre' in nonMatchingKeys: # Same production in 2 theatres
    # For now, tag it with a productionId
    if 'productionId' not in plays[playId-1]:
      plays[playId-1]['productionId'] = playId-1
    plays[playId]['productionId'] = plays[playId-1]['productionId']

  elif 'year' in matchingKeys and len(matchingKeys) > len(nonMatchingKeys)*2: # Probably a dupe
    plays[playId]['dupe'] = playId
    plays[playId-1]['dupe'] = playId
    plays[playId]['dupeKeys'] = matchingKeys
    plays[playId-1]['dupeKeys'] = matchingKeys
    plays[playId]['nonDupeKeys'] = nonMatchingKeys
    plays[playId-1]['nonDupeKeys'] = nonMatchingKeys
    dupes1.append(plays[playId])
    dupes2.append(plays[playId-1])
    dupeIds.append(playId)


  playId += 1

if __name__=="__main__":
  if YAML:
    import yaml
    # this is the magic that treats all strings as unicode<br>
    def represent_unicode(dumper, data):

        return dumper.represent_scalar("tag:yaml.org,2002:str", data)
    def construct_unicode(loader, node):
        return unicode(loader.construct_scalar(node))
    yaml.add_representer(unicode, represent_unicode)
    yaml.add_constructor("tag:yaml.org,2002:str", construct_unicode)

    print yaml.dump(plays,allow_unicode=True)
  else:
    from pprint import pprint
    print "plays = ",
    pprint(plays)
    print "castLinks = ",
    pprint(castLinks)

  sys.stderr.write("%s dupes removed\n" % removedDupes)
  sys.stderr.write("%s plays dumped\n" % len(plays))
  sys.stderr.write("%s more possible dupes found\n" % len(dupeIds))

  if missingImgs:
    for i in sorted(list(missingImgs)):
      sys.stderr.write("  '%s': '',\n" % i)
