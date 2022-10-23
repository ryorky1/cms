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
menu.apply  = function (uri,id,pid){
    id = id.replace(/ /g,'-')
    if(uri == null){
        return ;
    }
    $('.content').children().hide()
    
    var httpclient = HttpClient.instance()
   
        httpclient.setHeader('uri',uri)
        httpclient.setHeader('dom',id)
        httpclient.post('/page',function(x){
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
    console.log(_args)
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
            http.setHeader('dom','dialog')
            // http.setHeader('dom',_args.text)
            http.get('/dialog',function(x){
                
                jx.modal.show({html:x.responseText,id:'dialog'})
            })
        }
    }else{
        window.open(_args.url,_args.text)
    }

}