import {Injectable, OnInit} from '@angular/core';
import {TranslateService} from "@ngx-translate/core";
import {LocalStorageService} from "./local-storage.service";
import {LastUrlService} from "./last-url.service";
import {Title} from "@angular/platform-browser";

@Injectable({
    providedIn: 'root'
})

export class SettingsService {
    isMenuOpen: boolean = true;
    selectedSetting: string = "users";
    selectedParentSetting: string = "general";
    settingListOpenState: boolean = true;
    settingsParent: any[] = [
        {
            "id": "general",
            "label": this.translate.instant("SETTINGS.general"),
        },
        {
            "id": "verifier",
            "label": this.translate.instant("SETTINGS.verifier"),
        },
        {
            "id": "splitter",
            "label": this.translate.instant("SETTINGS.splitter"),
        },
    ];
    settings: any = {
        "general": [
            {
                "id"      : "users",
                "label"   : this.translate.instant("SETTINGS.users_list"),
                "icon"    : "fas fa-user",
                "route"   : '/settings/general/users',
                "actions" : [
                    {
                        "id"    : 'users_new',
                        "label" : this.translate.instant("USER.add"),
                        "route" : "/settings/general/users/new",
                        "icon"  : "fas fa-plus"
                    },
                    {
                        "id"    : 'users_new',
                        "label" : this.translate.instant("USER.update"),
                        "route" : "/settings/general/users/update/",
                        "icon"  : "fas fa-edit",
                        "showOnlyIfActive" : true
                    }
                ]
            },
            {
                "id"      : "roles",
                "label"   : this.translate.instant("SETTINGS.roles_list"),
                "icon"    : "fas fa-users",
                "route"   : "/settings/general/roles",
                "actions" : [
                    {
                        "label" : this.translate.instant("ROLE.add"),
                        "route" : "/settings/general/roles/new",
                        "icon"  : "fas fa-plus"
                    }
                ]
            },
            {
                "id": "custom-fields",
                "label": this.translate.instant("SETTINGS.custom_fields"),
                "icon": "fas fa-code",
            },
            {
                "id": "version-update",
                "label": this.translate.instant("SETTINGS.version_and_update"),
                "icon": "fas fa-sync",
            },
            {
                "id": "about-us",
                "label": this.translate.instant("SETTINGS.abouts_us"),
                "icon": "fas fa-address-card",
                "route": "/settings/general/about-us"
            }
        ],
        "verifier": [
            {
                "id"    : "form_builder",
                "label" : this.translate.instant("verifier.form_builder"),
                "icon"  : "fas fa-tools",
                "route" : "/settings/verifier/forms/builder"
            },
        ],
        "splitter": [
            {
                "id": "separator",
                "label": this.translate.instant("SETTINGS.document_separator"),
                "icon": "fas fa-qrcode",
            },
            {
                "id": "document-type",
                "label": this.translate.instant("SETTINGS.document_type"),
                "icon": "fas fa-file",
            },
            {
                "id": "connector",
                "label": this.translate.instant("SETTINGS.connector_EDM"),
                "icon": "fas fa-link",
            }
        ]
    };

    constructor(
        private titleService: Title,
        private translate: TranslateService,
        private routerExtService: LastUrlService,
        private localeStorageService: LocalStorageService
    ) {}

    init(){
        let lastUrl = this.routerExtService.getPreviousUrl()
        if (lastUrl.includes('roles') || lastUrl == '/' || lastUrl.includes('users')){
            let selectedSettings = this.localeStorageService.get('selectedSettings')
            let selectedParentSettings = this.localeStorageService.get('selectedParentSettings')

            if (selectedSettings)
                this.setSelectedSettings(selectedSettings)

            if (selectedParentSettings)
                this.setSelectedParentSettings(selectedParentSettings)
        }else{
            this.localeStorageService.remove('selectedSettings')
            this.localeStorageService.remove('selectedParentSettings')
            this.setSelectedSettings("users")
            this.setSelectedParentSettings('general')
        }
    }

    getTitle(){
        let title = this.titleService.getTitle()
        title = title.split(' - ')[0]
        return title
    }

    changeSetting(settingId: string, settingParentId: string) {
        this.setSelectedSettings(settingId)
        this.setSelectedParentSettings(settingParentId)
        this.localeStorageService.save('selectedSettings', settingId)
        this.localeStorageService.save('selectedParentSettings',settingParentId)
    }

    getIsMenuOpen(){
        return this.isMenuOpen;
    }

    getSelectedSetting(){
        return this.selectedSetting;
    }

    getSelectedParentSetting(){
        return this.selectedParentSetting;
    }

    getSettingListOpenState(){
        return this.settingListOpenState;
    }

    getSettingsParent(){
        return this.settingsParent;
    }

    getSettings(){
        return this.settings;
    }

    getSelectedSettingInfo(value: any){
        let data : any[] = []
        this.settings[this.selectedParentSetting].forEach((element: any) =>{
            if (element['id'] == this.selectedSetting){
                data = element[value]
            }
        })
        return data
    }

    getSettingsAction(setting_id: any){
        let actions = undefined
        this.settings[this.selectedParentSetting].forEach((element: any) =>{
            if (element['id'] == setting_id && element['actions']){
                actions = element['actions']
            }
        })
        return actions
    }

    setIsMenuOpen(value: boolean){
        this.isMenuOpen = value;
    }

    setSelectedSettings(value: string){
        this.selectedSetting = value;
    }

    setSelectedParentSettings(value: string){
        this.selectedParentSetting = value;
    }

    setSettingListOpenState(value: boolean){
        this.settingListOpenState = value;
    }

    toggleMenu() {
        this.isMenuOpen = !this.isMenuOpen;
    }
}
