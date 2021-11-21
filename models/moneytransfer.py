from odoo import models, fields


class Deposit(models.Model):
    _name = "deposit"
    _description = "Deposit"

    name = fields.Char(string='Name', default='Unknown Deposit', required=True)

    initial_principle = fields.Float(string='Initial principle', required=True, default=0.0)
    regular_deposit = fields.Float(string='Regular deposit', required=True, default=0.0)
    regular_frequency = fields.Selection(
        string='Frequency',
        required=True,
        selection=[('yearly', 'Yearly'), ('monthly', 'Monthly'), ('daily', 'Daily')],
        default=0
    )

    interest_rate = fields.Float(string='Interest rate (%)', required=True, default=6.0)
    compound_interest = fields.Boolean(string='Compound interest', required=True, default=True)

    starting_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    _sql_constraints = [
        ('check_unsigned_initial_principle', 'CHECK(initial_principle >= 0.0)',
         'The initial principle should be a positive number.'),
        ('check_unsigned_regular_deposit', 'CHECK(regular_deposit >= 0.0)',
         'The regular deposit should be a positive number.')
    ]


class Withdrawal(models.Model):
    _name = "withdrawal"
    _description = "Withdrawal"

    name = fields.Char(string='Name', default='Unknown Withdrawal', required=True)

    withdrawal_amount = fields.Float(string='Withdrawal amount', required=True, default=0.0)
    withdrawal_frequency = fields.Selection(
        string='Frequency',
        required=True,
        selection=[('yearly', 'Yearly'), ('monthly', 'Monthly'), ('daily', 'Daily')],
        default=0
    )

    starting_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    _sql_constraints = [
        ('check_unsigned_withdrawal_amount', 'CHECK(withdrawal_amount >= 0.0)',
         'The withdrawal amount should be positive.')
    ]
