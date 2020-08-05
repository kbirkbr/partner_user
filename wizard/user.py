# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import re
import unicodedata
import xlwt
import base64
import io
import random
import string

def get_password():
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(12)))
    return result_str

class CreateUser(models.TransientModel):
    _name = 'partner.user'
    _description = 'Create login from partner'

    groups_id = fields.Many2many('res.groups',column1='user_datas_id',column2="group_id",string='Groups')
    @api.model
    def default_get(self, fields):
        res = super(CreateUser, self).default_get(fields)
        vals = []
        for aid in self._context.get('active_ids'):
            partner_id = self.env['res.partner'].browse(aid)
            if not partner_id.user_id:
                vals.append((0,0,{'partner_id':partner_id.id,'login':partner_id.email or re.sub('[^A-Za-z0-9-_]+', '', unicodedata.normalize("NFD",partner_id.name).encode("ascii","ignore").decode("utf-8").replace(" ", "_")).lower()}))
        res['user_data'] = vals
        return res
    user_data = fields.One2many('user.datas','rel_id')
    @api.multi
    def create_login(self):
        for data in self:
            vals = {}
            user_data = []
            for da in data.user_data:
                rando_password = get_password()
                vals = {
                        'partner_id':da.partner_id.id,
                        'login':da.login,
                        'groups_id':data.groups_id,
                        'password':rando_password
                        }
                user = self.env['res.users'].create(vals)
                user_data.append({"user":user,"partner":da.partner_id,"wizard":data,"password":rando_password})
                da.partner_id.user_id = user.id
            excel_file = self.generate_excel(user_data)
            excel_file.seek(0)
            files = base64.b64encode(excel_file.read())
            attachment = self.env['ir.attachment'].create({
                'name': 'passwords.xls',
                'datas': files,
                'datas_fname': 'passwords.xls'
            })
            excel_file
            self.env["excel.download.wizard.user"].search([]).unlink()
            record_id = self.env["excel.download.wizard.user"].create({"binary":files,'file_name': 'passwords.xls'})
            return {'view_mode': 'form',
                    'res_id': record_id.id,
                    'view_id': self.env.ref('partner2user.wizar_user_view_form_excel').ids,
                    'res_model': 'excel.download.wizard.user',
                    'view_type': 'form',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    }

    @api.multi
    def generate_excel(self,data):
        stream = io.BytesIO()
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet(u'Passwords')
        sheet.write(0, 0, "user")
        sheet.write(0, 1, "password")
        sheet.write(0, 2, "email")
        sheet.write(0, 3, "name")
        sheet.write(0, 4, "user_id")
        sheet.write(0, 5, "partner_id")
        for index, item in enumerate(data, start=1):
            sheet.write(index, 0, item["user"].login)
            sheet.write(index, 1, item["password"])
            sheet.write(index, 2, item["partner"].email or "")
            sheet.write(index, 3, item["partner"].name)
            sheet.write(index, 4, item["user"].id)
            sheet.write(index, 5, item["partner"].id)
        book.save(stream)
        return stream

class CreateUserData(models.TransientModel):
    _name='user.datas'
    rel_id = fields.Many2one('partner.user')
    partner_id = fields.Many2one('res.partner',string='Partner')
    login = fields.Char('Login')


class ExcelDownloadWizard(models.Model):
    _name = "excel.download.wizard.user"

    binary = fields.Binary("Descargar", readonly=True)
    file_name = fields.Char(default="passwords.xls")