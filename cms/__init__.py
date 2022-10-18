from genericpath import isdir
import os
import pandas as pd
import transport
import copy
from jinja2 import Environment, BaseLoader

class components :
    def folders (_path):
        _content = os.listdir(_path)
        
        return [_name for _name in _content if os.path.isdir(os.sep.join([_path,_name]))]
        
    def content (_folder) :
        if os.path.exists(_folder) :
            # return [{'text':_name.split('.')[0].replace('_', ' ').replace('-',' ').strip(),'uri': os.sep.join([_folder,_name])} for _name in os.listdir(_folder) if not _name.startswith('_') and os.path.isfile( os.sep.join([_folder,_name]))]
            return [{'text':_name.split('.')[0].replace('_', ' ').replace('-',' ').strip(),'uri': os.sep.join([_folder,_name])} for _name in os.listdir(_folder) if not _name.startswith('_') and os.path.isfile( os.sep.join([_folder,_name]))]
        else:
            return []
    def menu(_path,_config):
        """
        This function will read menu and sub-menu items from disk structure,
        The files are loaded will
        """
        _items = components.folders(_path) 
        
        _layout = copy.deepcopy(_config['layout'])
        _overwrite = _layout['overwrite'] if 'overwrite' in _layout else {}
        #
        # content of each menu item
        _subItems = [ components.content (os.sep.join([_path,_name]))for _name in _items ]
        _object =  dict(zip(_items,_subItems))
        #-- applying overwrites to the menu items 
        for _name in _object :
            _submenu = _object[_name]
            _index = 0
            for _item in _submenu :
                text = _item['text']
                if text in _overwrite :
                    if 'uri' in _item and 'url' in 'url' in _overwrite[text] :
                        del _item['uri']
                    _item = dict(_item,**_overwrite[text])
                if 'uri' in _item:
                    _item['uri'] = _item['uri'].replace(_layout['root'],'')
                _submenu[_index] = _item
                _index += 1
        return _object 
    def html(uri,id,_args=None) :
        """
        This function reads a given uri and returns the appropriate html document, and applies environment context

        """
        _html = (open(uri)).read()       
        #return ' '.join(['<div id=":id" class=":id">'.replace(':id',id),_html,'</div>'])
        _html   = ' '.join(['<div id=":id" class=":id">'.replace(':id',id),_html,'</div>'])
        appContext = Environment(loader=BaseLoader()).from_string(_html)
        return appContext.render(**_args)
    def data (_args):
        """
        :store  data-store parameters (data-transport, github.com/lnyemba/data-transport)
        :query  query to be applied against the store (expected data-frame)
        """
        _store  = _args['store']
        reader  = transport.factory.instance(**_store)
        _queries= copy.deepcopy(_store['query'])
        _data   = reader.read(**_query)
        return _data
    def csv(uri) :
        return pd.read(uri).to_html()

