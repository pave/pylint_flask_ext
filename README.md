pylint_flask_ext
================

Pylint plugin that translates flask.ext.foo to flask_foo

Maybe this will be helpful for other people who use both Pylint and flask.

To run it, grab either flask_ext_clean.py, which is cleaner but longer, or flask_ext_short.py, which is shorter but hackier. You can either do pylint --load-plugins flask_ext_clean or add:

```
[MASTER]
load-plugins=flask_ext_clean
```

to your pylint.rc. (Note that load-plugins takes a Python module path, not a filename path.)

Included is flask_ext_test.py, which serves as a test case for the plugin.

Here's the errors it gave:

```
$ pylint --rcfile .pylint.rc flask_ext_test.py -r n -i y
************* Module pylint_test
W0404:  8,0: Reimport 'flask_login' (imported line 7)
F0401:  9,0: Unable to import 'flask_bla'
E1101: 15,6: Module 'flask_wtf' has no 'Flboltolo' member
E0602: 21,0: Undefined variable 'foo'
E1101: 23,6: Module 'flask_login' has no 'bloblobo' member
W0611:  8,0: Unused import login
```

We see that importing flask.ext.login is imported twice, using from and using import -- this is reported as a reimport of "flask_login", which isn't perfect, but is understandable. Similarly, flask_bla couldn't be found. It understands enough of flask_wtf to recognize that wtf.Form is fine, but wtf.Flboltolo isn't. Similarly, flask_login.login_user is fine, but flask_login.bloblobo isn't.
