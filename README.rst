==============
Odoo Candyshop
==============

.. image:: https://img.shields.io/pypi/v/odoo-candyshop.svg
        :target: https://pypi.python.org/pypi/odoo-candyshop

.. image:: https://img.shields.io/travis/vauxoo/odoo-candyshop.svg
        :target: https://travis-ci.org/vauxoo/odoo-candyshop

.. image:: https://readthedocs.org/projects/odoo-candyshop/badge/?version=latest
        :target: https://readthedocs.org/projects/odoo-candyshop/?badge=latest
        :alt: Documentation Status


Odoo Candyshop is a helper determine if all your dependencies were declared properly.

* Free software: AGPL-3
* Documentation: https://odoo-candyshop.readthedocs.org.

Features
--------

* Access an Odoo Module as an object abstraction.
* Get all module references from all xml files of a module.
* Generate and clone the dependency tree of a group of modules (bundle).
* Generate a virtual enviroment where you can add group of modules.
* Determine which Odoo Modules declare a dependency to another module that is not
  present in the environment.
* Determine which XML files make reference to an Odoo Module that is not present
  in the environment.
