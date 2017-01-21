# The script of the game goes in this file.
default player = Player("Nameless", [Attribute("STR","Strength",0), Attribute("FOU","Foundation",0), Attribute("DEX","Dextelity",0), Attribute("END","Endurance",0), Attribute("TOR","Toru",0), Attribute("INT","Intellect",0), Attribute("WIS","Wisdom",0)], [Bar("Health",50), Bar("Stamina"), Bar("Lust"), Bar("EXP")])
# The game starts here.
label start:
    show screen stats()
    show screen bars()
    $player.set_location("START")
    
label say:
    $renpy.say(globals()['g_1'].who, globals()['g_1'].what)
    $getByName(core.dialogs, globals()['g_dialog']).next()

label decision:
    $chosen = renpy.display_menu(globals()['g_1'])
    $addHistory(getByName(core.decisions, globals()['g_decision']).choices[chosen].text, "#a300cc")
    $getByName(core.decisions, globals()['g_decision']).next(getByName(core.decisions, globals()['g_decision']).choices[chosen].event)
    
label activities:
    python:
        activity = renpy.call_screen("activites")
        if activity == "map":
            renpy.jump('map')
    
label map:
    python:
        location = getByName(core.locations, player.location)
        map = getByName(core.maps, location.map)
        if map == None:
            map = getByName(core.maps, player.map)
        locations = core.locations

label reload_map:
    $player.set_location(renpy.call_screen("map", map, location, locations))
    
label win:
    return