import React from "react";
import type { ReactNode } from "react";
import classNames from "classnames";

import AccessibleButton from "../../src/components/views/elements/AccessibleButton";
import ContextMenu, {
    alwaysAboveRightOf,
    ChevronFace,
    useContextMenu,
} from "../../src/components/structures/ContextMenu";
import { _t } from "../../src/languageHandler";
import SdkConfig from "../../src/SdkConfig";

type ToolbarProps = {
    isPanelCollapsed?: boolean;
};

function Toolbar({ isPanelCollapsed }: ToolbarProps) {
    const [menuDisplayed, handle, openMenu, closeMenu] = useContextMenu<HTMLDivElement>();
    const buttons = SdkConfig.get().toolbar_items ?? [];

    if (buttons.length === 0) return null;

    let contextMenu: ReactNode = null;
    if (menuDisplayed && handle.current) {
        contextMenu = (
            <ContextMenu
                {...alwaysAboveRightOf(handle.current.getBoundingClientRect(), ChevronFace.None, 16)}
                wrapperClassName="mim_ToolbarButton_ContextMenuWrapper"
                onFinished={closeMenu}
                managed={false}
                focusLock={true}
            >
                <h2>{_t("toolbar|title")}</h2>
                {buttons.map(({ label, url }) => (
                    <AccessibleButton
                        key={label}
                        kind="primary_outline"
                        onClick={() => {
                            closeMenu();
                            window.open(url, "_blank")?.focus();
                        }}
                    >
                        {label}
                    </AccessibleButton>
                ))}
            </ContextMenu>
        );
    }

    return (
        <>
            <AccessibleButton
                ref={handle}
                onClick={openMenu}
                title={isPanelCollapsed ? _t("toolbar|title") : undefined}
                className={classNames("mim_ToolbarButton", { expanded: !isPanelCollapsed })}
                aria-label={_t("toolbar|title")}
                aria-expanded={!isPanelCollapsed}
            >
                {isPanelCollapsed ? null : _t("toolbar|title")}
            </AccessibleButton>
            {contextMenu}
        </>
    );
}

export default Toolbar;
