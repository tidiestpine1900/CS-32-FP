import random
import json

# This is a separation line, for aesthetics. 
global line 
line = "----------------------------------------------------------"

# This function loads a random data (1000 Spotify playlists) as the "library". The randomness keeps the playlist production fresh, even if user gives the same input several times.
def loaddata():
    options = ['mpd.slice.995000-995999.json', 'mpd.slice.996000-996999.json', 'mpd.slice.997000-997999.json', 'mpd.slice.998000-998999.json', 'mpd.slice.999000-999999.json']

    data = random.choice(options)
    
    f = open(data)
    library = json.load(f)

    return library

# This function grabs the length of the new playlist the user wants.
def getlength():
    while True:
        length = int(input("How many songs would you like in your playlist? "))
        if length > 0 and length < 31:
            break
        print("Enter a whole number in the range of [1, 30].")
    
    return length

# This functions grabs the playlist split the user wants. Split = % of playlist that should be the favorite artist's songs
def getsplit():
    while True:
        split = int(float(input("What percentage of the playlist would you like to be brand new? ")))
        if split >= 0 or split <= 100:
            break
        print("Enter a whole number in the range of [0, 100].")
    return ((100 - split) / 100)

# This functions grabs the user's favorite artist, which is not case-sensitive.
def getartist():
    while True:
        artist = (input("Who is your favorite artist? ")).lower()
        if len(artist) > 0:
            break
        print("Enter an artist name.")
    
    return artist
    
# This function welcomes the user and prompts them to provide all the necessary inputs.
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

# This function searches for all playlists within the library that contain the favorite artist and stores those playlist indices.
def searchartist(library, length, artist, playlist, status, split):
    
    playlist_matches = []
    
    for i in range(len(library["playlists"])):
        for j in range(len(library["playlists"][i]["tracks"])):
            curr_artist = (library["playlists"][i]["tracks"][j]["artist_name"]).lower()
            if curr_artist == artist:
                playlist_matches.append(i)

    # If there are enough artist songs to fulfill the user "split" request, status = 0
    # If there are some artist songs, but not enough to fulfill "split" request, status = 2
    if (len(playlist_matches) > 0) & (len(playlist_matches) < int(split * length)):
        status = 2
    # If there are no found artist songs in any of the 1000 playlists, then status = 1
    elif len(playlist_matches) == 0:
        status = 1

    playlist_matches = set(playlist_matches)
    playlist_matches = list(playlist_matches)

    return(playlist_matches, status)

# This function loads in the familiar-songs portion of the playlist by pulling the requested number of songs
# from the favorite artist from existing playlists.
def loadartist(library, length, artist, playlist, status, split):    
    
    working_playlists, status = searchartist(library, length, artist, playlist, status, split)

    # If status != 1, then there are some favorite artist songs to find. 
    if status != 1: 
        while True: 
            supply = random.choice(working_playlists)
            songs = []
            for i in range(len(library["playlists"][supply])):
                for j in range(len(library["playlists"][supply]["tracks"])):
                    curr_artist = (library["playlists"][supply]["tracks"][j]["artist_name"]).lower()
                    if curr_artist == artist:
                        songs.append(library["playlists"][supply]["tracks"][j]["track_name"])
            # Randomly choose one of the artist's songs to add to the playlist.
            song = random.choice(songs)
            # We only want unique song recommendations, not duplicates.
            unique_songs = list(set(songs))

            if song not in playlist["song"]: 
                # Adding songs and artist credits to new playlist
                playlist["song"].append(song)
                playlist["artist"].append(artist)
            # If there are enough artist songs to fullfil "split" request, then stop at the requested number
            if status == 0:
                stop = int(split * length)
                # Account for case when the requested number of familiar songs is < 1.
                if (split * length) < 1:
                    playlist["song"].pop()
                    playlist["artist"].pop()
            # If there are not enough artist songs to fulfill "split" request, then stop once all available songs have been added
            else: 
                stop = len(unique_songs)
            if len(playlist["song"]) >= (stop):
                break

    return(playlist, status)

# This function loads in new, unfamiliar (but related!) songs once the familiar, favorite-artist "split" request has been fulfillec
def loadnew(library, length, artist, playlist, status, split):
    
    working_playlists, status = searchartist(library, length, artist, playlist, status, split)

    # If favorite artist was found in existing playlists, then make sure to only load non-favorite-artist songs from their playlists
    if status != 1:
        while True: 
            supply = random.choice(working_playlists)
            songs = []
            musicians = []
            for i in range(len(library["playlists"][supply])):
                for j in range(len(library["playlists"][supply]["tracks"])):
                    curr_artist = (library["playlists"][supply]["tracks"][j]["artist_name"]).lower()
                    # If the song artist is not the favorite artist, then the song is a new one. We want it.
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
    # If artist was not found, then just load random songs from the existing playlists.
    else: 
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

# This function makes the playlist by calling two functions, one to deal with familiar songs, and another to load new ones.
def makeplaylist(library, length, artist, split):
    # An emply playlist
    playlist =  {                
        "song": list(),
        "artist": list()
    }
    status = 0

    # Load familiar songs first
    playlist, status = loadartist(library, length, artist, playlist, status, split)

    # If split < 1, then the user wants at least some new songs. In this case, load those new songs now. 
    if split < 1:
        playlist, status = loadnew(library, length, artist, playlist, status, split)

    return[playlist, status]

# This function displays the final playlist, artist credits, and some information for the user
def display(status, playlist, artist, length, split):
    # A fully compliant playlist
    if status == 0:
        print(f"Here it is: a playlist {round(split * 100)}% {artist.title()} and {round((1 - split) * 100)}% new. Enjoy!\n") 
    # Artist wasn't found
    elif status == 1:
        if split < 1:
            print(f"Couldn't find your artist, but here are {length} new songs \nfor you... a few more than you asked for. Enjoy!\n")
        elif (split == 1) & (len(playlist["song"]) == 0):
            print("No playlist for you. You found a really niche edge case!!")   
    # Artist was found, but not enough songs of theirs were
    else:
        print(f"I could only find a few {artist} songs, so you get\nmore new songs than you asked for. Enjoy!\n")
    for song in (range(len(playlist["song"]))):
        print(f'{playlist["song"][song]} - {playlist["artist"][song].title()}')

    print(line)

# This is the main() function. Everything runs from here.
def main():
    # Load Spotify playlist data.
    library = loaddata()

    # Welcome messages, get playlist details.
    length, split, artist = welcome()

    # Make playlist.
    [playlist, status] = makeplaylist(library, length, artist, split)

    # Display final messages. The fruits of my labor. 
    display(status, playlist, artist, length, split)

if __name__ == '__main__':
    main()
