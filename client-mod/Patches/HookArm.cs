/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using ArchipelagoULTRAKILL.Components;
using HarmonyLib;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(HookArm), "Update")]
    public class HookArm_Update_Patch
    {
        public static bool Prefix()
        {
            if (PlayerHelper.CurrentPowerup == Structures.Powerup.NoArms) return false;
            return true;
        }
    }
}
