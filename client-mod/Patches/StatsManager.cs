/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using HarmonyLib;

namespace ArchipelagoULTRAKILL.Patches
{
    // send check when touching a secret
    [HarmonyPatch(typeof(StatsManager), "SecretFound")]
    class StatsManager_SecretFound_Patch
    {
        public static bool Prefix(int i)
        {
            if (!AssistController.Instance.cheatsEnabled)
            {
                if (Core.DataExists()) LocationManager.CheckLocation(StatsManager.Instance.levelNumber.ToString() + "_s" + (i + 1));
                return true;
            }
            else return false;
        }
    }
}
