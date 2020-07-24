==================
 Sync Studio Free
==================

.. contents::
   :local:

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* Install python package that you need to use. For example, to try demo projects install following packages:

    sudo pip3 install python-telegram-bot

User Access Levels
==================

* ``Sync Studio: User``: read-only access
* ``Sync Studio: Developer``: restricted write access
* ``Sync Studio: Manager``: same as Developer, but with access to **Secrets**, **Protected Code**, **Network Access**

Project
=======

* Open menu ``[[ Sync Studio ]] >> Projects``
* Create a project

  * **Name**, e.g. *Legacy migration*
  * **Parameters**

    * **Key**
    * **Value**
  * **Secrets**: Parameters with restricted access: key values are visiable for Managers only
  * **Protected Code**, **Common Code**: code that is executed before running any
    project's task. Can be used for initialization or for helpers. Secret params
    and package importing are available in **Protected Code** only. Any variables
    and functions that don't start with underscore symbol will be available in
    task's code.
  * **[x] Network Access**: makes ``requests`` lib avaiable for using in Code.
    It's not recommended to use other libs. If unset, all outgoing connections are blocked.
  * **Tasks**

    * **Name**, e.g. *Sync products*
    * **Code**: code with at least one of the following functions

      * ``handle_cron()``
      * ``handle_db(records)``
        * ``records``: all records on which this task is triggered
      * ``handle_webhook(httprequest)``
        * ``httprequest``: contains information about request. E.g.
          * `httprequest.form <https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/#werkzeug.wrappers.BaseRequest.form>`__: request args
          * `httprequest.files <https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/#werkzeug.wrappers.BaseRequest.files>`__: uploaded files
          * `httprequest.remote_addr <https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/#werkzeug.wrappers.BaseRequest.remote_addr>`__: ip address of the caller.
          * See `Werkzeug doc
            <https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/#werkzeug.wrappers.BaseRequest>`__
            for more information.
      * ``handle_button(data, user)``

        * ``user``: who clicked the button
        * ``data``: data attached to the trigger

    * **Cron Triggers**, **DB Triggers**, **Webhook Triggers**, **Manual
      Triggers**: when to execute the Code. See below for further information

Job Triggers
============

Cron
----

* **Execute Every**: every 2 hours, every 1 week, etc.
* **Next Execution Date**
* **Scheduler User**

DB
--

* **Name**, e.g. *On Product price changed*
* **Model**
* **Trigger Condition**

  * On Creation
  * On Update
  * On Creation & Update
  * On Deletion
  * Based on Timed Condition

    * Allows to trigger task before, after on in time of Date/Time fields, e.g.
      1 day after Sale Order is closed

* **Apply on**: records filter
* **Before Update Domain**: additional records filter for *On Update* event
* **Watched fields**: fields list for *On Update* event

Webhook
-------

* **Name**
* **Webhook URL**: readonly.

Button
------

* **Name**, e.g. "Sync all Products"
* **Data**: json/yaml data to be passed to handler

Code
====

Available variables and functions:

* ``env``: Odoo Environment on which the action is triggered
* ``log(message, level='info')``: logging function to record debug information
* ``make_response``: Only for Webhook: data to return to the caller
* ``params.PARAM_NAME``: projects's params.
* ``secrets.SECRET_NAME``: only in **Protected Code**

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

Demo Project: Telegram support
==============================

In this project we create new partners and attaches messages sent to telegram bot.

To try it, you need to install this module in demo mode.

How it works
------------

*Webhook Trigger* waits for an update from telegram. Once it happened, the action depends on message text:

* for ``/start`` message (it's sent on first bot usage), we reply with welcome
  message (can be configured in project parameter TELEGRAM_WELCOME_MESSAGE) and
  create a partner with **Internal Reference** equal to *<TELEGRAM_USER_ID>@telegram*

* for any other message we attach a message copy to the partner with corresponding **Internal Reference**

*DB trigger* waits for a message attached to a telegram partner (telegram partners are filtered by **Internal Reference** field). If the message has ``/telegram`` prefix, task's code is run:

* a message copy (after removeing the prefix) is sent to corresponding telegram user
* attach report message to the partner record

Configuration
-------------

In Telegram:

* send message ``/new`` to @BotFather and follow further instructions to create bot and get the bot token

In Odoo:

* Open menu ``[[ Sync Studio ]] >> Projects``
* Select *Demo Telegram* project
* Set **Secrets**:

  * TELEGRAM_BOT_TOKEN

* Select task *Setup*
* Select Button Trigger *Setup webhook*
* Click button ``[Run Now]``

Usage
-----

In Telegram:

* send some message to the created bot

In Odoo:

* Open Contacts/Customers menu
* RESULT: there is new partner with name *Telegram: <YOUR TELEGRAM NAME>* (the prefix can be configured in project parameter PARTNER_NAME_PREFIX)
* Open the partner and attach a log/message with prefix ``/telegram``, e.g. ``/telegram Hello! How can I help you?``
* Wait few seconds to get confirmation
* RESULT: you will see new attached message from Odoo Bot with confirmation that message is sent to telegram

In telegram:

* RESULT: the message is delivered via bot

You can continue chatting in this way

Demo Project: Odoo2odoo
=======================

In this project we push partners to external Odoo and sync back avatar changes.

To try it, you need to install this module in demo mode.

How it works
------------

*DB trigger* waits for partner creation. When it happens, task's code is run:

* creates a copy of partner on external Odoo

  * XMLRPC is used as API

* gets back id of the partner copy on external Odoo
* attaches the id to the partner of our Odoo

  * the ``make_ref`` method is used to save the relation in ``ir.model.data`` model
  * for reference name we use a prefix ``odoo2odoo_partner.``
    followed partner copy id, e.g.
    ``odoo2odoo_partner.123``, where 123 is id in external
    Odoo

To sync changes on external Odoo we use *Cron trigger*. It runs every 15 minutes. You can also run it manually. The code works as following:

* search ``ir.model.data`` for references with prefix ``odoo2odoo_partner`` (field with the prefix is called ``module``, don't be confused) to collect ids to sync and the oldest update time
* request to the external Odoo for the partners, but filtered by update time (to don't load partner with old updates only)
* for each of the fetched partner compare its update time with information saved in ``ir.model.data``

  * if a partner is updated since last sync, then update partner

Configuration
-------------

* Open menu ``[[ Sync Studio ]] >> Projects``
* Select *Demo Odoo2odoo* project
* Set **Secrets**:

  * URL, e.g. ``https://3674665-12-0.runbot41.odoo.com``
  * USERNAME, e.g. ``admin``
  * PASSWORD, e.g. ``admin``

Usage
-----

**Syncing new partner.**

* Open Contacts/Customers menu
* Create new partner
* Go back to the *Demo Odoo2odoo* project
* Choose the DB Trigger and check that logs don't contain errors

* Open the external Odoo

  * RESULT: the partner copy is on the external Odoo
  * Update avatar image on it

* Go back to our Odoo and trigger the syncronization in some of the following ways:

  1. Go back to the *Demo Odoo2odoo* project

     * Choose Cron Trigger and click ``[Run Manually]``

  2. Simply wait up to 15 minutes :)

* Now open the partner in our Odoo
* RESULT: avatar is synced from external Odoo
* You can try to change avatar on external Odoo again and should get the same results

**Syncing all partners.**

* Open menu ``[[ Sync Studio ]] >> Projects``
* Select *Demo Odoo2odoo* project
* Choose Button Trigger *Sync All Partners*
* Click button ``[Run Now]``
* Open the external Odoo

  * RESULT: copies of all our partners are on the external Odoo; they have *Sync Studio:* prefix (can be configured in project parameter SYNC_ALL_PARTNER_PREFIX)
