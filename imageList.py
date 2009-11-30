imageList = {
  'images/09DuoCindlogo.jpg': 'Cinderella',
  'images/robinhoodNEW2008logo.gif': 'Robin Hood',
  'images/nppcindlow.jpg': 'Cinderella',
  'images/CambLogoNew.jpg': 'Cinderella',
  'images/ChelmsfordLogo07.jpg': 'Jack and the Beanstalk',
  'images/hammondbeautylogo.jpg': 'Sleeping Beauty',
  'images/BeautyLogoNots09.jpg': 'Beauty and the Beast',
  'images/SloughLogo07.jpg': 'Aladdin',
  'images/07GlasgowPavilion_logo.jpg': '',
  'images/07MillfordLogo2.jpg': '',
  'images/07NorthHykehamlogo.jpg': '',
  'images/08BasildonLogo.jpg': '',
  'images/08HitchinKids.jpg': '',
  'images/09CarlisleLogo.jpg': '',
  'images/09Fernehamlogo.jpg': '',
  'images/09Northlogo.jpg': '',
  'images/AldershotB&Beast-title.jpg': '',
  'images/AldershotLogoPan.jpg': '',
  'images/ByreLogoMG.jpg': '',
  'images/CamberleyPanLogo.jpg': '',
  'images/Capitol-ppan-logo-green-sma.jpg': '',
  'images/Chelmsfordlogo09.jpg': '',
  'images/ConsettLogo07_small.jpg': '',
  'images/DWLogoCamberleyTheatre.jpg': '',
  'images/HBPussBootslogo.jpg': '',
  'images/HolmanSWLogo-2.jpg': '',
  'images/HorshamLogo09.jpg': '',
  'images/Kids-show-logo.jpg': '',
  'images/OwenMoneyPanLogo.jpg': '',
  'images/PPLogo_new.jpg': '',
  'images/SWLogo-Stockport-Plaza.jpg': '',
  'images/Sinbad%20Logo.jpg': '',
  'images/SouthLogo09.jpg': '',
  'images/UKPRobinHoodLogo_new.jpg': '',
  'images/WISHdiclogo.jpg': '',
  'images/aldershotwizlogo.jpg': '',
  'images/bath_panto_logo.jpg': '',
  'images/beauty_artwork.jpg': '',
  'images/brightonozlogo.jpg': '',
  'images/camb08hi-res-logo.jpg': '',
  'images/cambridgediclogo.jpg': '',
  'images/carlisle07words.jpg': '',
  'images/chennailogo2007.jpg': '',
  'images/goldilocksqdoslogo.gif': '',
  'images/hammondpanlogo.jpg': '',
  'images/keydiclogo.jpg': '',
  'images/littlemermaidNEW_temp.jpg': '',
  'images/millfieldlogo09.jpg': '',
  'images/npp-beautyweb.jpg': '',
  'images/nppaladweb.jpg': '',
  'images/nppswweb.jpg': '',
  'images/pussinbootssmall.jpg': '',
  'images/rhyl_panto_logo.jpg': '',
  'images/robinsoncrusoeNEW2008logo.gif': '',
  'images/santawinterwonderlan.jpg': '',
  'images/sheffield_panto_logo.jpg': '',
  'images/south08logo.jpg': '',
  'images/tamesidehippodrime.gif': '',
  'images/windsorlogo08.jpg': '',
}
shortCuts = [
    ("aladdin","Aladdin"),
    ("batb","Beauty and the Beast"),
    ("cinder","Cinderella"),
    ("dick","Dick Whittington"),
    ("beanstalk","Jack and the Beanstalk"),
    ("jack","Jack and the Beanstalk"),
    ("goose","Mother Goose"),
    ("peter","Peter Pan"),
    ("sleep","Sleeping Beauty"),
    ("snow","Snow White"),
    ("wizard","The Wizard of Oz"),
    ]
def getTitleOfImage(img):
  if img in imageList:
    return imageList[img]
  img = img.lower()
  for i in shortCuts:
    if i[0] in img:
      return i[1]
