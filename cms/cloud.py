"""
Reads from nextcloud
"""

import nextcloud_client as nc
import copy
from mistune import markdown #version 0.8.4

import time
import json

_CLOUDHANDLER = None
def login(path): #(**_args):
    f = open(path)
    _args = json.loads(f.read())
    f.close()
    nx = nc.Client(_args['url'])
    nx.login(_args['uid'],_args['token'])
    time.sleep(1)
    return nx

def _format_root_folder (_root):
    if _root[0] == '/' :
        _root = _root[1:]
    if _root[-1] == '/' :
        _root = _root[:-1]
    
    return _root.replace('//','/')
def list_files(folder,_config) :
    """
    List the content of a folder (html/md) for now
    """
    _authfile = _config['system']['source']['auth']
    _handler = login(_authfile)    
    _files = _handler.list(folder,50)
    
    _content = []
    for _item in _files :
        if _item.file_type == 'file' and _item.get_content_type() in ['text/markdown','text/html'] :
            _uri = '/'.join(_item.path.split('/')[2:])
            _uri = _item.path
            # _content.append({'text':_item.name.split('.')[0],'uri':_uri})
            _content.append(_item.name)
    
    return _content

def content(_args):
    """
    :url
    :uid
    :token
    :folder
    """
    # global _CLOUDHANDLER
    # if not _CLOUDHANDLER :
    #     _handler = nc.Client(_args['url'])
    #     _handler.login(_args['uid'],_args['token'])
    # _CLOUDHANDLER = _handler
    _handler = login(_args['auth'])
    _root = _args['folder']
    if _root.startswith('/') :
        _root = _root[1:]
    if _root.endswith('/') :
        _root = _root[:-1]
    _files = _handler.list(_root,30)
    _menu = {} #[_args['folder']] + [_item for _item in _files if _item.file_type == 'dir' and _item.name[0] not in ['.','_']]
    _menu = {} #dict.fromkeys(_menu,[])
    for _item in _files :
        _folder = _item.path.split(_item.name)[0].strip()
        _folder = _folder.replace(_root,'').replace('//','') 

        #
        # The following lines are intended to prevent an irradict recursive read of a folder content
        # We want to keep things simple as we build the menu
        #
        if len (_folder.split('/')) > 2:
            continue
        else:
            _folder = _folder.replace('/','')
        if _item.name[0] in ['.','_'] or _folder == '':
            continue ;
        if _item.file_type == 'file' and _item.get_content_type() in ['text/markdown','text/html'] :
            # _folder = _item.path.split(_item.name)[0].strip()
            # _folder = _folder.replace(_root,'').replace('//','')
            if _folder == '' :
                _folder = str(_root)
            _folder = _folder.replace('/' ,' ').strip()
            if _folder not in _menu :
                _menu [_folder] = []
            uri = '/'.join(_item.path.split('/')[2:])
            uri = _item.path
            _menu[_folder].append({'text':_item.name.split('.')[0],'uri':uri})
    #
    # clean up the content ...
    _keys = [_name for _name in _menu.keys() if _name.startswith('_')]
    [_menu.pop(_name) for _name in _keys]
    _handler.logout()
    return _menu


def build(_config):
    """
    The function will build a menu based on a folder structure in nextcloud
    :_args  authentication arguments for nextcloud
    :_config    configuration for the cms
    """
    _args = {'auth':copy.deepcopy(_config['system']['source']['auth'])}
    _args['folder'] = _config['layout']['root']
    # update(_config)
    _menu =  content(_args)
    return _menu
def html (uri,_config) :
    # global _CLOUDHANDLER
    # _handler = _CLOUDHANDLER
    _handler = login(_config['system']['source']['auth'])
    _root = _format_root_folder(_config['layout']['root'])
    uri = _format_root_folder (uri)
    _context = _config['system']['context']
    
    _prefix = '/'.join (uri.split('/')[:-1])
    
    _link = '/'.join(['api/cloud/download?doc='+_prefix,'.attachments.'])
    if _context :
        _link = f'{_context}/{_link}'
    
    
    # _link = '/'.join(['api/cloud/download?doc='+_prefix,'_images'])
    _html = _handler.get_file_contents(uri).decode('utf-8')#.replace('.attachments.', copy.deepcopy(_link))
    # print ([uri,uri[-2:] ,uri[-2:] in ['md','MD','markdown']])
    _handler.logout()
    # if uri.endswith('.md'):
    if not _context :
        _html = _html.replace(_root,('api/cloud/download?doc='+_root)).replace('.attachments.', copy.deepcopy(_link))
    else:
        _html = _html.replace(_root,(f'{_context}api/cloud/download?doc='+_root)).replace('.attachments.', copy.deepcopy(_link))
    # _html = _html.replace('<br />','')
    return markdown(_html) if uri[-2:] in ['md','MD','Md','mD'] else _html
# def update (_config):
#     """
#     This function updates the configuration provided by loading default plugins
#     """
#     if 'plugins' not in _config :
#         _config['plugins'] = {}
#     _config['plugins'] = plugins ()
#     return _config
def download(**_args):
    _auth = _args['config']['system']['source']['auth']
    
    _request = _args['request']
    _handler = login(_auth)
    
    if _request.args['doc'][-2:] in ['md','ht']:
        _stream = html(_request.args['doc'],_args['config'])
    else:
        _stream = _handler.get_file_contents(_request.args['doc'])
    _handler.logout()
    
    return _stream
    pass
def _format (uri,_config) :
    """
    This function does nothing but is used to satisfy the demands of a design pattern
    @TODO: revisit the design pattern
    """
    return uri
def plugins (_context):
    """
    This function publishes the plugins associated with this module
    """
    key = 'api/cloud/download'
    if _context :
        key = f'{_context}/{key}'
    return {key:download}
