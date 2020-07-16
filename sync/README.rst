.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

=============
 Sync Studio
=============

Synchronize anything with anything, including Odoo

Provides a single place to handle synchronization trigered by one of the following events:

* **Cron** -- provided by ``ir.cron``
* **DB Event** -- provided by ``base.automation``
* **Incoming webhook** -- provided by ``base.automation::action_server_id.website_published`` (search for ``/website/action`` in ``website`` module)
* **Manual Triggering** -- when user clicks a special button

Allows to add extra imports to eval context.

Adds helpers to all models:

* ``get_ref`` -- search or create reference for current record

Credits
=======

Contributors
------------
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__:

      * :one::zero: init version of the module

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support
      you are kindly requested to purchase the module
      at `odoo apps store <https://apps.odoo.com/apps/modules/12.0/sync/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/sync-addons/12.0

HTML Description: https://apps.odoo.com/apps/modules/12.0/sync/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/sync-addons/commits/12.0/sync.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/sync-addons/commits/12.0/sync.atom>`_

Tested on Odoo 12.0 3fbfa87df85d6463dfcba47416f360fcdef4448e
