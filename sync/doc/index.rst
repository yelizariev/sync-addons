=============
 Sync Studio
=============

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Project
=======

* Open menu ``[[ Sync Studio ]] >> Projects``
* Create a project

  * **Name**, e.g. *Legacy migration*
  * **Params**

    * **Key**
    * **Value**
  * **Secrets** -- Params with restricted access
  * **Common Code** -- code that is executed before running any project's task.
    Can be used for initialization or for helpers. Secret params are available
    here, but not in task code.
  * **Tasks**

    * **Name**, e.g. *Sync products*
    * **Code** -- code with at least one of the following methods

      * ``handle_cron()``
      * ``handle_db(records)``
        * ``records`` -- all records on which this task is triggered
      * ``handle_webhook(data, httprequest)``
        * ``httprequest`` -- contains additional information about caller. E.g.
          ``httprequest.remote_addr`` -- ip address of the caller. See `Werkzeug
          doc
          <https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/#werkzeug.wrappers.BaseRequest>`__
          for more information.
      * ``handle_button(data, user)``

        * ``user`` -- who clicked the button
        * ``data`` -- data attached to the trigger

    * **Triggers** -- when to execute the Code. See below for further information

Code
====

Available variables and methods:

* ``env``: Odoo Environment on which the action is triggered
* ``log(message, level='info')``: logging function to record debug information


TODO: add notes about python libraries

Triggers
========

Cron
----

* **Execute Every** -- every 2 hours, every 1 week, etc.
* **Next Execution Date**

DB
--

* **Model**
* **Trigger Condition**

  * On Creation
  * On Update
  * On Creation & Update
  * On Deletion
  * Based on Timed Condition

    * Allows to trigger task before, after on in time of Date/Time fields, e.g.
      1 day after Sale Order is closed

* **Apply on** -- records filter
* **Before Update Domain** -- additional records filter for Update event
* **Watched fields** -- fields list for Update event

Webhook
-------

* **Name**
* **Webhook URL** -- readonly.

Button
------

* **Name**, e.g. "Sync all Products"
* **Data** -- json/yaml data to be passed to handler

Execution Logs
==============

TODO
