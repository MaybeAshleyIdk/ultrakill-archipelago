/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using ArchipelagoULTRAKILL.Components;
using ArchipelagoULTRAKILL.New;
using HarmonyLib;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(Punch), "PunchStart")]
    public class Punch_PunchStart_Patch
    {
        public static bool Prefix(Punch __instance)
        {
            if (PlayerHelper.CurrentPowerup == Structures.Powerup.NoArms
                || !Core.data.hasArm && __instance.type == FistType.Standard && !(SceneId.MissionWrathS.IsCurrent()))
                return false;
            return true;
        }
    }
}
