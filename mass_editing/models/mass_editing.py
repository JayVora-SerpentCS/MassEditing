# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import models, fields, api, tools, _
from lxml import etree

class ir_model_fields(models.Model):
    _inherit = 'ir.model.fields'

    @api.returns('self')  # If we keep @api.v7, we have to add @api.v8 code too.
    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        model_domain = []
        for domain in args:
            if domain[0] == 'model_id' and domain[2] and type(domain[2]) != list:
                model_domain += [('model_id', 'in', map(int, domain[2][1:-1].split(',')))]
            else:
                model_domain.append(domain)
        return super(ir_model_fields, self).search(cr, uid, model_domain, offset=offset, limit=limit, order=order, context=context, count=count)

    
#     @api.v8
#     def search(self, args, offset=0, limit=0, order=None, count=False):
#         model_domain = []
#         for domain in args:
#             if domain[0] == 'model_id' and domain[2] and type(domain[2]) != list:
#                 model_domain += [('model_id', 'in', map(int, domain[2][1:-1].split(',')))]
#             else:
#                 model_domain.append(domain)
#         return super(ir_model_fields, self).search(model_domain, offset=offset, limit=limit, order=order, count=count)

class mass_object(models.Model):
    _name = "mass.object"

    name = fields.Char(string="Name", required=True, select=1)
    model_id = fields.Many2one('ir.model', string='Model', required=False)
    field_ids = fields.Many2many('ir.model.fields', 'mass_field_rel', 'mass_id', 'field_id', string='Fields')
    ref_ir_act_window = fields.Many2one('ir.actions.act_window', string='Sidebar action', readonly=True,
                                        help="Sidebar action to make this template available on records "
                                             "of the related document model")
    ref_ir_value = fields.Many2one('ir.values', string='Sidebar button', readonly=True,
                                   help="Sidebar button to open the sidebar action")

    model_ids = fields.Many2many('ir.model', string='Model List')

    model_list = fields.Char(string='Model List', size=256)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('Name must be unique!')), ]

    @api.multi
    @api.onchange('model_id')
    def onchange_model(self):
        if self._context is None: self._context = {}
        if not self.model_id:
            self.model_ids = [(6, 0, [])]

        model_ids = [self.model_id.id]
        model_obj = self.env['ir.model']
        # active_model_obj = self.env[model_obj.browse(self.model_id.id).model]
        self.model_ids = [[6, 0, model_ids]]
        self.model_list = [self.model_ids.id]

    @api.multi
    def create_action(self):
        vals = {}
        action_obj = self.env['ir.actions.act_window']
        data_obj = self.env['ir.model.data']
        src_obj = self.model_id.model
        button_name = _('Mass Editing (%s)') % self.name
        vals['ref_ir_act_window'] = action_obj.create({
                 'name': button_name,
                 'type': 'ir.actions.act_window',
                 'res_model': 'mass.editing.wizard',
                 'src_model': src_obj,
                 'view_type': 'form',
                 'context': "{'mass_editing_object' : %d}" % (self.id),
                 'view_mode':'form,tree',
                 'target': 'new',
                 'auto_refresh':1
            }).id

        vals['ref_ir_value'] = self.env['ir.values'].create({
                 'name': button_name,
                 'model': src_obj,
                 'key2': 'client_action_multi',
                 'value': "ir.actions.act_window," + str(vals['ref_ir_act_window']),
                 'object': True,
             }).id

        self.write({
                    'ref_ir_act_window': vals.get('ref_ir_act_window', False),
                    'ref_ir_value': vals.get('ref_ir_value', False),
                })
        return True

    @api.one
    def unlink_action(self):
                if self.ref_ir_act_window:
                    winid = self.ref_ir_act_window.id
                    self.env['ir.actions.act_window'].search([('id', '=', winid)]).unlink()

                if self.ref_ir_value:
                    uinid = self.ref_ir_value.id
                    self.env['ir_values'].search([('id', '=', uinid)]).unlink()

    @api.one
    def unlink(self):
        self.unlink_action()
        return super(mass_object, self).unlink()

    @api.multi
    def copy(self, default):
        if default is None:
            default = {}

        default.update({'name':'', 'field_ids': []})
        return super(mass_object, self).copy(default)

class ir_module_module(models.Model):

    _inherit = 'ir.module.module'
    
    @api.multi
    def module_uninstall(self):
        cr, uid, context = self.env.args
        action_obj = self.pool.get('ir.actions.act_window')
        # search window actions of mass editing  and delete it
        if self.name == 'mass_editing':
            action_ids = action_obj.search (cr, uid, [('res_model', '=', 'mass.editing.wizard')], context=context)
            action_obj.unlink(cr, uid, action_ids, context=context)
        return super(ir_module_module, self).module_uninstall()
    
