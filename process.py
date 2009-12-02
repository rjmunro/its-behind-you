#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :
from BeautifulSoup import BeautifulSoup
from imageList import getTitleOfImage
import sys
YAML = False

def extractText(soup):
  """ Pull out just the text, with whitespace trimmed and normalised from a
      BeautifulSoup tag. I'm amazed Beautiful soup doesn't have something
      like this built in."""
  try:
    return ' '.join(' '.join(soup(text=True)).replace('&amp;','&').replace('&nbsp;',' ').replace('&rsquo;',"'").split())
  except:
    return soup

missingImgs = set()
plays = []
for year in range(2000,2010):
  soup = BeautifulSoup(open("diary"+str(year)+str(year+1)+".html"))
  for table in soup.findAll('table'):
    producer = ""
    producerImg = ""
    # Pull out the first row of the table as keys
    keys = []
    for col in table.tr('td'):
      keys.append(extractText(col))
    if 'Dates' not in keys:
      continue # Skip this table - it's not a normal list of productions
    for row in table.findAll('tr')[1:]:
      rawCols = dict(zip(keys,row.findAll('td')))

      # Get theatre column
      theatreCol = rawCols.get('Venue',rawCols.get('Theatre',''))
      # Get theatre logo if present
      if theatreCol.img:
        theatreImg = str(theatreCol.img['src'])
      else:
        theatreImg = ''
      # Get theatre name, cutting off text after "Box Office" if present
      theatre = extractText(theatreCol).split(" Box Office",1)[0]

      # Get date column and fix years like '01 to be 2001
      rawDates = extractText(rawCols['Dates']).replace(" '"," 20")

      # Split into start and end date
      if " to " in rawDates:
        dates = rawDates.split(" to ",1)
      elif " - " in rawDates:
        dates = rawDates.split(" - ",1)
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

      # Get the title
      rawTitle = rawCols.get('Pantomime',rawCols.get('Production',''))
      titleImg = ""
      # If part of it is bold, that's the title.
      if rawTitle.b:
        title = extractText(rawTitle.b)
      # If there is an image, that's the title.
      elif rawTitle.img:
        titleImg = rawTitle.img['src']
        title = getTitleOfImage(titleImg)
        if not title:
          title = "!!ERROR !! %s" % titleImg
          missingImgs.add(titleImg)
      else:
        title = extractText(rawTitle)
      # Strip the link to the handbill if present
      if title.lower().endswith(' handbill'):
        title = title[:-9]

      # Get text from cast column and strip the word "Handbill" from the end of it (if present)
      castText = extractText(rawCols.get('Starring',rawCols.get('Cast Details','')))
      if castText.lower().endswith(' handbill'):
        castText = castText[:-9]

      # Split the cast into a list of people
      if "; " in castText:
        cast = castText.split("; ")
      elif ", " in castText:
        cast = castText.split(", ")
      elif castText:
        cast = [castText]
      else:
        cast = []

      # Split the last cast member into 2 people if the list ends with " and "
      if cast and ' and ' in cast[-1]:
        cast[-1],extra = cast[-1].rsplit(' and ',1)
        cast.append(extra)

      # Producers
      if "Producer" in keys:
        producer = extractText(rawCols['Producer'])
        producerImg = rawCols['Producer'].img and rawCols['Producer'].img['src'] or ''

      # Add link to page sourced from
      source = "http://www.its-behind-you.com/diary%s%s.html" % (year,year+1)

      # Find any other images
      pictures = [i['src'] for i in row.findAll('img') if str(i['src']) not in (theatreImg, producerImg, titleImg)]

      plays.append({'theatre':theatre,'theatreImg':theatreImg,'dates':dates,'title':title,'cast':cast, 'year':year, 'source':source,
        "pictures": pictures, "producer":producer, "producerImg":producerImg, "titleImg":titleImg})

# Sort plays
plays.sort(lambda x,y: cmp(x['year'],y['year']) or cmp(x['title'],y['title']) or cmp(x['theatre'],y['theatre']))

# Search consecutive pairs for duplicate data
dupes1 = []
dupes2 = []
dupeIds = []
for playId in range(len(plays)-1):
  matching = 0
  matchingKeys = []
  nonMatching = 0
  nonMatchingKeys = []
  for key in plays[playId].keys():
    if plays[playId+1].has_key(key):
      if plays[playId][key] and plays[playId+1][key]: # Check both keys have data
        if plays[playId][key]==plays[playId+1][key]: # See if it's the same data
          matching += 1
          matchingKeys.append(key)
        else:
          nonMatching += 1
          nonMatchingKeys.append(key)
  #if 'year' in matchingKeys and matching > nonMatching*2: # Probably a dupe
  #if matching > 3 and nonMatching < 4 and 'dates' in nonMatchingKeys and 'theatre' in nonMatchingKeys: # Same production in 2 theatres
  if nonMatching==0: # Certainly a dupe - nothing disagrees. There may data missing from one or other.
    plays[playId]['dupe'] = playId
    plays[playId+1]['dupe'] = playId
    plays[playId]['dupeKeys'] = matchingKeys
    plays[playId+1]['dupeKeys'] = matchingKeys
    plays[playId]['nonDupeKeys'] = nonMatchingKeys
    plays[playId+1]['nonDupeKeys'] = nonMatchingKeys
    dupes1.append(plays[playId])
    dupes2.append(plays[playId+1])
    dupeIds.append(playId)

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

  sys.stderr.write("%s plays dumped\n" % len(plays))
  sys.stderr.write("%s dupes found\n" % len(dupeIds))

  if missingImgs:
    for i in sorted(list(missingImgs)):
      sys.stderr.write("  '%s': '',\n" % i)
