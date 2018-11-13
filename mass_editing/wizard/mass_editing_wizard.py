# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from lxml import etree

import openerp.tools as tools
from openerp import api, models


class MassEditingWizard(models.TransientModel):
    _name = 'mass.editing.wizard'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        result =\
            super(MassEditingWizard, self).fields_view_get(view_id=view_id,
                                                           view_type=view_type,
                                                           toolbar=toolbar,
                                                           submenu=submenu)
        context = self._context
        if context.get('mass_editing_object'):
            mass_obj = self.env['mass.object']
            editing_data = mass_obj.browse(context.get('mass_editing_object'))
            all_fields = {}
            xml_form = etree.Element('form', {
                'string': tools.ustr(editing_data.name)
            })
            xml_group = etree.SubElement(xml_form, 'group', {
                'colspan': '6',
                'col': '6',
            })
            etree.SubElement(xml_group, 'label', {
                'string': '',
                'colspan': '2',
            })
            xml_group = etree.SubElement(xml_form, 'group', {
                'colspan': '6',
                'col': '6',
            })
            model_obj = self.env[context.get('active_model')]
            field_info = model_obj.fields_get()
            for field in editing_data.field_ids:
                if field.ttype == "many2many":
                    all_fields[field.name] = field_info[field.name]
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove_m2m', 'Remove'),
                                      ('remove_m2m_all', 'Remove All'),
                                      ('add', 'Add')]
                    }
                    xml_group = etree.SubElement(xml_group, 'group', {
                        'colspan': '6',
                        'col': '6',
                    })
                    etree.SubElement(xml_group, 'separator', {
                        'string': field_info[field.name]['string'],
                        'colspan': '6',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '6',
                        'nolabel': '1'
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'colspan': '6',
                        'nolabel': '1',
                        'attrs': ("{'invisible': [('selection__" +
                                  field.name + "', '=', 'remove_m2m')]}"),
                    })
                elif field.ttype == "one2many":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove_o2m', 'Remove')],
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'relation': field.relation,
                    }
                    xml_group = etree.SubElement(xml_group, 'group', {
                        'colspan': '6',
                        'col': '6',
                    })
                    etree.SubElement(xml_group, 'separator', {
                        'string': field_info[field.name]['string'],
                        'colspan': '6',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '6',
                        'nolabel': '1',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'colspan': '6',
                        'nolabel': '1',
                        'attrs': ("{'invisible':[('selection__" +
                                  field.name + "', '=', 'remove_o2m')]}"),
                    })
                elif field.ttype == "many2one":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')],
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'relation': field.relation,
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '2',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'colspan': '4',
                        'attrs': ("{'invisible':[('selection__" +
                                  field.name + "', '=', 'remove')]}"),
                    })
                elif field.ttype == "char":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')],
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'size': field.size or 256,
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '2',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'attrs': ("{'invisible':[('selection__" +
                                  field.name + "','=','remove')]}"),
                        'colspan': '4',
                    })
                elif field.ttype == 'selection':
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')]
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '2',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'colspan': '4',
                        'attrs': ("{'invisible':[('selection__" +
                                  field.name + "', '=', 'remove')]}"),
                    })
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'selection': field_info[field.name]['selection'],
                    }
                else:
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                    }
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')]
                    }
                    if field.ttype == 'text':
                        xml_group = etree.SubElement(xml_group, 'group', {
                            'colspan': '6',
                            'col': '6',
                        })
                        etree.SubElement(xml_group, 'separator', {
                            'string': all_fields[field.name]['string'],
                            'colspan': '6',
                        })
                        etree.SubElement(xml_group, 'field', {
                            'name': "selection__" + field.name,
                            'colspan': '6',
                            'nolabel': '1',
                        })
                        etree.SubElement(xml_group, 'field', {
                            'name': field.name,
                            'colspan': '6',
                            'nolabel': '1',
                            'attrs': ("{'invisible':[('selection__" +
                                      field.name + "','=','remove')]}"),
                        })
                    else:
                        all_fields["selection__" + field.name] = {
                            'type': 'selection',
                            'string': field_info[field.name]['string'],
                            'selection': [('set', 'Set'), ('remove', 'Remove')]
                        }
                        etree.SubElement(xml_group, 'field', {
                            'name': "selection__" + field.name,
                            'colspan': '2',
                        })
                        etree.SubElement(xml_group, 'field', {
                            'name': field.name,
                            'nolabel': '1',
                            'attrs': ("{'invisible':[('selection__" +
                                      field.name + "','=','remove')]}"),
                            'colspan': '4',
                        })
            etree.SubElement(xml_form, 'separator', {
                'string': '',
                'colspan': '6',
                'col': '6',
            })
            xml_group3 = etree.SubElement(xml_form, 'footer', {})
            etree.SubElement(xml_group3, 'button', {
                'string': 'Apply',
                'class': 'btn-primary',
                'type': 'object',
                'name': 'action_apply',
            })
            etree.SubElement(xml_group3, 'button', {
                'string': 'Close',
                'class': 'btn-default',
                'special': 'cancel',
            })
            root = xml_form.getroottree()
            result['arch'] = etree.tostring(root)
            result['fields'] = all_fields
            doc = etree.XML(result['arch'])
            for field in editing_data.field_ids:
                field_name = "selection__" + field.name
                for node in doc.xpath("//field[@name='" + field.name + "']"):
                    modifiers = json.loads(node.get("modifiers", '{}'))
                    domain = [(field_name, '=', 'remove')]
                    if field.ttype == "many2many":
                        domain = [(field_name, '=', 'remove_m2m_all')]
                    elif field.ttype == "one2many":
                        domain = [(field_name, '=', 'remove_o2m')]
                    modifiers.update({'invisible': domain})
                    node.set("modifiers", json.dumps(modifiers))
            result['arch'] = etree.tostring(doc)
        return result

    @api.model
    def create(self, vals):
        model_name = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        model_id = self.env['ir.model'].search(
            [('model', '=', self._context.get('active_model'))])
        if model_name and active_ids:
            values = {}
            for key, val in vals.items():
                if key.startswith('selection_'):
                    split_key = key.split('__', 1)[1]
                    if val == 'set':
                        values.update({split_key: vals.get(split_key, False)})
                    elif val == 'remove':
                        values.update({split_key: False})
                    elif val in ['remove_m2m', 'remove_m2m_all']:
                        m2m_list = []
                        if vals.get(split_key):
                            for m2m_id in vals.get(split_key)[0][2]:
                                m2m_list.append((3, m2m_id))
                        if m2m_list:
                            values.update({split_key: m2m_list})
                        else:
                            values.update({split_key: [(5, 0, [])]})
                    elif val == 'remove_o2m':
                        # model_fieds will return the particular model
                        # in order to get the field of the model
                        # and its relation.
                        model_fields = self.env['ir.model.fields'].search(
                            [('name', '=', split_key),
                             ('model_id', '=', model_id and model_id.id)])
                        # field_model is relation of Object Relation
                        field_model = tools.ustr(model_fields and
                                                 model_fields.relation)
                        # field relation is relation field of O2m
                        field_relation = tools.ustr(
                            model_fields and
                            model_fields.relation_field)
                        # remove_ids is return O2m field particular ids
                        remove_ids = self.env[field_model].search(
                            [(field_relation, 'in',
                              self._context.get('active_ids'))])
                        o2m_list = [(2, rmv_id.id) for rmv_id in remove_ids]
                        values.update({split_key: o2m_list})
                    elif val == 'add':
                        m2m_list = []
                        for m2m_id in vals.get(split_key, False)[0][2]:
                            m2m_list.append((4, m2m_id))
                        values.update({split_key: m2m_list})
            if values:
                self.env[model_name].browse(active_ids).write(values)
        return super(MassEditingWizard, self).create({})

    @api.multi
    def action_apply(self):
        return {'type': 'ir.actions.act_window_close'}
