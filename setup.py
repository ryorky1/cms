from setuptools import setup, find_packages
import os
import sys
import meta
args    = {
    "name":"qcms",
    "version":meta.__version__,
    "author":meta.__author__,"author_email":"info@the-phi.com",
    "license":meta.__license__,
    # "packages":["transport","info","transport/sql"]},

    "packages": find_packages(include=['meta','cms', 'cms.*','cms.index'])}
args["keywords"]=['cms','www','https','flask','data-transport']
args["install_requires"] = ['flask','gitpython','termcolor','flask-session','mistune','typer','data-transport@git+https://github.com/lnyemba/data-transport.git']
args['classifiers'] = ['Topic :: utilities', 'License :: MIT']
args['include_package_data'] = True

args["url"] =   "https://healthcareio.the-phi.com/git/code/transport.git"
args['scripts'] = ['bin/qcms']
# if sys.version_info[0] == 2 :
#     args['use_2to3'] = True
#     args['use_2to3_exclude_fixers']=['lib2to3.fixes.fix_import']
setup(**args)

