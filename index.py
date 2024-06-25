__doc__ = """
    arguments :
        --config    path of the configuration otherwise it will look for the default in the working directory
"""
from flask import Flask,render_template,send_from_directory,request, redirect, Response, session
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
import typer
from typing_extensions import Annotated
from typing import Optional


import pandas as pd
import uuid
import datetime


from cms import disk, cloud, engine

_app = Flask(__name__)
cli = typer.Typer()
# @_app.route('/favicon.ico')
# def favicon():
#     global _route
#     _system = _route.get ().system()
#     _handler = _route.get()

#     _logo =_system['icon'] if 'icon' in _system else 'static/img/logo.svg'
#     return _handler.get(_logo)
#     # # _root = _route.get().config()['layout']['root']
#     # # print ([_system])
#     # # if 'source' in _system and 'id' in _system['source'] and (_system['source']['id'] == 'cloud'):
#     # #     uri = f'/api/cloud/downloads?doc=/{_logo}'
#     # #     print (['****' , uri])
#     #     # return redirect(uri,200) #,{'content-type':'application/image'}
#     # # else:
        
#     # #     return send_from_directory(_root, #_app.root_path, 'static/img'),
#     #                            _logo, mimetype='image/vnd.microsoft.icon')
def _getHandler () :
    _id = session.get('app_id','main')
    return _route._apps[_id]
def _setHandler (id) :
    session['app_id'] = id
@_app.route("/robots.txt")
def robots_txt():
    """
    This function will generate a robots expression for a variety of crawlers, the paths will be provided by
    menu options
    """
    global _route
    _system = _route.get ().system()

    _info  = ['''
    User-agent: *
    Allow: /
    ''']

    if 'routes' in _system  :
        for _key in _system['routes'] :
            _uri = '/'.join(['',_key])
            _info.append(f'''
    User-agent: *
    Allow: {_uri}
                        ''')
    
    # return '\n'.join(_info),200,{'Content-Type':'plain/text'}
    return Response('\n'.join(_info), mimetype='text/plain')    
@_app.route("/")
def _index ():
    # global _config
    # global _route
    # _handler = _route.get() 
    # _config = _route.config()
    _handler = _getHandler()
    _config = _handler.config()
    print ([' serving ',session.get('app_id','NA'),_handler.layout()['root']])
    # _system = _handler.system()
    # _plugins= _handler.plugins()
    # _args = {}
    # # if 'plugins' in _config :
    # #     _args['routes']=_config['plugins']
    # # _system = cms.components.get_system(_config) #copy.deepcopy(_config['system'])
    # _html = ""
    _args={'system':_handler.system(skip=['source','app','data']),'layout':_handler.layout()}
    try:
        uri = os.sep.join([_config['layout']['root'], _config['layout']['index']])
        
    #     # _html = _route.get().html(uri,'index',_config,_system)
    #     _html = _handler.html(uri,'index')
        _index_page = "index.html"
        _args = _route.render(uri,'index',session.get('app_id','main'))
    except Exception as e:
    #     print ()
        print (e)
        _index_page = "404.html"
    #     _args['uri'] = request.base_url
    #     pass
    # # if 'source' in _system :
    # #     del _system['source']
    # _args = {'layout':_config['layout'],'index':_html}
    # _args['system'] = _handler.system(skip=['source','app','route'])
    
    return render_template(_index_page,**_args),200 if _index_page != "404.html" else 200

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
    _uri = request.headers['uri']
    
    _id = request.headers['dom']
    # _html = ''.join(["<div style='padding:1%'>",str( e.render(**_args)),'</div>'])
    _args = _route.render(_uri,'html',session.get('app_id','main'))
    _args['title'] = _id
    return render_template('dialog.html',**_args) #title=_id,html=_html)
@_app.route("/caller/<app>/api/<module>/<name>")
def _delegate_call(app,module,name):
    global _route
    _handler = _route._apps[app]
    return _delegate(_handler,module,name)

@_app.route('/api/<module>/<name>')
def _getproxy(module,name) :
    """
    This endpoint will load a module and make a function call
    :_module entry specified in plugins of the configuration
    :_name  name of the function to execute
    """
    # global _config
    # global _route
    # _handler = _route.get()
    _handler = _getHandler()
    return _delegate(_handler,module,name)

def _delegate(_handler,module,name):
    global _route
    uri =  '/'.join(['api',module,name])
    # _args = dict(request.args,**{})
    # _args['config'] = _handler.config()
    _plugins = _handler.plugins()
    _context = _handler.system()['context']
    if _context :
        uri  = f'{_context}/{uri}'
    
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
        if type(_data) == pd.DataFrame :
            _data = _data.to_dict(orient='records')
        if type(_data) == list:
            _data = json.dumps(_data)   
        _code = 200 if _data else 500
    return _data,_code
@_app.route("/api/<module>/<name>" , methods=['POST'])
def _post (module,name):
    # global _config
    # global _route
    # _handler = _route.get()
    _handler = _getHandler()
    return _delegate(_handler,module,name)

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
            _handler.reload()
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
    # _handler = _route.get()
    # _config = _handler.config()
    _handler = _getHandler()
    _config = _handler.config()
    # _uri = os.sep.join([_config['layout']['root'],request.headers['uri']])
    _uri = request.headers['uri']
    if 'dom' not in request.headers :
        _id = _uri.split('/')[-1].split('.')[0]
    else:
        _id = request.headers['dom']
    # _args = {'layout':_config['layout']}
    # if 'plugins' in _config:
    #     _args['routes'] = _config['plugins']
    
    # _system = _handler.system() #cms.components.get_system(_config)
    # # _html =  _handler.html(_uri,_id,_args,_system) #cms.components.html(_uri,_id,_args,_system)

    # _html =  _handler.html(_uri,_id)
    # # _system = cms.components.get_system(_config)
    # _args['system'] = _handler.system(skip=['source','app'])
    # e = Environment(loader=BaseLoader()).from_string(_html)
    # _html = e.render(**_args)
    if 'read?uri=' in _uri or 'download?doc=' in _uri :
        _uri = _uri.split('=')[1]
    
    _args = _route.render(_uri,_id,session.get('app_id','main'))
    return _args[_id],200
    # return _html,200
@_app.route('/page')
def _cms_page ():
    # global _config
    global _route
    # _handler = _route.get()
    # _config = _handler.config()
    _uri = request.args['uri']
    
    # _uri = os.sep.join([_config['layout']['root'],_uri])
    _title = request.args['title'] if 'title' in request.args else ''
    _args = _route.render(_uri,_title,session.get('app_id','main'))
    return _args[_title],200

@_app.route('/set/<id>')
def set(id):
    global _route
    _setHandler(id)
    # _route.set(id)
    # _handler = _route.get()
    _handler = _getHandler()
    _context = _handler.system()['context']
    _uri = f'/{_context}'.replace('//','/')
    return redirect(_uri)
@_app.route('/<id>')    
def _open(id):
    global _route
    # _handler = _route.get()

    _handler = _getHandler()
    if id not in _route._apps :

        _args = {'config':_handler.config(), 'layout':_handler.layout(),'system':_handler.system(skip=['source','app'])}
        return render_template("404.html",**_args)
    else:
        _setHandler(id)
        # _route.set(id)
        return _index()


@cli.command()
def start (
    path:Annotated[str,typer.Argument(help="path of the manifest file")]='qcms-manifest.json',
    shared:bool=False) :
    """
    This function is designed to start the application with its associated manifest (configuration) location
    :path   path to the  the manifest
    :shared run in shared mode i.e 
    """
    global _route

    if os.path.exists(path) and os.path.isfile(path):
        _args = {'path':path}
        # if shared :
        #     _args['location'] = path
        #     _args['shared'] = shared
        _args['location'] = path
        _args['shared'] = shared
        
        # _route = cms.engine.Router(**_args) #path=path,shared=shared)
        
        _route = cms.engine.basic.CMS(**_args)
        # dir(_route)
        # _args = _route.get().get_app()
        _args = _route.get().app()
        _app.secret_key = str(uuid.uuid4())
        _app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=24)
        _app.run(**_args)
        _status = 'found'
    else:
        _status = 'not found'
    print(f'''
            manifest: {path}
            status  : {_status}
        ''')
@cli.command(name='help')
def _help() :
    pass
if __name__ == '__main__' :
    cli()
