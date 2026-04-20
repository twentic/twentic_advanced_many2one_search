from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DynamicSearchGeneratorLine(models.Model):
    _name = 'dynamic.search.generator.line'
    _description = 'Dynamic Search Generator Line'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    generator_id = fields.Many2one(
        comodel_name='dynamic.search.generator',
        string='Generator',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        string='Label',
        required=True,
        help='Label shown to the user in the search bar.',
    )
    field_expression = fields.Char(
        string='Field Expression',
        required=True,
        help=(
            'Field or dotted path to filter on. '
            'Examples: name, partner_id.city, bank_ids.acc_number'
        ),
    )
    model_technical_name = fields.Char(
        related='generator_id.model_id.model',
        string='Model Technical Name',
        readonly=True,
        store=False,
    )
    view_id = fields.Many2one(
        comodel_name='ir.ui.view',
        string='Generated View',
        readonly=True,
        ondelete='set null',
        help='Technical view record generated for this search filter.',
    )
    is_deployed = fields.Boolean(
        string='Deployed',
        compute='_compute_is_deployed',
    )

    # -------------------------------------------------------------------------
    # Computed fields
    # -------------------------------------------------------------------------

    @api.depends('view_id')
    def _compute_is_deployed(self):
        for rec in self:
            rec.is_deployed = bool(rec.view_id)

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------

    @api.constrains('field_expression')
    def _check_field_expression(self):
        import re
        pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$')
        for rec in self:
            if not pattern.match(rec.field_expression):
                raise ValidationError(
                    _('Field expression "%s" is invalid. '
                      'Use a field name or a dotted path such as "partner_id.city".')
                    % rec.field_expression
                )
