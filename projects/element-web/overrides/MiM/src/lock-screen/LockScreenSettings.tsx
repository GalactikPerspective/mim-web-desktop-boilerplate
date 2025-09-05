import React from "react";
import { SettingsSection } from "../../../src/components/views/settings/shared/SettingsSection";
import AccessibleButton from "../../../src/components/views/elements/AccessibleButton";
import { useSettingValue } from "../../../src/hooks/useSettings";
import { parseCode } from "./utils";
import { _t } from "../../../src/languageHandler";
import Modal from "../../../src/Modal";
import SetupPinDialog from "./SetupPinDialog";
import {
    SettingsSubsection,
    SettingsSubsectionText,
} from "../../../src/components/views/settings/shared/SettingsSubsection";
import RemovePinDialog from "./RemovePinDialog";

function LockScreenSettings() {
    const [currentCode] = parseCode(useSettingValue("LockScreen.hiddenCode"));
    let content: React.ReactNode = null;

    if (!currentCode) {
        content = (
            <AccessibleButton
                kind="primary"
                onClick={() => {
                    const { finished, close } = Modal.createDialog(SetupPinDialog);
                    finished.then(() => {
                        close();
                    });
                }}
            >
                {_t("settings|security|lock_screen|configure_button")}
            </AccessibleButton>
        );
    } else {
        content = (
            <>
                <SettingsSubsectionText>
                    <strong>{_t("settings|security|lock_screen|code_set")}</strong>
                </SettingsSubsectionText>
                <AccessibleButton
                    onClick={() => {
                        const { finished, close } = Modal.createDialog(RemovePinDialog);
                        finished.then(() => {
                            close();
                        });
                    }}
                    kind="danger"
                >
                    {_t("settings|security|lock_screen|remove_button")}
                </AccessibleButton>
            </>
        );
    }

    return (
        <SettingsSection heading={_t("settings|security|lock_screen|heading")}>
            <SettingsSubsection heading="Set pin">
                <SettingsSubsectionText>{_t("settings|security|lock_screen|description")}</SettingsSubsectionText>
                {content}
            </SettingsSubsection>
        </SettingsSection>
    );
}

export default LockScreenSettings;
