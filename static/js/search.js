var search = {}
search.find = function(id,_domid,_attr){
    var nodes = jx.dom.get.children(id)
    jx.dom.set.focus(_domid)
    var term = jx.dom.get.value(_domid).trim()
    term = term == ''?'*':term
    if (term.length < 2){
        $(nodes).show()
        jx.dom.set.value('found',nodes.length)
        return ;}
    $(nodes).hide()
    term = RegExp(term.replace(/ /,'|'),'ig')
    _count = 0
    jx.utils.patterns.visitor (nodes,function(_node){
        
        var _data = _node.getAttribute('data') ;
        if (_data[0] == '{' || _data[0] == '['){
            _data = JSON.parse(_data)
            _found = 0
            _attr.forEach(function(_name){
                _found += _data[_name].match(term) !=null?1:0
            })
        }else{
            _found = _data.match(term)!=null?1:0
        }
        _count += _found
        if (_found > 0){
            $(_node).show()
        }
    })
    jx.dom.set.value('found',_count)
}
search._find = function(id,_domid){
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

