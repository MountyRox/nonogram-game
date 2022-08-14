import os
import yaml
import locale

MSG_TEXT_FILEPATH = 'locals'

def YamlLoader (filePath):
    try:
        with open (filePath, 'r', encoding='utf8') as f:
            data = yaml.load (f, Loader=yaml.SafeLoader)
        return data
    except:
        return None
    


def YamlDump (filepath, data):
    with open (filepath, 'w', encoding='utf8') as f:
        yaml.dump (data, f)

def GetAppDataPath ():
    dir_path = '%s\\%s\\Nonogram\\' %  (os.environ['APPDATA'], os.environ.get( 'USERNAME'))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def GetAppDataFilePath (fileName):
    return r'%s\%s%s' % (GetAppDataPath (), fileName, '.cfg')

    
def ReadProperties (fileName):
    return YamlLoader (GetAppDataFilePath (fileName))

def WriteProperties (fileName, props):
    YamlDump (GetAppDataFilePath (fileName), props)

def GetLocalMsgText ():
    languageCode, _ = locale.getdefaultlocale()
    if languageCode.upper().startswith ('DE'):  # If German language we take the German cfg file
        filepath = os.path.join (MSG_TEXT_FILEPATH, 'de.cfg')
    else: # if not we take an English one
        filepath = os.path.join (MSG_TEXT_FILEPATH, 'en.cfg')

    msgDict = YamlLoader (filepath)
    #msgDict = YamlLoader ('test.dat')
    return msgDict


if __name__ == "__main__":
    myDict = {# 1: 'vollständig gelöst', 'ar': [1,2,3,4,5,6], 3: 'Geeks'}
        'NoSolutionFound': ['Nonogramm konnte nicht vollständig gelöst werden', ' '],
        'SolutionNotWellDef': ['Keine Lösung gefunden', 'Evtl. ist das Nonogramm nicht eindeutig lösbar'],
        'WantToSave': ['Nonogram has been modified.', 'Want to save?'],
        'NoValidNonoFile': ['Ausgewählte Datei ist keine gültige Nonogramm-Datei', ' '],
        'alleUml': 'ae:ä    oe:ö  ue:ü   AE:Ä   OE:Ö   UE:Ü'
    }

    YamlDump ('test.dat', myDict)
    data =YamlLoader ('test.dat')
    data = GetLocalMsgText ()
    print (data)
