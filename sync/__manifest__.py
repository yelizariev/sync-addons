# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

{
    "name": """Sync Studio Free""",
    "summary": """Synchronize anything with anything, including Odoo""",
    "category": "Extra Tools",
    "images": [],
    "version": "12.0.1.0.0",
    "application": True,
    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/12.0/sync/",
    "license": "Other OSI approved licence",  # MIT
    "depends": ["base_automation", "mail", "website", "queue_job"],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/sync_groups.xml",
        "security/ir.model.access.csv",
        "views/sync_menus.xml",
        # "views/sync_job_views.xml",
        "views/sync_trigger_cron_views.xml",
        "views/sync_trigger_automation_views.xml",
        "views/sync_trigger_webhook_views.xml",
        "views/sync_trigger_button_views.xml",
        "views/sync_task_views.xml",
        "views/sync_project_views.xml",
    ],
    "demo": [
        # "data/sync_project_telegram_demo.xml",
        "data/sync_project_odoo2odoo_demo.xml",
        # "data/sync_project_trello_github_demo.xml",
        "data/sync_project_unittest_demo.xml",
    ],
    "qweb": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": "uninstall_hook",
    "auto_install": False,
    "installable": True,
}
