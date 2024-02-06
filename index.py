__doc__ = """
    arguments :
        --config    path of the configuration otherwise it will look for the default in the working directory
"""
from flask import Flask,render_template,send_from_directory,request, redirect
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
    global _route
    _system = _route.get ().system()
    _handler = _route.get()

    _logo =_system['icon'] if 'icon' in _system else 'static/img/logo.svg'
    return _handler.get(_logo)
    # # _root = _route.get().config()['layout']['root']
    # # print ([_system])
    # # if 'source' in _system and 'id' in _system['source'] and (_system['source']['id'] == 'cloud'):
    # #     uri = f'/api/cloud/downloads?doc=/{_logo}'
    # #     print (['****' , uri])
    #     # return redirect(uri,200) #,{'content-type':'application/image'}
    # # else:
        
    # #     return send_from_directory(_root, #_app.root_path, 'static/img'),
    #                            _logo, mimetype='image/vnd.microsoft.icon')

@_app.route("/")
def _index ():
    global _config
    global _route
    _handler = _route.get() 
    _config = _handler.config()
    _system = _handler.system()
    _plugins= _handler.plugins()
    _args = {}
    # if 'plugins' in _config :
    #     _args['routes']=_config['plugins']
    # _system = cms.components.get_system(_config) #copy.deepcopy(_config['system'])
    _html = ""
    try:
        
        uri = os.sep.join([_config['layout']['root'], _config['layout']['index']])
        _html = _route.get().html(uri,'index',_config,_system)
        _index_page = "index.html"
    except Exception as e:
        print ()
        print (e)
        _index_page = "404.html"
        _args['uri'] = request.base_url
        pass
    # if 'source' in _system :
    #     del _system['source']
    _args = {'layout':_config['layout'],'index':_html}
    _args['system'] = _handler.system(skip=['source','app','route'])
    
    return render_template(_index_page,**_args)

# @_app.route('/id/<uid>') 
# def people(uid):
#     """
#     This function will implement hardened links that can directly "do something"
#     """
#     global _config    
#     return "0",200
  
@_app.route('/dialog')
def _dialog ():
    # global _config 
    global _route
    _handler = _route.get()
    _system = _handler.system()
    _config = _handler.config()
    _uri = os.sep.join([_config['layout']['root'],request.headers['uri']])
    # _uri = request.headers['uri']
    _id = request.headers['dom']
    # _data = cms.components.data(_config)
    _args = {} #{'system':_config['system']}
    _args['title'] = _id
    # if 'plugins' in _config :
    #     _args['routes'] = _config['plugins']
    # _system = copy.deepcopy(_config['system'])
    
    # _html =  cms.components.html(_uri,_id,_config,_system)
    _html =  _handler.html(_uri,_id,_config,_system)

    e = Environment(loader=BaseLoader()).from_string(_html)     
    # if 'source' in _system :
    #     del _system['source']
    _args['system'] = _handler.system(skip=['source','routes','app'])
    
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
    # global _config
    global _route
    _handler = _route.get()


    uri =  '/'.join(['api',module,name])
    # _args = dict(request.args,**{})
    # _args['config'] = _handler.config()
    _plugins = _handler.plugins()
    if uri not in _plugins :
        _data = {}
        _code = 404
    else:
        pointer = _plugins[uri]
        # if _args :
        #     _data = pointer (**_args)
        # else:
        #     _data = pointer()
        _data = pointer(request=request,config=_handler.config())
        _code = 200 if _data else 500
    
    
    return _data,_code
@_app.route("/api/<module>/<name>" , methods=['POST'])
def _post (module,name):
    # global _config
    global _route
    _handler = _route.get()
    _config = _handler.config()
    _plugins = _handler.plugins()
    uri =  '/'.join(['api',module,name])
    
    # _args = request.json
    # _args['config'] = _config
    code = 404
    
    _info = ""
    if uri in _plugins :
        _pointer = _plugins[uri]
        # _info = _pointer(**_args)
        _info = _pointer(request=request,config=_handler.config() )
        if _info:
            code = 200
        else:
            # _info = ""
            code = 500
            
        # _info  =io.BytesIO(_info)
        
        # _info = base64.encodebytes(_info.getvalue()).decode('ascii')
    
    return _info,code
@_app.route('/version')
def _version ():
    global _route
    _handler = _route.get()
    global _config 
    return _handler.system()['version']
@_app.route('/reload',methods=['POST'])
def reload():
    global _route

    _handler = _route.get_main()
    _system = _handler.system()
    _key = request.headers['key'] if 'key' in request.headers else None
    if not 'source' in _system :
        _systemKey = None
    elif 'key' in _system['source'] and _system['source']['key']:
        _systemKey = _system['source']['key']
    print ([_key,_systemKey,_systemKey == _key])
    if _key and _systemKey and _systemKey == _key :
        _handler.load()
        return "",200
        pass
    return "",403
@_app.route('/page',methods=['POST'])
def cms_page():
    """
    return the content of a folder formatted for a menu
    """
    # global _config
    global _route
    _handler = _route.get()
    _config = _handler.config()

    # _uri = os.sep.join([_config['layout']['root'],request.headers['uri']])
    _uri = request.headers['uri']
    if 'dom' not in request.headers :
        _id = _uri.split('/')[-1].split('.')[0]
    else:
        _id = request.headers['dom']
    _args = {'layout':_config['layout']}
    if 'plugins' in _config:
        _args['routes'] = _config['plugins']
    
    
    _system = _handler.system() #cms.components.get_system(_config)
    _html =  _handler.html(_uri,_id,_args,_system) #cms.components.html(_uri,_id,_args,_system)
    e = Environment(loader=BaseLoader()).from_string(_html)
    # _data = {} #cms.components.data(_config)
    _system = cms.components.get_system(_config)
    _args['system'] = _handler.system(skip=['source','app'])
   
    _html = e.render(**_args)
    return _html,200
@_app.route('/page')
def _cms_page ():
    # global _config
    global _route
    _handler = _route.get()
    _config = _handler.config()
    _uri = request.args['uri']
    # _uri = os.sep.join([_config['layout']['root'],_uri])
    _title = request.args['title'] if 'title' in request.args else ''
    _args = {'system':_handler.system()} #cms.components.get_system(_config) }
    # if 'plugins' in _config:
    #     _args['routes'] = _config['plugins']
    _html = _handler.html(_uri,_title,_args) #  cms.components.html(_uri,_title,_args)
    e = Environment(loader=BaseLoader()).from_string(_html)
    _args['system'] = _handler.system(skip=['app','source'])
    return e.render(**_args),200

@_app.route('/set/<id>')
def set(id):
    global _route
    _handler = _route.set(id)
    return redirect('/')
@_app.route('/<id>')    
def _open(id):
    global _route
    _route.set(id)
    return _index()
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
    
    pass
   
    _path = SYS_ARGS['config'] if 'config' in SYS_ARGS else 'config.json'
    if os.path.exists(_path):
        _route = cms.engine.Router(path=_path)
        _args = _route.get().get_app()
        _app.run(**_args)
    #     _config = json.loads((open (_path)).read())
    #     if 'theme' not in _config['system'] :
    #         _config['system']['theme'] = 'magazine.css'
    #     #
    #     # root can be either on disk or in the cloud ...
    #     #   root: "<path>"  reading from disk
    #     #   root: {uid,token,folder}
    #     #

    #     _root = _config['layout']['root']        
    #     _menu = cms.components.menu(_config)  
    #     if 'order' in _config['layout'] and 'menu' in _config['layout']['order']:
    #         _sortedmenu = {}
    #         for _name in _config['layout']['order']['menu'] :
    #             if _name in _menu :
    #                 _sortedmenu[_name] = _menu[_name]
            
    #         _menu = _sortedmenu if _sortedmenu else _menu
    #     _config['layout']['menu'] = _menu #cms.components.menu(_config)
    #     # if 'data' in _config :
    #     #     _config['data'] = cms.components.data(_config['data'])
    #     #
    #     _map = cms.components.plugins(_config)
    #     _config['plugins'] = _map
    #     # Let us load the plugins if any are available 
    #     # if 'plugins' in _config :
    #     #     _map = cms.components.plugins(_config)
    #     #     if _map :  
    #     #        _config['plugins'] = _map
    #         #
    #         # register the functions with Jinja2
    #         # cms.components.context(_config)
        
    #     _args = _config['system']['app']
    #     _app.run(**_args)
    # else:
    #     print (__doc__)
    #     print ()    
