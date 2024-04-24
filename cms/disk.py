"""
This file pulls the content from the disk 
"""
import os
import importlib
import importlib.util
import copy
from mistune import markdown


def folders (_path,_config):
    """
    This function reads the content of a folder (no depth, it must be simple)
    """
    _content = os.listdir(_path)        
    return [_name for _name in _content if os.path.isdir(os.sep.join([_path,_name])) if not _name.startswith('_')]
def content(_folder,_config,keep=[]):
    """
    :content of the folder
    """
    _layout = _config['layout']
    if 'location' in _layout :
        _uri = os.sep.join([_layout['root'] ,_folder.split(os.sep)[-1]])
        _path = os.sep.join([_layout['root'],_folder.split(os.sep)[-1]])
    else:
        
        _path = _folder
    if os.path.exists(_folder) :
        _menuItems = list_files(_folder,_config) #os.listdir(_folder)
        # return [{'text':_name.split('.')[0].replace('_', ' ').replace('-',' ').strip(),'uri': os.sep.join([_folder,_name])} for _name in os.listdir(_folder) if not _name.startswith('_') and os.path.isfile( os.sep.join([_folder,_name]))]
        
        return [{'text':_name.split('.')[0].replace('_', ' ').replace('-',' ').strip(),'uri': os.sep.join([_path,_name])} for _name in os.listdir(_folder) if not _name[0] in ['.','_'] and os.path.isfile( os.sep.join([_folder,_name])) and _name.split('.')[-1] in ['html','md']]
    else:
        return []
def list_files(_folder,_config, keep=[]):

    return [name for name in os.listdir(_folder) if name[0] not in ['.','_']]
def build (_config, keep=[]): #(_path,_content):
    """
    building the menu for the site given the content is on disk
    :path  path of the files on disk
    :config configuration associated with the 
    """
    _path = _config['layout']['root']
    # if 'location' in _config['layout'] :
    #     _path = _config['layout']['location']
    _path = _realpath(_path,_config)
    # print (_path)
    _items = folders(_path,_config)
    _subItems = [ content (os.sep.join([_path,_name]),_config)for _name in _items  ]
    
    _r = {}
    for _name in _items :
        _index = _items.index(_name)
        if _name.startswith('_') or len(_subItems[_index]) == 0:
            continue
        # print ([_name,_subItems[_index]])
        if _name not in _r :
            _r[_name] = []
        _r[_name] += _subItems[_index]
    # _r  = [_r[_key] for _key in _r if len(_r[_key]) > 0]
    return _r
    # return dict.fromkeys(_items,_subItems)

def _realpath (uri,_config) :
    _layout = _config['layout']
    
    _uri = copy.copy(uri)
    if 'location' in _layout :
        _uri = os.sep.join([_layout['location'],_uri])
    return _uri

def _format (uri,_config):
    _layout = _config['layout']
    if 'location' in _layout :
        return 'api/disk/read?uri='+uri
    return uri
def read (**_args):
    """
    This will read binary files from disk, and allow the location or not to be read
    @TODO: add permissions otherwise there can be disk-wide reads
    """
    request = _args['request']
    _layout = _args['config']['layout']

    _uri = request.args['uri']    # if 'location' in _layout :
    #     _uri = os.sep.join([_layout['location'],_uri])
    _uri = _realpath(_uri, _args['config'])
    if os.path.exists(_uri):
        f = open(_uri,mode='rb')
        _stream = f.read()
        f.close()
        
        return _stream
    return None
def exists(**_args):
    _path = _realpath(_args['uri'],_args['config'])
    
    # _layout = _args['config']['layout']
    # if 'location' in _layout :
    #     _path = os.sep.join([_layout['location'],_path])
    return os.path.exists(_path)
def html(_uri,_config) :
    # _html = (open(uri)).read()   
    _path = _realpath(_uri,_config) 
    _context = _config['system']['context']
    _html = ( open(_path)).read()
    _layout = _config['layout']
    if 'location' in _layout :
        if not _config :
            _api = os.sep.join(['api/disk/read?uri=',_layout['root']])
        else:
            _api = os.sep.join([f'{_context}/api/disk/read?uri=',_layout['root']])

        _html = _html.replace(_layout['root'],_api)
    _html = markdown(_html) if _uri[-2:] in ['md','MD','Md','mD'] else _html
    return _html
def plugins (**_args):
    """
    This function will load plugins from disk given where they come from 
    :path   path of the files
    :name   name of the module
    """
    _context = _args['context']
    if 'path' not in _args :
        key = 'api/disk/read'
        if _context :
            key = f'{_context}/{key}'
        return {key:read}
    
    _path = _args['path'] #os.sep.join([_args['root'],'plugin'])        
    if os.path.isdir(_path):
        files = os.listdir(_path)
        if files :
            files = [name for name in files if name.endswith('.py')]
            if files:
                _uri = [_path,files[0]]
                if _context :
                    _uri = [_context] + _uri
                _path = os.sep.join(_uri)
            else:
                return None
        else:
            #
            # LOG: not a file
            return None
    #-- We have a file ...  
    _name = _args['name']
    spec = importlib.util.spec_from_file_location(_name, _path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    #
    # LOG This plugin ....
    return getattr(module,_name) if hasattr(module,_name) else None    
    