import getpass
import uuid
import hashlib
import curses
import time
import mysql.connector
from mysql.connector import Error
import random

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='spotify',
                                         user='root',
                                         password = 'Pass2myword')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)

mycursor = connection.cursor()
# finally:
#     if (connection.is_connected()):
#         cursor.close()
#         connection.close()
#         print("MySQL connection is closed")

menu = ['SIGN UP', 'SIGN IN', 'QUIT']
role = ['Artist', 'User']
artist_can = ['New Album', 'QUIT']
user_can = ['Unfollow']

def print_menu_role(stdscr, selected_row_idx, menu_role) :
    
    # stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    for idx, row in enumerate(menu_role) :
        x = w//2 - len(row)//2
        y = h//2 - len(menu)//2 + idx
        if idx == selected_row_idx: 
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else :
            stdscr.addstr(y, x, row)
        

    stdscr.refresh()

def motion(stdscr, some_menu, *name_username):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_WHITE)

    current_row_idx = 0
    stdscr.addstr(0, 45, "Welcom To Spotify!")
    print_menu_role(stdscr, current_row_idx, some_menu)

    while (1) :
        key = stdscr.getch()
        stdscr.clear()

        #KEY_UP
        if key == ord("w") and current_row_idx > 0:
            # stdscr.addstr(0, 0, "you pressed up")
            current_row_idx -= 1
        #KEY_DOWN
        elif key == ord("s") and current_row_idx < len(some_menu) - 1:
            current_row_idx += 1
        #ENTER KEY
        elif key == curses.KEY_ENTER or key in [10, 13]:
            stdscr.addstr(0, 0, "you pressed {}".format(some_menu[current_row_idx]))
            if some_menu[current_row_idx] == 'SIGN UP':
                artist_action_signup(stdscr)
            elif some_menu[current_row_idx] == 'SIGN IN':
                artist_action_signin(stdscr)
            elif some_menu[current_row_idx] == 'New Album':
                artist_action_new_album(stdscr, name_username)
            elif menu[current_row_idx] == 'QUIT':
                break
        
        


# def show_columns(mycursor):
#     mycursor.execute("select * FROM artist")
#     records = mycursor.fetchall()
#     for row in records :
#         print ("id = ", row[0], )
#         print ("hashed_password = ", row[1], )
#         print ("username = ", row[2], )
#         print ("about = ", row[3], )
#         print ("is_verified = ", row[4], )
#         print('\n')

def check_username(username):
    mycursor.execute("select * from artist where username = '{}'" .format(username))
    record = mycursor.fetchall()
    if len(record) != 0 :
        return False 
    return True

def hash_password(password):
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

def decide_verification() :
    return random.randint(0, 1)

def number_of_plays():
    return random.randint(0, 50000)

def sign_up(password, username):
    is_verified = decide_verification() 
    hashed_password = hash_password(password)
    mycursor.execute("INSERT INTO artist(hashed_password, username, about, is_verified) VALUES ('{}', '{}', NUll, {})".format(hashed_password, username, is_verified))
    connection.commit()

def get_pass_from_db(username):
    mycursor.execute("select hashed_password from artist where username = '{}'".format(username))
    record = mycursor.fetchall()
    return record[0][0]

def get_artist_id(username):
    mycursor.execute("select id from artist where username = '{}'".format(username))
    record = mycursor.fetchall()
    return record[0][0]

def get_album_id(title):
    mycursor.execute("select id from album where title = '{}'".format(title))
    record = mycursor.fetchall()
    return record[0][0]

def artist_followers(username):
    id = get_artist_id(username)
    mycursor.execute("select user_id from artist_follow where artist_id = {}".format(id))
    record = mycursor.fetchall()
    return len(record)

def artist_albums(username):
    id = get_artist_id(username)
    albums = []

    mycursor.execute("select count(album_id) from inside where artist_id = {}".format(id))
    records = mycursor.fetchall()

    if records[0][0] != 0 :
        mycursor.execute("select title from album where id in (select album_id from inside where artist_id = {})".format(id))
        records = mycursor.fetchall()
        for row in records:
            albums += row

    return albums 

def monthly_listeners():
    return random.randint(1, 30000)

def show_dashboard(username, stdscr):
    stdscr.clear()
    curses.curs_set(0)

    stdscr.attron(curses.color_pair(2))
    stdscr.border(00000000)
    stdscr.addstr(0, 0, "Dashboard!")
    stdscr.addstr(0, 40, username)

    number_of_followers = artist_followers(username)
    albums = artist_albums(username)
    number_of_albums = len(albums)

    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(3, 5, "{} albums: ".format(number_of_albums))
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(1, 5, "followers : {}".format(number_of_followers))
    
    idx = 25
    for row in albums:
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(3, idx, "{}".format(row))
        idx += 12
    
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(1, 25, "monthly listeners: {}".format(str(monthly_listeners())))
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(5, 5, "New album ('n'), Add songs ('a'), Add participants ('p'), Quit ('q') ?")
    key = stdscr.getch()
    if key == ord("n"):
        artist_action_new_album(stdscr, username)
    elif key == ord("a") :
        artist_action_new_songs(stdscr, username)
    elif key == ord("p"):
        artist_action_add_new_participant(stdscr, username)
    elif key == ord("q"):
        exit()

def get_current_date():
    mycursor.execute("select curdate()")
    record = mycursor.fetchall()
    return record[0][0]

def artist_action_new_album(stdscr, username):
    stdscr.addstr(5, 5, "Enter Album's title:")
    title = stdscr.getstr()
    date = get_current_date()
    stdscr.addstr(0, 0, "Single or Ep or Album ?")
    key = chr(stdscr.getch())
    stdscr.addstr(0, 0, "Copyright : ")
    copy_right = stdscr.getstr()
    create_new_album(username, title, date, key, copy_right)

def create_new_album(username, title, date, single_or_ep, cp):
    artist_id = get_artist_id(username)
    mycursor.execute("insert into album(title, release_year, copyright, is_single_or_ep) values ('{}', '{}', '{}', '{}')".format(title, date, cp, single_or_ep))
    connection.commit()
    album_id = get_album_id(title)
    mycursor.execute("insert into inside(artist_id, album_id, is_owner) values ({}, {}, 1)".format(artist_id, album_id))
    connection.commit()

def artist_action_new_songs(stdscr, username):
    curses.echo()
    stdscr.addstr(0, 0, "Which album?")
    album_title = stdscr.getstr()
    stdscr.addstr(0, 0, "Enter name of the new Song :")
    music_title = stdscr.getstr()
    stdscr.addstr(0, 0, "Song Duration :")
    music_duration = stdscr.getstr()
    is_explicit = random.randint(0,1)
    stdscr.addstr(0, 0, "Status ?")
    is_active = stdscr.getstr()
    played_number = number_of_plays()
    stdscr.addstr(0, 0, "File reference :")
    reference = stdscr.getstr()
    stdscr.addstr(0, 0, "Cover reference :")
    cover_reference = stdscr.getstr()

    add_new_songs(stdscr,album_title, music_title, music_duration, is_explicit, is_active, played_number, reference, cover_reference)

def add_new_songs(stdscr,album_title, title, dur, exp, acv, played_num, f_ref, c_ref):
    album_id = get_album_id(album_title)
    mycursor.execute("insert into music(title, duration, number_of_plays, file_reference, is_active, is_explicit, cover_reference, album_id) values ('{}', '{}', {}, '{}', {}, {}, '{}', {})".format(title, dur, played_num, f_ref, acv, exp, c_ref, album_id) )
    connection.commit()

def artist_action_add_new_participant(stdscr, username):
    stdscr.addstr(0, 0, "Enter name of the album :")
    album_name = stdscr.getstr()
    album_id = get_album_id(album_name)
    stdscr.addstr(0, 0, "Enter username of participant :")
    part_username = stdscr.getstr()
    artist_id = get_artist_id(part_username)

    add_new_participant(stdscr, album_id, artist_id)

def add_new_participant(stdscr, album_id, artist_id):
    mycursor.execute("insert into inside (artist_id, album_id, is_owner) values({}, {}, 1)".format(artist_id, album_id))
    connection.commit()

def sign_in(username, password, stdscr): #show artist_dashboard
    curses.curs_set(0)
    stdscr.clear()
    show_dashboard(username, stdscr)

    stdscr.refresh()
    time.sleep(5)

##############
########################
#########################################   USER
########################
##############

def user_motion(stdscr, menu):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_WHITE)

    current_row_idx = 0
    stdscr.addstr(0, 45, "Welcom To Spotify!")
    print_menu_role(stdscr, current_row_idx, menu)
    
    while (1) :
        key = stdscr.getch()
        stdscr.clear()

        #KEY_UP
        if key == ord("w") and current_row_idx > 0:
            current_row_idx -= 1
        #KEY_DOWN
        elif key == ord("s") and current_row_idx < len(menu) - 1:
            current_row_idx += 1
        #ENTER KEY
        elif key == curses.KEY_ENTER or key in [10, 13]:
            stdscr.addstr(0, 0, "you pressed {}".format(menu[current_row_idx]))
            if menu[current_row_idx] == 'SIGN UP':
                user_action_signup(stdscr)
            elif menu[current_row_idx] == 'SIGN IN':
                user_action_signin(stdscr)
            elif menu[current_row_idx] == 'QUIT':
                exit()

            stdscr.refresh()
            stdscr.getch()

        print_menu_role(stdscr, current_row_idx, menu)
        stdscr.refresh()
    
def check_email(email):
    mycursor.execute("select * from user where email = '{}'" .format(email))
    record = mycursor.fetchall()
    if len(record) != 0 :
        return False 
    return True
    
def user_action_signup(stdscr):
    stdscr.clear()
    curses.echo()

    stdscr.addstr(0, 0, "Enter a name :")
    name = stdscr.getstr()
    stdscr.addstr(0, 0, "Enter your country :")
    land = stdscr.getstr()
    stdscr.addstr(0, 0, "Enter your image location :")
    image_ref = stdscr.getstr()
    stdscr.addstr(0, 0, "Enter an email :")
    email = stdscr.getstr()
    while (check_email(email) != True):
        stdscr.addstr(0, 0, "invalid email :( Enter another email address :")
        email = stdscr.getstr()


    stdscr.clear()
    curses.noecho()
    stdscr.addstr(0, 0, "enter password")
    password = stdscr.getstr()
    stdscr.addstr(0, 0, "enter password again")
    password_again = stdscr.getstr()
    while (password != password_again):
        stdscr.addstr(0, 0, "enter password again")
        password_again = stdscr.getstr()

    user_signup(stdscr, email, name, password, land, image_ref)
    stdscr.clear()
    stdscr.refresh()

def user_signup(stdscr, email, name, password, land, image_ref):
    hashed_password = hash_password(password)   
    mycursor.execute("INSERT INTO user(image_reference, hashed_password, land, email, name) VALUES ('{}', '{}', '{}', '{}', '{}')".format(image_ref, hashed_password, land, email, name))
    connection.commit()

def get_user_name(email):
    mycursor.execute("select name from user where email = '{}'".format(email))
    record = mycursor.fetchall()
    return record[0][0]

def get_user_pass_from_db(email):
    mycursor.execute("select hashed_password from user where email = '{}'".format(email))
    record = mycursor.fetchall()
    return record[0][0]

def user_action_signin(stdscr):
    h, w = stdscr.getmaxyx()
    x = w//2
    y = h//2

    curses.echo()
    stdscr.addstr(0, 0, "Enter your email")
    email = stdscr.getstr()
               
    #checking for unique username
    while (check_email(email) != False) :
        stdscr.clear()
        stdscr.addstr(0, 0, "email is not correct :( try again: ")
        email = stdscr.getstr()
        
    #checking for correct password
    stdscr.clear()
    curses.noecho()
    stdscr.addstr(0, 0, "enter password")
    password = stdscr.getstr()
    hashed_pass = get_user_pass_from_db(email)
    check_password(hashed_pass, password)
    while (check_password(hashed_pass, password) != True):
        stdscr.addstr(0, 0, "password not correct ... try again: ")
        password = stdscr.getstr()
        # check_password(hashed_pass, password)
    
    user_sign_in(email, password, stdscr)
    stdscr.clear()
    stdscr.refresh()
    # time.sleep(3)

def user_sign_in(email, password, stdscr):
    curses.curs_set(0)
    stdscr.clear()
    get_name = get_user_name(email)
    show_user_dashboard(email, stdscr)

    stdscr.refresh()
    time.sleep(5)

def get_user_id(email):
    mycursor.execute("select id from user where email = '{}'".format(email))
    record = mycursor.fetchall()
    return record[0][0]

def number_of_user_followers(email):
    id = get_user_id(email)
    mycursor.execute("select follower_id from user_follow where following_id = {}".format(id))
    records = mycursor.fetchall()
    return len(records)

def number_of_user_followings(email):
    id = get_user_id(email)
    mycursor.execute("select following_id from user_follow where follower_id = {}".format(id))
    records = mycursor.fetchall()
    return len(records)

def create_board(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    stdscr.attron(curses.color_pair(2))
    stdscr.border(00000000)
    stdscr.addstr(0, 0, "Dashboard!")

def show_user_dashboard(email, stdscr):
    stdscr.clear()
    curses.curs_set(0)
    
    create_board(stdscr)

    name = get_user_name(email)
    followers_num = number_of_user_followers(email)
    following_num = number_of_user_followings(email)
    #add number of playlists followed or created

    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    stdscr.addstr(0, 40, name)

    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(3, 5, "{} followings".format(following_num))
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(1, 5, "{} followers".format(followers_num))
    
    idx = 25
    # for row in albums:
    #     stdscr.attron(curses.color_pair(2))
    #     stdscr.addstr(3, idx, "{}".format(row))
    #     idx += 12
    
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(5, 5, "c/d/u playlist ('p'), a/d/l songs to/from a playlist ('s'), search for artists/songs ('w'), favorite songs ('f'), f/unf artist/user ('u'), Quit ('q') ?")
    key = stdscr.getch()
    if key == ord("p"):
        user_playlist_manage(stdscr, email)
    elif key == ord("s") :
        user_songs_manage(stdscr, email)
    elif key == ord("u"):
        user_follow_unfollow_manage(stdscr, email)
    elif key == ord("w"):
        user_search(stdscr, email)
    elif key == ord("f"):
        user_favorite_list(stdscr, email)
    elif key == ord("q"):
        exit()

def user_playlist_manage(stdscr, email):
    create_board(stdscr)
    stdscr.addstr(0, 0, "Create, Delete, Follow or Unfollow a playlist ('c'/'d'/'f'/'u')?")
    key = stdscr.getch()

    if key == ord("c"):
        user_create_playlist(stdscr, email)
    elif key == ord("d"):
        user_delete_playlist(stdscr, email)
    elif key == ord("u"): 
        user_unfollow_playlist(stdscr, email)

def user_create_playlist(stdscr, email):
    id = get_user_id(email)
    create_board(stdscr)
    curses.echo()
    stdscr.addstr(0, 0, "enter a name for playlist")
    name = stdscr.getstr()
    mycursor.execute("insert into playlist(name, description, image_refrence, user_id) values('{}', 'vibin', 'some reference', {})".format(name, id))
    connection.commit()


def user_delete_playlist(stdscr, email):
    stdscr.clear()
    playlists = []
    id = get_user_id(email)
    curses.echo()
    stdscr.addstr(0, 0,"enter playlist's name: ")
    name = stdscr.getstr(0, 20, 20)
    if check_playlist_name(name, email) :
        playlist_id = get_playlist_id(name)
        mycursor.execute("delete from playlist where id = {}".format(playlist_id))
        connection.commit()
        mycursor.execute("delete from playlist_follow where playlist_id = {}".format(playlist_id))
        connection.commit()
        

def user_unfollow_playlist(stdscr, email):
    user_id = get_user_id(email)
    stdscr.addstr(0, 0, "enter playlist's name:")
    name = stdscr.getstr()

    if check_playlist_name(name, email):
        playlist_id = get_playlist_id(name)
        mycursor.execute("delete from playlist_follow where user_id = {} and playlist_id = {}".format(user_id, playlist_id))
        connection.commit()

def user_songs_manage(stdscr, email):
    stdscr.clear()
    create_board(stdscr)
    stdscr.addstr(0, 0, "Add, Delete songs from playlist ('a'/'d')?")
    key = stdscr.getch()

    if key == ord("a"):
        user_add_song(stdscr, email)
    elif key == ord("d"):
        user_delete_song(stdscr, email)
    elif key == ord("l"):
        user_like_song(stdscr, email)

def user_add_song(stdscr, email):
    user_id = get_user_id(email)
    stdscr.addstr(0, 0, "enter playlist's name:")
    playlist_name = stdscr.getstr()
    try:
        playlist_id = get_playlist_id(playlist_name)
    except :
        print("such playlist doesn't exist")
        exit()
    playlists = created_playlists(email)
    if playlist_name in playlists:
        stdscr.addstr(0, 0, "enter music's name:")
        music_name = stdscr.getstr()
        try :
            music_id = get_music_id(music_name)
        except:
            print("such song doesn't exist")
            exit()
        date = get_current_date()
        mycursor.execute("insert into on_playlist (music_id, playlist_id, date_of_add) values({}, {}, '{}')".format(music_id, playlist_id, date))
        connection.commit()
    
def user_delete_song(stdscr, email):
    user_id = get_user_id(email)
    stdscr.addstr(0, 0, "enter playlist's name:")
    playlist_name = stdscr.getstr()
    playlist_id = get_playlist_id(playlist_name)

    playlists = created_playlists(email)
    if playlist_name in playlists:
        stdscr.addstr(0, 0, "enter music's name:")
        music_name = stdscr.getstr()
        music_id = get_music_id(music_name)
        mycursor.execute("delete from on_playlist where music_id = {} and playlist_id = {}".format(music_id, playlist_id))
        connection.commit()

def user_like_song(stdscr, email):
    user_id = get_user_id(email)
    stdscr.addstr(0, 0, "enter music's name:")
    music_name = stdscr.getstr()
    music_id = get_music_id(music_name)
    date = get_current_date()
    mycursor.execute("insert into liked (date, user_id, music_id) values('{}', {}, {})".format(date, user_id, music_id))
    connection.commit()

def user_follow_unfollow_manage(stdscr, email):
    stdscr.clear()
    create_board(stdscr)
    stdscr.addstr(0, 0, "follow, unfollow user ('u') / artist ('a')?")
    key = stdscr.getch()
    if key == ord("a"):
        follow_unfollow_artist(email, stdscr)
    elif key == ord("u"):
        follow_unfollow_user(email, stdscr)

def follow_unfollow_artist(email,stdscr):
    stdscr.clear()
    create_board(stdscr)
    stdscr.addstr(0, 0, "follow, unfollow artist ('f'/'u')?")
    key = stdscr.getch()
    if key == ord("f"):
        user_follow_artist(email, stdscr)
    elif key == ord("u"):
        user_unfollow_artist(email, stdscr)
    
def user_follow_artist(email, stdscr):
    stdscr.clear()
    create_board(stdscr)
    stdscr.addstr(0, 0, "Enter artist's username?")
    username = stdscr.getstr()
    if check_username(username) == True:
        if not(in_artist_follow(email, username)):
            user_id = get_user_id(email)
            artist_id = get_artist_id(username)
            mycursor.execute("insert into artist_follow(user_id, artist_id) values({}, {})".format(user_id, artist_id))
            connection.commit()
        else:
            stdscr.addstr(0, 10, "you already have them followed")
    
def user_unfollow_artist(email, stdscr):
    stdscr.clear()
    create_board(stdscr)
    stdscr.addstr(0, 0, "Enter artist's username?")
    username = stdscr.getstr()
    if check_username(username) == True:
        if in_artist_follow(email, username):
            user_id = get_user_id(email)
            artist_id = get_artist_id(username)
            mycursor.execute("delete from artist_follow where user_id = {} and artist_id = {}".format(user_id, artist_id))
            connction.commit()

def follow_unfollow_user(email, stdscr):
    stdscr.clear()
    create_board(stdscr)
    stdscr.addstr(0, 0, "follow ('f') , unfollow ('u') user?")
    key = stdscr.getch()
    if key == ord("f"):
        user_follow_user(email, stdscr)
    elif key == ord("u"):
        user_unfollow_user(email, stdscr)

def user_follow_user(email, stdscr):
    stdscr.clear()
    create_board(stdscr)
    stdscr.addstr(0, 0, "Enter user's email?")
    user_email = stdscr.getstr()
    if not(check_email(email)):
        if not(in_user_follow(email, user_email)):
            follower_id = get_user_id(email)
            following_id = get_user_id(user_email)
            mycursor.execute("insert into user_follow(follower_id, following_id) values({}, {})".format(follower_id, following_id))
            connection.commit()

def user_unfollow_user(email, stdscr):
    stdscr.clear()
    create_board(stdscr)
    stdscr.addstr(0, 0, "Enter user's email?")
    user_email = stdscr.getstr()
    if in_user_follow(email, user_email):
        following_id = get_user_id(user_email)
        follower_id = get_user_id(email)
        mycursor.execute("delete from user_follow where follower_id = {} and following_id = {}".format(follower_id, following_id))
        connection.commit()

def user_favorite_list(stdscr, email):
    stdscr.clear()
    create_board(stdscr)

    user_id = get_user_id(email)

    stdscr.addstr(0, 0, "Favorite songs :")
    mycursor.execute("select music_id from liked where user_id = {}".format(user_id))
    records = mycursor.fetchall()
    musics = []
    if len(records) != 0:
        records = show_musics_liked(email)
        for row in records :
            musics += row
    for idx, music in enumerate(musics):
        stdscr.addstr(idx+1, 40, music)
    
def user_search(stdscr, email):
    stdscr.clear()
    create_board(stdscr)
    stdscr.addstr(0, 0, "Search for an Artist ('a') , Song ('s')?")
    key = stdscr.getch()
    if key == ord("a"):
        user_search_artist(stdscr, email)
    elif key == ord("s"):
        user_search_music(stdscr, email)

def user_search_artist(stdscr, email):
    albums = []
    stdscr.clear()
    create_board(stdscr)
    curses.echo()
    stdscr.addstr(0, 0, "Enter Artist's username")
    username = stdscr.getstr()
    stdscr.clear()

    create_board(stdscr)
    stdscr.addstr(0, 0, username)

    if not check_username(username):
        albums = artist_albums(username)
        show_albums(stdscr, albums)
    
def show_albums(stdscr, albums):
    for idx, name in enumerate(albums) :
        stdscr.addstr(1+idx, 20, name)
        show_album_details(stdscr, name, idx)
        

def show_album_details(stdscr, name, idx):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_RED)
    details = get_album_details(name)
    release_single_ep = "release date:" + str(details[0]) + " single_or_album" + str(details[1])
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(1+idx, 50, release_single_ep)
    stdscr.attroff(curses.color_pair(1))

def get_album_details(name):
    detail = []
    album_id = get_album_id(name)
    mycursor.execute("select release_year, is_single_or_ep from album where id = {}".format(album_id))
    record = mycursor.fetchall()
    for row in record :
        detail += row
    return detail

def user_search_music(stdscr, email):
    stdscr.clear()
    create_board(stdscr)
    curses.echo()
    stdscr.addstr(0, 0, "Enter music's name")
    name = stdscr.getstr()
    stdscr.clear()

    create_board(stdscr)
    stdscr.addstr(0, 0, name)
    show_music_details(stdscr, name)

def show_music_details(stdscr, name):
    details = []
    details = get_music_details(name)
    stdscr.addstr(2, 20, "music info: ")
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_RED)
    stdscr.attron(curses.color_pair(1))
    d = "duration: " + str(details[0]) + " number of plays: " + str(details[1]) + " cover reference: " + str(details[2]) + " file reference: " + str(details[3]) 
    stdscr.addstr(2, 40, d)
    stdscr.attroff(curses.color_pair(1))

def get_music_details(name):
    music_id = get_music_id(name)
    detail = []
    mycursor.execute("select duration, number_of_plays, cover_reference, file_reference from music where id = {}".format(music_id))
    record = mycursor.fetchall()
    for row in record :
        detail += row
    return detail



def show_musics_liked(email):
    user_id = get_user_id(email)
    mycursor.execute("select title from music where id in (select music_id from liked where user_id = {})".format(user_id))
    records = mycursor.fetchall()
    return records


def in_user_follow(u1_email, u2_email):
    u1_id = get_user_id(u1_email)
    u2_id = get_user_id(u2_email)
    mycursor.execute("select following_id from user_follow where following_id = {} and follower_id = {}".format(u2_id, u1_id))
    records = mycursor.fetchall()
    if len(records) != 0:
        return True
    return False 

def in_artist_follow(email, username):
    user_id = get_user_id(email)
    artist_id = get_artist_id(username)
    mycursor.execute("select user_id from artist_follow where user_id = {} and artist_id = {}".format(user_id, artist_id))
    records = mycursor.fetchall()
    if len(records != 0):
        return True
    return False

def get_playlist_id(name):
    mycursor.execute("select id from playlist where name = '{}'".format(name))
    record = mycursor.fetchall()
    return record[0][0]

def get_music_id(name):
    mycursor.execute("select id from music where title = '{}'".format(name))
    record = mycursor.fetchall()
    return record[0][0]

def created_playlists(email):
    id = get_user_id(email)
    mycursor.execute("select name from playlist where user_id = {}".format(id))
    records = mycursor.fetchall()
    playlist = [row[0] for row in records]
    return playlist

def check_playlist_name(name, email):
    id = get_user_id(email)
    mycursor.execute("select id from playlist where user_id = {} and name = '{}' ".format(id, name))
    record = mycursor.fetchall()
    if len(record) != 0 :
        return True
    return False

# def user_delete_playlist(stdscr, email):
#     create_board(stdscr)
#     curses.echo()
#     playlist = []
#     playlist = created_playlists(email)
#     stdscr.addstr(0, 0, playlist)
#     stdscr.addstr(2, 0, "enter the name of the playlist :")
#     name = stdscr.getstr()
#     if check_playlist_name(name, email) == False:
#         stdscr.addstr(1, 0, "such playlist doesnt exist")
#     else :
#         mycursor.execute("delete from playlist where ")


def authenticate(stdscr) :

    curses.curs_set(0)
    stdscr.addstr(0, 0, "artist or user?")
    stdscr.keypad(1)
    key = stdscr.getch()
    stdscr.clear()
    if key == ord("a"):
        stdscr.addstr(0, 0, "Artist!")
        motion(stdscr, menu)
    elif key == ord("u"):
        stdscr.addstr(0, 0, "User!") 
        user_motion(stdscr, menu)
        # user_action(stdscr) 

    stdscr.refresh()
    time.sleep(3)


def artist_action_signup(stdscr):
    #sign up
    curses.echo()
    stdscr.addstr(0, 0, "enter username")
    h, w = stdscr.getmaxyx()
    x = w//2
    y = h//2
    username = stdscr.getstr(y, x, 20)
    username_validity = check_username(username)
               
    #checking for unique username
    while (username_validity != True) :
        stdscr.clear()
        stdscr.addstr(0, 0, "username not available :( enter another username :")
        username = stdscr.getstr(y, x, 20)
        username_validity = check_username(username)

    stdscr.clear()
    curses.noecho()
    stdscr.addstr(0, 0, "enter password")
    password = stdscr.getstr(y, x, 20)
    stdscr.addstr(0, 0, "enter password again")
    password_agin = stdscr.getstr(y, x, 20)
    while (password != password_agin):
        stdscr.addstr(0, 0, "enter password again")
        password_agin = stdscr.getstr(y, x, 20)

    sign_up(password, username)
    stdscr.clear()
    # stdscr.addstr(0, 0, password + " " + username)

def artist_action_signin(stdscr):
    #sign in
    h, w = stdscr.getmaxyx()
    x = w//2
    y = h//2

    curses.echo()
    stdscr.addstr(0, 0, "enter username")
    username = stdscr.getstr(y, x, 20)
    username_validity = check_username(username)
               
    #checking for unique username
    while (username_validity != False) :
        stdscr.clear()
        stdscr.addstr(0, 0, "username is not correct :( try again: ")
        username = stdscr.getstr(y, x, 20)
        username_validity = check_username(username)
    #checking for correct password
    stdscr.clear()
    curses.noecho()
    stdscr.addstr(0, 0, "enter password")
    password = stdscr.getstr(y, x, 20)
    hashed_pass = get_pass_from_db(username)
    check_password(hashed_pass, password)
    while (check_password(hashed_pass, password) != True):
        stdscr.addstr(0, 0, "password not correct ... try again: ")
        password = stdscr.getstr(y, x, 20)
        check_password(hashed_pass, password)
    
    sign_in(username, password, stdscr)
    stdscr.clear()
    stdscr.refresh()
    # time.sleep(3)

curses.wrapper(authenticate)