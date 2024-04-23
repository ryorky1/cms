import json

from genericpath import isdir
import os
import pandas as pd
import transport
import copy
from jinja2 import Environment, BaseLoader, FileSystemLoader
import importlib
import importlib.util
from cms import disk, cloud
from . import basic

class Loader :
    """
    This class is designed to exclusively load configuration from disk into an object
    :path       path to the configuraiton file
    :location   original location (caller)
    """
    def __init__(self,**_args):
        self._path = _args['path']
        self._original_location = None if 'location' not in _args else _args['location']
        self._location = None
        self._caller = None if 'caller'  not in _args else _args['caller']
        self._menu = {}
        self._plugins={}
        self.load()
        
    
    def load(self):
        """
        This function will load menu (overwrite) and plugins
        """
        self.init_config()
        self.init_menu()
        self.init_plugins()
    def init_config(self):
        """
        Initialize & loading configuration from disk
        """
        f = open (self._path)
        self._config = json.loads(f.read())

        if self._caller :
            self._location = self._original_location.split(os.sep) # needed for plugin loading
            self._location = os.sep.join(self._location[:-1])
        self._config['system']['portal'] = self._caller != None

        #
        # let's see if we have a location for a  key (i.e security key) in the configuration
        #
        self.update_config()
        # _system = self._config['system']
        # if 'source' in _system and 'key' in _system['source'] :
        #     _path = _system['source']['key']
        #     if os.path.exists(_path):
        #         f = open(_path)
        #         _system['source']['key'] = f.read()
        #         f.close()
        #         self._system = _system
        #         self._config['system'] = _system
    def update_config(self):
        """
        We are going to update the configuration (source.key, layout.root)
        """        
        _system = self._config['system']
        #
        # updating security-key that allows the application to update on-demand
        if 'source' in _system and 'key' in _system['source'] :
            _path = _system['source']['key']
            if os.path.exists(_path):
                f = open(_path)
                _system['source']['key'] = f.read()
                f.close()
                self._system = _system
                self._config['system'] = _system
        _layout = self._config['layout']
        #
        # update root so that the app can be launched from anywhere
        #   This would help reduce the footprint of the app/framework
        _path = os.sep.join(self._path.split(os.sep)[:-1])
        _p = 'source' not in _system
        _q = 'source' in _system and _system['source']['id'] != 'cloud'
        _r = os.path.exists(_layout['root'])
        if not _r and (_p or _q) :
            #
            # If we did running this app from installed framework (this should not apply to dependent apps)
            #
            _root = os.sep.join([_path,_layout['root']])
            self._config['layout']['root'] = _root
            self._config['layout']['root_prefix'] = _root

    def init_menu(self):
        """
        This function will read menu and sub-menu items from disk structure,
        The files are loaded will
        """
        
        _config = self._config        
        if 'source' in _config['system'] and _config['system']['source']['id'] == 'cloud' :
            _sourceHandler = cloud
        else:
            _sourceHandler = disk
        _object = _sourceHandler.build(_config)
        
        #
        # After building the site's menu, let us add the one from 3rd party apps
        #
        
        
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
                
                if 'uri' in _item and 'type' in _item and _item['type'] != 'open':
                    _item['uri'] = _item['uri'].replace(_layout['root'],'')

                _submenu[_index] = _item
                _index += 1
        self.init_apps(_object)
        self._menu = _object 
        self._order()
        
    def init_apps (self,_menu):
        """
        Insuring that the apps are loaded into the menu with an approriate label
        """
        _system = self._config['system']
        _context = _system['context']
        if 'routes' in _system :
            # _items = []
            _overwrite = {} if 'overwrite' not in self._config['layout'] else self._config['layout']['overwrite']
            for _text in _system['routes'] :
                _item = _system['routes'][_text]
                if 'menu' not in _item :
                    continue
                uri = f'{_context}/{_text}'
                # _items.append ({"text":_text,'uri':uri,'type':'open'})
                _label = _item['menu']
                if _label not in _menu :
                    _menu [_label] = []
                _menu[_label].append ({"text":_text,'uri':uri,'type':'open'})
                # _overwrite[_text] = {'text': _text.replace('-',' ').replace('_',' '),'uri':uri,'type':'open'}
            # _menu['products'] = _items
            #
            # given that the menu items assumes redirecting to a page ...
            # This is not the case
            #
            # self._config['overwrite'] = _overwrite
        else:
            pass
        
        pass
    def _order (self):
        _config = self._config
        if 'order' in _config['layout'] and 'menu' in _config['layout']['order']:
            _sortedmenu = {}
            _menu = self._menu
            for _name in _config['layout']['order']['menu'] :
                if _name in _menu :
                    _sortedmenu[_name] = _menu[_name]
            
            _menu = _sortedmenu if _sortedmenu else _menu
            #
            # If there are missing items in the sorting
            _missing = list(set(self._menu.keys()) - set(_sortedmenu))
            if _missing :
                for _name in _missing :
                    _menu[_name] = self._menu[_name]
        _config['layout']['menu'] = _menu #cms.components.menu(_config)  
        self._menu = _menu    
        self._config = _config  
    def init_plugins(self) :
        """
        This function looks for plugins in the folder on disk (no cloud support) and attempts to load them
        """
        _config = self._config
        PATH= os.sep.join([_config['layout']['root'],'_plugins'])
        if not os.path.exists(PATH) :
            #
            # we need to determin if there's an existing 
            PATH = os.sep.join(self._path.split(os.sep)[:-1]+ [PATH] )
        if not os.path.exists(PATH) and self._location and os.path.exists(self._location) :
            #
            # overriding the location of plugins ...
            PATH = os.sep.join([self._location, _config['layout']['root'],'_plugins'])
            
        _map = {}
        # if not os.path.exists(PATH) :
        #     return _map
        if 'plugins' not in _config :
            _config['plugins'] = {}
        _conf = _config['plugins'] 
        
        for _key in _conf :
            
            _path = os.sep.join([PATH,_key+".py"])
            if not os.path.exists(_path):
                continue
            for _name in _conf[_key] :
                _pointer = self._load_plugin(path=_path,name=_name)
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
        else:
            pass
        self._plugins =  _map
        self._config['plugins'] = self._plugins
        
    def _load_plugin(self,**_args):
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

class Getter (Loader):
    def __init__(self,**_args):
        super().__init__(**_args)
    def load(self):
        super().load()
        _system = self.system()
        _logo = _system['logo']
        if 'source' in _system and 'id' in _system['source'] and (_system['source']['id'] == 'cloud'):
            
            _icon = f'/api/cloud/download?doc=/{_logo}'
            _system['icon'] = _icon 
            
        else:
            _root = self._config['layout']['root']
            _icon = os.sep.join([_root,_logo])
            _system['icon'] = _logo

        self._config['system'] = _system
        if self._caller :
            _system['caller'] = {'icon': self._caller.system()['icon']}
    def html(self,uri,id,_args={},_system={}) :
        """
        This function reads a given uri and returns the appropriate html document, and applies environment context

        """
        _system = self._config['system']
        if 'source' in _system and _system['source']['id'] == 'cloud':
            _html = cloud.html(uri,dict(_args,**{'system':_system}))
            
        else:

            _html = disk.html(uri,self.layout())
        # _html = (open(uri)).read()       

        
        #return ' '.join(['<div id=":id" class=":id">'.replace(':id',id),_html,'</div>'])
        _html   = ' '.join(['<div id=":id" class=":id">'.replace(':id',id),_html,'</div>'])
        appContext = Environment(loader=BaseLoader()).from_string(_html)
        _args['system'] = _system
        #
        # If the rendering of the HTML happens here we should plugin custom functions (at the very least)
        #
        
        return appContext.render(**_args)
        # return _html
    
    def data (self,_args):
        """
        :store  data-store parameters (data-transport, github.com/lnyemba/data-transport)
        :query  query to be applied against the store (expected data-frame)
        """
        _store  = _args['store']
        reader  = transport.factory.instance(**_store)
        _queries= copy.deepcopy(_store['query'])
        _data   = reader.read(**_queries)
        return _data
    def csv(self,uri) :
        return pd.read(uri).to_html()
   
        return _map
    def menu(self):
        return self._config['menu']
    def plugins(self):
        return copy.deepcopy(self._plugins) if 'plugins' in self._config else {}
    def context(self):
        """
        adding custom variables functions to Jinja2, this function should be called after plugins are loaded
        """
        _plugins = self.plugins()
        # if not location:
        #     env = Environment(loader=BaseLoader())
        # else:
        location = self._config['layout']['root']
        # env = Environment(loader=FileSystemLoader(location))
        env = Environment(loader=BaseLoader())
        # env.globals['routes'] = _config['plugins']
        return env
    def config(self):
        return copy.deepcopy(self._config)
    def system(self,skip=[]):
        """
        :skip   keys to ignore in the object ...
        """
        _data = copy.deepcopy(self._config['system'])
        _system = {}
        if skip and _system:
            for key in _data.keys() :
                if key not in skip :
                    _system[key] = _data[key]
        else:
            _system= _data
        return _system
    def layout(self):
        return self._config['layout']
    def get_app(self):
        return self._config['system']['app']


class Router :
    def __init__(self,**_args) :
        
        # _app = Getter (path = path)
        _app = Getter (**_args)


        self._id = 'main'
        # _app.load()
        self._apps = {}
        _system = _app.system()
        if 'routes' in _system :
            _system = _system['routes']
            for _name in _system :
                _path = _system[_name]['path']
                self._apps[_name] = Getter(path=_path,caller=_app,location=_path)
        self._apps['main'] = _app    

    def set(self,_id):
        self._id = _id
    def get(self):
        
        return self._apps['main'] if self._id not in self._apps else self._apps[self._id]
    def get_main(self):
        return self._apps['main']
