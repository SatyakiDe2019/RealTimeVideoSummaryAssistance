################################################
####                                        ####
#### Written By: SATYAKI DE                 ####
#### Written On:  15-May-2020               ####
#### Modified On: 20-Apr-2025               ####
####                                        ####
#### Objective: This script is a config     ####
#### file, contains all the keys for        ####
#### MCP protocol evaluation to fetch the   ####
#### important attributes to run the app.   ####
####                                        ####
################################################

import os
import platform as pl

class clsConfigClient(object):
    Curr_Path = os.path.dirname(os.path.realpath(__file__))

    os_det = pl.system()
    if os_det == "Windows":
        sep = '\\'
    else:
        sep = '/'

    conf = {
        'APP_ID': 1,
        'ARCH_DIR': Curr_Path + sep + 'arch' + sep,
        'PROFILE_PATH': Curr_Path + sep + 'profile' + sep,
        'LOG_PATH': Curr_Path + sep + 'log' + sep,
        'DATA_PATH': Curr_Path + sep + 'data' + sep,
        'OUTPUT_PATH': Curr_Path + sep + 'Output' + sep,
        'TEMP_PATH': Curr_Path + sep + 'temp' + sep,
        'IMAGE_PATH': Curr_Path + sep + 'Image' + sep,
        'MODEL_PATH': Curr_Path + sep + 'Model' + sep,
        'AUDIO_PATH': Curr_Path + sep + 'audio' + sep,
        'SESSION_PATH': Curr_Path + sep + 'my-app' + sep + 'src' + sep + 'session' + sep,
        'APP_DESC': 'LLM Performance Comparison!',
        'DEBUG_IND': 'Y',
        'INIT_PATH': Curr_Path,
        'HF_CACHE': "/Volumes/WD_BLACK/PythonCourse/Pandas/blog/huggingface",
        'MODEL_NAME_1': 'gpt-4o',
        'MODEL_NAME_2': 'claude-3-5-sonnet-20241022',
        'CHANNEL_NAME': 'sd_channel',
        'HF_KEY': "hf_jfhUUYTT7dSlzrxMUuLkdo",
        'OPEN_AI_KEY': "sk-Jdhdufif98JHHudkdHhXPnN3Y9Pt2OmKuLy",
        'ANTHROPIC_AI_KEY': "sk-ant-api03-i-aCJW__Jdjduu87JjfdpznyvgcmfH5mQYrUISLFRbtyxIJOEf0RKdjdi8jHYBrCQ-0g5ZhUIA",
        'GOOGLE_API_KEY': "AIzaSjhu*&dhTBj_tZ9ltPzXbLKdiuU74wA4Y",
        'SARVAM_AI_KEY': "80913ebf-a55d-4c0c-b945-98juy6H79k07",
        'SARVAM_URL': "https://api.sarvam.ai/v1/chat/completions",
        'TEMP_VAL': 0.2,
        'PATH' : Curr_Path,
        'MAX_TOKEN' : 1000,
        'MAX_CNT' : 5,
        'OUT_DIR': 'data',
        'OUTPUT_DIR': 'output',
        "DB_PATH": Curr_Path + sep + 'data' + sep
    }
