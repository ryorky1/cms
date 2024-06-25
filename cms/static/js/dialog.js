var dialog = {}
dialog.context = ''
dialog.show = function(_title,_internalURI,_message,_pointer){
   var http = HttpClient.instance()
//    http.setData({title:_title,html:_message},'application/json')
   var uri = dialog.context+'/dialog'
   http.setHeader('dom',_title)
   http.setHeader('uri',_internalURI)
   http.get(uri,function(x){
      $('.jxmodal').remove()
       jx.modal.show({html:x.responseText,id:'body'})
       if(jx.dom.exists('dialog-message') && _message != null){
          jx.dom.set.value('dialog-message',_message)
         
       }
      //
      // In order to perhaps execute any js script that should have been executed on load ...
      //
      
      var scripts = $('.jxmodal script')
      jx.utils.patterns.visitor(scripts,function(_item){
         if(_item.text.trim().length > 0){
            var _routine = eval(_item.text)
            //
            //@TODO:
            // Find a way to add the running function into the page to enable scripts to work
            //
         }
      })
   })
}