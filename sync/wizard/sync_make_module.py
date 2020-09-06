# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
import base64

from lxml import etree

from odoo import api, fields, models

from odoo.addons.http_routing.models.ir_http import slugify

MODULE = "sync"
PARAM_NAME = "sync.export_project.author_name"
PARAM_URL = "sync.export_project.author_url"
PARAM_LICENSE = "sync.export_project.license"


class SyncMakeModule(models.TransientModel):
    _name = "sync.make.module"
    _description = "Generating XML data file for a module"

    name = fields.Char("File Name", readonly=True, compute="_compute_name")
    name2 = fields.Char("File Name", readonly=True, compute="_compute_name")
    data = fields.Binary("File", readonly=True, attachment=False)
    data2 = fields.Binary(related="data")
    copyright_years = fields.Char("Copyright Year", default="2020", required=True)
    author_name = fields.Char("Author Name", help="e.g. Ivan Yelizariev", required=True)
    author_url = fields.Char("Author URL", help="e.g. https://twitter.com/yelizariev")
    license = fields.Char(
        "License",
        default="License MIT (https://opensource.org/licenses/MIT)",
        required=True,
    )
    state = fields.Selection([("choose", "choose"), ("get", "get")], default="choose")
    project_id = fields.Many2one("sync.project")

    def _compute_name(self):
        for r in self:
            name = slugify(r.project_id.name).replace("-", "_")
            name = "sync_project_{}_data.xml".format(name)
            r.name = name
            r.name2 = "{}.txt".format(name)

    @api.model
    def default_get(self, fields):
        vals = super().default_get(fields)
        vals["author_name"] = self.env["ir.config_parameter"].get_param(PARAM_NAME, "")
        vals["author_url"] = self.env["ir.config_parameter"].get_param(PARAM_URL, "")
        license = self.env["ir.config_parameter"].get_param(PARAM_LICENSE)
        if license:
            vals["license"] = license
        return vals

    def act_makefile(self):
        self.env["ir.config_parameter"].set_param(PARAM_NAME, self.author_name)
        self.env["ir.config_parameter"].set_param(PARAM_LICENSE, self.license)
        if self.author_url:
            self.env["ir.config_parameter"].set_param(PARAM_URL, self.author_url)

        url = " <{}>".format(self.author_url) if self.author_url else ""
        copyright_str = "<!-- Copyright {years} {name}{url}\n     {license}. -->".format(
            years=self.copyright_years,
            name=self.author_name,
            url=url,
            license=self.license,
        )
        root = etree.Element("odoo")
        project = self.project_id.with_context(active_test=False)
        records = [
            (project, ("name", "active", "secret_code", "common_code")),
        ]
        for secret in project.secret_ids:
            records.append((secret, ("key", "description", "url", "project_id")))

        for param in project.param_ids:
            records.append(
                (param, ("key", "value", "description", "url", "project_id"))
            )

        for task in project.task_ids:
            records.append((task, ("name", "active", "project_id", "code")))
            for trigger in task.button_ids:
                records.append((trigger, ("trigger_name", "name", "sync_task_id")))
            for trigger in task.cron_ids:
                records.append(
                    (
                        trigger,
                        (
                            "trigger_name",
                            "active",
                            "sync_task_id",
                            "interval_number",
                            "interval_type",
                        ),
                    )
                )
            for trigger in task.automation_ids:
                records.append(
                    (
                        trigger,
                        (
                            "trigger_name",
                            "active",
                            "sync_task_id",
                            "model_id",
                            "trigger",
                        ),
                    )
                )

            for trigger in task.webhook_ids:
                records.append(
                    (trigger, ("trigger_name", "active", "name", "sync_task_id"))
                )

        for r, field_names in records:
            root.append(self._record2xml(r, field_names))

        if hasattr(etree, "indent"):
            etree.indent(root, space="    ")
        data = etree.tostring(
            root,
            xml_declaration=True,
            encoding="UTF-8",
            pretty_print=True,
            doctype=copyright_str,
        )
        data = base64.encodebytes(data)
        self.write({"state": "get", "data": data})
        return self.get_wizard()

    @api.model
    def _record2id(self, record):
        existing = self.env["ir.model.data"].search(
            [("model", "=", record._name), ("res_id", "=", record.id)]
        )
        if existing:
            existing = existing[0]
            if existing.module == MODULE:
                return existing.name
            else:
                return existing.complete_name

        xmlid = "{}_{}".format(
            slugify(record.display_name), slugify(record._description)
        )

        self.env["ir.model.data"].create(
            {
                "model": record._name,
                "res_id": record.id,
                "module": MODULE,
                "name": xmlid,
            }
        )
        return xmlid

    @api.model
    def _field2xml(self, record, fname):
        field = record._fields[fname]
        value = getattr(record, fname)
        xml = etree.Element("field", name=fname)
        if field.type in ["char", "selection", "integer"]:
            xml.text = str(value) if value else ""
        elif field.type == "text":
            xml.text = etree.CDATA(value)
        elif field.type == "many2one":
            xml.set("ref", MODULE + "." + self._record2id(value))
        elif field.type == "boolean":
            xml.set("eval", str(value))
        return xml

    @api.model
    def _record2xml(self, record, fields):
        xml = etree.Element("record", id=self._record2id(record), model=record._name)
        for fname in fields:
            xml.append(self._field2xml(record, fname))
        return xml

    def act_configure(self):
        self.write({"state": "choose"})
        return self.get_wizard()

    def get_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }
