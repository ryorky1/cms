var search = {}
search.find = function(id,_domid){
    var nodes = jx.dom.get.children(id)
    $(nodes).hide()
    jx.dom.set.focus(_domid)
    var term = jx.dom.get.value(_domid).trim()
    if (term.trim().match(/^(author|paper)\:$|''/)){
        $('.search .input-frame .found').text(0)
        return ;
    }
    qfocus = (term.match(/author|paper/))
    
    
    term.replace(/^((author|paper)\:*)/ig,'').trim() 
    
    term = RegExp(term.replace(/ /,'|'),'ig')
    count = 0;
    
    jx.utils.patterns.visitor(nodes,function(node){
        try{
            var _data = node.getAttribute('data') ;
            if (_data != null){
                var _data = JSON.parse( _data) ;
                _hasauthors = _data.authors.match(term) != null
                _hastitle = _data.title.match(term) != null
                _haspub = _data.publication.match(term) != null
                _hasname = _data.name.match(term) != null
                
                if(qfocus != null){
                    if (qfocus[0].trim() == 'author'){
                        _hasauthors = _hastitle = _haspub = false
                    }else if (qfocus[0] == 'paper'){
                        _hasauthors = _haspub = _hasname =false
                    }
                    
                }
                if (_hasauthors || _hastitle || _haspub || _hasname){
                    $(node).show()
                    ++ count;
                    
                }
            }
        }catch(e){
            // console.log(e);
            ;
        }
        $('.'+id).slideDown()
            $('.search .input-frame .found').text(count)
        
      
        
    })
}