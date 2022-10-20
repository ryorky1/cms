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

from jinja2 import Environment, BaseLoader



_app = Flask(__name__)
@_app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(_app.root_path, 'static/img'),
                               'vanderbilt-logo.png', mimetype='image/vnd.microsoft.icon')

@_app.route("/")
def _index ():
    global _config
    _args = {}
    try:
        _args = {'system':_config['system']}
        _args['layout'] = _config['layout']
        # _args = dict(_args,**_config['layout'])
        # _args = copy.copy(_config)
        uri = os.sep.join([_config['layout']['root'], _config['layout']['index']])
        _html  = cms.components.html(uri,'index')
        e = Environment(loader=BaseLoader()).from_string(_html)     
        _args['index'] = e.render(**_args)
        _index_page = "index.html"
    except Exception as e:
        _index_page = "404.html"
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
    _html =  cms.components.html(_uri,_id)
    e = Environment(loader=BaseLoader()).from_string(_html)     
    _data = cms.components.data(_config)
    _args = {'system':_config['system'],'data':_data}
    
    _html = ''.join(["<div style='padding:1%'>",str( e.render(**_args)),'</div>'])
    
    return render_template('dialog.html',title=_id,html=_html)
    # return _html
    # e = Environment(loader=BaseLoader()).from_string(_html)
    # _data = cms.components.data(_config)
    # _args = {'system':_config['system'],'data':_data}
    
    # _html = ( e.render(**_args))

@_app.route('/page',methods=['POST'])
def cms_page():
    """
    return the content of a folder formatted for a menu
    """
    global _config
    _uri = os.sep.join([_config['layout']['root'],request.headers['uri']])
    _id = request.headers['dom']
    
    _html =  cms.components.html(_uri,_id)
    e = Environment(loader=BaseLoader()).from_string(_html)
    _data = cms.components.data(_config)
    _args = {'system':_config['system'],'data':_data}
    
    _html = ( e.render(**_args))
    return _html,200


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
        # _config['data'] = cms.components.data(_config)
        
        _args = _config['system']['app']
        _app.run(**_args)
    else:
        print (__doc__)
        print ()
