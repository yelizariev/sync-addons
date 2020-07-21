==================
 Sync Studio Free
==================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

User Access Levels
==================

* ``Sync Studio: User`` -- read-only access
* ``Sync Studio: Developer`` -- restricted write access
* ``Sync Studio: Manager`` -- same as Developer, but with access to **Secrets**, **Protected Code**, **Network Access**

Project
=======

* Open menu ``[[ Sync Studio ]] >> Projects``
* Create a project

  * **Name**, e.g. *Legacy migration*
  * **Params**

    * **Key**
    * **Value**
  * **Secrets** -- Params with restricted access: key values are visiable for Managers only
  * **Protected Code**, **Common Code** -- code that is executed before running any
    project's task. Can be used for initialization or for helpers. Secret params
    and package importing are available in **Protected Code** only. Any variables
    and methods that don't start with underscore symbol will be available in
    task code.
  * **[x] Network Access** -- makes ``requests`` lib avaiable for using in Code.
    It's not recommended to use other libs. If unset, all outgoing connections are blocked.
  * **Tasks**

    * **Name**, e.g. *Sync products*
    * **Code** -- code with at least one of the following methods

      * ``handle_cron()``
      * ``handle_db(records)``
        * ``records`` -- all records on which this task is triggered
      * ``handle_webhook(httprequest)``
        * ``httprequest`` -- contains information about request. E.g.
          * `httprequest.form <https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/#werkzeug.wrappers.BaseRequest.form>`__ -- request args
          * `httprequest.files <https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/#werkzeug.wrappers.BaseRequest.files>`__ -- uploaded files
          * `httprequest.remote_addr <https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/#werkzeug.wrappers.BaseRequest.remote_addr>`__ -- ip address of the caller.
          * See `Werkzeug doc
            <https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/#werkzeug.wrappers.BaseRequest>`__
            for more information.
      * ``handle_button(data, user)``

        * ``user`` -- who clicked the button
        * ``data`` -- data attached to the trigger

    * **Job Triggers** -- when to execute the Code. See below for further information

Job Triggers
============

Cron
----

* **Execute Every** -- every 2 hours, every 1 week, etc.
* **Next Execution Date**
* **Scheduler User**

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

Code
====

Available variables and methods:

* ``env``: Odoo Environment on which the action is triggered
* ``log(message, level='info')``: logging function to record debug information
* ``make_response`` -- Only for Webhook: data to return to the caller

Running Job
===========

Depending on Trigger, a job may:

* be added to a queue or runs immediatly
* be retried in case of failure

Cron
----

* job is added to queue only if previous job has finished
* failed job can be retried if failed

DB
--

* job is always added to the queue before run
* failed job can be retried if failed

Webhook
-------

* runs immediatly
* failed job cannot be retried via backend UI; the webhook should be called again.

Button
------

* job is always added to the queue before run
* failed job can be retried if failed, though it's same as new button click

Execution Logs
==============

In Project, Task and Job Trigger forms you can find ``Logs`` button in top-right
hand corner. You can filter and group logs by following fields:

* Sync Project
* Sync Task
* Job Trigger
* Job Start Time
* Log Level
* Status (Success / Fail)
