/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using HarmonyLib;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(LeaderboardController), "SubmitLevelScore")]
    class LeaderboardController_SubmitLevelScore_Patch
    {
        public static bool Prefix()
        {
            if (Core.DataExists())
            {
                Core.Logger.LogInfo("Current save file is randomized. Skipped leaderboard submission.");
                return false;
            }
            else return true;
        }
    }

    [HarmonyPatch(typeof(LeaderboardController), "SubmitCyberGrindScore")]
    class LeaderboardController_SubmitCyberGrindScore_Patch
    {
        public static bool Prefix()
        {
            if (Core.DataExists())
            {
                Core.Logger.LogInfo("Current save file is randomized. Skipped leaderboard submission.");
                return false;
            }
            else return true;
        }
    }
}
