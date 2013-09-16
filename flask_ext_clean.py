"""
Plugin for pylint that tells it about flask's extension classes.
"""

from pylint.utils import PyLintASTWalker
from logilab.astng import MANAGER
from logilab.astng import node_classes

def copy_node_info(src, dest):
    """Copy information from src to dest

Every node in the AST has to have line number information. Get
the information from the old stmt."""
    for attr in ['lineno', 'fromlineno', 'tolineno',
                 'col_offset', 'parent']:
        if hasattr(src, attr):
            setattr(dest, attr, getattr(src, attr))


def splice(stmt, new_stmt):
    """Replace stmt with new_stmt in the AST

Also, copy useful information from stmt to new_stmt.

This assumes that stmt and new_stmt are of the same type and
define the same names.
"""
    copy_node_info(stmt, new_stmt)

    # Replace stmt with new_stmt in the sequence of statements that
    # included stmt.
    body = stmt.parent.child_sequence(stmt)
    i = body.index(stmt)
    stmt.parent.body[i] = new_stmt

    # The names defined by an import statement are kept in stmt.names
    # as a pair of (exported_name, as_name). For example, "import foo,
    # bar as baz" corresponds to an import statement with
    # names=[("foo", None), ("bar", "baz")].
    #
    # All names that stmt defined should now be defined by new_stmt.
    for (name, as_name) in stmt.names:
        stmt.parent.set_local(as_name or name, new_stmt)

class ImportRewriterVisitor(object):
    """AST Visitor that looks for flask.ext imports and rewrites them

This is something like the Visitor Pattern. For every Foo node in
the AST, PyLintASTWalker will call visit_foo."""
    def __init__(self):
        self.flask_ext_imported = {}

    def visit_from(self, stmt):
        """Visit 'from foo import bar' statements"""
        if stmt.modname == 'flask.ext':
            # Replace 'from flask.ext import login' with
            # 'import flask_login as login'.
            new_stmt = node_classes.Import()
            new_stmt.names = []
            for pair in stmt.names:
                (name, as_name) = pair
                new_stmt.names.append(('flask_'+name, as_name or name))

            splice(stmt, new_stmt)

        if stmt.modname.startswith('flask.ext.'):
            # Replace 'from flask.ext.wtf import Foo' with 'from
            # flask_wtf import Foo'.
            ext_name = stmt.modname[10:]
            new_stmt = node_classes.From('flask_'+ext_name,
                                         stmt.names, stmt.level)
            splice(stmt, new_stmt)

    def visit_import(self, stmt):
        """Visit 'import flask.ext.login' statements

Pretend that flask.ext did "import flask_login as login"."""
        flask_ext_names = []
        for (name, as_name) in stmt.names:
            if name.startswith('flask.ext.'):
                flask_ext_names.append(name[10:])

        if not flask_ext_names:
            # We visited an import that doesn't import any flask.ext stuff.
            # Not our problem.
            return

        module = stmt.root()
        if not self.flask_ext_imported.get(module):
            # Make sure flask.ext is imported already at least once.
            import_stmt = node_classes.Import()
            import_stmt.names = [('flask.ext', None)]
            import_stmt.fromlineno = import_stmt.tolineno = -1
            import_stmt.parent = module

            body = stmt.parent.child_sequence(stmt)
            body.insert(0, import_stmt)
            self.flask_ext_imported[module] = True
            # Mark this as the first definition of flask
            module.locals.setdefault('flask', []).insert(0, import_stmt)

        # Change all names in this statement in-place.
        for i, (modname, as_name) in enumerate(stmt.names):
            if modname.startswith('flask.ext.'):
                newmodname = modname.replace('flask.ext.', 'flask_')
                stmt.names[i] = (newmodname, as_name)

        # This import statement no longer defines "flask" (since it
        # imports flask_foo), so remove it from locals
        module.locals['flask'].remove(stmt)

        # Fool the inference engine by pretending that flask.ext does
        # an "import flask_foo as foo".
        for name in flask_ext_names:
            # Get real flask_ext
            flask_ext_module = module.import_module('flask.ext')

            values = flask_ext_module.locals.setdefault(name, [])
            if values:
                # We're fine, it's already been "imported"
                continue

            new_import = node_classes.Import()
            new_import.tolineno = new_import.fromlineno = -1
            new_import.parent = flask_ext_module
            new_import.names = [('flask_'+name, name)]

            # We don't actually need to be in the AST. We just want
            # the inference engine to find us.
            values.append(new_import)

def register(linter): #pylint: disable=W0613
    """Pylint calls this hook to actually activate the plugin"""
    walker = PyLintASTWalker(linter)
    walker.add_checker(ImportRewriterVisitor())
    MANAGER.register_transformer(walker.walk)
