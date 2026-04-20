{
    'name': 'Dynamic Search Extended',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Dynamically add search fields to any model via inherited views',
    'description': """
        Allows administrators to add search fields (text filters in the search bar)
        to any model dynamically, by automatically creating inherited ir.ui.view records.
    """,
    'author': 'TwenTIC',
    'website': 'https://twentic.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'assets': {
        'web.assets_backend': [
            'dynamic_search_extended/static/src/field_expression_widget.js',
            'dynamic_search_extended/static/src/field_expression_widget.xml',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/dynamic_search_generator_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
