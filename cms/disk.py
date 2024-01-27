"""
This file pulls the content from the disk 
"""
import os
def folders (_path):
    """
    This function reads the content of a folder (no depth, it must be simple)
    """
    _content = os.listdir(_path)        
    return [_name for _name in _content if os.path.isdir(os.sep.join([_path,_name])) if not _name.startswith('_')]

def content(_folder):
    """
    :content of the folder
    """

    if os.path.exists(_folder) :
        _menuItems = os.listdir(_folder)
        # return [{'text':_name.split('.')[0].replace('_', ' ').replace('-',' ').strip(),'uri': os.sep.join([_folder,_name])} for _name in os.listdir(_folder) if not _name.startswith('_') and os.path.isfile( os.sep.join([_folder,_name]))]
        return [{'text':_name.split('.')[0].replace('_', ' ').replace('-',' ').strip(),'uri': os.sep.join([_folder,_name])} for _name in os.listdir(_folder) if not _name.startswith('_') and os.path.isfile( os.sep.join([_folder,_name]))]
    else:
        return []
def build (_config): #(_path,_content):
    """
    building the menu for the site given the content is on disk
    :path  path of the files on disk
    :config configuration associated with the 
    """
    _path = _config['layout']['root']
    _items = folders(_path)
    _subItems = [ content (os.sep.join([_path,_name]))for _name in _items ]
    _r = {}
    for _name in _items :
        _index = _items.index(_name)
        if _name not in _r :
            _r[_name] = []
        _r[_name] += _subItems[_index]
    return _r
    # return dict.fromkeys(_items,_subItems)

def html(uri) :
    _html = (open(uri)).read()    
    return _html
def plugins ():
    return {}
    