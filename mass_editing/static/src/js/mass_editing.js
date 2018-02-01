odoo.define('mass_editing.mass_editing', function (require) {
"use strict";

    var BasicModel = require("web.BasicModel");

    BasicModel.include({
        /**
         * parse the server values to javascript framwork
         * @param {String} fieldNames
         * @param {Object} element the dataPoint used as parent for the created
         *   dataPoints
         * @param {Object} data the server data to parse
         */
        _parseServerData: function (fieldNames, element, data) {
            var self = this;
            _.each(fieldNames, function (fieldName) {
                var field = element.fields[fieldName];
                var val = data[fieldName];
                if (field.type === 'many2one') {
                    // process many2one: split [id, nameget] and create corresponding record
                    // For val = Null
                    if (val && val !== false) {
                        // the many2one value is of the form [id, display_name]
                        var r = self._makeDataPoint({
                            modelName: field.relation,
                            fields: {
                                display_name: {type: 'char'},
                                id: {type: 'integer'},
                            },
                            data: {
                                display_name: val[1],
                                id: val[0],
                            },
                            parentID: element.id,
                        });
                        data[fieldName] = r.id;
                    } else {
                        // no value for the many2one
                        data[fieldName] = false;
                    }
                } else {
                    data[fieldName] = self._parseServerValue(field, val);
                }
            });
        },
    });

});
