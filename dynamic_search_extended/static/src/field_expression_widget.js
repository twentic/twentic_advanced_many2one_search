/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { ModelFieldSelector } from "@web/core/model_field_selector/model_field_selector";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class FieldExpressionWidget extends Component {
    static template = "dynamic_search_extended.FieldExpressionWidget";
    static components = { ModelFieldSelector };
    static props = {
        ...standardFieldProps,
    };

    get resModel() {
        return this.props.record.data.model_technical_name || "";
    }

    get currentPath() {
        return this.props.record.data[this.props.name] || "";
    }

    onUpdate = (path) => {
        this.props.record.update({ [this.props.name]: path });
    };
}

registry.category("fields").add("field_expression_selector", {
    component: FieldExpressionWidget,
    supportedTypes: ["char"],
});
