/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using HarmonyLib;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(DeathSequence), "OnEnable")]
    public class DeathSequence_OnEnable_Patch
    {
        public static void Postfix()
        {
            Multiworld.DeathLinkManager?.NotifyOfPlayerDeath();
        }
    }
}
