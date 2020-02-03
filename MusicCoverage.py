import re
import urllib
from sgmllib import SGMLParser  # to help with some HTML

def getForkURLs():
    '''Reads Pitchfork pages, finds longest line in each, and finds
    strings in the line that come after /reviews/albums/. Makes a big list
    of these strings for all pages.
    INPUTS: none
    OUTPUTS: allreviewlinks (list) - list of URL fragments'''

    ## Try the test function testForkURLs in TestFunctions.py.
    ## It is identical to this function, but works on a smaller dataset.

    allreviewlinks = []
    fragment_regex = re.compile('(?<=/reviews/albums/)(.*?)/')
    
    # Cycle through pages that possibly link to reviews written in 2011.
    for pagenumber in range(23,87):
        url = 'http://pitchfork.com/reviews/albums/' + str(pagenumber)
        myURLFile = urllib.urlopen(url)
        myString = myURLFile.read()
        myURLFile.close()

        # Get the longest line in each page source.
        # longestLine contains the actual links to the reviews.
        myList = myString.split('\n')
        longestLine = ''
        for line in myList:
            if len(line) > len(longestLine):
                longestLine = line
        myStr = longestLine
        
        # Find the 20 review links in longestLine.
        # Positive lookbehind assertion fetches a URL fragment that comes after each match.
        # These link fragments get put in a list, and will be used in getForkInfo.
        reviewlinks = fragment_regex.findall(myStr) 
        del reviewlinks[20:]  # remove extraneous fragments
        allreviewlinks.extend(reviewlinks) # add onto cumulative list of links
   
    return allreviewlinks

def getForkInfo():
    '''Loops through URLs of individual reviews via URL trick (using the link fragments
    obtained from getForkURLs). Takes reviews published in 2011, and for each, writes artist name to a file.
    INPUTS: none
    OUTPUTS: none'''
    ### This takes forever! Try running the test function testForkInfo in TestFunctions.py.

    # Since the expressions are used over and over, it seems more efficient to save these.
    date_regex = re.compile('(?<="pub-date">)(.*?)(201\d)')
    artist_regex = re.compile('(?<=h1>)<a\s\href="(.*?)">(.*?)</a></h1>')
    alt_artist_regex = re.compile('(?<="info">)\s<h1>(.*?)</h1>')
    collab_artist_regex = re.compile('(?<=h1>)<a\s\href="(.*?)">(.*?)</a>\s/\s(.*?)">(.*?)</')
    
    allreviewlinks = getForkURLs()
    infofile = open('fork_artists.txt','w')
    artist_noduplicates = []
    
    # URL trick
    for link in allreviewlinks:
        url = 'http://pitchfork.com/reviews/albums/' + link
        myURLFile = urllib.urlopen(url)
        myString = myURLFile.read()
        myURLFile.close()

        # Luckily, the longest line happens to contain everything we need.
        # It has the publication date of the review and the artist's name.
        myList = myString.split('\n')
        longestLine = ''
        for line in myList:
            if len(line) > len(longestLine):
                longestLine = line
        myStr = longestLine

        dateMatch = date_regex.search(myStr, 100, 700)
        # Preventing potential error. Some pages don't have everything we need on one line.
        # For such pages, search the entire page instead of just one line.
        if dateMatch == None:
            dateMatch = date_regex.search(myString)
        pubdateStr = dateMatch.group(2)
        # Need to ignore any links we may have gotten that aren't for reviews published in 2011.
        # If year of publication is not 2011, pass. If it is, move on.
        if pubdateStr != '2011':
            pass
        else:
            # Three possible situations for how Pitchfork formats artist names:
                # (1) <h1><a href="/artists/1477-fennesz/">Fennesz</a> / <a href="/artists/5272-sakamoto/">Sakamoto</a></h1>
                # (2) <h1><a href="/artists/27233-the-lonely-island/">The Lonely Island</a></h1>
                # (3) <div class="info"> <h1>Various Artists</h1>
            # These nested statements account for each case. This must be done to avoid an exception being thrown.
            artistMatch = collab_artist_regex.search(myStr, 100, 800)
            if artistMatch == None:
                artistMatch = artist_regex.search(myStr, 100, 800)
                if artistMatch == None:
                    artistMatch = alt_artist_regex.search(myStr, 100, 800)
                    artistStr = artistMatch.group(1)
                else:
                    artistStr = artistMatch.group(2)
            else:
                artistStr = artistMatch.group(2) + ' coll. ' + artistMatch.group(4)

            # write artists to file, separated by newline
            infofile.write(artistStr + '\n')
    
    infofile.close()
    return

class artistGetter(SGMLParser):
    '''Used in getStoneInfo() - below - to extract artist names from inside nested
    HTML tags on the Rolling Stone website.'''
    def reset(self):
        SGMLParser.reset(self)
        self.artists = []
        self.in_h3 = False
        self.in_a = False
    # As soon as the parser hits an <h3> tag, our first criterion is fulfilled.
    def start_h3(self, attrs):
        self.in_h3 = True
    # When an <a> tag is encountered, check if it has href as an attribute.
    # Also check if the href value is the kind of link we want, for the year that we want.
    # If all this is true, then our second criterion is fulfilled.
    def start_a(self, attrs):
        for a, b in attrs:
            if a=='href' and b.startswith('/music/albumreviews/') and '-2011' in b:
                self.in_a = True
    # boolean becomes false as soon as tag is exited
    def end_h3(self):
        self.in_h3 = False
    def end_a(self):
        self.in_a = False
    # for data that satisfies all the criteria, i.e. is an artist name, add data to list
    def handle_data(self, data):
        if self.in_h3 and self.in_a:
            self.artists.append(data)

def getStoneInfo():
    '''Fetches album reviews published by Rolling Stone in 2011 and writes artist names
    to the file 'stone_artists.txt'.
    INPUTS: none
    OUTPUTS: none'''
    ## Already-completed file is included in the project folder.
    ## This function has a corresponding test function, testStoneInfo, in TestFunctions.py.
    
    infofile = open('stone_artists.txt','w')
    for pagenum in range(16,66):
        url = 'http://www.rollingstone.com/music/albumreviews?page=' + str(pagenum)
        myURLFile = urllib.urlopen(url)
        myString = myURLFile.read()
        myURLFile.close()
        artistparser = artistGetter()
        artistparser.feed(myString)  # feed the parser some HTML
        artistparser.close()
        artistlist = artistparser.artists
        artistfinal = []
        artist_noduplicates = []
        for artist in artistlist:
            # Clean the artist name strings.
            # Otherwise, they show up like this: '\n\t\t\t\t\t\t\t\t\t\tT-Pain\t\t\t\t\t\t\t\t\t'
            artist = artist[11:(len(artist)-9)]
            artistfinal.append(artist)
        for artist in artistfinal:
            infofile.write(artist + '\n')
    infofile.close()

    # clean away some strange bits of text in stone_artists.txt
    cleanStoneInfo()

    # Use the file of artist names to make a duplicate-free list of
    # artist names.
    myfile = open('stone_artists.txt','r')
    mystring = myfile.read()
    myfile.close()
    mystring = mystring.split('\n')
    for artist in mystring:
        if artist not in artist_noduplicates:
                artist_noduplicates.append(artist)

    # Look up every artist reviewed by Rolling Stone in 2011
    # and make a list of all associated genres.
    stonegenres_all = []
    for name in artist_noduplicates:
        stonegenre = getGenre(name)
        stonegenres_all.append(stonegenre)

    # sort genre list
    stonegenres = stonegenres_all.sort()
    
    genre_count = 0
    for i in range(1, len(stonegenres_all)):
        # If the current genre is the same as the one before it in the list, do nothing.
        if stonegenres_all[i] == stonegenres_all[i-1] and i < len(stonegenres_all):
            pass
        else:
            # If they're different, get the previous genre and count its occurrences in the list.
            # This tells us how many artists belong to each genre.
            # Also add 1 to the running total of how many distinct genres there are.
            genre_count += 1
            if stonegenres_all[i-1] == '':
                pass
            else:
                print stonegenres_all.count(stonegenres_all[i-1]),'RS-reviewed artist(s) practiced',stonegenres_all[i-1]
    print 'In 2011, Rolling Stone published',len(mystring),'album reviews.'
    print 'These reviews represented',len(artist_noduplicates),'different artists.'
    print 'These artists represent',genre_count,'different genres.'
    return

def cleanStoneInfo():
    '''Takes the file that was written in getStoneInfo and makes cosmetic improvements.
    Is called in getStoneInfo, above.
    INPUTS: none
    OUTPUTS: none'''
    # Straightforward. Same technique as in Data Import help file from class.
    myFile = open('stone_artists.txt','r')
    myString = myFile.read()
    myFile.close()

    myString = re.sub('&quot;','"',myString)
    myString = re.sub('&#039;','\'',myString)
    myString = re.sub(';\sroperty=(.*?)/>;', '', myString)
    myString = re.sub('&amp;','&',myString)
    
    outFile = open('stone_artists.txt','w')
    outFile.write(myString)
    outFile.close()
    return

def forkFinalInfo():
    '''Opens the file containing artist names for Pitchfork reviews and
    ultimately prints out facts about Pitchfork's coverage in 2011, e.g.
    how many reviews were published, how much variety of artist and genre was
    captured by those reviews, and the popularity of different genres.
    INPUTS: none
    OUTPUTS: none'''

    artist_noduplicates = []
    forkgenres_all = []
   
    myfile = open('fork_artists.txt','r')
    mystring = myfile.read()
    myfile.close()
    mystring = mystring.split('\n')
    for artist in mystring:
        if artist not in artist_noduplicates:
                artist_noduplicates.append(artist)

    for forkartist in artist_noduplicates:
        forkgenre = getGenre(forkartist)
        forkgenres_all.append(forkgenre)

    # sort genre list
    forkgenres = forkgenres_all.sort()

    # If the current genre is the same as the one before it in the list, do nothing.
    # If they're different, get the previous genre and count its occurrences in the list.
    # This tells us how many artists are identified as belonging to each genre.
    genre_count = 0
    for i in range(1, len(forkgenres_all)):
        if forkgenres_all[i] == forkgenres_all[i-1] and i < len(forkgenres_all):
            pass
        else:
            genre_count += 1  # add to the count we're keeping of distinct genres
            if forkgenres_all[i-1] == '':
                pass
            else:
                print forkgenres_all.count(forkgenres_all[i-1]),'P4k-reviewed artist(s) practiced',forkgenres_all[i-1]

    print 'In 2011, Pitchfork published',len(mystring),'album reviews.'
    print 'These reviews represented',len(artist_noduplicates),'different artists.'
    print 'These artists represent',genre_count,'different genres.'
    return

class genreGetter(SGMLParser):
    '''Another SGMLParser subclass. This is used in the function getGenre() - at the bottom of this file - to
    scrape the last.fm site for information about what genres an artist is associated with.'''
    def reset(self):
        SGMLParser.reset(self)
        self.genres = []
        self.in_div = False
        self.in_meta = False
    # When <div> is encountered, check if it has 'class' as an attribute.
    # Also check if the 'class' value is 'tags'.
    # If all this is true, then our first criterion is fulfilled.
    def start_div(self, attrs):
        for a, b in attrs:
            if a=='class' and b=='tags':
                self.in_div = True
    # When <meta is encountered, check if it has 'content' as an attribute.
    # If it does, then our second criterion is fulfilled.
    def start_meta(self, attrs):
        for a, b in attrs:
            if a=='content':
                self.in_meta = True
    def end_div(self):
        self.in_div = False
    def end_meta(self):
        self.in_meta = False
    # for data that satisfies all the criteria, i.e. is (hopefully) a popular
    # genre tag for the artist, add data to list of genres for the artist
    def handle_data(self, data):
        if self.in_div and self.in_meta:
            self.genres.append(data)

def getGenre(artistname):
    '''Given an artist, this function looks up the artist
    on the music site last.fm and returns what last.fm says
    the artist's genre is.
    INPUTS: artistname (string) - artist to look up
    OUTPUTS: genre (string) - genre of looked-up artist'''
    # Add artist name to the main url in a way that fits
    # the format of the music site's URLs, i.e. in a way that
    # takes the words of the artist's name and tacks them onto the end
    # of the main url, separated by plus signs. Note that the last part
    # of the artist name should not have a plus sign after it.
    artistname = artistname.split()
    artiststr = ''
    genre = ''
    for i in range(0,len(artistname)):
        if artistname[i] not in artiststr and i != len(artistname) - 1:
            artistname[i] = artistname[i] + '+'
        artiststr = artiststr + artistname[i]
    url = 'http://www.last.fm/music/' + artiststr
    myURLFile = urllib.urlopen(url)
    myString = myURLFile.read()
    myURLFile.close()
    # Getting rid of something potentially error-causing. I was
    # getting an SGMLParseError that said "expected name token."
    myString = re.sub('<!(.*)endi','',myString)
    genrelist = []
    genreparser = genreGetter()
    genreparser.feed(myString)  # feed the parser
    genreparser.close()
    genrelistrough = genreparser.genres
    if genrelistrough == []:
        pass
    else:    
        genrelistclean = genrelistrough[3:13]  # clean up
        # Get the first string in the list. With this music site, the first
        # Popular Tag is the one that tends to be a legitimate genre name and
        # not some random user-tagged category like "swag".
        genre = genrelistclean[0]
    return genre


