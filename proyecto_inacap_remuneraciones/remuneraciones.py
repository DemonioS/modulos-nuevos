# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 S&C (<http://salazarcarlos.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
 
import time
from openerp import models, fields
# from datetime import date, datetime, timedelta

class hr_salary_employee_bymonth(models.TransientModel):

    _name = 'hr.salary.employee.month'
    _description = 'Libro de Remuneraciones Haberes'

    end_date = fields.Date('End Date', required=True)

    _defaults = {

        'end_date': lambda *a: time.strftime('%Y-%m-%d'),

    }

    def print_report(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: return report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}

        res = self.read(cr, uid, ids, context=context)
        res = res and res[0] or {}
        datas.update({'form': res})
        return self.pool['report'].get_action(
            cr, uid, ids, 'l10n_cl_hr_payroll.report_hrsalarybymonth',
            data=datas, context=context)


class hr_contract(models.Model):

    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    afp_id = fields.Many2one('hr.afp', 'AFP')
    aporte_voluntario = fields.Float(
        'Aporte Voluntario', help="Aporte Voluntario al ahorro individual")
    anticipo_sueldo = fields.Float(
        'Anticipo de Sueldo',
        help="Anticipo De Sueldo Realizado Contablemente")
    carga_familiar = fields.Integer(
        'Carga Familiar',
        help="Carga Familiar para el calculo de asignacion familiar")
    colacion = fields.Float('Colacion', help="Colacion")
    isapre_id = fields.Many2one('hr.isapre', 'ISAPRE')
    isapre_cotizacion_uf = fields.Float(
        'Cotizacion UF',  help="Cotizacion Pactada en UF")
    movilizacion = fields.Float(
        'Movilizacion', help="Movilizacion")
    mutual_seguridad = fields.Boolean('Mutual Seguridad')
    otro_no_imp = fields.Float(
        'Otros No Imponible', help="Otros Haberes No Imponibles")
    otros_imp = fields.Float(
        'Otros Imponible', help="Otros Haberes Imponibles")
    pension = fields.Boolean('Pensionado')
    # seguro_complementario_id = fields.Many2one('hr.seguro.complementario',
    #    'Seguro Complementario')
    seguro_complementario_cotizacion_uf = fields.Float(
        'Cotizacion UF',  help="Cotizacion Pactada en UF")
    viatico_santiago = fields.Float(
        'Viatico Santiago',  help="Viatico Santiago")


class hr_type_employee(models.Model):
    _name = 'hr.type.employee'
    _description = 'Tipo de Empleado'

    id_type = fields.Char('Codigo', required=True)
    name = fields.Char('Nombre', required=True)


class hr_employee(models.Model):

    _inherit = 'hr.employee'
    _description = 'Employee Contract'

    type_id = fields.Many2one('hr.type.employee', 'Tipo de Empleado')


class hr_payslip_employees(models.TransientModel):

    _inherit = 'hr.payslip.employees'

    def compute_sheet(self, cr, uid, ids, context=None):
        run_pool = self.pool.get('hr.payslip.run')
        if context is None:
            context = {}
        if context.get('active_id'):
            run_data = run_pool.read(
                cr, uid, context['active_id'], ['indicadores_id'])
        indicadores_id = run_data.get('indicadores_id')
        indicadores_id = indicadores_id and indicadores_id[0] or False
        if indicadores_id:
            context = dict(context, indicadores_id=indicadores_id)
        return super(hr_payslip_employees, self).compute_sheet(
            cr, uid, ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
