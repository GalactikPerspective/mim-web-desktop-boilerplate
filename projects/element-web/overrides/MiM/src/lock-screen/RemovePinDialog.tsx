import React, { useEffect, useState } from "react";
import BaseDialog from "../../../src/components/views/dialogs/BaseDialog";
import { useSettingValue } from "../../../src/hooks/useSettings";
import { _t } from "../../../src/languageHandler";
import PinInput from "./PinInput";
import dispatcher from "../../../src/dispatcher/dispatcher";
import { DEFAULT_ATTEMPTS, encodeCode, parseCode } from "./utils";
import SettingsStore from "../../../src/settings/SettingsStore";
import { SettingLevel } from "../../../src/settings/SettingLevel";

type RemoveStages = "initial" | "success";

type RemovePinDialogProps<T> = {
    onFinished(success?: boolean, result?: T | Error | null): void;
};

function RemovePinDialog<T>({ onFinished }: RemovePinDialogProps<T>) {
    const [stage, setStage] = useState<RemoveStages>("initial");
    const [code, remainingAttempts] = parseCode(useSettingValue("LockScreen.hiddenCode"));

    const checkResponse = (submittedCode: string) => {
        const match = submittedCode === code;
        if (match) {
            SettingsStore.setValue("LockScreen.hiddenCode", null, SettingLevel.DEVICE, "");
            setStage("success");
        } else {
            SettingsStore.setValue(
                "LockScreen.hiddenCode",
                null,
                SettingLevel.DEVICE,
                encodeCode(code, remainingAttempts - 1),
            );
        }
        return true;
    };

    useEffect(() => {
        if (remainingAttempts > 0) return;
        // TODO: logout ??
        dispatcher.dispatch({ action: "logout" });
    }, [remainingAttempts]);

    let content = null;
    switch (stage) {
        case "initial":
            content = (
                <div className="mim_RemovePinDialog_Container">
                    <h4>{_t("settings|security|lock_screen|remove_pin_dialog|body")}</h4>
                    <div>
                        <PinInput onSubmit={checkResponse} resetOnTrue />
                        <h4
                            className="mim_LockScreen_AttemptsWarning"
                            style={{ visibility: remainingAttempts < DEFAULT_ATTEMPTS ? undefined : "hidden" }}
                        >
                            {_t("settings|security|lock_screen|remaining_attempts_warning", { remainingAttempts })}
                        </h4>
                    </div>
                </div>
            );
            break;
        case "success":
            content = _t("settings|security|lock_screen|remove_pin_dialog|success");
    }

    return (
        <BaseDialog title={_t("settings|security|lock_screen|remove_pin_dialog|title")} onFinished={onFinished}>
            {content}
        </BaseDialog>
    );
}

export default RemovePinDialog;
