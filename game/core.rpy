init -10 python:
    ###IMPORTS###
    
    import json
    import os
    import glob
    
    ###Functions###
    
    #Gets first object from list with name equal to value
    def getByName(list, value):
        return next((x for x in list if x.name == value), None)
        
    def addHistory(what, color = "#ffffff"):
        Character(None).add_history("adv", None, what)
        _history_list[-1].what_args["color"] = color
        
    ###CoreData class###
    
    class CoreData:
        def __init__(self):
            self.maps = []
            self.locations = []
            self.dialogs = []
            self.decisions = []
            self.events = []
            parser_dialogs(self)
            parser_decisions(self)
            parser_events(self)
            parser_maps(self)
            parser_locations(self)
    
    ###Player class###
    
    class Player(object):
        def __init__(self, name, attributes, bars):
            self.char = DynamicCharacter(name)
            self.attributes = attributes
            self.bars = bars
            self.maps = {}
            self.locations = {}
            self.map = None
            self.location = None
        
        def set_location(self, name):
            if name != "START":
                addHistory("You entered "+name+".", "#22ff22")
            location = getByName(core.locations, name)
            self.location = name
            renpy.scene()
            renpy.show("bg "+location.background)
            if location.name in self.locations and 'event' in self.locations[location.name]:
                event_name = self.locations[location.name]['event']
            else:
                event_name = location.event
            self.doEvent(event_name)
            
        def doEvent(self, event_name, start_from_next = False):
            if start_from_next:
                event = getByName(core.events, event_name)
                event_name = event.next()
            while event_name != None:
                event = getByName(core.events, event_name)
                event_name = event.fire()
            renpy.jump('activities')
                
    ###Classes###
    
    class Attribute:
        def __init__(self, tag, name, value):
            self.tag = tag
            self.name = name
            self.value = value
            
    class Bar:
        def __init__(self, name, value = -1, max = 100):
            self.name = name
            if value < 0:
                self.value = max
            else:
                self.value = value
            self.max = max
    
    class Map:
        def __init__(self, name, image, x, y):
            self.name = name
            self.image = image
            self.x = x
            self.y = y
            
    class Location:
        def __init__(self, name, map, image, x, y, event, background):
            self.name = name
            self.map = map
            self.image = image
            self.x = x
            self.y = y
            self.event = event
            self.background = background
            
    class Event:
        def __init__(self, name, event, events_list):
            self.name = name
            self.event = event
            self.events_list = events_list
            
        def fire(self):
            globals()['g_event'] = self.name
            if self.event != None:
                result = self.event.fire()
                if result != None:
                    return result
            return self.next()
            
        def next(self):
            if self.events_list != None:
                random = renpy.random.randint(1, 100)
                for event in self.events_list:
                    random -= event['chance']
                    if random <= 0:
                        return event['name']
                        break
    
    class EventChanger:
        def __init__(self, location, new_event):
            self.location = location
            self.new_event = new_event
            
        def fire(self):
            if self.location not in player.locations:
                player.locations[self.location] = {}
            player.locations[self.location]['event'] = self.new_event
                
    class LocationEnabler:
        def __init__(self, location):
            self.location = location
            
        def fire(self):
            if self.location not in player.locations:
                player.locations[self.location] = {}
            player.locations[self.location]['known'] = True
            if getByName(core.locations, self.location).map not in player.maps:
                player.maps[getByName(core.locations, self.location).map] = True
            if player.map == None:
                player.map = getByName(core.locations, self.location).map
    
    class Dialog:
        def __init__(self, name, says):
            self.name = name
            self.says = says
            
        def fire(self):
            globals()['g_dialog'] = self.name
            globals()['g_index'] = 0
            self.next()
            
        def next(self):
            if globals()['g_index'] < len(self.says):
                globals()['g_1'] = self.says[globals()['g_index']]
                globals()['g_index'] += 1
                renpy.jump('say')
            else:
                player.doEvent(globals()['g_event'], True)
        
    class Say:
        def __init__(self, what, who = None):
            self.what = what
            self.who = who
            
    class Decision:
        def __init__(self, name, text, choices):
            self.name = name
            self.text = text
            self.choices = choices
            
        def fire(self):
            globals()['g_decision'] = self.name
            list = []
            if self.text != None:
                list.append([self.text, None])
            for i, v in enumerate(self.choices):
                list.append([v.text, i])
            globals()['g_1'] = list
            renpy.jump('decision')
            
        def next(self, chosen = None):
            if chosen != None:
                player.doEvent(chosen)
            else:
                player.doEvent(globals()['g_event'], True)
            
    class DecisionItem:
        def __init__(self, text, event):
            self.text = text
            self.event = event
            
    ###JSON PARSING SECTION###
    
    PATH_MAPS = "data/maps/"
    PATH_LOCATIONS = "data/locations/"
    PATH_DIALOGS = "data/dialogs/"
    PATH_EVENTS = "data/events/"
    PATH_DECISIONS = "data/decisions/"
    
    def parser_maps(self):
        for filename in glob.glob(os.path.join(renpy.loader.transfn(PATH_MAPS), '*.json')):
            file = open(filename, "r")
            data = json.loads(file.read())
            self.maps.append(Map(data['name'],data['image'],data['x'],data['y']))
            file.close()

    def parser_locations(self):
        for filename in glob.glob(os.path.join(renpy.loader.transfn(PATH_LOCATIONS), '*.json')):
            file = open(filename, "r")
            data = json.loads(file.read())
            if 'event' not in data:
                data['event'] = None
            if 'image' not in data:
                data['image'] = "placeholder"
            if 'background' not in data:
                data['background'] = "placeholder"
            if 'map' not in data:
                data['map'] = None
            if 'x' not in data:
                data['x'] = -1
            if 'y' not in data:
                data['y'] = -1    
            self.locations.append(Location(data['name'],data['map'],data['image'],data['x'],data['y'],data['event'],data['background']))
            file.close()
            
    def parser_dialogs(self):
        for filename in glob.glob(os.path.join(renpy.loader.transfn(PATH_DIALOGS), '*.json')):
            file = open(filename, "r")
            data = json.loads(file.read())
            says = []
            for v in data['says']:
                if 'who' not in v:
                    says.append(Say(v['what']))
                else:
                    says.append(Say(v['what'],v['who']))
            self.dialogs.append(Dialog(data['name'],says))
            file.close()
            
    def parser_decisions(self):
        for filename in glob.glob(os.path.join(renpy.loader.transfn(PATH_DECISIONS), '*.json')):
            file = open(filename, "r")
            data = json.loads(file.read())
            choices = []
            for v in data['choices']:
                choices.append(DecisionItem(v['text'],v['event']))
            if 'text' not in data:
                data['text'] = None
            self.decisions.append(Decision(data['name'],data['text'],choices))
            file.close()        
            
    def parser_events(self):
        for filename in glob.glob(os.path.join(renpy.loader.transfn(PATH_EVENTS), '*.json')):
            file = open(filename, "r")
            data = json.loads(file.read())
            if 'event' in data:
                if data['event']['type'] == "dialog":
                    event = getByName(self.dialogs, data['event']['name'])
                elif data['event']['type'] == "decision":
                    event = getByName(self.decisions, data['event']['name'])    
                elif data['event']['type'] == "enable location":
                    event = LocationEnabler(data['event']['location'])
                elif data['event']['type'] == "change event":
                    event = EventChanger(data['event']['location'], data['event']['new event'])
            else:
                event = None
            if 'events list' not in data:
                data['events list'] = None
            self.events.append(Event(data['name'], event, data['events list']))
            file.close()
            
    ###core initialization###    
    core = CoreData()
