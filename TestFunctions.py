import re
import urllib
import MusicCoverage  # allows us to use the SGMLParser subclasses from MusicCoverage.py

def testForkURLs():
    '''Tests getForkURLs for just two pages.'''
    allreviewlinks = []
    fragment_regex = re.compile('(?<=/reviews/albums/)(.*?)/')
    
    for pagenumber in range(23,25):
        url = 'http://pitchfork.com/reviews/albums/' + str(pagenumber)
        myURLFile = urllib.urlopen(url)
        myString = myURLFile.read()
        myURLFile.close()

        myList = myString.split('\n')
        longestLine = ''
        for line in myList:
            if len(line) > len(longestLine):
                longestLine = line
        myStr = longestLine
        
        reviewlinks = fragment_regex.findall(myStr)
        del reviewlinks[20:]
        allreviewlinks.extend(reviewlinks)
    
    return allreviewlinks  # Expect a list of strings that look similar to '16134-echoes-of-silence'

def testForkInfo():
    '''Tests getForkInfo for the two pages in testForkURLs.'''
    
    date_regex = re.compile('(?<="pub-date">)(.*?)(201\d)')
    artist_regex = re.compile('(?<=h1>)<a\s\href="(.*?)">(.*?)</a></h1>')
    alt_artist_regex = re.compile('(?<="info">)\s<h1>(.*?)</h1>')
    collab_artist_regex = re.compile('(?<=h1>)<a\s\href="(.*?)">(.*?)</a>\s/\s(.*?)">(.*?)</')
    
    allreviewlinks = testForkURLs()
    infofile = open('test_fork_info.txt','w')
    artist_noduplicates = []
    
    for link in allreviewlinks:
        url = 'http://pitchfork.com/reviews/albums/' + link
        myURLFile = urllib.urlopen(url)
        myString = myURLFile.read()
        myURLFile.close()

        myList = myString.split('\n')
        longestLine = ''
        for line in myList:
            if len(line) > len(longestLine):
                longestLine = line
        myStr = longestLine

        dateMatch = date_regex.search(myStr, 100, 700)
        if dateMatch == None:
            dateMatch = date_regex.search(myString)
            if dateMatch == None:
                continue
        pubdateStr = dateMatch.group(2)
        if pubdateStr != '2011':
            pass
        else:
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

            infofile.write(artistStr + '\n')
    
    infofile.close()

    myfile = open('test_fork_info.txt','r')
    mystring = myfile.read()
    myfile.close()
    mystring = mystring.split('\n')
    for artist in mystring:
        if artist not in artist_noduplicates:
                artist_noduplicates.append(artist)
    return

def testStoneInfo():
    '''Tests getStoneInfo for two pages only.
    INPUTS: none
    OUTPUTS: none'''
    
    infofile = open('test_stone_info.txt','w')
    for pagenum in range(21,23):
        url = 'http://www.rollingstone.com/music/albumreviews?page=' + str(pagenum)
        myURLFile = urllib.urlopen(url)
        myString = myURLFile.read()
        myURLFile.close()
        artistparser = MusicCoverage.artistGetter()
        artistparser.feed(myString)
        artistparser.close()
        artistlist = artistparser.artists
        artistfinal = []
        artist_noduplicates = []
        for artist in artistlist:
            artist = artist[11:(len(artist)-9)]
            artistfinal.append(artist)
        for artist in artistfinal:
            infofile.write(artist + '\n')
    infofile.close()

    testcleanstone()
    
    myfile = open('test_stone_info.txt','r')
    mystring = myfile.read()
    myfile.close()
    mystring = mystring.split('\n')
    for artist in mystring:
        if artist not in artist_noduplicates:
                artist_noduplicates.append(artist)
    
    stonegenres_all = []
    for name in artist_noduplicates:
        stonegenre = testGetGenre(name)
        stonegenres_all.append(stonegenre)

    stonegenres = stonegenres_all.sort()
    
    genre_count = 0
    for i in range(1, len(stonegenres_all)):
        if stonegenres_all[i] == stonegenres_all[i-1] and i < len(stonegenres_all):
            pass
        else:
            genre_count += 1
            if stonegenres_all[i-1] == '':
                pass
            else:
                print stonegenres_all.count(stonegenres_all[i-1]),'RS-reviewed artist(s) practiced',stonegenres_all[i-1]
    # These numbers will be much smaller than the values for the actual dataset.
    print 'In 2011, Rolling Stone published',len(mystring),'album reviews.'
    print 'These reviews represented',len(artist_noduplicates),'different artists.'
    print 'These artists represent',genre_count,'different genres.'
    return


def testcleanstone():
    '''Tests cleanStoneInfo.
    INPUTS: none
    OUTPUTS: none'''
    myFile = open('test_stone_info.txt','r')
    myString = myFile.read()
    myFile.close()

    myString = re.sub('&quot;','"',myString)
    myString = re.sub('&#039;','\'',myString)
    myString = re.sub(';\sroperty=(.*?)/>;', '', myString)
    myString = re.sub('&amp;','&',myString)
    
    outFile = open('test_stone_info.txt','w')
    outFile.write(myString)
    outFile.close()
    return

def testforkFinal():
    '''Tests forkFinalInfo.
    INPUTS: none
    OUTPUTS: none'''
    artist_noduplicates = []
    forkgenres_all = []
   
    myfile = open('test_fork_info.txt','r')
    mystring = myfile.read()
    myfile.close()
    mystring = mystring.split('\n')
    for artist in mystring:
        if artist not in artist_noduplicates:
                artist_noduplicates.append(artist)

    for forkartist in artist_noduplicates:
        forkgenre = testGetGenre(forkartist)
        forkgenres_all.append(forkgenre)

    forkgenres = forkgenres_all.sort()

    genre_count = 0
    for i in range(1, len(forkgenres_all)):
        if forkgenres_all[i] == forkgenres_all[i-1] and i < len(forkgenres_all):
            pass
        else:
            genre_count += 1
            if forkgenres_all[i-1] == '':
                pass
            else:
                print forkgenres_all.count(forkgenres_all[i-1]),'P4k-reviewed artist(s) practiced',forkgenres_all[i-1]
    print 'In 2011, Pitchfork published',len(mystring),'album reviews.'
    print 'These reviews represented',len(artist_noduplicates),'different artists.'
    print 'These artists represent',genre_count,'different genres.'
    return


def testGetGenre(artistname):
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
  
    myString = re.sub('<!(.*)endi','',myString)
    
    genrelist = []
    genreparser = MusicCoverage.genreGetter()
    genreparser.feed(myString)
    genreparser.close()
    genrelistrough = genreparser.genres
    if genrelistrough == []:
        pass
    else:    
        genrelistclean = genrelistrough[3:13]
        genre = genrelistclean[0]
    return genre

