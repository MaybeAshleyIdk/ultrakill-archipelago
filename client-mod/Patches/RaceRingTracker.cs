/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using HarmonyLib;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(RaceRingTracker), "Victory")]
    public class RaceRingTracker_Victory_Patch
    {
        public static void Postfix()
        {
            if (Core.DataExists() && Core.data.rocketReward) LocationManager.CheckLocation("rr");
        }
    }
}