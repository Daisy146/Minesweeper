#minesweeper based game
#made by Tinja Untinen

import random #for randomization of the mines
import time
import json
import math
import sweeperlib as sw #marking sweeperlib as sw for easier code writing



SIZE = 40
LIST_NBRS = ["1", "2", "3", "4", "5", "6", "7", "8"]

data = {
    "field": [],
    "fake_field": [],
    "click": -1,
    "been_there": [],
    "width_provided": 0,
    "length_provided": 0,
    "nbr_mines_provided": 0,
    "state_win": False,
    "state_lose": False,
    "start_time": 0,
    "end_time": 0,
    "turns": 0,
    "tiles_opened": [],
    }
   
    
def reset():
    """
    resets all library values after game finished.
    """
    data["field"] = []
    data["fake_field"] = []
    data["click"] = -1
    data["been_there"] = []
    data["width_provided"] = 0
    data["length_provided"] = 0
    data["nbr_mines_provided"] = 0
    data["state_win"] = False
    data["state_lose"] = False
    data["start_time"] = 0
    data["end_time"] = 0
    data["turns"] = 0
    data["tiles_opened"] = []
    

def menu():
    """
    Shows three menu options and works as a fork in code.
    Decision is changed by user every time the menu is called.
    """
    print("Welcome to the minesweeper game.")
    while True:
        print("Select from the following: \n(S)tart new game")
        print("(L)ook at statistics \n(Q)uit")
        #ask user what they wish to do and then based on 
        #that answer run functions or close the program
        decision = input("Input your decision (a letter): ").strip().lower()
        if decision == "s":
            new_game()
        elif decision == "l":
            look_at_statistics()
        elif decision == "q":
            break
        else:
            print("This choice is not an option. Choose something else.")  
    
def main():
    """
    Loads game graphics, sets draw handler and creates game window.
    Also starts game timer. 
    """
    sw.load_sprites('sprites')
    sw.create_window(len(data["field"][0]) * SIZE, len(data["field"]) * SIZE)
    sw.set_mouse_handler(handle_mouse)
    sw.set_draw_handler(draw_game)
    data["start_time"] = time.time() 
    sw.start()

    
    
def handle_mouse(x,y,button,keys):
    """
    Is called when mouse button is clicked inside game window. 
    Gives position and clicked button of the mouse.
    When game is lost, it's the one that makes sure window closes by calling end_game.
    """
    buttons = {
        sw.MOUSE_LEFT: "left",
        sw.MOUSE_RIGHT: "right",
        sw.MOUSE_MIDDLE: "middle"
    }
    if buttons[button] == "right" or buttons[button] == "middle":
        print("Click only the left button.")
    else:
        if data["state_win"] is True or data["state_lose"] is True:
            end_game(data["state_win"], True)
        else:
            tile_opened(int(x/SIZE), int(y/SIZE), data["field"], data["fake_field"])
        

    
def prompt_number(text):
    """
    Asks user for numbers and checks that they are right.
    """
    while True:
        try:
            user = int(input(text))
        except ValueError:
            print("You need to input a positive integer.")
        else:
            if user > 0:
                return user    
            print("You need to input a positive integer.")

def new_game():
    """
    If player chooses new game this function start the new game. 
    Asks dimensions and number of mines. 
    """
    #here we first get the user's answers and then check them.
    data["length_provided"] = prompt_number("Input length of minefield: ")
    data["width_provided"] = prompt_number("Input width of minefield: ")
    data["nbr_mines_provided"] = int(prompt_number(f"Number of mines to place "
    f"into the minefield (less than {data["width_provided"] * data["length_provided"]}): "))
    #checking with while that amount of mines is not bigger than the number of tiles in field
    while data["nbr_mines_provided"] > (data["width_provided"] * data["length_provided"]):
        print("Input number smaller than the amount of tiles.")
        data["nbr_mines_provided"] = int(prompt_number(f"Number of mines to place into the "
        f"minefield (less than {data["width_provided"] * data["length_provided"]}): "))
    #put mines to field and their surrounding numbers
    put_mines(make_field(data["width_provided"], data["length_provided"]), 
    data["field"], data["nbr_mines_provided"])
    find_numbers(data["field"])
    main()
    
    
def save_collection(collection_1, filename):
    """
    Saves collection. Checks for error and let's user know if couldn't save.
    """
    try:
        with open(filename, "w") as target:
            json.dump(collection_1, target)
    except IOError:
        print("Can't open the target file. Saving failed.")
        
def load_collection():
    """
    Loads collection and returns it, if there's not an existing one it'll create one.
    """
    try:
        with open("minesweeper_collection.json") as source:
            collection_2 = json.load(source)
    except (IOError, json.JSONDecodeError):
        print("Can't open target file. Starting with empty collection.")
        collection_2 = []
    return collection_2

def look_at_statistics():
    """
    Show's user statistics based on time, oldest first.
    """
    looks = math.ceil(len(collection) / 5)
    #here we make sure the file is shown nice and easily for user.
    for pages in range(looks):
        start = pages * 5
        end = (pages + 1) * 5
        format_page(collection[start:end], pages)
        if pages < looks - 1:
            input("Press enter to see next page.")
            
def format_page(lines, page_nbr):
    """
    For printing the statistics.
    """
    #printing each game played
    for k, game in enumerate(lines, page_nbr * 5 + 1):
        print(
            f"{k:2}."
            f"{game["date"]}\n"
            f" Game was played for {game["time_minutes"]} minutes and "
            f"{game["time_seconds"]} seconds.\n"
            f" You took {game["turns"]} turns.\n"
            f" {game["outcome"]} There were {game["number_of_mines"]} mines in the field.\n"
        )
    
   
def save_statistics(end_state, collection):
    """
    Saves the played game into the statistics file. 
    """
    #here we make the seconds into minutes and rounded seconds so that it's easier to read
    time_min = int((data["end_time"] - data["start_time"]) / 60)
    time_sec = round((data["end_time"] - data["start_time"]) - (time_min * 60))
    #adding to collection all the facts about the game
    collection.append({
        "date": time.ctime(time.time()),
        "time_minutes": time_min,
        "time_seconds": time_sec,
        "turns": data["turns"],
        "outcome": end_state,
        "number_of_mines": data["nbr_mines_provided"]
    })
    #immediately saving the added statistics
    save_collection(collection, "minesweeper_collection.json") 
     
def make_field(width, length):
    """
    makes field into list based on user's dimensions.
    """
    f = [] #using a inside function variable for making the field
    #making field based on numbers given by user
    for row in range(length):
        f.append([])
        for col in range(width):
            f[-1].append(" ")
    data["field"] = f #here we put the made field into the actual field
    a = [] #using a inside function variable for making the fakefield that we will draw
    #same function just different field
    for row in range(length):
        a.append([])
        for col in range(width):
            a[-1].append(" ")
    data["fake_field"] = a
    available = [] #this list is for the randomization of the mines
    for x in range(width):
        for y in range(length):
            available.append((x, y))
    #we return the available list for putting the mines function
    return available

def draw_game():
    """
    Draws game situation with user provided variables into a game window. 
    It is called whenever the engine requests an update.
    """
    sw.clear_window() #clears away everything drawn last time
    sw.draw_background() #draws the background color
    #we go through the fake field and prepare the sprites based on their values
    for i in enumerate(data["fake_field"]):
        for k in enumerate(i[1]):
            if k[1] == " ":
                sw.prepare_sprite(" ", k[0] * SIZE, i[0] * SIZE)
            elif k[1] == "x":
                sw.prepare_sprite("x", k[0] * SIZE, i[0] * SIZE)
            elif k[1] == "0":
                sw.prepare_sprite("0", k[0] * SIZE, i[0] * SIZE)
            else:
                for number in range(1,9):
                    if k[1] == str(number):
                        sw.prepare_sprite(str(number), k[0] * SIZE, i[0] * SIZE)
    #after preparing whole field we draw it 
    sw.draw_sprites() 

def end_game(state, first_click):
    """
    Happens when user loses or wins. Also makes sure window closes after user clicked it.
    """
    #here we check if we can close the window after game ended
    if first_click:
        reset()
        print("endgame1")
        sw.close()
        menu()
    #checking the time that the game ended at
    data["end_time"] = time.time()
    #next to see if user won or lost
    if data["state_win"] is True:
        print("Congratulations! You won! \n \n")
        state = "Victory"
    else:
        print("Sorry you hit a mine. You lost!  \n \n")
        state = "Game lost"
    print("You can exit the game window by clicking it.")
    #saving game information to the statistics
    save_statistics(state, collection)

def tile_opened(tile_x, tile_y, district, fake_district):
    """
    figures out what the opened tile is, whether floodfill, end of game or nbr tile needs to happen.
    Counts turns and sees if user has won based on the count_x.
    """
    #here we see if tile was opened
    if (tile_y, tile_x) not in data["tiles_opened"]:
        #next we check what type of tile user opened
        if district[tile_y][tile_x] == "x":
            data["state_lose"] = True
            #still drawing the x
            fake_district[tile_y][tile_x] = "x"
            #counting still this turn too
            data["turns"] += 1
            #running the end_game
            end_game(data["state_lose"], False)
        elif district[tile_y][tile_x] in LIST_NBRS:
            data["turns"] += 1
            fake_district[tile_y][tile_x] = district[tile_y][tile_x]
        #if opened tile is empty running the floodfill
        elif district[tile_y][tile_x] == " ":
            data["turns"] += 1
            floodfill(district, tile_x, tile_y, fake_district)
    #here we check whether user has won, it runs while we know user hasn't lost
    if not data["state_lose"]:
        count_x = 0
        for unopened_mines in range(data["length_provided"]):
            count_x += data["fake_field"][unopened_mines].count(" ")
        #nbr of empty tiles in fake field equals mines user input
        if count_x == data["nbr_mines_provided"]: 
            data["state_win"] = True
            end_game(data["state_win"], False)
    #add the tile that's been opened to library's list of opened tiles
    data["tiles_opened"].append((tile_y, tile_x))
        
def find_numbers(place):
    """
    Put's numbers that should surround the mines to the field.
    """
    for i in enumerate(place):
        for k in enumerate(i[1]):
            count_mines(k[0], i[0], place)

def count_mines(mine_x, mine_y, structure):
    """
    Counts the mines surrounding one tile in the given room and
    returns the result. The function assumes the selected tile does
    not have a ninja in it - if it does, it counts that one as well.
    """
    mines = 0
    #if the tile is an x we don't count it
    if structure[mine_y][mine_x] == "x":
        pass
    else:
        #range based on tile coordinates
        #set limit for corners and sides
        limit = len(structure)
        for i in range(mine_y-1,mine_y+2):
            if 0 <= i < limit:
                new_list = structure[i]
                for k in range(mine_x-1,mine_x+2):
                    #limit for corners and sides again
                    another_limit = len(new_list)
                    if 0 <= k < another_limit:
                        if new_list[k] == 'x':
                            mines = mines + 1
                            #save the number to the field
                            data["field"][mine_y][mine_x] = str(mines)
 
def put_mines(tiles, zone, nbr_mines):
    """
    puts mines into the game at randomized positions.
    """
    while nbr_mines != 0:
        #make list based on the available list from making the field and nbr of mines input by user
        random_list = random.sample(tiles, nbr_mines)
        for e in random_list:
            x_spot, y_spot = e
            #check whether randomized spot is in the available list
            if (x_spot,y_spot) in tiles:
                #this makes sure we get the right amount of randomized mines
                nbr_mines = nbr_mines-1
                #add the x to the real field 
                zone[y_spot][x_spot] = 'x'
                #remove this spot from list of availables
                tiles.remove((x_spot,y_spot))

def floodfill(area, starting_point_x, starting_point_y, fake_area):
    """
    Goes through real list but saves into the drawing one.
    Opens all empty tiles until we reach mines based on given coordinates.
    Doesn't do anything if opened tile is a mine.
    """
    processing_list = [(starting_point_y, starting_point_x)]
    while processing_list:
        #remove spot from processing_list but keep it in the y and x
        y, x = processing_list.pop(0)
        #marking the spot as empty for the fake field that we draw
        if area[y][x] == " " or area[y][x] == "0":
            fake_area[y][x] = "0" 
        #add the spot to the been there list so we don't add same tiles to the processing list
        data["been_there"].append((y,x))
        #similar to the numbers surrounding mines function 
        for l in range(y-1,y+2):
            for w in range(x-1,x+2):
                if ( 0 <= l < len(area)) and (0 <= w < len(area[0])):
                    #if the spot is a nbr adds the number to be drawn but not to the processing list
                    if area[l][w] in LIST_NBRS:
                        fake_area[l][w] = area[l][w]
                        continue
                    #here we add spots to processing list if they're not nbrs or 
                    #mines and haven't been checked already
                    if ((area[l][w] == " ") or (area[l][w] == "0") or (area[l][w] in LIST_NBRS)) and ((l,w) not in data["been_there"]):
                        processing_list.append((l, w)) 
    
                   

if __name__ == "__main__":
    collection = load_collection()
    menu()
