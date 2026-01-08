/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using ArchipelagoULTRAKILL.Components;
using ArchipelagoULTRAKILL.New;
using ArchipelagoULTRAKILL.Structures;
using HarmonyLib;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(FinalDoorOpener), "GoTime")]
    public class FinalDoorOpener_GoTime_Patch
    {
        public static void Prefix()
        {
            if (Core.DataExists())
            {
                SceneId currentSceneId = CurrentScene.Id;
                //if (Core.data.musicRandomizer && Core.CurrentLevelHasInfo && Core.CurrentLevelInfo.Music == MusicType.Special2) AudioManager.ChangeMusic();
                if (PlayerHelper.Instance && !currentSceneId.IsSecretMission() && !(currentSceneId == SceneId.DeveloperMuseum || currentSceneId == SceneId.Sandbox)) PlayerHelper.Instance.CanGetPowerup = true;
            }
        }
    }
}
