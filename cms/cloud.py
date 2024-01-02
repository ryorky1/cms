"""
Reads from nextcloud
"""

import nextcloud_client as nc
import copy
from mistune import markdown


_CLOUDHANDLER = None
def _format_root_folder (_root):
    if _root[0] == '/' :
        _root = _root[1:]
    if _root[-1] == '/' :
        _root = _root[:-1]
    return _root
def content(_args):
    """
    :url
    :uid
    :token
    :folder
    """
    global _CLOUDHANDLER
    _handler = nc.Client(_args['url'])
    _handler.login(_args['uid'],_args['token'])
    _CLOUDHANDLER = _handler
    _files = _handler.list(_args['folder'],10)
    _root = _args['folder']
    if _root.startswith('/') :
        _root = _root[1:]
    if _root.endswith('/') :
        _root = _root[:-1]
    _menu = {} #[_args['folder']] + [_item for _item in _files if _item.file_type == 'dir' and _item.name[0] not in ['.','_']]
    _menu = {} #dict.fromkeys(_menu,[])
    for _item in _files :
        _folder = _item.path.split(_item.name)[0].strip()
        _folder = _folder.replace(_root,'').replace('/','')
        
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
            # print ([_item.name,_key, _key in _menu])

            # _menuItem = _ref[_key]
            # uri = '/'.join([_args['url'],_item.path])
            # uri = _item
            # print ([_menuItem, _menuItem in _menu])
            uri = '/'.join(_item.path.split('/')[2:])
            _menu[_folder].append({'text':_item.name.split('.')[0],'uri':uri})
    #
    # clean up the content ...
    _keys = [_name for _name in _menu.keys() if _name.startswith('_')]
    [_menu.pop(_name) for _name in _keys]
    return _menu


def build(_config):
    """
    The function will build a menu based on a folder structure in nextcloud
    :_args  authentication arguments for nextcloud
    :_config    configuration for the cms
    """
    _args = copy.deepcopy(_config['system']['source']['auth'])
    _args['folder'] = _config['layout']['root']
    # update(_config)
    return content(_args)
def html (uri,_config) :
    global _CLOUDHANDLER
    _handler = _CLOUDHANDLER
    _root = _format_root_folder(_config['layout']['root'])
    uri = _format_root_folder (uri)
    
    
    _prefix = '/'.join (uri.split('/')[:-1])
    _link = '/'.join(['{{context}}api/cloud/download?doc='+_prefix,'.attachments.'])
    # _link = '/'.join(['api/cloud/download?doc='+_prefix,'_images'])
    _html = _handler.get_file_contents(uri).decode('utf-8').replace('.attachments.',_link)
    # print ([uri,uri[-2:] ,uri[-2:] in ['md','MD','markdown']])
    return markdown(_html) if uri[-2:] in ['md','MD','Md','mD'] else _html.replace(_root,('{{context}}api/cloud/download?doc='+_root))
# def update (_config):
#     """
#     This function updates the configuration provided by loading default plugins
#     """
#     if 'plugins' not in _config :
#         _config['plugins'] = {}
#     _config['plugins'] = plugins ()
#     return _config
def download(**_args):
    _handler = _CLOUDHANDLER

    if _args['doc'][-2:] in ['md','ht']:
        _stream = html(_args['doc'],_args['config'])
    else:
        _stream = _handler.get_file_contents(_args['doc'])
    
    return _stream
    pass

def plugins ():
    """
    This function publishes the plugins associated with this module
    """
    return {'api/cloud/download':download}
