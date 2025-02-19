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

# @dev : Nathan Cheval <nathan.cheval@edissyum.com>

import base64
from flask_babel import gettext
from src.backend.import_controllers import auth, verifier
from flask import Blueprint, make_response, request

bp = Blueprint('verifier', __name__, url_prefix='/ws/')


@bp.route('verifier/upload', methods=['POST'])
@auth.token_required
def upload():
    input_id = None
    if 'inputId' in request.args:
        input_id = request.args['inputId']
    files = request.files
    res = verifier.handle_uploaded_file(files, input_id)
    if res:
        return make_response('', 200)
    else:
        return make_response(gettext('UNKNOW_ERROR'), 400)


@bp.route('verifier/invoices/list', methods=['POST'])
@auth.token_required
def invoices_list():
    data = request.json
    res = verifier.retrieve_invoices(data)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/<int:invoice_id>', methods=['GET'])
@auth.token_required
def invoice_info(invoice_id):
    res = verifier.get_invoice_by_id(invoice_id)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/<int:invoice_id>/updatePosition', methods=['PUT'])
@auth.token_required
def update_invoice_position(invoice_id):
    data = request.json['args']
    res = verifier.update_position_by_invoice_id(invoice_id, data)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/<int:invoice_id>/updatePage', methods=['PUT'])
@auth.token_required
def update_invoice_page(invoice_id):
    data = request.json['args']
    res = verifier.update_page_by_invoice_id(invoice_id, data)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/delete/<int:invoice_id>', methods=['DELETE'])
@auth.token_required
def delete_invoice(invoice_id):
    res = verifier.delete_invoice(invoice_id)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/<int:invoice_id>/updateData', methods=['PUT'])
@auth.token_required
def update_invoice_data(invoice_id):
    data = request.json['args']
    res = verifier.update_invoice_data_by_invoice_id(invoice_id, data)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/<int:invoice_id>/export_xml', methods=['POST'])
@auth.token_required
def export_xml(invoice_id):
    data = request.json['args']
    res = verifier.export_xml(invoice_id, data)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/<int:invoice_id>/export_maarch', methods=['POST'])
@auth.token_required
def export_maarch(invoice_id):
    data = request.json['args']
    res = verifier.export_maarch(invoice_id, data)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/<int:invoice_id>/deleteData', methods=['PUT'])
@auth.token_required
def delete_invoice_data(invoice_id):
    field_id = request.json['args']
    res = verifier.delete_invoice_data_by_invoice_id(invoice_id, field_id)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/<int:invoice_id>/deletePosition', methods=['PUT'])
@auth.token_required
def delete_invoice_position(invoice_id):
    field_id = request.json['args']
    res = verifier.delete_invoice_position_by_invoice_id(invoice_id, field_id)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/<int:invoice_id>/deletePage', methods=['PUT'])
@auth.token_required
def delete_invoice_page(invoice_id):
    field_id = request.json['args']
    res = verifier.delete_invoice_page_by_invoice_id(invoice_id, field_id)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/<int:invoice_id>/update', methods=['PUT'])
@auth.token_required
def update_invoice(invoice_id):
    data = request.json['args']
    res = verifier.update_invoice(invoice_id, data)
    return make_response(res[0], res[1])


@bp.route('verifier/invoices/removeLockByUserId/<string:user_id>', methods=['PUT'])
@auth.token_required
def remove_lock_by_user_id(user_id):
    res = verifier.remove_lock_by_user_id(user_id)
    return make_response(res[0], res[1])


@bp.route('verifier/ocrOnFly', methods=['POST'])
@auth.token_required
def ocr_on_fly():
    data = request.json
    positions_masks = False
    if 'positionsMasks' in data:
        positions_masks = data['positionsMasks']
    result = verifier.ocr_on_the_fly(data['fileName'], data['selection'], data['thumbSize'], positions_masks)
    return make_response({'result': result}, 200)


@bp.route('verifier/getThumb', methods=['POST'])
@auth.token_required
def get_thumb():
    data = request.json['args']
    file_content = verifier.get_file_content(data['path'], data['filename'], 'image/jpeg')
    return make_response({'file': str(base64.b64encode(file_content.get_data()).decode('UTF-8'))}), 200


@bp.route('verifier/getTokenINSEE', methods=['GET'])
@auth.token_required
def get_token_insee():
    token = verifier.get_token_insee()
    return make_response({'token': token[0]}, token[1])


@bp.route('verifier/verifySIREN', methods=['POST'])
@auth.token_required
def verify_siren():
    token = request.json['token']
    siren = request.json['siren']
    status = verifier.verify_siren(token, siren)
    return make_response({'status': status[0]}, status[1])


@bp.route('verifier/verifySIRET', methods=['POST'])
@auth.token_required
def verify_siret():
    token = request.json['token']
    siret = request.json['siret']
    status = verifier.verify_siret(token, siret)
    return make_response({'status': status[0]}, status[1])


@bp.route('verifier/verifyVATNumber', methods=['POST'])
@auth.token_required
def verify_vat_number():
    vat_number = request.json['vat_number']
    status = verifier.verify_vat_number(vat_number)
    return make_response({'status': status[0]}, status[1])


@bp.route('verifier/invoices/totals', defaults={'status': None}, methods=['GET'])
@bp.route('verifier/invoices/totals/<string:status>', methods=['GET'])
@auth.token_required
def get_totals(status):
    totals = verifier.get_totals(status)
    return make_response({'totals': totals[0]}, totals[1])
