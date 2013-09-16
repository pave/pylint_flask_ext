"""
Plugin for pylint that tells it about flask's extension classes.
"""

from logilab.astng import MANAGER

def flask_ext_wrapper(func):
    """Wrap ASTNGManager.astng_from_module_name

This kind of sucks but apart from monkeypatching, I can't find any
other way to do this.

Intercept all calls to ASTNGManager.astng_from_module_name
and convert lookups for flask.ext.foo to flask_foo.
"""
    def wrapper(modname, context_file=None):
        """flask.ext.foo -> flask_foo"""
        if modname.startswith('flask.ext.'):
            newname = modname.replace('flask.ext.', 'flask_')
            module = func(newname, context_file)
            module.name = modname
            return module

        return func(modname, context_file)
    return wrapper

def register(linter): #pylint: disable=W0613
    """Pylint calls this hook to actually activate the plugin"""
    patched = flask_ext_wrapper(MANAGER.astng_from_module_name)
    MANAGER.astng_from_module_name = patched
