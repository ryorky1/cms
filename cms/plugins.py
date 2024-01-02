"""
These are a few default plugins that will be exported and made available to the calling code
The purpose of plugins is to perform data processing
"""




def copyright (_args) :
    return {"author":"Steve L. Nyemba","email":"steve@the-phi.com","organization":"The Phi Technology","license":"MIT", "site":"https://dev.the-phi.com/git/cloud/qcms"}

def log (_args):
    """
    perform logging against duckdb  
    """
    pass