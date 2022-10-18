/**
 * Steve L. Nyemba
 * The modal window creates a modal window on the basis of a url or a html
 * The namespace also provides a mechanism for the modal to be removed upon
 */
var __jx_modalw__ = {width:0,height:0}
/**
 * @param {*} info  {uri|html}
 */
__jx_modalw__.init = function(info,pointers){
    // if(info.match(/^[a-z](+\/[a-z,.]+){1,}/i)){
    //     var uri = info
    //     var http = HttpClient.instance()
    //     http.get(uri,function(x){
    //         var html = x.responseText
    //         __jx_modalw__.render.modal(html,pointers)
    //     })
    // }else{
    //     var html = info
    //     __jx_modalw__.render.modal(id,html,pointers)
    // }
}
__jx_modalw__.cache = {}
__jx_modalw__.render = {}
__jx_modalw__.render.modal = function(args){
    var bg      = jx.dom.get.instance('DIV')
    var frame   = jx.dom.get.instance('DIV')
    
    var buttons  = jx.dom.get.instance('DIV')
    bg.style.position       = 'relative'
    bg.style.zIndex         = 99
    bg.style.width          = '100%'
    bg.style.height         = '100%'
    bg.style.overflow       = 'hidden'
    bg.style.backgroundColor= 'rgba(242,242,242,0.7)'
    bg.style.display = 'grid'
    
    if(args.url != null){
        //
        // a modal window that is a reference to another site
        
        bg.style.gridTemplateColumns = '10% 80% 10%'
        bg.style.gridTemplateRows = '10% 80% 10%'
        var iframe = jx.dom.get.instance('IFRAME')
        args.css = (args.css != null)?args.css:{}
        
        iframe.src = args.url
        iframe.frameBorder = 0
        iframe.style.width = '99%' //(args.css.width == null)?'99%':args.css.width
        iframe.style.height= '99%' //(args.css.height==null)?'99%':args.css.height
        iframe.style.backgroundColor = '#ffffff'
        iframe.className = 'border-round border'
        frame.appendChild(iframe)
            
    }else{
        //
        // This is the case of a modal window that's based on an html document/inline script
        //
        var text   = jx.dom.get.instance('DIV')
        text.innerHTML = args.html
        frame.appendChild(text)
        bg.style.gridTemplateColumns = '20% 60% 20%'
        bg.style.gridTemplateRows = '20% 60% 20%'
        frame.style.display = 'flex'
        frame.style.justifyContent = 'center'
        frame.style.alignItems = 'center'
        // frame.style.resize = 'both'
        text.className = 'border border-round'
        text.style.backgroundColor = '#ffffff'
        
    }
    frame.style.gridRow = '2/3'
    frame.style.gridColumn = '2/3'

    bg.appendChild(frame)
    if(args.id == null){
        //
        // If no identifier is assigned to the modal window
        // This means it will close upon click on the background
        bg.onclick = function(){
            jx.dom.remove(this)
        }
    
    }else{
        //
        // We will persist the pane and the calling code will invoke jx.modal.remove
        //
        jx.modal.set(args.id,bg)
        
    }
    args.frame = frame
    args.background = bg
    return args
}

/**
 * This function is designed to layout the pane with the background on it
 */
__jx_modalw__.render.show = function(info){
    info.background.className = 'jxmodal'
    // info.background.style.position = 'absolute'
    
    var parent = (info.target != null)?jx.dom.get.instance(info.target): document.body
    
    var height = $(parent).height()
    var width = $(parent).width()
    
    parent.appendChild(info.background)
    // if(info.html == null){
    
        info.background.style.top = 0
        info.background.style.left =0
        info.background.style.position = 'absolute'
    
    // }else{
    //     $(info.background).width(width+(width*0.01))
    //     $(info.background).height(height+(height*0.1))
    //     info.background.style.top =  -(height)
    //     info.background.style.left= -10
    
    // }
    
    
    
}

if(! jx){
    var jx = {}
}
/**
 * This function will generate a modal window
 * @param {*} args {html,url,id}
 */
jx.modal = {cache:{}}
jx.modal.show= function(args){
    if(args.constructor == String){
        if (args.match(/^http|^\//)){
            args = {url:args}
        }else{
            args={html:args}
        }
    }
    
    var info = __jx_modalw__.render.modal(args)
    __jx_modalw__.render.show(info)
    if(info.render != null){
        if(info.render.args != null){
            var args = info.render.args
        }else{
            var args = null
        }
        info.render.pointer(args)
    }
}
jx.modal.remove = function(id){
    if(jx.modal.cache[id] == null){
        var pane = $('.jxmodal')[0]
        
    }else{
        var pane = jx.modal.cache[id]    
        
    
    }
    jx.dom.remove(pane)
}
jx.modal.set = function(id,pane){
    
    jx.modal.cache[id] = pane
    delete jx.modal.cache[id]
}
jx.modal.close = jx.modal.remove
// jx.modal.render = function(id,html){
//     var info = __jx_modalw__.render.modal(id,html)
//     // console.log(info)
    
// }
jx.modal_example = function(){
    
    busy = '<div class="small" align="center">Please wait</div><i class="fa fa-cog fa-5x faa-wrench animated" style="color:#4682b4"></i><i class="fa fa-cog fa-spin fa-3x" style="color:black"></i><i class="fa fa-cog faa-wrench animated fa-5x" style="color:#4682B4"></i>'
    jx.modal(busy)
}