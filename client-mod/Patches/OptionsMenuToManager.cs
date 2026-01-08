/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using ArchipelagoULTRAKILL.New;
using ArchipelagoULTRAKILL.New.UI;
using HarmonyLib;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(OptionsMenuToManager), "SetPauseMenu")]
    public class OptionsMenuToManager_SetPauseMenu_Patch
    {
        public static void Postfix(OptionsMenuToManager __instance)
        {
            if (Core.DataExists())
            {
                if (Core.IsInLevel && !(SceneId.MainMenu.IsCurrent()))
                {
#nullable enable
                    PauseMenuElementsManager.InitializeElements(Multiworld.DeathLinkManager, __instance.pauseMenu);
#nullable restore

                    UIManager.CreatePauseRecents(__instance.pauseMenu);
                }

                if (Core.CurrentLevelHasSkulls) UIManager.CreatePauseSkullIcons(__instance.pauseMenu);
                if (Core.CurrentLevelHasSwitches) UIManager.CreatePauseSwitchIcons(__instance.pauseMenu);
            }
        }
    }
}
