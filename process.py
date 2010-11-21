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
    result = ' '.join(soup(text=True))
    result = result.replace('&nbsp;',' ').replace('&rsquo;',"'").replace('&lsquo;',"'")
    result = result.replace('&quot;','"')
    result = result.replace('&amp;','&')
    return ' '.join(result.split()) # Normalise whitespace
  except:
    return soup

def fixLinks(link):
  if not link:
    return ""
  elif link.startswith('http://'):
    return link
  elif link.startswith('www.'):
    return 'http://'+link
  elif link.startswith('/'):
    return 'http://www.its-behind-you.com'+link
  else:
    return 'http://www.its-behind-you.com/'+link

missingImgs = set()
plays = []
castLinks = {}
theatres = {}

for year in range(2000,2011):
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
      description = ''
      theatreImg = ''
      theatre = ''
      rawdates =''
      dates = ['','']
      titleImg = ''
      title = ''
      cast = []
      links = {}
      pictures = set()

      for colname,colsoup in zip(keys,row.findAll('td')):
        # Find any images
        colPictures = [fixLinks(i['src']) for i in colsoup.findAll('img')]

        # Find any links
        linksSoup = colsoup.findAll('a')
        i = 0
        while i<len(linksSoup):
          if "handbill" in extractText(linksSoup[i]).lower():
            bill = linksSoup.pop(i)
            while bill.next and (not isinstance(bill.next, BeautifulSoup.NavigableString)) and bill.next.name !='td':
              description += unicode(bill.next.extract())
            bill.extract()
            pictures.add(fixLinks(bill['href']))
          i += 1
        colLinks = dict([(fixLinks(i['href']),extractText(i)) for i in colsoup.findAll('a') if i.has_key('href')])


        if colname in ('venue','theatre'):
          # Get theatre name, cutting off text after "Box Office" if present
          theatreList = extractText(colsoup).split(" Box Office",1)
          theatre = theatreList[0]
          if theatre not in theatres:
            theatres[theatre] = {}
          if len(theatreList)>1:
            theatres[theatre]['boxOffice'] = theatreList[1]

          # Get theatre logo if present
          if colPictures:
            theatreImg = colPictures[0]
            if 'logos' not in theatres[theatre]:
              theatres[theatre]['logos'] = set(colPictures[0:1])
            else:
              theatres[theatre]['logos'].add(theatreImg)
            colPictures.pop(0)

          # Get theatre link if there is only a single link in the theatre column.
          if len(colLinks)==1:
            theatreLink = colLinks.items()[0]
            if 'links' not in theatres[theatre]:
              theatres[theatre]['links'] = set([theatreLink])
            colLinks = {}

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
            colsoup.b.extract()
          # If there is an image, that's the title.
          elif colPictures:
            titleImg = colPictures.pop(0)
            title = getTitleOfImage(titleImg)
            if not title:
              title = "!!ERROR !! %s" % titleImg
              missingImgs.add(titleImg)
          else:
            title = extractText(colsoup)

          description += extractText(colsoup)

        elif colname in ('starring','cast details'):
          castText = extractText(colsoup)

          # Split the cast into a list of people
          if "; " in castText:
            cast = [i.strip() for i in castText.split("; ")]
          elif ", " in castText:
            cast = [i.strip() for i in castText.split(", ")]
          elif castText:
            cast = [castText]

          # Split the last cast member into 2 people if the list ends with " and "
          if cast and ' and ' in cast[-1]:
            cast[-1],extra = cast[-1].rsplit(' and ',1)
            cast.append(extra)

          for url,name in colLinks.items():
            if name in cast:
              if name in castLinks:
                castLinks[name].add(url)
              else:
                castLinks[name] = set([url])
              colLinks.pop(url)

        # Producers
        elif colname == "producer":
          producer = extractText(colsoup)
          if colPictures:
            producerImg = colPictures.pop(0)
          else:
            producerImg = ''

        pictures.update(colPictures)
        links.update(colLinks)

      # Add link to page sourced from
      source = "http://www.its-behind-you.com/diary%s%s.html" % (year,year+1)

      plays.append({'title': title, 'cast': cast, 'year': year, 'source': source,
        "pictures": pictures, "producer": producer, "producerImg": producerImg, "titleImg": titleImg, "links": links, 'description': description,
        'dates':set([(tuple(dates), theatre)])})

# Sort plays
plays.sort(lambda x,y: cmp(x['year'],y['year']) or cmp(x['title'],y['title']) or cmp(x['producer'],y['producer']))

# Search consecutive pairs for duplicate data
dupes1 = []
dupes2 = []
dupeIds = []
playId = 1
removedDupes = 0
while playId < len(plays):
  for compare in range(1,1+max(playId,4)): # compare up to the last 4 records
    matchingKeys = set()
    nonMatchingKeys = set()
    for key in plays[playId].keys():
      if plays[playId-compare].has_key(key):
        if plays[playId][key] and plays[playId-compare][key]: # Check both keys have data
          if plays[playId][key]==plays[playId-compare][key]: # See if it's the same data
            matchingKeys.add(key)
          else:
            nonMatchingKeys.add(key)

    if nonMatchingKeys.issubset(set(['dates','description','links','images'])): # Certainly a dupe - nothing disagrees. There may data missing from one or other.
      # Mash data together & remove it.
      for key in plays[playId].keys():
        if key in ('links','images','dates'):
          plays[playId-compare][key].update(plays[playId][key])
        elif key in ('dupe','dupeKeys','nonDupeKeys'):
          pass
        else:
          plays[playId-compare][key] = plays[playId-compare][key] or plays[playId][key]
      plays.pop(playId)
      removedDupes += 1
      playId -= 1 # don't increment playId
      break # Stop checking this

    elif 'year' in matchingKeys and len(matchingKeys) > len(nonMatchingKeys)*2: # Probably a dupe
      plays[playId]['dupe'] = playId
      plays[playId-compare]['dupe'] = playId
      plays[playId]['dupeKeys'] = matchingKeys
      plays[playId-compare]['dupeKeys'] = matchingKeys
      plays[playId]['nonDupeKeys'] = nonMatchingKeys
      plays[playId-compare]['nonDupeKeys'] = nonMatchingKeys
      dupes1.append(plays[playId])
      dupes2.append(plays[playId-compare])
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
    print "theatres = ",
    pprint(theatres)

  sys.stderr.write("%s dupes removed\n" % removedDupes)
  sys.stderr.write("%s plays dumped\n" % len(plays))
  sys.stderr.write("%s more possible dupes found\n" % len(dupeIds))

  if missingImgs:
    for i in sorted(list(missingImgs)):
      sys.stderr.write("  '%s': '',\n" % i)
