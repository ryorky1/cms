from genericpath import isdir
import os
import pandas as pd
import transport
import copy
from jinja2 import Environment, BaseLoader, FileSystemLoader
import importlib
import importlib.util
from cms import disk, cloud
# import cloud

class components :
    # @staticmethod
    # def folders (_path):
    #     """
    #     This function reads the content of a folder (no depth, it must be simple)
    #     """
    #     _content = os.listdir(_path)        
    #     return [_name for _name in _content if os.path.isdir(os.sep.join([_path,_name])) if not _name.startswith('_')]
    # @staticmethod
    # def content (_folder) :
    #     if os.path.exists(_folder) :
    #         # return [{'text':_name.split('.')[0].replace('_', ' ').replace('-',' ').strip(),'uri': os.sep.join([_folder,_name])} for _name in os.listdir(_folder) if not _name.startswith('_') and os.path.isfile( os.sep.join([_folder,_name]))]
    #         return [{'text':_name.split('.')[0].replace('_', ' ').replace('-',' ').strip(),'uri': os.sep.join([_folder,_name])} for _name in os.listdir(_folder) if not _name.startswith('_') and os.path.isfile( os.sep.join([_folder,_name]))]
    #     else:
    #         return []
    @staticmethod
    def menu(_config):
        """
        This function will read menu and sub-menu items from disk structure,
        The files are loaded will
        """
        # _items = components.folders(_path) 
        
        # _layout = copy.deepcopy(_config['layout'])
        # _overwrite = _layout['overwrite'] if 'overwrite' in _layout else {}
        #
        # content of each menu item
        # _subItems = [ components.content (os.sep.join([_path,_name]))for _name in _items ]
        # if 'map' in _layout :
        #     _items = [_name if _name not in _layout['map'] else _layout['map'][_name] for _name in _items]
 
        # _object =  dict(zip(_items,_subItems))
        
        if 'source' in _config['system'] and _config['system']['source']['id'] == 'cloud' :
            _sourceHandler = cloud
        else:
            _sourceHandler = disk
        _object = _sourceHandler.build(_config)
        # _object = disk.build(_path,_config) if type(_path) == str else cloud.build(_path,_config)        
        _layout = copy.deepcopy(_config['layout'])
        _overwrite = _layout['overwrite'] if 'overwrite' in _layout else {}
        
        #
        # @TODO: Find a way to translate rename/replace keys of the _object (menu) here 
        #
        #-- applying overwrites to the menu items 
        for _name in _object :
            _submenu = _object[_name]
            _index = 0
            for _item in _submenu :
                text = _item['text'].strip()
                
                if text in _overwrite :
                    if 'uri' in _item and 'url' in 'url' in _overwrite[text] :
                        del _item['uri']
                    _item = dict(_item,**_overwrite[text])
                if 'uri' in _item:
                    _item['uri'] = _item['uri'].replace(_layout['root'],'')
                _submenu[_index] = _item
                _index += 1
        return _object 
   
    @staticmethod
    def html(uri,id,_args={},_system={}) :
        """
        This function reads a given uri and returns the appropriate html document, and applies environment context

        """

        if 'source' in _system and _system['source']['id'] == 'cloud':
            _html = cloud.html(uri,dict(_args,**{'system':_system}))
            
        else:
            _html = disk.html(uri)
        # _html = (open(uri)).read()       

        
        #return ' '.join(['<div id=":id" class=":id">'.replace(':id',id),_html,'</div>'])
        _html   = ' '.join(['<div id=":id" class=":id">'.replace(':id',id),_html,'</div>'])
        appContext = Environment(loader=BaseLoader()).from_string(_html)
        #
        # If the rendering of the HTML happens here we should plugin custom functions (at the very least)
        #
        
        return appContext.render(**_args)
        # return _html
    @staticmethod
    def data (_args):
        """
        :store  data-store parameters (data-transport, github.com/lnyemba/data-transport)
        :query  query to be applied against the store (expected data-frame)
        """
        _store  = _args['store']
        reader  = transport.factory.instance(**_store)
        _queries= copy.deepcopy(_store['query'])
        _data   = reader.read(**_queries)
        return _data
    @staticmethod
    def csv(uri) :
        return pd.read(uri).to_html()
    @staticmethod
    def load_plugin(**_args):
        """
        This function will load external module form a given location and return a pointer to a function in a given module
        :path   absolute path of the file (considered plugin) to be loaded
        :name   name of the function to be applied
        """
        _path = _args['path'] #os.sep.join([_args['root'],'plugin'])
        if os.path.isdir(_path):
            files = os.listdir(_path)
            if files :
                files = [name for name in files if name.endswith('.py')]
                if files:
                    _path = os.sep.join([_path,files[0]])
                else:
                    return None
            else:
                return None
        #-- We have a file ...  
        _name = _args['name']
        
        spec = importlib.util.spec_from_file_location(_name, _path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return getattr(module,_name) if hasattr(module,_name) else None
    @staticmethod
    def plugins(_config) :
        """
        This function looks for plugins in the folder on disk (no cloud support) and attempts to load them
        """
        PATH= os.sep.join([_config['layout']['root'],'_plugins'])
        _map = {}
        # if not os.path.exists(PATH) :
        #     return _map
        if 'plugins' not in _config :
            _config['plugins'] = {}
        _conf = _config['plugins'] 
        
        for _key in _conf :
            _path = os.sep.join([PATH,_key+".py"])
            if not os.sep.path.exists(_path):
                continue
            for _name in _conf[_key] :
                _pointer = components.load_plugin(path=_path,name=_name)
                if _pointer :
                    _uri = "/".join(["api",_key,_name])
                    _map[_uri] = _pointer
        #
        # We are adding some source specific plugins to the user-defined plugins
        # This is intended to have out-of the box plugins...
        #
        if 'source' in _config['system'] and _config['system']['source']['id'] == 'cloud' :
            _plugins = cloud.plugins()
        else:
            _plugins = disk.plugins()
        #
        # If there are any plugins found, we should load them and use them
        
        if _plugins :
            _map = dict(_map,**_plugins)
        return _map
    @staticmethod
    def context(_config):
        """
        adding custom variables functions to Jinja2, this function should be called after plugins are loaded
        """
        _plugins = _config['plugins']
        # if not location:
        #     env = Environment(loader=BaseLoader())
        # else:
        location = _config['layout']['root']
        # env = Environment(loader=FileSystemLoader(location))
        env = Environment(loader=BaseLoader())
        # env.globals['routes'] = _config['plugins']
        return env
    @staticmethod
    def get_system(_config,skip_keys=[]):
        _system = copy.deepcopy(_config['system'])
        if skip_keys :
            for key in skip_keys :
                if key in _system :
                    del _system
        return _system

