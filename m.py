import random
import json
global line 
line = "----------------------------------------------------------"

def loaddata():
    options = ['mpd.slice.995000-995999.json', 'mpd.slice.996000-996999.json', 'mpd.slice.997000-997999.json', 'mpd.slice.998000-998999.json', 'mpd.slice.999000-999999.json']

    data = random.choice(options)
    
    f = open(data)
    library = json.load(f)

    return library
    
def getlength():
    while True:
        length = int(input("How many songs would you like in your playlist? "))
        if length > 0 and length < 31:
            break
        print("Enter a whole number in the range of [1, 30].")
    
    return length

def getsplit():
    while True:
        split = int(float(input("What percentage of the playlist would you like to be brand new? ")))
        if split >= 0 or split <= 100:
            break
        print("Enter a whole number in the range of [0, 100].")
    return ((100 - split) / 100)

def getartist():
    while True:
        artist = (input("Who is your favorite artist? ")).lower()
        if len(artist) > 0:
            break
        print("Enter an artist name.")
    
    return artist
    
def welcome():
    print(line)
    print("Hi! Welcome to the Playlist Producer. It's what it sounds \nlike - I produce a playlist for you, and you enjoy it.\n")
    length = getlength()
    print("Life's all about exploration.\n")
    split = getsplit()
    print("\nPerfect. Let's get a sense of what you like.\n")
    artist = getartist()
    print(line)

    return(length, split, artist)

def searchartist(library, length, artist, playlist, status, split):
    
    playlist_matches = []
    
    # print(library.keys())
    # pulls first song of first playlist 
    #print(library["playlists"][0]["tracks"][0])
    for i in range(len(library["playlists"])):
        # print("\n\nPlaylist #: ", i + 1)
        for j in range(len(library["playlists"][i]["tracks"])):
            curr_artist = (library["playlists"][i]["tracks"][j]["artist_name"]).lower()
            if curr_artist == artist:
                # print("h")
                # print(library["playlists"][i])
                playlist_matches.append(i)

    #pulling individual playlists that have artist match
    if (len(playlist_matches) > 0) & (len(playlist_matches) < int(split * length)):
        status = 2
    elif len(playlist_matches) == 0:
        status = 1

    playlist_matches = set(playlist_matches)
    playlist_matches = list(playlist_matches)

    return(playlist_matches, status)
    # if for updating status according to how well the search has gone. keep 0 for fine, 1 for no artist at all? 2 for not enough artist findings?

def loadartist(library, length, artist, playlist, status, split):    
    working_playlists, status = searchartist(library, length, artist, playlist, status, split)

    if status != 1: #then there are some songs to find
        while True: 
            supply = random.choice(working_playlists)
            songs = []
            for i in range(len(library["playlists"][supply])):
                for j in range(len(library["playlists"][supply]["tracks"])):
                    curr_artist = (library["playlists"][supply]["tracks"][j]["artist_name"]).lower()
                    if curr_artist == artist:
                        songs.append(library["playlists"][supply]["tracks"][j]["track_name"])
            song = random.choice(songs)
            unique_songs = list(set(songs))

            if song not in playlist["song"]: 
                playlist["song"].append(song)
                playlist["artist"].append(artist)
            if status == 0:
                stop = int(split * length)
                if (split * length) < 1:
                    playlist["song"].pop()
                    playlist["artist"].pop()
            else: 
                stop = len(unique_songs)
            if len(playlist["song"]) >= (stop):
                break

    return(playlist, status)
    
def loadnew(library, length, artist, playlist, status, split):
    
    # print(library.keys())
    # pulls first song of first playlist 
    #print(library["playlists"][0]["tracks"][0])
    # for i in range(len(library["playlists"])):
    #     print("\n\nPlaylist #: ", i + 1)
    #     for j in range(len(library["playlists"][i]["tracks"])):
    #         print(library["playlists"][i]["tracks"][j]["artist_name"])

    working_playlists, status = searchartist(library, length, artist, playlist, status, split)

    if status != 1: #then there are some songs to find
        while True: 
            supply = random.choice(working_playlists)
            songs = []
            musicians = []
            for i in range(len(library["playlists"][supply])):
                for j in range(len(library["playlists"][supply]["tracks"])):
                    curr_artist = (library["playlists"][supply]["tracks"][j]["artist_name"]).lower()
                    if curr_artist != artist:
                        songs.append(library["playlists"][supply]["tracks"][j]["track_name"])
                        musicians.append(curr_artist)
            index = random.choice(range(len(songs)))
            song = songs[index]
            musician = musicians[index]

            if song not in playlist["song"]: 
                playlist["song"].append(song)
                playlist["artist"].append(musician)
            if len(playlist["song"]) == length:
                break
    else: #then there are some songs to find
        while True: 
            supply = random.choice(range(len(library["playlists"])))
            songs = []
            musicians = []
            for i in range(len(library["playlists"][supply])):
                for j in range(len(library["playlists"][supply]["tracks"])):
                    curr_artist = (library["playlists"][supply]["tracks"][j]["artist_name"]).lower()
                    songs.append(library["playlists"][supply]["tracks"][j]["track_name"])
                    musicians.append(curr_artist)
            
            index = random.choice(range(len(songs)))
            song = songs[index]
            musician = musicians[index]

            if song not in playlist["song"]: 
                playlist["song"].append(song)
                playlist["artist"].append(musician)
            if len(playlist["song"]) == length:
                break
                
    return(playlist, status)

def makeplaylist(library, length, artist, split):
    playlist =  {                
        "song": list(),
        "artist": list()
    }
    status = 0
    # Half the playlist will be (ideally) songs from that artist. To do this, randomly select length/2 songs by artist from playlists
    playlist, status = loadartist(library, length, artist, playlist, status, split)
    # The other half of the playlist will random songs from playlists that contained that artist. To do this, randomly select playlists with that artist, then randomly select length/2 total songs by not-artist from playlists
    if split < 1:
        playlist, status = loadnew(library, length, artist, playlist, status, split)
    ## if else ladder for message to accompany playlist according to status, aka details about playlist composition... all artist/new? half? none? 
    # print(playlist)
    return[playlist, status]

def display(status, playlist, artist, length, split):
    if status == 0:
        print(f"Here it is: a playlist {round(split * 100)}% {artist.title()} and {round((1 - split) * 100)}% new. Enjoy!\n") 
    elif status == 1:
        if split < 1:
            print(f"Couldn't find your artist, but here are {length} new songs \nfor you... a few more than you asked for. Enjoy!\n")
        elif (split == 1) & (len(playlist["song"]) == 0):
            print("No playlist for you. You found a really niche edge case!!")   
    else:
        print(f"I could only find a few {artist} songs, so you get\nmore new songs than you asked for. Enjoy!\n")
    for song in (range(len(playlist["song"]))):
        print(f'{playlist["song"][song]} - {playlist["artist"][song].title()}')

    print(line)

def main():
    # Load Spotify songs (.zip file)
    library = loaddata()

    # Welcome messages, get playlist details
    length, split, artist = welcome()

    # Make playlist
    [playlist, status] = makeplaylist(library, length, artist, split)

    display(status, playlist, artist, length, split)

if __name__ == '__main__':
    main()