import React from "react";
import { useCallback, useEffect, useRef, useState, type PropsWithChildren } from "react";
import SettingsStore from "../../../src/settings/SettingsStore";
import PinInput from "./PinInput";
import { parseCode, encodeCode, DEFAULT_ATTEMPTS } from "./utils";
import { useSettingValue } from "../../../src/hooks/useSettings";
import { SettingLevel } from "../../../src/settings/SettingLevel";
import dispatcher from "../../../src/dispatcher/dispatcher";
import Modal from "../../../src/Modal";
import { _t } from "../../../src/languageHandler";

type LockScreenProps = PropsWithChildren;

const TIMEOUT_TIME = 2 * 60 * 1000;

const EVENTS: (keyof WindowEventMap)[] = ["mousemove", "mousedown", "resize", "keydown", "touchstart", "wheel"];

function LockScreenProvider({ children }: LockScreenProps) {
    const [code, remainingAttempts] = parseCode(useSettingValue("LockScreen.hiddenCode"));
    const [locked, setLocked] = useState(!!code);
    const timeout = useRef<ReturnType<typeof setTimeout>>(null);

    const checkResponse = (submittedCode: string) => {
        const match = submittedCode === code;
        let newAttempts = remainingAttempts;
        if (match) {
            setLocked(false);
            newAttempts = DEFAULT_ATTEMPTS;
        } else {
            newAttempts -= 1;
        }
        SettingsStore.setValue("LockScreen.hiddenCode", null, SettingLevel.DEVICE, encodeCode(code, newAttempts));
        return true;
    };

    const resetTimer = useCallback(() => {
        if (timeout.current) clearTimeout(timeout.current);
        timeout.current = setTimeout(() => setLocked(!!SettingsStore.getValue("LockScreen.hiddenCode")), TIMEOUT_TIME);
    }, []);

    useEffect(() => {
        // Set it on start
        resetTimer();

        // Set the handlers
        EVENTS.forEach((ev) => window.addEventListener(ev, resetTimer));
        return () => {
            EVENTS.forEach((ev) => window.removeEventListener(ev, resetTimer));
        };
    }, []);

    useEffect(() => {
        if (!locked || !code) return;
        Modal.forceCloseAllModals();
    }, [locked]);

    useEffect(() => {
        if (remainingAttempts > 0) return;
        // TODO: logout ??
        dispatcher.dispatch({ action: "logout" });
    }, [remainingAttempts]);

    if (code && locked)
        return (
            <div className="mim_LockScreen_Container">
                <div className="mim_LockScreen_Content">
                    <PinInput onSubmit={checkResponse} resetOnTrue />
                    <h5
                        className="mim_LockScreen_AttemptsWarning"
                        style={{ visibility: remainingAttempts < DEFAULT_ATTEMPTS ? undefined : "hidden" }}
                    >
                        {_t("settings|security|lock_screen|remaining_attempts_warning", { remainingAttempts })}
                    </h5>
                </div>
            </div>
        );
    return children;
}

export default LockScreenProvider;
