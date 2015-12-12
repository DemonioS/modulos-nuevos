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
from openerp.osv import osv
from openerp.report import report_sxw
from openerp import models, fields
# from datetime import date, datetime, timedelta


class report_hr_salary_employee_bymonth(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_hr_salary_employee_bymonth, self).__init__(
            cr, uid, name, context=context)

        self.localcontext.update({
            'time': time,
            'get_employee': self.get_employee,
            'get_employee2': self.get_employee2,
            'get_analytic': self.get_analytic,
        })

        self.context = context
        self.mnths = []
        self.mnths_total = []
        self.total = 0.0

    def get_worked_days(self, form, emp_id, emp_salary, mes, ano):

        self.cr.execute(
            '''select number_of_days from hr_payslip_worked_days as p
left join hr_payslip as r on r.id = p.payslip_id
where r.employee_id = %s  and (to_char(date_to,'mm')= %s)
and (to_char(date_to,'yyyy')= %s) and p.code ='WORK100'
group by number_of_days''', (emp_id, mes, ano,))

        max = self.cr.fetchone()

        if max is None:
            emp_salary.append(0.00)
        else:
            emp_salary.append(max[0])
        return emp_salary

    def get_employe_basic_info(self, emp_salary, cod_id, mes, ano):

        self.cr.execute(
            '''select sum(pl.total) from hr_payslip_line as pl
left join hr_payslip as p on pl.slip_id = p.id
left join hr_employee as emp on emp.id = p.employee_id
left join resource_resource as r on r.id = emp.resource_id
where p.state = 'done' and (pl.code like %s) and (to_char(date_to,'mm')=%s)
and (to_char(date_to,'yyyy')=%s)
group by r.name, p.date_to''', (cod_id, mes, ano,))

        max = self.cr.fetchone()

        if max is None:
            emp_salary.append(0.00)
        else:
            emp_salary.append(max[0])

        return emp_salary

    def get_analytic(self, form):
        emp_salary = []
        salary_list = []
        last_year = form['end_date'][0:4]
        last_month = form['end_date'][5:7]
        cont = 0

        self.cr.execute(
            '''select sum(pl.total), w.name from hr_payslip_line as pl
left join hr_payslip as p on pl.slip_id = p.id
left join hr_employee as emp on emp.id = p.employee_id
left join hr_contract as r on r.id = p.contract_id
left join account_analytic_account as w on w.id = r.analytic_account_id
where p.state = 'done' and (to_char(date_to,'mm')=%s)
and (to_char(date_to,'yyyy')=%s)
group by w.name order by name''', (last_month, last_year,))

        id_data = self.cr.fetchall()
        if id_data is None:
            emp_salary.append(0.00)
            emp_salary.append(0.00)

        else:
            for index in id_data:
                emp_salary.append(id_data[cont][0])
                emp_salary.append(id_data[cont][1])

                cont = cont + 1
                salary_list.append(emp_salary)

                emp_salary = []

        return salary_list

    def get_salary(self, emp_id, emp_salary, cod_id, mes, ano):

        self.cr.execute(
            '''select sum(pl.total) from hr_payslip_line as pl
left join hr_payslip as p on pl.slip_id = p.id
left join hr_employee as emp on emp.id = p.employee_id
left join resource_resource as r on r.id = emp.resource_id
where p.state = 'done' and p.employee_id = %s and (pl.code like %s)
and (to_char(date_to,'mm')=%s) and (to_char(date_to,'yyyy')=%s)
group by r.name, p.date_to,emp.id''', (emp_id, cod_id, mes, ano,))

        max = self.cr.fetchone()

        if max is None:
            emp_salary.append(0.00)
        else:
            emp_salary.append(max[0])

        return emp_salary

    def get_employee2(self, form):
        emp_salary = []
        salary_list = []
        last_year = form['end_date'][0:4]
        last_month = form['end_date'][5:7]
        cont = 0

        self.cr.execute(
            '''select emp.id, emp.identification_id, emp.name_related
from hr_payslip as p left join hr_employee as emp on emp.id = p.employee_id
left join hr_contract as r on r.id = p.contract_id
where p.state = 'done'  and (to_char(date_to,'mm')=%s)
and (to_char(date_to,'yyyy')=%s)
group by emp.id, emp.name_related, emp.identification_id
order by name_related''', (last_month, last_year,))

        id_data = self.cr.fetchall()
        if id_data is None:
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
        else:
            for index in id_data:
                emp_salary.append(id_data[cont][0])
                emp_salary.append(id_data[cont][1])
                emp_salary.append(id_data[cont][2])
                emp_salary = self.get_worked_days(
                    form, id_data[cont][0], emp_salary, last_month, last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'BASIC', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'HEX%', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'GRAT', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'BONO', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'TOTIM', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'ASIGFAM', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'TOTNOI', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'TOTNOI', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'HAB', last_month, last_year)

                cont = cont + 1
                salary_list.append(emp_salary)

                emp_salary = []

        return salary_list

    def get_employee(self, form):
        emp_salary = []
        salary_list = []
        last_year = form['end_date'][0:4]
        last_month = form['end_date'][5:7]
        cont = 0

        self.cr.execute(
            '''select emp.id, emp.identification_id, emp.name_related
from hr_payslip as p left join hr_employee as emp on emp.id = p.employee_id
left join hr_contract as r on r.id = p.contract_id
where p.state = 'done'  and (to_char(date_to,'mm')=%s)
and (to_char(date_to,'yyyy')=%s)
group by emp.id, emp.name_related, emp.identification_id
order by name_related''', (last_month, last_year))

        id_data = self.cr.fetchall()
        if id_data is None:
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
        else:
            for index in id_data:
                emp_salary.append(id_data[cont][0])
                emp_salary.append(id_data[cont][1])
                emp_salary.append(id_data[cont][2])
                emp_salary = self.get_worked_days(
                    form, id_data[cont][0], emp_salary, last_month, last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'PREV', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'SALUD', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'IMPUNI', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'SECE', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'ADISA', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'TODELE', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'SMT', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'TDE', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'LIQ', last_month,
                    last_year)

                cont = cont + 1
                salary_list.append(emp_salary)

                emp_salary = []

        return salary_list


class wrapped_report_employee_salary_bymonth(osv.AbstractModel):
    _name = 'report.l10n_cl_hr_payroll.report_hrsalarybymonth'
    _inherit = 'report.abstract_report'
    _template = 'l10n_cl_hr_payroll.report_hrsalarybymonth'
    _wrapped_report_class = report_hr_salary_employee_bymonth

class hr_indicadores_previsionales(models.Model):

    _name = 'hr.indicadores'
    _description = 'Indicadores Previsionales'

    name = fields.Char('Nombre', required=True)
    asignacion_familiar_primer = fields.Float(
        'Asignacion Familiar Tramo 1', 
        help="Asig Familiar Primer Tramo")
    asignacion_familiar_segundo = fields.Float(
        'Asignacion Familiar Tramo 2', 
        help="Asig Familiar Segundo Tramo")
    asignacion_familiar_tercer = fields.Float(
        'Asignacion Familiar Tramo 3', 
        help="Asig Familiar Tercer Tramo")
    asignacion_familiar_monto_a = fields.Float(
        'Monto Tramo Uno', help="Monto A")
    asignacion_familiar_monto_b = fields.Float(
        'Monto Tramo Dos',  help="Monto B")
    asignacion_familiar_monto_c = fields.Float(
        'Monto Tramo Tres',  help="Monto C")
    contrato_plazo_fijo_empleador = fields.Float(
        'Contrato Plazo Fijo Empleador', 
        help="Contrato Plazo Fijo Empleador")
    contrato_plazo_indefinido_empleador = fields.Float(
        'Contrato Plazo Indefinido Empleador', 
        help="Contrato Plazo Fijo")
    contrato_plazo_indefinido_empleador_otro = fields.Float(
        'Contrato Plazo Indefinido 11 anos o mas', 
        help="Contrato Plazo Indefinido 11 anos")
    caja_compensacion = fields.Float(
        'Caja Compensacion Los Andes', 
        help="Caja de Compensacion")
    deposito_convenido = fields.Float(
        'Deposito Convenido', help="Deposito Convenido")
    fonasa = fields.Float('Fonasa',  help="Fonasa")
    mutual_seguridad = fields.Float(
        'Mutual Seguridad',  help="Mutual de Seguridad")
    pensiones_ips = fields.Float(
        'Pensiones IPS',  help="Pensiones IPS")
    sueldo_minimo = fields.Float(
        'Sueldo Minimo',  help="Sueldo Minimo")
    sueldo_minimo_otro = fields.Float(
        'Sueldo Minimo Menores de 18 y Mayores de 65', 
        help="Sueldo Minimo para Menores de 18 y Mayores a 65")
    tasa_mutual = fields.Float(
        'Tasa Mutual', help="Tasa AFP Mutual")
    tasa_afp_cuprum = fields.Float(
        'Cuprum',  help="Tasa AFP Cuprum")
    tasa_afp_capital = fields.Float(
        'Capital',  help="Tasa AFP Capital")
    tasa_afp_provida = fields.Float(
        'ProVida',  help="Tasa AFP Provida")
    tasa_afp_modelo = fields.Float(
        'Modelo',  help="Tasa AFP Modelo")
    tasa_afp_planvital = fields.Float(
        'PlanVital',  help="Tasa AFP PlanVital")
    tasa_afp_habitat = fields.Float(
        'Habitat',  help="Tasa AFP Habitat")
    tasa_sis_cuprum = fields.Float(
        'SIS', help="Tasa SIS Cuprum")
    tasa_sis_capital = fields.Float(
        'SIS', help="Tasa SIS Capital")
    tasa_sis_provida = fields.Float(
        'SIS',  help="Tasa SIS Provida")
    tasa_sis_planvital = fields.Float(
        'SIS',  help="Tasa SIS PlanVital")
    tasa_sis_habitat = fields.Float(
        'SIS',  help="Tasa SIS Habitat")
    tasa_sis_modelo = fields.Float(
        'SIS',  help="Tasa SIS Modelo")
    tasa_independiente_cuprum = fields.Float(
        'SIS',  help="Tasa Independientes Cuprum")
    tasa_independiente_capital = fields.Float(
        'SIS',  help="Tasa Independientes Capital")
    tasa_independiente_provida = fields.Float(
        'SIS',  help="Tasa Independientes Provida")
    tasa_independiente_planvital = fields.Float(
        'SIS',  help="Tasa Independientes PlanVital")
    tasa_independiente_habitat = fields.Float(
        'SIS',  help="Tasa Independientes Habitat")
    tasa_independiente_modelo = fields.Float(
        'SIS',  help="Tasa Independientes Modelo")
    tope_anual_apv = fields.Float(
        'Tope Anual APV',  help="Tope Anual APV")
    tope_mensual_apv = fields.Float(
        'Tope Mensual APV',  help="Tope Mensual APV")
    tope_imponible_afp = fields.Float(
        'Tope imponible AFP',  help="Tope Imponible AFP")
    tope_imponible_ips = fields.Float(
        'Tope Imponible IPS',  help="Tope Imponible IPS")
    tope_imponible_salud = fields.Float(
        'Tope Imponible Salud')
    tope_imponible_seguro_cesantia = fields.Float(
        'Tope Imponible Seguro Cesantia', 
        help="Tope Imponible Seguro de Cesantia")
    uf = fields.Float(
        'UF',  required=True, help="UF fin de Mes")
    utm = fields.Float(
        'UTM',  required=True, help="UTM Fin de Mes")
    uta = fields.Float('UTA',  help="UTA Fin de Mes")
    uf_otros = fields.Float(
        'UF Otros',  help="UF Seguro Complementario")

class hr_payslip(models.Model):

    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'

    indicadores_id = fields.Many2one(
        'hr.indicadores', 'Indicadores',
        states={'draft': [('readonly', False)]}, readonly=True, required=True)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        else:
            vals.update({'indicadores_id': context.get('indicadores_id')})
        return super(hr_payslip, self).create(
            cr, uid, vals, context=context)

class hr_payslip_run(models.Model):

    _inherit = 'hr.payslip.run'
    _description = 'Payslip Run'

    indicadores_id = fields.Many2one(
        'hr.indicadores', 'Indicadores',
        states={'draft': [('readonly', False)]}, readonly=True, required=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

