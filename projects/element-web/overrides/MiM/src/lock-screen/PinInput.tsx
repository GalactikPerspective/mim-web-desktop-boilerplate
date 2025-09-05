import React, { useEffect, useState } from "react";
import AccessibleButton from "../../../src/components/views/elements/AccessibleButton";
import { ArrowLeftIcon, CheckIcon } from "@vector-im/compound-design-tokens/assets/web/icons";

type PinInputProps = {
    onSubmit: (value: string) => void | boolean;
    resetOnTrue?: boolean;
};

function PinInput({ onSubmit, resetOnTrue }: PinInputProps) {
    const [value, setValue] = useState("");

    const handleButtonClick = (num: number) => {
        if (value.length >= 4) return;
        setValue((v) => v + num.toString());
    };

    const handleSubmit = () => {
        if (value.length < 4) return;
        const res = onSubmit(value);
        if (res && resetOnTrue) setValue("");
    };

    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            if (e.key === "Backspace" && value.length > 0) setValue((v) => v.slice(0, -1));
            else if (e.key === "Escape") setValue("");
            else if (["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"].includes(e.key) && value.length < 4)
                setValue((v) => v + e.key);
            else if (e.key === "Enter") handleSubmit();
        };
        window.addEventListener("keydown", handler);
        return () => {
            window.removeEventListener("keydown", handler);
        };
    }, [value]);

    return (
        <div className="mim_PinInput">
            <div className="mim_PinInput_Row">
                {[...Array(4).keys()].map((_, i) => (
                    <div className="mim_PinInput_Dot" data-active={value.length > i} tabIndex={-1} />
                ))}
            </div>
            <div className="mim_PinInput_Row">
                {[...Array(3).keys()]
                    .map((_, i) => i + 1)
                    .map((num) => (
                        <AccessibleButton
                            kind="icon_primary_outline"
                            onClick={() => {
                                handleButtonClick(num);
                            }}
                            tabIndex={-1}
                        >
                            {num}
                        </AccessibleButton>
                    ))}
            </div>
            <div className="mim_PinInput_Row">
                {[...Array(3).keys()]
                    .map((_, i) => i + 4)
                    .map((num) => (
                        <AccessibleButton
                            kind="icon_primary_outline"
                            onClick={() => {
                                handleButtonClick(num);
                            }}
                            tabIndex={-1}
                        >
                            {num}
                        </AccessibleButton>
                    ))}
            </div>
            <div className="mim_PinInput_Row">
                {[...Array(3).keys()]
                    .map((_, i) => i + 7)
                    .map((num) => (
                        <AccessibleButton
                            kind="icon_primary_outline"
                            onClick={() => {
                                handleButtonClick(num);
                            }}
                            tabIndex={-1}
                        >
                            {num}
                        </AccessibleButton>
                    ))}
            </div>
            <div className="mim_PinInput_Row">
                <AccessibleButton
                    disabled={value.length < 4}
                    kind="icon_primary_outline"
                    onClick={() => handleSubmit()}
                    tabIndex={-1}
                >
                    <CheckIcon />
                </AccessibleButton>
                <AccessibleButton
                    kind="icon_primary_outline"
                    onClick={() => {
                        handleButtonClick(0);
                    }}
                    tabIndex={-1}
                >
                    0
                </AccessibleButton>
                <AccessibleButton
                    kind="icon_primary_outline"
                    onClick={() => setValue((v) => v.slice(0, -1))}
                    tabIndex={-1}
                    style={{ ...(value.length === 0 && { visibility: "hidden" }) }}
                >
                    <ArrowLeftIcon />
                </AccessibleButton>
            </div>
        </div>
    );
}

export default PinInput;
