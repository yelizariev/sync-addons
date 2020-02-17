# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import models, fields


class Log(models.Model):
    _name = 'openapi.log'
    _order = 'id desc'
    _description = 'OpenAPI logs'

    namespace_id = fields.Many2one('openapi.namespace', 'Integration')
    request = fields.Char('Request')
    request_data = fields.Text('Request Data')
    response_data = fields.Text('Response Data')
    # create_uid -- auto field
    # create_date -- auto field
