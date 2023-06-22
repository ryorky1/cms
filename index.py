__doc__ = """
    arguments :
        --config    path of the configuration otherwise it will look for the default in the working directory
"""
from flask import Flask,render_template,send_from_directory,request
import flask
import transport
from transport import providers
import cms
import sys
import os
import json
import copy
import io
import base64
from jinja2 import Environment, BaseLoader



_app = Flask(__name__)
@_app.route('/favicon.ico')
def favicon():
    global _config
    
    return send_from_directory(os.path.join(_app.root_path, 'static/img'),
                               'logo.png', mimetype='image/vnd.microsoft.icon')

@_app.route("/")
def _index ():
    global _config
    _args = {'system':_config['system']}
    if 'plugins' in _config :
        _args['routes']=_config['plugins']
    try:
        
        _args['layout'] = _config['layout']
        # _args = dict(_args,**_config['layout'])
        # _args = copy.copy(_config)
        uri = os.sep.join([_config['layout']['root'], _config['layout']['index']])
        _html  = cms.components.html(uri,'index',_args)
        _args['index'] = _html
        # e = Environment(loader=BaseLoader()).from_string(_html)   
        # e = cms.components.context(_config).from_string(_html)
        # _args['index'] = e.render(**_args)
        _index_page = "index.html"
    except Exception as e:
        print ()
        print (e)
        _index_page = "404.html"
        _args['uri'] = request.base_url
        pass
    
    return render_template(_index_page,**_args)

@_app.route('/id/<uid>') 
def people(uid):
    """
    This function will implement hardened links that can directly "do something"
    """
    global _config    
    return "0",200
  
@_app.route('/dialog')
def _dialog ():
    global _config 
    _uri = os.sep.join([_config['layout']['root'],request.headers['uri']])
    _id = request.headers['dom']
    # _data = cms.components.data(_config)
    _args = {'system':_config['system']}
    _args['title'] = _id
    if 'plugins' in _config :
        _args['routes'] = _config['plugins']
    _html =  cms.components.html(_uri,_id,_args)
    e = Environment(loader=BaseLoader()).from_string(_html)     

    
    _args['html'] = _html
    _html = ''.join(["<div style='padding:1%'>",str( e.render(**_args)),'</div>'])
    
    return render_template('dialog.html',**_args) #title=_id,html=_html)
    # return _html
    # e = Environment(loader=BaseLoader()).from_string(_html)
    # _data = cms.components.data(_config)
    # _args = {'system':_config['system'],'data':_data}
    
    # _html = ( e.render(**_args))
@_app.route('/api/<module>/<name>')
def _getproxy(module,name) :
    """
    This endpoint will load a module and make a function call
    :_module entry specified in plugins of the configuration
    :_name  name of the function to execute
    """
    global _config

    uri =  '/'.join(['api',module,name])
    if uri not in _config['plugins'] :
        _data = {}
        _code = 404
    else:
        pointer = _config['plugins'][uri]
        _data = pointer ()
        _code = 200
    
    
    return _data,_code
@_app.route("/api/<module>/<name>" , methods=['POST'])
def _post (module,name):
    global _config
    uri =  '/'.join(['api',module,name])
    
    _args = request.json
    code = 404
    
    _info = ""
    if uri in _config['plugins']  and _args:
        _pointer = _config['plugins'][uri]
        _info = _pointer(_args)
        if _info:
            code = 200
        else:
            _info = ""
            
        # _info  =io.BytesIO(_info)
        
        # _info = base64.encodebytes(_info.getvalue()).decode('ascii')
    return _info,code
@_app.route('/version')
def _version ():
    global _config 
    return _config['system']['version']
@_app.route('/page',methods=['POST'])
def cms_page():
    """
    return the content of a folder formatted for a menu
    """
    global _config
    _uri = os.sep.join([_config['layout']['root'],request.headers['uri']])
    _id = request.headers['dom']
    _args = {'system':_config['system']}
    if 'plugins' in _config:
        _args['routes'] = _config['plugins']
        
    _html =  cms.components.html(_uri,_id,_args)
    e = Environment(loader=BaseLoader()).from_string(_html)
    # _data = {} #cms.components.data(_config)
    
   
    _html = e.render(**_args)
    return _html,200
@_app.route('/page')
def _cms_page ():
    global _config
    _uri = request.args['uri']
    _uri = os.sep.join([_config['layout']['root'],_uri])
    _title = request.args['title'] if 'title' in request.args else ''
    _args = {'system':_config['system']}
    if 'plugins' in _config:
        _args['routes'] = _config['plugins']
        
    _html =  cms.components.html(_uri,_title,_args)
    e = Environment(loader=BaseLoader()).from_string(_html)    
    return e.render(**_args),200
#
# Let us bootup the application
SYS_ARGS = {}

if len(sys.argv) > 1:
    
    N = len(sys.argv)
    for i in range(1,N):
        value = None
        if sys.argv[i].startswith('--'):
            key = sys.argv[i][2:] #.replace('-','')
            SYS_ARGS[key] = 1			
            if i + 1 < N:
                value = sys.argv[i + 1] = sys.argv[i+1].strip()
            if key and value and not value.startswith('--'):
                SYS_ARGS[key] = value
                


        i += 2
if __name__ == '__main__' :
    
   
    _path = SYS_ARGS['config'] if 'config' in SYS_ARGS else 'config.json'
    if os.path.exists(_path):
        _config = json.loads((open (_path)).read())
        _root = _config['layout']['root']
        _config['layout']['menu'] = cms.components.menu(_root,_config)
        if 'map' in _config['layout'] and 'order' in _config['layout'] and 'menu' in _config['layout']['order'] :
            """
            We are insuring that the order of the menu items can be manually configured and have proper representation without quircks associated with folder name convention
            """
            _map = _config['layout']['map']
            labels = [_name if _name not in _map else _map[_name] for _name in _config['layout']['order']['menu']]
            labels = [_name for _name in labels if _name in _config['layout']['menu']]
            _config['layout']['order']['menu'] = labels
 
        else:
            _config['layout']['order']['menu'] = list(_config['layout']['menu'].keys())        
 
        # _config['data'] = cms.components.data(_config)
        #
        # Let us load the plugins if any are available 
        if 'plugins' in _config :
            _map = cms.components.plugins(_config)
            if _map :  
               _config['plugins'] = _map
            #
            # register the functions with Jinja2
            cms.components.context(_config)
        _args = _config['system']['app']
        _app.run(**_args)
    else:
        print (__doc__)
        print ()
