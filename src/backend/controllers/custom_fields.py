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

from src.backend.import_models import custom_fields
from src.backend.import_controllers import forms


def add_custom_field(args):
    res, error = custom_fields.add_custom_field(args)
    if res:
        response = {
            "id": res
        }
        return response, 200
    else:
        response = {
            "errors": "CUSTOM_FIELDS_ERROR",
            "message": error
        }
        return response, 401


def retrieve_custom_fields(args):
    custom_fields_res, error = custom_fields.retrieve_custom_fields(args)

    if error is None:
        response = {
            "customFields": custom_fields_res
        }
        return response, 200

    response = {
        "errors": "CUSTOM_FIELDS_ERROR",
        "message": error
    }
    return response, 401


def update(args):
    res, error = custom_fields.update(args)
    if res:
        forms.update_custom_field_from_forms(args)
        return '', 200
    else:
        response = {
            "errors": "CUSTOM_FIELDS_ERROR",
            "message": error
        }
        return response, 401


def delete(args):
    res, error = custom_fields.delete(args)
    if not error:
        forms.delete_custom_field_from_forms(args)
        return '', 200
    else:
        response = {
            "errors": "CUSTOM_FIELDS_DELETE_ERROR",
            "message": error
        }
        return response, 401
