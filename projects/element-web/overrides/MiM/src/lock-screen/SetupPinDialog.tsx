import React, { useState } from "react";
import BaseDialog from "../../../src/components/views/dialogs/BaseDialog";
import { _t } from "../../../src/languageHandler";
import PinInput from "./PinInput";
import SettingsStore from "../../../src/settings/SettingsStore";
import { SettingLevel } from "../../../src/settings/SettingLevel";
import { encodeCode } from "./utils";

type SetupStages = "initial" | "confirm" | "success";

type SetupPinDialogProps<T> = {
    onFinished(success?: boolean, result?: T | Error | null): void;
};

function SetupPinDialog<T>({ onFinished }: SetupPinDialogProps<T>) {
    const [stage, setStage] = useState<SetupStages>("initial");
    const [currentPin, setCurrentPin] = useState("");
    const [hasError, setHasError] = useState(false);

    let content = null;
    switch (stage) {
        case "initial":
            content = (
                <div className="mim_SetupPinDialog_Column">
                    <div>
                        <h4>{_t("settings|security|lock_screen|setup_pin_dialog|initial")}</h4>
                        <h4>{_t("settings|security|lock_screen|setup_pin_dialog|initial_warning")}</h4>
                        {hasError && (
                            <h3 className="mim_SetupPinDialog_Incorrect">
                                {_t("settings|security|lock_screen|setup_pin_dialog|incorrect")}
                            </h3>
                        )}
                    </div>
                    <PinInput
                        onSubmit={(v) => {
                            setCurrentPin(v);
                            setStage("confirm");
                            setHasError(false);
                            return true;
                        }}
                        resetOnTrue
                    />
                </div>
            );
            break;
        case "confirm":
            content = (
                <div className="mim_SetupPinDialog_Column">
                    <h4>{_t("settings|security|lock_screen|setup_pin_dialog|confirm")}</h4>
                    <PinInput
                        onSubmit={(v) => {
                            if (v === currentPin) {
                                SettingsStore.setValue(
                                    "LockScreen.hiddenCode",
                                    null,
                                    SettingLevel.DEVICE,
                                    encodeCode(v),
                                );
                                setStage("success");
                                return true;
                            }
                            setCurrentPin("");
                            setStage("initial");
                            setHasError(true);
                            return true;
                        }}
                        resetOnTrue
                    />
                </div>
            );
            break;
        case "success":
            content = _t("settings|security|lock_screen|setup_pin_dialog|success");
    }

    return (
        <BaseDialog title={_t("settings|security|lock_screen|setup_pin_dialog|title")} onFinished={onFinished}>
            {content}
        </BaseDialog>
    );
}

export default SetupPinDialog;
