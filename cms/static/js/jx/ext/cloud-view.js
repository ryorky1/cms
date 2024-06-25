/**
 * This framework is intended to work and handle authentication with the cloud view engine
 * DEPENDENCIES :
 *	rpc.js	HttpClient, urlparser
 * @TODO: A registration process maybe required
 */

/**
 * @param id	service identifier
 * @param key	callback/ user key
 */
jx.cloudview = { popup:null,cache: {},oauth:{},url:'https://the-phi.com/cloud-view',host:'the-phi.com',protocol:'https'}
jx.cloudview.init = function(url,redir_url){//host,protocol){
	// jx.cloudview.host = host
	// jx.cloudview.protocol = protocol
	jx.cloudview.url = url.trim().replace(/\/$/,'')
	jx.cloudview.host = url.match(/^.+\/\/([a-z,0-9,.,-]+)\/.+$/)[1]
	jx.cloudview.protocol = url.match(/^(https|http).+/)[1]
	if(redir_url != null){
		jx.cloudview.redirect_url = redir_url
	}
	if(jx.cloudview.handler != null){
		clearInterval(jx.cloudview.handler)
	}
}
jx.cloudview.oauth.init = function (id, key,callback,err) {
	// var url = ":protocol://:host/cloud-view/" +id+"/get"
	// url = url.replace(/:protocol/,jx.cloudview.protocol).replace(/:host/,jx.cloudview.host)
	var url = ([jx.cloudview.url,id,'get']).join('/')
	var httpclient = HttpClient.instance()
	httpclient.setHeader("platform",navigator.appName)

	try{
		
		httpclient.post(url, function (x) {
		
			var url = x.responseText
			
			if(url.match(/^http.+$/)){
				
				
				var oauth_uri = url.match(/redirect_uri=(.+)\&/)[1];	
				url = url.replace(oauth_uri, key)
	
				
	
				jx.cloudview.handler = null
				jx.cloudview.popup = window.open(url, 'oauth', 'width=405, height=900')		
				jx.cloudview.popup.focus()
				jx.cloudview.oauth.listen(key,callback,err)
			}else{
				
				setTimeout(()=>{
					jx.dom.set.value('dialog.status','<i class="fa fa-times" style="color:maroon; font-size:12px"></i> http error '+x.status+' ... closing window')
					err()
				},2500);
			}
			
		})
	}catch(error){
		err()
	}	
}

/**
 * @param key
 */
jx.cloudview.oauth.listen = function (key,callback,err) { 
	if (jx.cloudview.handler != null) {
		clearInterval(jx.cloudview.handler)
		
	}
	
	jx.cloudview.handler = setInterval(function () {
		try { 
			
			if (jx.cloudview.popup.location.search.match(/code=/)) {
				clearInterval(jx.cloudview.handler)
				var p = urlparser(jx.cloudview.popup.location.search)
				
				var url = ([":protocol://:host/cloud-view/", p.state, "/set/authentication"]).join('')
				url = url.replace(/:protocol/,jx.cloudview.protocol).replace(/:host/,jx.cloudview.host)
				var http = HttpClient.instance()
				http.setHeader('code', encodeURIComponent(p.code))
				http.setHeader('pid', 'authentication')
				http.setHeader('platform', navigator.appName)
				http.setHeader('redirect-uri', key)
                
				http.post(url, function (x) {
                    try{
						var info = JSON.parse(x.responseText)
						callback(info)
	
					}catch(e){
						if (err != null){
							err(e)
						}else {console.log(e)}
						
					}
					 
					// jx.dom.set.value('name', info.user.uii)
				})

			}
			//
			// Until the control is returned an exception will be generated
			// So the popup.close will never be executed ...			
			jx.cloudview.popup.close()
		} catch (error) {
			//
			// If the window was closed chances are the user closed the window without loging in
			if(jx.cloudview.popup != null){
				if(jx.cloudview.popup.closed){
					clearInterval(jx.cloudview.handler)
					callback(null)
					if (err != null){
						err(error)
					}

				}
			}
			console.log([jx.cloudview.popup.closed,error])
		}
	},1500)
}
