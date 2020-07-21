# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

{
    "name": """Sync Studio Free""",
    "summary": """Synchronize anything with anything, including Odoo""",
    "category": "Extra Tools",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/12.0/sync/",
    "license": "Other OSI approved licence",  # MIT

    "depends": [
        "base_automation",
        "base_automation_webhook",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/sync_job_views.xml',
        'views/sync_trigger_views.xml',
        "security/ir.model.access.csv",
        "views/sync_project_views.xml",
        "views/sync_task_views.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
