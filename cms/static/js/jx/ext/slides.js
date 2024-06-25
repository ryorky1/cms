/**
 * This file goes along with slides.css
 */
if(!jx){
    var jx = {}
}

jx.slides = {}
/**
 * 
 * @params args:
 *      main_id     main panel
 *      nav_id      control panel
 *      nav_left    left button
 *      nav_right   right button
 *      data        data    (array of items)
 *      renderer    point to the function that will render an item in the data
 */
jx.slides.instance = function(args){
    this.main_id    = args.main_id
    this.nav_id     = args.nav_id
    this.data       = args.data 
    this.nav_left   = args.nav_left;
    this.nav_right  = args.nav_right;
    this.enable_auto= args.auto == true
    this.handler    = null;
    this.page   = {index:0,count:0};
    this.left   = function(){
        var pane = jx.dom.get.children(this.main_id)[0]
        var width = $('#'+this.main_id).width()
        // var page = jx.dom.get.attribute('controls','info')
        var i = this.page.index
        var N = this.page.count
        
        i = ((i+1) < N)? (i+1):0
        
        
        $(pane).animate({'margin-left':-(width+4)*i})
        this.page.index = i
        // jx.dom.set.attribute(this.nav_id,'info',page)
            
    }
    this.right  = function(){
        var pane = jx.dom.get.children(this.main_id)[0]
        var width = $('#'+this.main_id).width()
        // var page = jx.dom.get.attribute('controls','info')
        
        var i = this.page.index
        var N = this.page.count
        // alert(N)
        i = ((i-1) > -1)?(i-1):(N-1) ;
        
        $(pane).animate({'margin-left':-width*i})
        this.page.index = i
        // jx.dom.set.attribute(this.nav_id,'info',page)        
    }
    
    this.stop   = function(){
        if(this.handler != null){
            clearInterval(this.handler)
            this.handler = null
        }
    }
    this.auto   = function(){
        if(this.handler == null){
            this.handler = setInterval(this.right,2000)        }
    }
    this.bind   = function(){
        var _ileft = jx.dom.get.instance(this.nav_left)
        _ileft.onclick = this.left
        _ileft.onmouseover = this.stop
        
        var _iright = jx.dom.get.instance(this.nav_left)
        _iright.onclick = this.left
        _iright.onmouseover = this.stop
        if(this.enable_auto){
            _ileft.onmouseout = this.auto
            _iright.onmouseout = this.auto
        }
        
    }
/**
 * This section will handle the initialization 
 */    
    
    var pane = jx.dom.get.instance('DIV')
    var width   = $('#'+this.main_id).width()
    var height  = $('#'+this.main_id).height()    
    var N = this.data.length
    
    this.page = {index:0,count:N}

    // jx.dom.set.attribute(this.nav_id,"info",info)
    // jx.dom.set.attribute("controls","page.count",N)

    // $(pane).width(width*N)
    $(pane).css("width",width*N)
    $(pane).height(height)
    $(pane).css('overflow','hidden')

    jx.dom.set.value(this.main_id,'')
    jx.dom.append(this.main_id,pane)

    jx.utils.patterns.visitor(this.data,function(item){
        console.log(item.constructor.prototype.name)
        var frame = jx.dom.get.instance('DIV')
        var picframe = jx.dom.get.instance('DIV')
        var image = jx.dom.get.instance('IMG')
        var info = jx.dom.get.instance('DIV')

        image.src = item.src
        
        info.innerHTML = item.text
        info.className = 'text'
        picframe.appendChild(image)
        picframe.className = 'pic-frame'
        // $(picframe).height(height-148)
        $(frame).css("height",height)
        $(frame).css("width",width)
        $(frame).css('overflow','hidden')
        frame.appendChild(picframe)
        frame.appendChild(info)
        pane.appendChild(frame)
        $(frame).width(width)
        $(frame).height(height)
        frame.className = 'slides left'

    })
    if(this.enable_auto){
        this.auto()
    }
}