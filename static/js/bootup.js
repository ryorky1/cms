/**
 * This file has functions that allow pages to be fetched and rendered on bootup
*/

var bootup = {}
//
// We implement this function using an observer design pattern
bootup.CMSObserver = function(_sysId,_domId,_fileURI){
    this._domId     = _domId
    this._fileURI   = _fileURI
    this.apply      = function (_caller){
            var http = HttpClient.instance()
            http.setHeader('uri',_fileURI)
            var uri = sessionStorage[_sysId]+'/page'
            try{
                var _domElement = jx.dom.get.instance('div')
                
                _domElement.className = 'busy-loading'
                jx.dom.append(_domId, _domElement)

                http.post(uri,function(x){
                    // console.log(jx.dom.exists(_domId))
                    // var _domElement = jx.dom.get.instance('div')
                    // _domElement.className = 'busy-and-loading'
                    // jx.dom.append(_domId, _domElement)
                    if (x.status == 200){
                        // jx.dom.set.value(_domId,x.responseText)
                        // var _domElement = jx.dom.get.instance('div')
                        // _domElement.innerHTML = x.responseText
                        
                        
                        setTimeout(function(){
                            _domElement.innerHTML = x.responseText
                            _domElement.className = null
                        },1500)

                        
                    }
                    
                    _caller.notify()
                })

            }catch(error){
                _caller.notify()
            }
    }
    
}
//
// Finalize the process of rendering the content on the fly
bootup.finalize = function(_id){
    this.apply = function(_caller){
        menu.runScript('#'+_id)
    }
}

bootup.init = function(sys_id,_layout){
    if (!_layout) {
        return ;
    }
    if (_layout.on){
        jx.utils.keys(_layout.on.load).forEach(function(_domId){
                
            var observers = 
            jx.utils.patterns.visitor(_layout.on.load[_domId], function(_uri){
                return new bootup.CMSObserver(sys_id,_domId,_uri)
            })
            observers.push(new bootup.finalize(_domId))
            //
            // At this point we can execute the observer design pattern
            //
            // console.log(observers)
            jx.utils.patterns.observer(observers,'apply')

        })
    }

}