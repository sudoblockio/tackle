Difference Between Cookiecutter and Tackle Box
==============================================

Tackle box was derived from cookiecutter and thus shares a lot of similarities but due to the differences in goals (code generation vs DSL) and experimental nature, it was determined to be turned into its own tool.  That being said, all cookiecutter templates should work 1:1 with tackle box with the same functionalities.

There are a few differences though.

Context Files
^^^^^^^^^^^^^

When running cookiecutter templates, you can write the context file \(`cookiecutter.json`\) in both json and yaml now. Tackle box context files are generally written in yaml now.


Variable Rendering
^^^^^^^^^^^^^^^^^^

Variables normally require a `cookiecutter` prefix such as `\{\{ cookiecutter.variable \}\}` but when they are run from tackle box they don't, ie `\{\{ variable \}\}` will work.

Hooks
^^^^^

Cookiecutter has the concept of pre/post-generation hooks which are scripts that run after the context file is run and before and after the associated code is generated.  Tackle-box extends this concept to allow users to run arbitrary hooks from within the context file itself.

