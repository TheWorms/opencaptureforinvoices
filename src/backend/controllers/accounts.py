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

import os
import json
import subprocess
from flask import current_app
from flask_babel import gettext
from src.backend.import_classes import _Files
from src.backend.import_models import accounts
from src.backend.main import create_classes_from_current_config


def retrieve_suppliers(args):
    _vars = create_classes_from_current_config()
    _config = _vars[1]

    suppliers = accounts.retrieve_suppliers(args)
    response = {
        "suppliers": suppliers
    }
    return response, 200


def get_supplier_by_id(supplier_id):
    supplier_info, error = accounts.get_supplier_by_id({'supplier_id': supplier_id})

    if error is None:
        return supplier_info, 200
    else:
        response = {
            "errors": gettext('GET_SUPPLIER_BY_ID_ERROR'),
            "message": error
        }
        return response, 401


def get_address_by_id(address_id):
    address_info, error = accounts.get_address_by_id({'address_id': address_id})

    if error is None:
        return address_info, 200
    else:
        response = {
            "errors": gettext('GET_ADDRESS_BY_ID_ERROR'),
            "message": error
        }
        return response, 401


def update_supplier(supplier_id, data):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    _spreadsheet = _vars[7]
    supplier_info, error = accounts.get_supplier_by_id({'supplier_id': supplier_id})

    if error is None:
        res, error = accounts.update_supplier({'set': data, 'supplier_id': supplier_id})

        if error is None:
            _spreadsheet.update_supplier_ods_sheet(_db)
            return '', 200
        else:
            response = {
                "errors": gettext('UPDATE_SUPPLIER_ERROR'),
                "message": error
            }
            return response, 401
    else:
        response = {
            "errors": gettext('UPDATE_SUPPLIER_ERROR'),
            "message": error
        }
        return response, 401


def update_position_by_supplier_id(supplier_id, data):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    supplier_info, error = accounts.get_supplier_by_id({'supplier_id': supplier_id})
    if error is None:
        column = ''
        position = ''
        for _position in data:
            column = _position
            position = data[_position]

        supplier_positions = supplier_info['positions']
        supplier_positions.update({
            column: position
        })
        res, error = accounts.update_supplier({'set': {"positions": json.dumps(supplier_positions)}, 'supplier_id': supplier_id})
        if error is None:
            return '', 200
        else:
            response = {
                "errors": gettext('UPDATE_SUPPLIER_POSITIONS_ERROR'),
                "message": error
            }
            return response, 401


def update_page_by_supplier_id(supplier_id, data):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    supplier_info, error = accounts.get_supplier_by_id({'supplier_id': supplier_id})
    if error is None:
        column = ''
        page = ''
        for _page in data:
            column = _page
            page = data[_page]
        supplier_pages = supplier_info['pages']
        supplier_pages.update({
            column: page
        })
        res, error = accounts.update_supplier({'set': {"pages": json.dumps(supplier_pages)}, 'supplier_id': supplier_id})
        if error is None:
            return '', 200
        else:
            response = {
                "errors": gettext('UPDATE_SUPPLIER_PAGES_ERROR'),
                "message": error
            }
            return response, 401


def update_address(address_id, data):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    address_info, error = accounts.get_address_by_id({'address_id': address_id})

    if error is None:
        _set = {
            'address1': data['address1'],
            'address2': data['address2'],
            'postal_code': data['postal_code'],
            'city': data['city'],
            'country': data['country']
        }

        res, error = accounts.update_address({'set': _set, 'address_id': address_id})

        if error is None:
            return '', 200
        else:
            response = {
                "errors": gettext('UPDATE_ADDRESS_ERROR'),
                "message": error
            }
            return response, 401
    else:
        response = {
            "errors": gettext('UPDATE_ADDRESS_ERROR'),
            "message": error
        }
        return response, 401


def update_address_by_supplier_id(supplier_id, data):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    address_info, error = accounts.get_supplier_by_id({'select': ['address_id'], 'supplier_id': supplier_id})

    if error is None:
        _set = {
            'address1': data['address1'],
            'address2': data['address2'],
            'postal_code': data['postal_code'],
            'city': data['city'],
            'country': data['country']
        }

        res, error = accounts.update_address({'set': _set, 'address_id': address_info['address_id']})

        if error is None:
            return '', 200
        else:
            response = {
                "errors": gettext('UPDATE_ADDRESS_ERROR'),
                "message": error
            }
            return response, 401
    else:
        response = {
            "errors": gettext('UPDATE_ADDRESS_ERROR'),
            "message": error
        }
        return response, 401


def create_address(data):
    _vars = create_classes_from_current_config()
    _db = _vars[0]

    _columns = {
        'address1': data['address1'],
        'address2': data['address2'],
        'postal_code': data['postal_code'],
        'city': data['city'],
        'country': data['country']
    }

    res, error = accounts.create_address({'columns': _columns})

    if error is None:
        response = {
            "id": res
        }
        return response, 200
    else:
        response = {
            "errors": gettext('CREATE_ADDRESS_ERROR'),
            "message": error
        }
        return response, 401


def create_supplier(data):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    _spreadsheet = _vars[7]
    _columns = {
        'name': data['name'],
        'siret': data['siret'] if 'siret' in data else None,
        'siren': data['siren'] if 'siren' in data else None,
        'iban': data['iban'] if 'iban' in data else None,
        'vat_number': data['vat_number'] if 'vat_number' in data else None,
        'form_id': data['form_id'] if 'form_id' in data else None,
        'address_id': data['address_id'],
        'get_only_raw_footer': data['get_only_raw_footer'] if 'get_only_raw_footer' in data else False,
    }

    supplier = accounts.retrieve_suppliers({'where': ['vat_number = %s'], 'data': [data['vat_number']]})

    if not supplier:
        res, error = accounts.create_supplier({'columns': _columns})

        if error is None:
            _spreadsheet.update_supplier_ods_sheet(_db)
            response = {
                "id": res
            }
            return response, 200
        else:
            response = {
                "errors": gettext('CREATE_SUPPLIER_ERROR'),
                "message": error
            }
            return response, 401
    else:
        response = {
            "errors": gettext('CREATE_SUPPLIER_ERROR'),
            "message": gettext('SUPPLIER_VAT_NUMBER_ALREADY_EXISTS')
        }
        return response, 401


def retrieve_customers(args):
    _vars = create_classes_from_current_config()
    _config = _vars[1]

    customers = accounts.retrieve_customers(args)
    response = {
        "customers": customers
    }
    return response, 200


def get_customer_by_id(customer_id):
    customer_info, error = accounts.get_customer_by_id({'customer_id': customer_id})

    if error is None:
        return customer_info, 200
    else:
        response = {
            "errors": gettext('GET_CUSTOMER_BY_ID_ERROR'),
            "message": error
        }
        return response, 401


def get_accounting_plan_by_customer_id(customer_id):
    accounting_plan, error = accounts.get_accounting_plan_by_customer_id({'customer_id': customer_id})
    return accounting_plan, 200


def get_default_accounting_plan():
    accounting_plan, error = accounts.get_default_accounting_plan()
    return accounting_plan, 200


def update_customer(customer_id, data):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    supplier_info, error = accounts.get_customer_by_id({'customer_id': customer_id})

    if error is None:
        _set = {}
        if 'address_id' in data:
            _set.update({'address_id': data['address_id']})
        if 'name' in data:
            _set.update({'name': data['name']})
        if 'siret' in data:
            _set.update({'siret': data['siret']})
        if 'siren' in data:
            _set.update({'siren': data['siren']})
        if 'vat_number' in data:
            _set.update({'vat_number': data['vat_number']})
        if 'company_number' in data:
            _set.update({'company_number': data['company_number']})

        res, error = accounts.update_customer({'set': _set, 'customer_id': customer_id})

        if error is None:
            return '', 200
        else:
            response = {
                "errors": gettext('UPDATE_CUSTOMER_ERROR'),
                "message": error
            }
            return response, 401
    else:
        response = {
            "errors": gettext('UPDATE_CUSTOMER_ERROR'),
            "message": error
        }
        return response, 401


def create_customer(data):
    _vars = create_classes_from_current_config()
    _db = _vars[0]

    _columns = {
        'name': data['name'],
        'siret': data['siret'],
        'siren': data['siren'],
        'vat_number': data['vat_number'],
        'company_number': data['company_number'],
        'address_id': data['address_id'],
    }

    customer = accounts.retrieve_customers({'where': ['vat_number = %s'], 'data': [data['vat_number']]})

    if not customer:
        res, error = accounts.create_customer({'columns': _columns})

        if error is None:
            response = {
                "id": res
            }
            return response, 200
        else:
            response = {
                "errors": gettext('CREATE_CUSTOMER_ERROR'),
                "message": error
            }
            return response, 401
    else:
        response = {
            "errors": gettext('CREATE_CUSTOMER_ERROR'),
            "message": gettext('CUSTOMER_VAT_NUMBER_ALREADY_EXISTS')
        }
    return response, 401


def delete_customer(customer_id):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    customer_info, error = accounts.get_customer_by_id({'customer_id': customer_id})

    if error is None:
        res, error = accounts.delete_customer({'customer_id': customer_id})
        if error is None:
            return '', 200
        else:
            response = {
                "errors": gettext('DELETE_CUSTOMER_ERROR'),
                "message": error
            }
            return response, 401
    else:
        response = {
            "errors": gettext('DELETE_CUSTOMER_ERROR'),
            "message": error
        }
        return response, 401


def delete_supplier(supplier_id):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    supplier_info, error = accounts.get_supplier_by_id({'supplier_id': supplier_id})

    if error is None:
        res, error = accounts.delete_supplier({'supplier_id': supplier_id})
        if error is None:
            return '', 200
        else:
            response = {
                "errors": gettext('DELETE_SUPPLIER_ERROR'),
                "message": error
            }
            return response, 401
    else:
        response = {
            "errors": gettext('DELETE_SUPPLIER_ERROR'),
            "message": error
        }
        return response, 401


def import_suppliers(file):
    _vars = create_classes_from_current_config()
    _cfg = _vars[1]

    filename = _Files.save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
    res = subprocess.Popen('python3 ' + _cfg.cfg['GLOBAL']['projectpath'] + "/loadReferencial.py -f " +
                           filename + " -c " + current_app.instance_path + '/config.ini',
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = res.communicate()
    if err.decode('utf-8'):
        response = {
            "errors": gettext('LOAD_SUPPLIER_REFERENCIAL_ERROR'),
            "message": ''
        }
        return response, 401

    try:
        os.remove(filename)
    except FileNotFoundError:
        pass
    return '', 200
