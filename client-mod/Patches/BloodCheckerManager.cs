/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using HarmonyLib;
using UnityEngine;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(BloodCheckerManager), "IsRoomCompleted")]
    public class BloodCheckerManager_IsRoomCompleted_Patch
    {
        public static void Postfix(BloodCheckerManager __instance, GameObject roomToCheck, bool __result)
        {
            if (Core.DataExists() && Core.data.cleanRewards && __result)
            {
                int num = __instance.trackedRooms.IndexOf(roomToCheck);
                LocationManager.CheckLocation($"clean{num}");
            }
        }
    }
}
