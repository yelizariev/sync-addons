.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

=========================
 WooCommerce Integration
=========================

Integration with https://woocommerce.com/

Sandbox
=======

To install local WooCommerce add following specification to your docker-compose.yml::

    services:

      # ...

      woo_db:
        image: mysql:5.7
        volumes:
            - woo_db:/var/lib/mysql
        environment:
          MYSQL_ROOT_PASSWORD: pass
          MYSQL_DATABASE: woo
          MYSQL_USER: woo
          MYSQL_PASSWORD: woo

      woo:
        image: wordpress:latest
        depends_on:
          - woo_db
        ports:
          - 8080:80
        environment:
          WORDPRESS_DB_HOST: woo_db:3306
          WORDPRESS_DB_USER: woo
          WORDPRESS_DB_PASSWORD: woo
        volumes:
          - woo:/var/www/html/wp-content

    volumes:
      woo:
      woo_db:

Open http://localhost:8080 and follow setup instructions

Navigate to ``Plugins >> Add New >> search for "woocommerce"``,  click `[Install Now]` and then `[Activate]`.

Add some products.

In Odoo set ``API_URL`` to ``http://woo``.

To setup webhooks from WooCommerce to Odoo:

* set System Parameters:

  * ``web.base.url`` -> ``http://odoo:8069`` (in assumption that your odoo service has name is ``odoo``)
  * ``web.base.url.freeze`` -> *any value*
* run  ``SETUP_WOO_WEBHOOKS``
* finaly, open Woo and check `webhooks <https://docs.woocommerce.com/document/webhooks/>`__

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Further information
===================

Apps store: https://apps.odoo.com/apps/modules/12.0/sync_1c/

Notifications on updates: `via Atom <https://github.com/itpp-labs/sync-addons/commits/12.0/sync_1c.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/itpp-labs/sync-addons/commits/12.0/sync_1c.atom>`_

Tested on `Odoo 12.0 <https://github.com/odoo/odoo/commit/84d554f436ab4c2e7fa05c3f4653244a50fcc495>`_
