/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using HarmonyLib;
using UnityEngine;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(ShopZone), "TurnOff")]
    public class ShopZone_TurnOff_Patch
    {
        public static void Postfix()
        {
            if (Core.DataExists()) Core.ValidateArms();
        }
    }
}
