/** This file is part of Open-Capture for Invoices.

Open-Capture for Invoices is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Open-Capture is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Open-Capture for Invoices. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.

@dev : Nathan Cheval <nathan.cheval@outlook.fr> */

import { Component, OnInit } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {ActivatedRoute, Router} from "@angular/router";
import {FormBuilder} from "@angular/forms";
import {AuthService} from "../../../../../services/auth.service";
import {UserService} from "../../../../../services/user.service";
import {TranslateService} from "@ngx-translate/core";
import {NotificationService} from "../../../../../services/notifications/notifications.service";
import {SettingsService} from "../../../../../services/settings.service";
import {PrivilegesService} from "../../../../../services/privileges.service";
import {API_URL} from "../../../../env";
import {catchError, finalize, tap} from "rxjs/operators";
import {of} from "rxjs";
import {LastUrlService} from "../../../../../services/last-url.service";
import {LocalStorageService} from "../../../../../services/local-storage.service";
import {Sort} from "@angular/material/sort";
import {ConfirmDialogComponent} from "../../../../../services/confirm-dialog/confirm-dialog.component";
import {MatDialog} from "@angular/material/dialog";
import {MAT_FORM_FIELD_DEFAULT_OPTIONS} from "@angular/material/form-field";
import {HistoryService} from "../../../../../services/history.service";

@Component({
    selector: 'app-list',
    templateUrl: './form-list.component.html',
    styleUrls: ['./form-list.component.scss'],
    providers: [
        { provide: MAT_FORM_FIELD_DEFAULT_OPTIONS, useValue: { appearance: 'fill' } },
    ]
})
export class FormListComponent implements OnInit {
    loading: boolean            = true;
    columnsToDisplay: string[]  = ['id', 'label', 'default_form', 'enabled', 'actions'];
    pageSize : number           = 10;
    pageIndex: number           = 0;
    total: number               = 0;
    offset: number              = 0;
    forms : any                 = [];

    constructor(
        public router: Router,
        private http: HttpClient,
        private dialog: MatDialog,
        private route: ActivatedRoute,
        public userService: UserService,
        private formBuilder: FormBuilder,
        private authService: AuthService,
        public translate: TranslateService,
        private notify: NotificationService,
        private historyService: HistoryService,
        public serviceSettings: SettingsService,
        private routerExtService: LastUrlService,
        public privilegesService: PrivilegesService,
        private localeStorageService: LocalStorageService,
    ) {
    }

    ngOnInit(): void {
        this.serviceSettings.init();
        const lastUrl = this.routerExtService.getPreviousUrl();
        if (lastUrl.includes('settings/verifier/forms') || lastUrl === '/') {
            if (this.localeStorageService.get('formsPageIndex'))
                this.pageIndex = parseInt(this.localeStorageService.get('formsPageIndex') as string);
            this.offset = this.pageSize * (this.pageIndex);
        }else
            this.localeStorageService.remove('formsPageIndex');
        this.loadForms();
    }

    onPageChange(event: any) {
        this.pageSize = event.pageSize;
        this.offset = this.pageSize * (event.pageIndex);
        this.pageIndex = event.pageIndex;
        this.localeStorageService.save('formsPageIndex', event.pageIndex);
        this.loadForms();
    }

    loadForms(): void {
        this.loading = true;
        this.http.get(API_URL + '/ws/forms/list?module=verifier&limit=' + this.pageSize + '&offset=' + this.offset, {headers: this.authService.headers}).pipe(
            tap((data: any) => {
                if (data.forms[0]) this.total = data.forms[0].total;
                else if (this.pageIndex !== 0) {
                    this.pageIndex = this.pageIndex - 1;
                    this.offset = this.pageSize * (this.pageIndex);
                    this.loadForms();
                }
                this.forms = data.forms;
            }),
            finalize(() => this.loading = false),
            catchError((err: any) => {
                console.debug(err);
                this.notify.handleErrors(err);
                return of(false);
            })
        ).subscribe();
    }

    async getInputs(formId: any) {
        return await this.http.get(API_URL + '/ws/inputs/getByFormId/' + formId, {headers: this.authService.headers}).toPromise();
    }

    async deleteConfirmDialog(formId: number, form: string) {
        const inputs: any = await this.getInputs(formId);
        if (inputs.length !== 0) {
            const forms = this.forms;
            forms.forEach((form: any, cpt: number) => {
                if (form.id === formId) {
                    forms.splice(cpt, 1);
                }
            });
            const inputList: any = [];
            const inputListLabel: any = [];
            inputs.forEach((input: any) => {
                inputList.push({'id': input.id, 'label': input.input_label});
                inputListLabel.push(input.input_label);
            });
            const dialogRef = this.dialog.open(ConfirmDialogComponent, {
                data:{
                    confirmTitle        : this.translate.instant('GLOBAL.new_input_link'),
                    confirmText         : this.translate.instant('FORMS.inputs_list_already_linked', {"inputsList": inputListLabel.join('<br>')}),
                    selectValues        : forms,
                    selectLabel         : this.translate.instant('FORMS.choose_form'),
                    confirmButton       : this.translate.instant('GLOBAL.delete_form_and_reassign_input'),
                    confirmButtonColor  : "warn",
                    cancelButton        : this.translate.instant('GLOBAL.cancel'),
                },
                width: "600px",
            });

            dialogRef.afterClosed().subscribe(result => {
                if (result) {
                    this.updateInputsDefaultForm(result, inputList);
                    this.deleteForm(formId);
                    this.historyService.addHistory('verifier', 'delete_form', this.translate.instant('HISTORY-DESC.delete-form', {form: form}));
                }
            });
        } else {
            const dialogRef = this.dialog.open(ConfirmDialogComponent, {
                data:{
                    confirmTitle        : this.translate.instant('GLOBAL.confirm'),
                    confirmText         : this.translate.instant('FORMS.confirm_delete', {"form": form}),
                    confirmButton       : this.translate.instant('GLOBAL.delete'),
                    confirmButtonColor  : "warn",
                    cancelButton        : this.translate.instant('GLOBAL.cancel'),
                },
                width: "600px",
            });

            dialogRef.afterClosed().subscribe(result => {
                if (result) {
                    this.deleteForm(formId);
                    this.historyService.addHistory('verifier', 'delete_form', this.translate.instant('HISTORY-DESC.delete-form', {form: form}));
                }
            });
        }
    }

    duplicateConfirmDialog(formId: number, form: string) {
        const dialogRef = this.dialog.open(ConfirmDialogComponent, {
            data:{
                confirmTitle        : this.translate.instant('GLOBAL.confirm'),
                confirmText         : this.translate.instant('FORMS.confirm_duplicate', {"form": form}),
                confirmButton       : this.translate.instant('GLOBAL.duplicate'),
                confirmButtonColor  : "warn",
                cancelButton        : this.translate.instant('GLOBAL.cancel'),
            },
            width: "600px",
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result) {
                this.duplicateForm(formId);
                this.historyService.addHistory('verifier', 'duplicate_form', this.translate.instant('HISTORY-DESC.duplicate-form', {form: form}));
            }
        });
    }

    disableConfirmDialog(formId: number, form: string) {
        const dialogRef = this.dialog.open(ConfirmDialogComponent, {
            data:{
                confirmTitle        : this.translate.instant('GLOBAL.confirm'),
                confirmText         : this.translate.instant('FORMS.confirm_disable', {"form": form}),
                confirmButton       : this.translate.instant('GLOBAL.disable'),
                confirmButtonColor  : "warn",
                cancelButton        : this.translate.instant('GLOBAL.cancel'),
            },
            width: "600px",
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result) {
                this.disableForm(formId);
            }
        });
    }

    enableConfirmDialog(formId: number, form: string) {
        const dialogRef = this.dialog.open(ConfirmDialogComponent, {
            data:{
                confirmTitle        : this.translate.instant('GLOBAL.confirm'),
                confirmText         : this.translate.instant('FORMS.confirm_enable', {"form": form}),
                confirmButton       : this.translate.instant('GLOBAL.enable'),
                confirmButtonColor  : "warn",
                cancelButton        : this.translate.instant('GLOBAL.cancel'),
            },
            width: "600px",
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result) {
                this.enableForm(formId);
            }
        });
    }

    deleteForm(formId: number) {
        if (formId !== undefined) {
            this.http.delete(API_URL + '/ws/forms/delete/' + formId, {headers: this.authService.headers}).pipe(
                tap(() => {
                    this.loadForms();
                    this.notify.success(this.translate.instant('FORMS.form_deleted'));
                }),
                catchError((err: any) => {
                    console.debug(err);
                    this.notify.handleErrors(err);
                    return of(false);
                })
            ).subscribe();
        }
    }

    updateInputsDefaultForm(newFormId: number, inputs: any) {
        if (newFormId !== undefined) {
            for (const cpt in inputs) {
                const args = {'default_form_id': newFormId};
                this.http.put(API_URL + '/ws/inputs/update/' + inputs[cpt].id, {'args': args}, {headers: this.authService.headers}).pipe(
                    catchError((err: any) => {
                        console.debug(err);
                        this.notify.handleErrors(err);
                        return of(false);
                    })
                ).subscribe();
            }
        }
    }

    duplicateForm(formId: number) {
        if (formId !== undefined) {
            this.http.post(API_URL + '/ws/forms/duplicate/' + formId, {}, {headers: this.authService.headers}).pipe(
                tap(() => {
                    this.loadForms();
                }),
                catchError((err: any) => {
                    console.debug(err);
                    this.notify.handleErrors(err);
                    return of(false);
                })
            ).subscribe();
        }
    }

    disableForm(formId: number) {
        if (formId !== undefined) {
            this.http.put(API_URL + '/ws/forms/disable/' + formId, null, {headers: this.authService.headers}).pipe(
                tap(() => {
                    this.loadForms();
                }),
                catchError((err: any) => {
                    console.debug(err);
                    this.notify.handleErrors(err);
                    return of(false);
                })
            ).subscribe();
        }
    }

    enableForm(formId: number) {
        if (formId !== undefined) {
            this.http.put(API_URL + '/ws/forms/enable/' + formId, null, {headers: this.authService.headers}).pipe(
                tap(() => {
                    this.loadForms();
                }),
                catchError((err: any) => {
                    console.debug(err);
                    this.notify.handleErrors(err);
                    return of(false);
                })
            ).subscribe();
        }
    }

    sortData(sort: Sort) {
        const data = this.forms.slice();
        if (!sort.active || sort.direction === '') {
            this.forms = data;
            return;
        }

        this.forms = data.sort((a: any, b: any) => {
            const isAsc = sort.direction === 'asc';
            switch (sort.active) {
                case 'id': return this.compare(a.id, b.id, isAsc);
                case 'label': return this.compare(a.label, b.label, isAsc);
                case 'default': return this.compare(a.default, b.default, isAsc);
                case 'enabled': return this.compare(a.enabled, b.enabled, isAsc);
                default: return 0;
            }
        });

    }

    compare(a: number | string, b: number | string, isAsc: boolean) {
        return (a < b ? -1 : 1) * (isAsc ? 1 : -1);
    }

}
