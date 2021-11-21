from datetime import datetime, timedelta
from odoo import models, fields


class SimulationTableAction(models.Model):
    _name = "simulation"
    _description = "Financial simulation object"

    name = fields.Char(string="Name", required=True, default="Unnamed Simulation")
    output = fields.Text(string="Result", readonly=True)

    selected_deposits = fields.Many2many("deposit", string="Deposits")
    selected_withdrawals = fields.Many2many("withdrawal", string="Withdrawals")

    years_to_simulate = fields.Integer(string="Length (years)", required=True)

    _sql_constraints = [
        ('check_positive_years_to_simulate', 'CHECK(years_to_simulate > 0)',
         'The length (years) must be greater than 0.')
    ]

    def action_simulate(self):
        for record in self:
            first_simulation_year = datetime.now().year
            last_simulation_year = first_simulation_year + record.years_to_simulate

            year_to_amount = {year: 0.0 for year in range(first_simulation_year, last_simulation_year)}

            for deposit in record.selected_deposits:
                year_to_deposit = self._simulation_deposit(deposit, last_simulation_year)
                year_to_amount = self._merge_dicts_by_addition(year_to_amount, year_to_deposit)

            for withdrawal in record.selected_withdrawals:
                year_to_withdrawal = self._simulation_withdrawal(withdrawal, last_simulation_year)
                year_to_amount = self._merge_dicts_by_addition(year_to_amount, year_to_withdrawal)

            record.output = 'year,\tamount\n' + \
                            '\n'.join(str(key) + ',\t' + "{:.2f}".format(value) for key, value in year_to_amount.items())
        return True

    def action_download(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/csv/download?name=%s&id=%s' % (self.name, self.id),
            'target': 'self'
        }

    def _simulation_withdrawal(self, withdrawal, last_simulation_year):
        return self._money_transfer_simulation(withdrawal.start_date, withdrawal.end_date, last_simulation_year,
                                               0.0, -withdrawal.withdrawal_amount, withdrawal.withdrawal_frequency,
                                               interest_rate=0.0, compound=False)

    def _simulation_deposit(self, deposit, last_simulation_year):
        return self._money_transfer_simulation(deposit.start_date, deposit.end_date, last_simulation_year,
                                               deposit.initial_principle, deposit.regular_deposit,
                                               deposit.regular_frequency, deposit.interest_rate,
                                               deposit.compound_interest)

    def _money_transfer_simulation(self, starting_date, ending_date, last_simulation_year,
                                   initial_principle, regular_deposit, frequency,
                                   interest_rate, compound):
        days_to_skip = self._get_days_to_skip(frequency)
        adjusted_interest_rate = self._get_adjusted_interest_rate(interest_rate, frequency)

        result = {}
        running_sum = initial_principle
        while starting_date.year < last_simulation_year:
            if starting_date < ending_date:
                running_sum += regular_deposit
                if compound:
                    running_sum += running_sum * (adjusted_interest_rate / 100.0)
                else:
                    running_sum += initial_principle * (adjusted_interest_rate / 100.0)

            result[starting_date.year] = running_sum
            starting_date += timedelta(days=days_to_skip)

        return result

    def _merge_dicts_by_addition(self, return_dict, other_dict):
        for key, value in other_dict.items():
            try:
                return_dict[key] += value
            except KeyError:
                pass
        return return_dict

    def _get_days_to_skip(self, frequency):
        if frequency == 'yearly':
            return 365
        elif frequency == 'monthly':
            return 30
        else:
            return 1

    def _get_adjusted_interest_rate(self, interest_rate, frequency):
        if frequency == 'yearly':
            return interest_rate
        elif frequency == 'monthly':
            return interest_rate / 12
        else:
            return interest_rate / 365
