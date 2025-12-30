/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using ArchipelagoULTRAKILL.Components;
using ArchipelagoULTRAKILL.Structures;
using HarmonyLib;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(WeaponCharges), "Charge")]
    public class WeaponCharges_Charge_Patch
    {
        public static void Prefix(ref float amount)
        {
            if (PlayerHelper.CurrentPowerup == Powerup.QuickCharge) amount *= 3;
        }
    }
}
