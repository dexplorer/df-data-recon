"""
When the package is executed with the package name, __main__.py is invoked.
Here, we invoke the CLI module's main function.
"""

from dr_app import dr_app_cli as drc

drc.main()
