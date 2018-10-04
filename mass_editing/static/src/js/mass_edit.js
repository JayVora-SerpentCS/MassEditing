odoo.define('mass_editing.mass_editing', function (require) {
"use strict";

var FormView = require('web.FormView');
FormView.include({
    _build_onchange_specs: function() {
        var self = this;
        var find = function(field_name, root) {
            var fields = [root];
            while (fields.length) {
                var node = fields.pop();
                if (!node) {
                    continue;
                }
                if (node.tag === 'field' && node.attrs.name === field_name) {
                    return node.attrs.on_change || "";
                }
                fields = _.union(fields, node.children);
            }
            return "";
        };

        self._onchange_fields = [];
        self._onchange_specs = {};
        _.each(this.fields, function(field, name) {
            self._onchange_fields.push(name);
            self._onchange_specs[name] = find(name, field.node);

            // we get the list of first-level fields of x2many firstly by
            // getting them from the field embedded views, then if no embedded
            // view is present for a loaded view, we get them from the default
            // view that has been loaded

            // gather embedded view objects
            var views = _.clone(field.field.views);
            // also gather default view objects
            if (field.viewmanager) {
                _.each(field.viewmanager.views, function(view, view_type) {
                    // add default view if it was not embedded and it is loaded
                    var not_embedded = view.embedded_view === undefined; // ONLY FOR 9.0
//                    Checked views only then check for view_type
                    if (views && views[view_type] === undefined && view.controller && not_embedded) {
                        views[view_type] = view.controller.fields_view;
                    }
                });
            }
            _.each(views, function(view) {
                _.each(view.fields, function(_, subname) {
                    self._onchange_specs[name + '.' + subname] = find(subname, view.arch);
                });
            });
        });
    },
})

});
