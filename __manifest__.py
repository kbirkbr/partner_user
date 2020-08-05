# -*- coding: utf-8 -*-
{
    'name': "Partner to User 2",
    'version':'2.0',
    'summary': """
        Create a Login/User from a partner""",
    'license': 'AGPL-3',
    'author': "KABEER KB and Aitor Rosell Torralba",
    'website': "",
    'category': 'base',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [

        'wizard/user_view.xml',
        'views/partner_views.xml'
    ]
}
