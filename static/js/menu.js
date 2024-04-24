/*
* Let us load the menu items here ...
*/
var menu = {}
/*
* This function will load menu items from the configuration file
* :uri
* :id
* :pid  parent identifier                                            
*/

menu.apply  = function (uri,id,pid,_context){
    id = id.replace(/ /g,'-')
    if(uri == null){
        return ;
    }
    $('.content').children().hide()
    
    var httpclient = HttpClient.instance()
   
        httpclient.setHeader('uri',uri)
        httpclient.setHeader('dom',id)
        httpclient.post(_context+'/page',function(x){
            var _html = x.responseText
            var template = document.createElement('template');
            template.innerHTML = _html.trim();
            var _dom =  template.content.firstChild;
            if(jx.dom.exists(pid) && jx.dom.exists(id)){
                jx.dom.remove(id)
            }
            $('#'+pid).append(_dom)
            // jx.dom.append(pid,_dom)
            // $('#'+id).show('fast',function(){
                // $('#'+pid).slideUp()
            // })
            
            $('#'+pid).children().slideUp('fast', function(){
                $('#'+id).slideDown('fast',function(){
                    $('#'+pid).slideDown('fast',function(){
                        var input = $('#'+pid).find('input')
                        if (input.length > 0 ){
                            $(input[0]).focus()
                        }
                    })
                   
                })
    
            })
            
                // $('.content').append(_dom)
        })
    
}

menu.apply_link =function(_args){
    //
    // type:
    //  redirect open new window
    //  dialog      open in a dialog
    //
    
    var url = _args['url']
    _args.type = (_args.type == null)? 'redirect' :_args.type
    
    if (_args.type.match(/dialog|embed/i) ) {
        //
        // calling jx.modal.show
        if (_args.url){
            jx.modal.show(_args.url)
        }else{
            // _html = jx.dom.get.value(_args.text)
            // console.log(_html)
            // jx.modal.show(_html)
            var http = HttpClient.instance()
            http.setHeader('uri',_args.uri)
            http.setHeader('dom',(_args.title)?_args.title:'dialog')
            // http.setHeader('dom',_args.text)
            http.get('/dialog',function(x){
                
                jx.modal.show({html:x.responseText,id:'dialog'})
                console.log([$('.jxmodal')])
                menu.runScript ('.jxmodal')
            })
        }
    }else{
        window.open(_args.url,_args.text)
    }

}

var _delegate = {scripts:{}}
menu.runScript  = function(_id){
    var scripts = $(_id+' script')
    
    jx.utils.patterns.visitor(scripts,function(_item){
       if(_item.text.trim().length > 0){
          var _code = eval(_item.text)
          var id = _id
          if (_item.parentNode != null){
            var id = _item.parentNode.id == null?_item.parentNode.className : _item.parentNode.id
          }
          id = (id != null)?id : _id 
          
        //   _delegate.scripts[id] = _code
       }
    })    
}

