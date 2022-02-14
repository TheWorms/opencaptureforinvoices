# This file is part of Open-Capture for Invoices.

# Open-Capture for Invoices is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Open-Capture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Open-Capture for Invoices. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.

# @dev : Nathan Cheval <nathan.cheval@outlook.fr>
# @dev : Oussama Brich <oussama.brich@edissyum.com>

from src.backend.import_models import doctypes
from src.backend.import_classes import _SeparatorQR
from src.backend.main import create_classes_from_current_config
from flask_babel import gettext


def add_doctype(args):
    res, error = doctypes.add_doctype(args)
    if res:
        response = {
            "id": res
        }
        return response, 200
    else:
        response = {
            "errors": "DOC_TYPE_ERROR",
            "message": error
        }
        return response, 401


def retrieve_doctypes(args):
    _doctypes, error = doctypes.retrieve_doctypes(args)

    if error is None:
        response = {
            "doctypes": _doctypes
        }
        return response, 200

    response = {
        "errors": "DOC_TYPE_ERROR",
        "message": error
    }
    return response, 401


def update(args):
    doctype_old_data, _ = doctypes.retrieve_doctypes({
        'where': ['key = %s'],
        'data': [args['key']]
    })
    doctype_childs, _ = doctypes.retrieve_doctypes({
        'where': ['code like %s'],
        'data': ['{}.%'.format(doctype_old_data[0]['code'])]
    })
    for doctype_child in doctype_childs:
        res, error = doctypes.update({
            'key': doctype_child['key'],
            'code': doctype_child['code'].replace(doctype_old_data[0]['code'], args['code']),
            'label': doctype_child['label'],
            'status': doctype_child['status']
        })
        if not res:
            response = {
                "errors": "DOC_TYPE_ERROR",
                "message": error
            }
            return response, 401

    res, error = doctypes.update(args)
    if res:
        response = {
            "res": res
        }
        return response, 200
    else:
        response = {
            "errors": "DOC_TYPE_ERROR",
            "message": error
        }
        return response, 401


def generate_separator(args):
    _vars = create_classes_from_current_config()
    _cfg = _vars[1]
    qr_code_value = ""
    separator_type_label = ""
    if args['type'] == "docTypeSeparator":
        qr_code_value = f"DOCSTART|DOCTYPE|{args['key']}"
        separator_type_label = gettext('DOCTYPESEPARATOR')
    elif args['type'] == "documentSeparator":
        qr_code_value = "DOCSTART|GEN"
        separator_type_label = gettext('DOCUMENTSEPARATOR')
    elif args['type'] == "bundleSeparator":
        qr_code_value = "BUNDLESTART|META1"
        separator_type_label = gettext('BUNDLESEPARATOR')

    encoded_file = _SeparatorQR.generate_separator(qr_code_value, args['label'], separator_type_label)
    res, error = encoded_file, None
    if res:
        response = {
            "res": res
        }
        return response, 200
    else:
        response = {
            "errors": "DOC_TYPE_ERROR",
            "message": error
        }
        return response, 401