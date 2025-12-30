/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using HarmonyLib;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(GearCheckEnabler), "Start")]
    public class GearCheckEnabler_Start_Patch
    {
        public static bool Prefix(GearCheckEnabler __instance)
        {
            if (Core.DataExists() && __instance.gear == "revalt") return false;
            else return true;
        }
    }
}
