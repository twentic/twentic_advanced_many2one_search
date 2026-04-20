import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DynamicSearchGenerator(models.Model):
    _name = 'dynamic.search.generator'
    _description = 'Dynamic Search Generator'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
    )
    model_name = fields.Char(
        related='model_id.model',
        string='Model Technical Name',
        readonly=True,
        store=True,
    )
    line_ids = fields.One2many(
        comodel_name='dynamic.search.generator.line',
        inverse_name='generator_id',
        string='Search Lines',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
        ],
        string='State',
        default='draft',
        required=True,
        readonly=True,
    )

    # -------------------------------------------------------------------------
    # Onchange
    # -------------------------------------------------------------------------

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            self.name = self.model_id.name

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_primary_search_view(self, model_name):
        """Return the primary search view for a given model."""
        View = self.env['ir.ui.view']
        view = View.search([
            ('model', '=', model_name),
            ('type', '=', 'search'),
            ('mode', '=', 'primary'),
        ], order='priority asc', limit=1)
        if not view:
            # Fallback: any search view (could be inherited primary)
            view = View.search([
                ('model', '=', model_name),
                ('type', '=', 'search'),
            ], order='priority asc', limit=1)
        return view

    @staticmethod
    def _sanitize_for_xml_id(value):
        """Convert a string to a safe XML ID segment (lowercase alphanumeric + underscore)."""
        return re.sub(r'[^a-z0-9]', '_', value.lower()).strip('_')

    def _build_arch(self, field_name, label, field_expression):
        """Build the arch XML string for a single inherited search field."""
        # Escape special XML characters in label and expression
        safe_label = (label
                      .replace('&', '&amp;')
                      .replace('"', '&quot;')
                      .replace('<', '&lt;')
                      .replace('>', '&gt;'))
        safe_expr = field_expression.replace("'", "\\'")
        return (
            '<data>'
            '<xpath expr="//search" position="inside">'
            '<field'
            f' name="{field_name}"'
            f' string="{safe_label}"'
            f' filter_domain="[(\'{safe_expr}\', \'ilike\', self)]"'
            '/>'
            '</xpath>'
            '</data>'
        )

    # -------------------------------------------------------------------------
    # Business actions
    # -------------------------------------------------------------------------

    def action_create_search_filters(self):
        """Generate one inherited search ir.ui.view per line."""
        self.ensure_one()

        if not self.line_ids:
            raise UserError(_('Please add at least one search line before creating filters.'))

        model_name = self.model_id.model
        search_view = self._get_primary_search_view(model_name)
        if not search_view:
            raise UserError(
                _('No primary search view found for model "%s".') % model_name
            )

        safe_generator = self._sanitize_for_xml_id(self.name)

        for line in self.line_ids:
            if line.view_id:
                # Filter already deployed for this line – skip
                continue

            safe_field = self._sanitize_for_xml_id(line.field_expression)
            xml_id_name = f'view_search_{safe_generator}_{safe_field}_{line.id}'

            # First segment of the expression is the actual field on the model
            field_name = line.field_expression.split('.')[0]
            arch = self._build_arch(field_name, line.name, line.field_expression)

            # Check whether the external ID already exists (idempotency guard)
            full_xml_id = f'dynamic_search_extended.{xml_id_name}'
            existing_view = self.env.ref(full_xml_id, raise_if_not_found=False)
            if existing_view:
                existing_view.write({'arch': arch, 'active': True})
                line.view_id = existing_view.id
                continue

            view = self.env['ir.ui.view'].create({
                'name': f'dynamic.search.{safe_generator}.{safe_field}',
                'model': model_name,
                'inherit_id': search_view.id,
                'arch': arch,
                'active': True,
            })

            # Register a stable external ID so the view can be referenced and
            # so duplicates are prevented across reinstalls / re-activations.
            self.env['ir.model.data'].create({
                'name': xml_id_name,
                'module': 'dynamic_search_extended',
                'model': 'ir.ui.view',
                'res_id': view.id,
                'noupdate': True,
            })

            line.view_id = view.id

        self.state = 'active'

    def action_remove_search_filters(self):
        """Delete all generated views and reset the generator to draft."""
        self.ensure_one()

        for line in self.line_ids:
            if not line.view_id:
                continue

            # Remove the ir.model.data entry so the external ID is freed
            xml_data = self.env['ir.model.data'].search([
                ('model', '=', 'ir.ui.view'),
                ('res_id', '=', line.view_id.id),
                ('module', '=', 'dynamic_search_extended'),
            ])
            xml_data.unlink()

            line.view_id.unlink()
            line.view_id = False

        self.state = 'draft'
