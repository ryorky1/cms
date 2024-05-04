import json
import os
import io
import copy
from cms import disk, cloud
from jinja2 import Environment, BaseLoader, FileSystemLoader
import importlib
import importlib.util


class Initializer :
    """
    This class handles initialization of all sorts associated with "cms engine" 
    :path
    :location
    :shared
    """
    def __init__(self,**_args):
        self._config = {'system':{},'layout':{},'plugins':{}}
        self._shared = False if not 'shared' in _args else _args['shared']
        self._location= _args['location'] if 'location' in _args else None
        self._menu = {}
        # _source = self._config ['system']['source'] if 'source' in self._config['system'] else {}
        # self._ISCLOUD = 'source' in self._config['system'] and self._config['system']['source']['id'] == 'cloud'
        # print ([self._ISCLOUD,self._config['system'].keys()])
        self._ISCLOUD = False
        self._caller = None if 'caller'  not in _args else _args['caller']
        
        #
        # actual initialization of the CMS components 
        # self._iconfig(**_args)
        # self._uconfig(**_args)
        # self._isource()
        # self._imenu()        
        # self._iplugins()
        
        self._args = _args
        self.reload()

    def reload(self):
        self._iconfig(**self._args)
        self._uconfig(**self._args)
        self._isource()
        self._imenu()        
        self._iplugins()
        

        # self._ISCLOUD = 'source' in self._config['system'] and self._config['system']['source']['id'] == 'cloud'

    def _handler  (self):
        """
        This function returns the appropriate handler to the calling code, The handler enables read/write from a location
        """
        
        if self._ISCLOUD: #'source' in self._config['system'] and self._config['system']['source']['id'] == 'cloud' :
            return cloud
        else:
            return disk
        
    def _imenu(self,**_args) :
        pass
    def _iplugins(self,**_args) :
        """
        Initialize plugins from disk (always)
        :plugins
        """
        _config = self._config
        PATH= os.sep.join([_config['layout']['root'],'_plugins'])
        
        if not os.path.exists(PATH) and self._location and os.path.exists(self._location) :
            #
            # overriding the location of plugins ...
            if os.path.isfile(self._location) :
                _location = os.sep.join(self._location.split(os.sep)[:-1])
            else:
                _location = self._location 
            PATH = os.sep.join([_location, _config['layout']['root'],'_plugins'])
        _context = _config['system']['context']
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
                _pointer = disk.plugins(path=_path,name=_name,context=_context)
                if _pointer :
                    _uri = "/".join(["api",_key,_name]) 
                    if _context :
                        _uri = f'{_context}/{_uri}'
                    _map[_uri] = _pointer
        #
        # We are adding some source specific plugins to the user-defined plugins
        # This is intended to have out-of the box plugins...
        #
        
        if self._ISCLOUD :
            _plugins = cloud.plugins(_context)
        else:
            _plugins = disk.plugins(context=_context)
        #
        # If there are any plugins found, we should load them and use them
        
        if _plugins :
            _map = dict(_map,**_plugins)
        else:
            pass
        
        self._plugins =  _map
        self._config['plugins'] = self._plugins
   

    def _isource (self):
        """
        Initializing the source of the data, so we can read/write load from anywhere
        """
        if 'source' not in self._config['system'] :
            return
        #
        #
        self._ISCLOUD = 'source' in self._config['system'] and self._config['system']['source']['id'] == 'cloud'
        _source = self._config['system']['source']
        if 'key' in _source :
            #
            _path = _source['key']
            if os.path.exists(_path) :
                f = open(_path)
                _source['key'] = f.read()
                f.close()
                self._config['system']['source'] = _source
    def _ilayout(self,**_args):
        """
        Initialization of the layout section (should only happen if ) being called via framework
        :path   path to the dependent apps
        """
        _layout = self._config['layout']
        _path = os.sep.join(_args['path'].split(os.sep)[:-1])
        #
        # find the new root and the one associated with the dependent app
        #

        pass
    def _imenu(self,**_args):
        _gshandler = self._handler()
        _object = _gshandler.build(self._config) #-- this will build the menu
        #
        # post-processing menu, overwrite items and behaviors
        #
        
        _layout = copy.deepcopy(self._config['layout'])
        _overwrite = _layout['overwrite'] if 'overwrite' in _layout else {}
        _context = self.system()['context']
        for _name in _object :
            _submenu = _object[_name]
            _index = 0
            for _item in _submenu :
                text = _item['text'].strip()
                if text in _overwrite :
                    if 'uri' in _item and  'url' in _overwrite[text] :
                        del _item['uri']
                    _item = dict(_item,**_overwrite[text])
                
                if 'uri' in _item and 'type' in _item and _item['type'] != 'open':
                    _item['uri'] = _item['uri'] #.replace(_layout['root'],'')
                    # _item['uri'] = _gshandler._format(_item['uri'],self._config)

                _submenu[_index] = _item
                _index += 1
        #
        # updating menu _items as it relates to apps, configuration and the order in which they appear
        #
        _layout['menu'] = _object
        self._menu      = _object 
        self._config['layout'] = _layout
        self._iapps()
        self._iorder()
        pass

    def _iorder (self):
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
    def _iapps (self):
        """
        Initializing dependent applications into a menu area if need be
        """
        _layout = self._config['layout']
        _menu   = _layout['menu'] if 'menu' in _layout else {}
        _system = self._config['system']
        _context= _system['context']
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
        #
        # update the menu items and the configuration 
        #
        _layout['menu'] = _menu
        self._config['layout'] = _layout
    def _ilogo(self):
        _gshandler = self._handler()

        pass
    def _iconfig(self,**_args):
        """
        Implement this in a base class
        :path or uri
        """
        raise Exception ("Configuration Initialization is NOT implemented")
    def _uconfig(self,**_args):
        """
        This file will update the configuration provided the CMS is run in shared mode (framework level)
        """
        if not self._location :
            return ;
        _path = os.sep.join(self._location.split(os.sep)[:-1])
        _layout = self._config['layout']
        _oroot = _layout['root']
        _orw = _layout['overwrite']
        _index = _layout['index']
        _newpath = os.sep.join([_path,_oroot])
        self._config['system']['portal'] = self._caller != None
        _context = self.system()['context']
        if self._caller :
            #
            _callerContext = self._caller.system()['context']
            if not self._config['system']['context'] :
                self._config['system']['context'] = _callerContext
            self._config['system']['caller'] = {'icon': 'caller/main/'+self._caller.system()['icon'].replace(_callerContext,'')}
            _context = _callerContext
        
        
        if os.path.exists(_newpath) and not self._ISCLOUD:
            #
            # LOG: rewrite due to the mode in which the site is being run
            #
            _api = f'{_context}/api/disk/read?uri='+_oroot
            _stream = json.dumps(self._config)
            _stream = _stream.replace(_oroot,_api)
            # self._config = json.loads(_stream)            
            self._config['layout']['root'] = _oroot

            # self._config['layout']['overwrite'] = _orw
        #
        # We need to update the  logo/icon
        _logo = self._config['system']['logo']
        if self._ISCLOUD:
            
            _icon = f'{_context}/api/cloud/download?doc=/{_logo}'
            
            
        else:
            
            _icon = f'{_context}/api/disk/read?uri={_logo}'  
            if disk.exists(uri=_logo,config=self._config):
                _icon = _logo
            if self._location :
                self._config['layout']['location'] = _path
                
        self._config['system']['icon'] = _icon 
        self._config['system']['logo'] = _logo 
        
        # self.set('layout.root',os.sep.join([_path,_oroot]))
        pass
class Accessor (Initializer):
    """
    This is a basic structure for an application working in either portal or app mode
    """
    def __init__(self,**_args):
        super().__init__(**_args)
        pass
    def _iconfig(self, **_args):
        """
        initialization of the configuration file i.e loading the files and having a baseline workable structure
        :path|stream   path of the configuration file
                        or stream of JSON configuration file
        """
        if 'path' in _args :
            f = open(_args['path'])
            self._config = json.loads(f.read())
            f.close()
        elif 'stream' in _args :
            _stream = _args['stream']
            if type(_stream) == 'str' :
                self._config  = json.loads(_stream)
            elif type(_stream) == io.StringIO :
                self._config =  json.loads( _stream.read())
        self._ISCLOUD = 'source' in self._config['system'] and self._config['system']['source']['id'] == 'cloud'
        #
        #
        # self._name = self._config['system']['name'] if 'name' in self._config['system'] else _args['name']
    def system (self,skip=[]):
        """
        This function returns system attributes without specific components
        """
        _data = copy.deepcopy(self._config['system'])
        exclude = skip
        _system = {}
        if exclude and _system:
            for key in _data.keys() :
                if key not in exclude :
                    _system[key] = _data[key]
        else:
            _system= _data
        return _system 
    def layout (self):
        return copy.copy(self._config['layout'])
    def plugins (self):
        return copy.copy(self._config['plugins'])
    def config (self):
        
        return copy.copy(self._config)
    def app(self):
        _system = self.system()
        return _system['app'] 
    def set(self,key,value):
        """
        This function will update/set an attribute with a given value
        :key    
        """
        _keys = key.split('.')
        _found = 0
        if _keys[0] in self._config :
            _object = self._config[_keys[0]]
            for _akey in _object.keys() :
                if _akey == _keys[-1] :
                    _object[_akey] = value
                    _found = 1
                    break

        #
        #
        return _found
        #
class MicroService (Accessor):
    """
    This is a CMS MicroService class that is capable of initializing a site and exposing accessor functions
    """
    def __init__(self,**_args):
        super().__init__(**_args)
    def format(_content,mimetype):
        pass
    def html (self,uri, id) :
        _system = self.system()
        _gshandler = self._handler()
        #
        #@TODO:
        # The uri here must be properly formatted, We need to define the conditions for this
        #
        _html = _gshandler.html(uri,self._config)
        return " ".join([f'<div id="{id}" > ',_html, '</div>'])
    def context(self):
        return Environment(loader=BaseLoader())
    def data (self,**_args):
        request = _args['request']
    def icon (self):
        _handler = self._handler()
        _uri = self.system()['icon']

        return _handler.read(uri=_uri,config=self._config)
class CMS:
    def __init__(self,**_args) :
        
        # _app = Getter (path = path)
        # _void = MicroService()
        
        _app = MicroService (**_args)
        self._id = 'main'
        # _app.load()
        self._apps = {}
        _system = _app.system()
        if 'routes' in _system :
            _system = _system['routes']
            for _name in _system :
                _path = _system[_name]['path']
                
                self._apps[_name] = MicroService(context=_name,path=_path,caller=_app,location=_path)

        self._apps['main'] = _app    
    #
    # The following are just a simple delegation pattern (it makes the calling code simpler)
    #
    def config (self):
        return self.get().config()
    
    def render(self,_uri,_id,_appid):
        # _handler = self.get()
        _handler = self._apps[_appid]
        _config = _handler.config()
        _args = {'layout':_handler.layout()}
        if 'plugins' in _config:
            _args['routes'] = _config['plugins']
        
        _html =  _handler.html(_uri,_id)
        _args['system'] = _handler.system(skip=['source','app'])
        e = Environment(loader=BaseLoader()).from_string(_html)
        _args[_id] =  str(e.render(**_args)) #,_args
        return _args
    def set(self,_id):
        self._id = _id
    def get(self):
        return self._apps['main'] if self._id not in self._apps else self._apps[self._id]
    def get_main(self):
        return self._apps['main']
