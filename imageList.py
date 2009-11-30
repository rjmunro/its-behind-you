imageList = {
  'images/09DuoCindlogo.jpg': 'Cinderella',
  'images/robinhoodNEW2008logo.gif': 'Robin Hood',
  'images/nppcindlow.jpg': 'Cinderella',
  'images/CambLogoNew.jpg': 'Cinderella',
  'images/ChelmsfordLogo07.jpg': 'Jack and the Beanstalk',
  'images/hammondbeautylogo.jpg': 'Sleeping Beauty',
  'images/BeautyLogoNots09.jpg': 'Beauty and the Beast',
  'images/SloughLogo07.jpg': 'Aladdin',
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
    ]
def getTitleOfImage(img):
  if img in imageList:
    return imageList[img]
  img = img.lower()
  for i in shortCuts:
    if i[0] in img:
      return i[1]
