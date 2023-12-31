# PROJECT
import config
import system
import windows

# SET VARS
cutscene = None

def run():
    return [
        windows.main([
            windows.window_upper(),
            window_center(),
            windows.window_lower_continue()
        ])
    ]

def input(key, mod = None):
    valid_input = False
    if key in config.controls['scroll_center_up'] or (key in config.controls['up'] and (mod in config.controls['mod_scroll_center'])):
        valid_input = system.ui_scroll_minus('center')
    elif key in config.controls['scroll_center_down'] or (key in config.controls['down'] and (mod in config.controls['mod_scroll_center'])):
        valid_input = system.ui_scroll_plus('center')
    elif key in config.controls['action']:
        valid_input = True
        config.trigger_animation(config.ANIMATION_UI_CONTINUE_DEFAULT, 'ui_confirm', 'ui', animation_data = config.UI_TAGS['continue'])
        for line in cutscene['on_exit']:
            system.execute_action(line)
    return valid_input

def window_center():
    return windows.Content(windows.WINDOW_CENTER, load_cutscene(system.active_cutscene))

def load_cutscene(cutscene_id):
    global cutscene
    cutscene = system.cutscenes[cutscene_id]
    config.add_debug_log('Running cutscene -> ' + str(cutscene_id))
    result = []
    if(config.settings['debug_mode']):
        result.append("DEBUG: Running cutscene " + str(cutscene_id))
    for line in cutscene['on_enter']:
        system.execute_action(line)
    for line in cutscene['text']:
        result.append(line)
    return result