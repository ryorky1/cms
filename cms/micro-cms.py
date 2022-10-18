class Project :
    @staticmethod 
    def create (**_args) :
        _version = "0.0.1" if "version" not in _args else _args['version']
        _context = "" if 'context' not in _args else _args['context']
        _logo = "logo.png"
        _system = {"version":_version,"context":_context,"logo":_logo}
        _app = {"port":8084,"debug":True}
        pass
    
