from odoo import http
from odoo.http import request


class CsvDownload(http.Controller):
    @http.route('/csv/download', type='http', auth='user')
    def download_csv(self, **kwargs):
        id = int(kwargs['id'])
        name = kwargs['name']
        prod = request.env['simulation.table'].search([('id', 'ilike', id)]).read()[0]
        return request.make_response(prod['output'], [('Content-Type', 'text/csv'),
                                                      ('Content-Disposition', 'attachment; filename=%s.csv' % name)])
