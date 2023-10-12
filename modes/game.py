# PROJECT
import audio
import config
import system
import utils
import windows

# SET VARS
room_id = None
room = None

def set_room():
    global room_id
    global room
    room_id = system.active_room
    room = system.rooms[room_id]

def run():
    set_room()
    system.set_selection_options(selection_options())
    system.run_queued_actions()
    return windows.combine([
        windows.window_upper(),
        window_center(),
        window_log(),
        window_lower(),
    ])

def input(key):
    selected_option = system.get_selected_option()
    if(key == 'up'):
        system.ui_log_or_selection_up()
    elif(key == 'down'):
        system.ui_log_or_selection_down()
    elif(key == 'left'):
        system.ui_log_or_selection_left()
    elif(key == 'right'):
        system.ui_log_or_selection_right()
    elif(key == 'escape' or key == 'mouse3'):
        if config.ui_log_scroll_pos > 0:
            config.ui_log_scroll_pos = 0
        elif system.ui_pre_quit_prompt:
            audio.ui_back()
            system.pre_quit_prompt()
        elif system.ui_restart_prompt:
            audio.ui_back()
            system.restart_game_prompt()
        elif system.ui_quit_prompt:
            audio.ui_back()
            system.quit_game_prompt()
    elif(key == 'return'):
        if selected_option.name == "pre_quit_prompt":
            config.trigger_animation(config.ANIMATION_UI_SELECTION)
            if system.ui_pre_quit_prompt:
                audio.ui_back()
            else:
                audio.ui_confirm()
            system.pre_quit_prompt()
        elif selected_option.name == "restart_game_prompt":
            config.trigger_animation(config.ANIMATION_UI_SELECTION)
            if system.ui_pre_quit_prompt:
                system.pre_quit_prompt()
                audio.ui_confirm()
            else:
                audio.ui_back()
            system.restart_game_prompt()
        elif selected_option.name == "quit_game_prompt":
            config.trigger_animation(config.ANIMATION_UI_SELECTION)
            if system.ui_pre_quit_prompt:
                system.pre_quit_prompt()
                audio.ui_confirm()
            else:
                audio.ui_back()
            system.quit_game_prompt()
        elif selected_option.name == "restart_game":
            audio.ui_back()
            config.trigger_animation(config.ANIMATION_UI_SELECTION)
            system.restart_game()
        elif selected_option.name == "quit_game":
            system.quit_game()
        elif selected_option.name == "help":
            audio.ui_confirm()
            config.trigger_animation(config.ANIMATION_UI_SELECTION)
            system.change_mode(config.MODE_HELP)
        elif selected_option.name == "settings":
            audio.ui_confirm()
            config.trigger_animation(config.ANIMATION_UI_SELECTION)
            system.change_mode(config.MODE_SETTINGS)
        elif selected_option.name == "debug":
            audio.ui_confirm()
            config.trigger_animation(config.ANIMATION_UI_SELECTION)
            system.change_mode(config.MODE_DEBUG)
        elif selected_option.name == "map":
            audio.ui_confirm()
            config.trigger_animation(config.ANIMATION_UI_SELECTION)
            system.change_mode(config.MODE_MAP)
        elif selected_option.name == "move":
            audio.fx_move()
            config.trigger_animation(config.ANIMATION_UI_SELECTION_SHORT)
            system.change_position(selected_option.link, True)
        elif selected_option.name == "examine":
            audio.ui_confirm()
            config.trigger_animation(config.ANIMATION_UI_SELECTION_SHORT)
            examine(selected_option.link)
        elif selected_option.name == "portal":
            audio.fx_change_room()
            config.trigger_animation(config.ANIMATION_UI_SELECTION_LONG)
            enter_portal(selected_option.link)

def selection_options():
    result = []
    if system.ui_pre_quit_prompt:
        result.append([
        system.SelectionOption("restart_game_prompt", "RETURN TO TITLE SCREEN"),
        system.SelectionOption("quit_game_prompt", "QUIT GAME"),
        system.SelectionOption("pre_quit_prompt", "CANCEL"),
        ])
    elif system.ui_quit_prompt:
        result.append([
        system.SelectionOption("quit_game", "YES"),
        system.SelectionOption("quit_game_prompt", "NO"),
        ])
    elif system.ui_restart_prompt:
        result.append([
        system.SelectionOption("restart_game", "YES"),
        system.SelectionOption("restart_game_prompt", "NO"),
        ])
    else:
        result.append(check_move_options())
        result.append(check_interact_options())
        result.append([
            system.SelectionOption("map", "MAP"),
        ])
        result.append([
            system.SelectionOption("debug", "DEBUG SCREEN"),
            system.SelectionOption("settings", "SETTINGS"),
            system.SelectionOption("help", "HELP"),
            system.SelectionOption("pre_quit_prompt", "QUIT"),
        ])
    return result

def window_center():
    lines = []
    lines.extend(show_active_status())
    lines.append("")
    lines.extend(load_room())
    return windows.Content(windows.WINDOW_CENTER, lines)

def window_lower():
    ui_blocks = []
    #selection_options_display = windows.format_selection_options_display(system.ui_selection_options, r_align = 2)
    selection_options_display = windows.format_selection_options_display(system.ui_selection_options)
    if system.ui_pre_quit_prompt:
        selection_options_display[0].insert(0, 'SELECT ACTION:')
    elif system.ui_quit_prompt or system.ui_restart_prompt:
        selection_options_display[0].insert(0, 'ARE YOU SURE?')
    else:
        if config.settings['enable_minimap']:
            ui_blocks.append(windows.block_minimap(room, system.current_position))
        option_titles = ["MOVE / WAIT:", "INTERACT:", "OTHER:", "SYSTEM:"]
        selection_options_display = windows.format_selection_options_display_add_titles(selection_options_display, option_titles)
    ui_blocks.extend(selection_options_display)
    return windows.Content(windows.WINDOW_LOWER, windows.combine_blocks(ui_blocks, r_align = 2))

def window_log():
    lines = []
    lines.extend(windows.log_content(system.log_list))
    return windows.Content(windows.WINDOW_LOG, lines)

def check_move_options():
    result = []
    result.append(system.SelectionOption("move", 'WAIT AT THE CURRENT POSITION', system.current_position))
    for pos, text in utils.DIRECTION_ABR.items():
        pos_coord = utils.DIRECTION_TO_COORD[pos]
        current_pos_coord = utils.DIRECTION_TO_COORD[system.current_position]
        if system.current_position != pos and abs(pos_coord['x'] - current_pos_coord['x']) <= 1 and abs(pos_coord['y'] - current_pos_coord['y']) <= 1:
            text = 'MOVE TO THE ' + text
            position_text = text.upper()
            if pos != "c":
                position_text += " SIDE"
            position_text += " OF " + room['noun'].upper()
            result.append(system.SelectionOption("move", position_text, pos))
    return result

def check_interact_options():
    result = []
    for entry in room['interactable']:
        if entry['position'] == system.current_position and not entry['disabled']:
            result.append(system.SelectionOption("examine", "(EXAMINE) " + entry['content'].upper(), entry['link']))
    for entry in room['portal']:
        if entry['position'] == system.current_position and not entry['disabled']:
            result.append(system.SelectionOption("portal", "(EXIT) " + entry['content'].upper(), entry['link']))
    return result

def enable_event(link, category, disable = False):
    num = 0
    for room in system.rooms.values():
        for line in room[category]:
                if line['link'] == link:
                    line['disabled'] = disable
                    num += 1
    if num > 0:
        disable_text = "enabled"
        if disable:
            disable_text = "disabled"
        config.add_debug_log("Change event (" + str(num) + "): " + category + ":" + link + " -> " + disable_text)

def disable_event(link, category):
    enable_event(link, category, True)

def enable_event_interactable(link, disable = False):
    enable_event(link, "interactable", disable)

def disable_event_interactable(link):
    enable_event_interactable(link, True)
    
def enable_event_sight(link, disable = False):
    enable_event(link, "sight", disable)

def disable_event_sight(link):
    enable_event_sight(link, True)
    
def enable_event_smell(link, disable = False):
    enable_event(link, "smell", disable)

def disable_event_smell(link):
    enable_event_smell(link, True)
    
def enable_event_sound(link, disable = False):
    enable_event(link, "sound", disable)

def disable_event_sound(link):
    enable_event_sound(link, True)

def enable_event_portal(link, disable = False):
    enable_event(link, "portal", disable)

def disable_event_portal(link):
    enable_event_portal(link, True)

def enable_event_all(link):
    enable_event_sight(link)
    enable_event_smell(link)
    enable_event_sound(link)

def disable_event_all(link):
    disable_event_sight(link)
    disable_event_smell(link)
    disable_event_sound(link)

def load_room():
    result = []
    if(config.settings['debug_mode']):
        result.append("DEBUG: You are in room " + str(room_id))
    result.append(room['location'])
    result.extend(sense_sight())
    result.extend(sense_sound())
    result.extend(sense_smell())
    result.append("")
    result.append("You are positioned at the " + windows.format_position_text(system.current_position) + " of the " + room['noun'] + ".")
    result.extend(sense_sight(True))
    result.extend(sense_sound(True))
    result.extend(sense_smell(True))
    return result

def show_active_status():
    result = []
    for status in system.statuses.values():
        if (status['active']):
            result.append(windows.format_status(status['text']))
    return result

def sense_scan(sense, sense_text, position_mode = False):
    result = []
    for line in room[sense]:
        if not line['disabled']:
            content = windows.format_color_tags(line['content'])
            if not position_mode and (line['position'] == "" or (line['position'][0] == "-" and line['position'][1:] != system.current_position)):
                result.append(sense_text + content)
            elif (position_mode and line['position'] == system.current_position):
                result.append(sense_text + content)
    return result

def sense_sight(position_mode = False):
    result = []
    sense_text = "You look around: "
    if position_mode:
        sense_text = "You inspect your immediate surroundings: "
    if not system.statuses['blind']['active']:
        result.extend(sense_scan("sight", sense_text, position_mode))
    if not result:
        result.append(sense_text + "You see nothing.")
    return result

def sense_sound(position_mode = False):
    result = []
    sense_text = "You focus on your sense of hearing: "
    if position_mode:
        sense_text = "You focus on the sounds in you immediate proximity: "
    if not system.statuses['deaf']['active']:
        result.extend(sense_scan("sound", sense_text, position_mode))
    if system.statuses['blind']['active'] and not result:
        result.append(sense_text + "You don't hear anything.")
    return result
    
def sense_smell(position_mode = False):
    result = []
    sense_text = "You focus on your sense of smell: "
    if position_mode:
        sense_text = "You focus on the smells in you immediate proximity: "
    if not system.statuses['anosmic']['active']:
        result.extend(sense_scan("smell", sense_text, position_mode))
    if system.statuses['blind']['active'] and not result:
        result.append(sense_text + "You don't smell anything.")
    return result

def examine(link):
    interactable = system.interactables[link]
    disable_event_interactable(link)
    if interactable['enable']:
        enable_event_all(interactable['enable'])
    if interactable['disable']:
        disable_event_all(interactable['disable'])
    if interactable['type'] == "item":
        add_to_inventory(interactable['link'])
        system.add_log("You pick up: " + interactable['text'])
    if interactable['type'] == "portal":
        enable_event_portal(interactable['link'])
        system.add_log("You have discovered: " + interactable['text'])
    for line in interactable['on_interact']:
        execute_action(line)

def enter_portal(link):
    portal = system.portals[link]
    target_room = None
    target_pos = None
    if portal['link1'] == room_id:
        target_room = portal['link2']
        target_pos = portal['pos2']
        system.add_log(portal['text1to2'])
    else:
        target_room = portal['link1']
        target_pos = portal['pos1']
        system.add_log(portal['text2to1'])
    system.enter_room(target_room)
    system.change_position(target_pos)
    for line in portal['on_interact']:
        system.execute_action(line)

def add_to_inventory(item):
    system.inventory_list.append(item)