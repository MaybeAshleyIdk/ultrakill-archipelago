/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using ArchipelagoULTRAKILL.Components;
using ArchipelagoULTRAKILL.New;
using ArchipelagoULTRAKILL.Structures;
using HarmonyLib;
using UnityEngine;

namespace ArchipelagoULTRAKILL.Patches
{
    [HarmonyPatch(typeof(PlayerActivatorRelay), "Activate")]
    class PlayerActivatorRelay_Activate_Patch
    {
        public static void Postfix()
        {
            if (Core.DataExists() && PlayerHelper.Instance == null)
            {
                NewMovement.Instance.gameObject.AddComponent<PlayerHelper>().Init(NewMovement.Instance);

                SceneId currentSceneId = CurrentScene.Id;

                if (currentSceneId == SceneId.MissionPrelude1) Core.obj.AddComponent<FirstLevelSetup>();

                if ((currentSceneId == SceneId.MissionLimbo1 || currentSceneId == SceneId.MissionLimbo2
                    || currentSceneId == SceneId.MissionLimbo3 || currentSceneId == SceneId.MissionGreed4
                    || currentSceneId == SceneId.MissionWrath2 || currentSceneId == SceneId.MissionWrath3
                    || currentSceneId == SceneId.MissionHeresy1 || currentSceneId == SceneId.MissionLimboE)
                    && Core.data.randomizeSkulls)
                    LevelManager.AddDoorClosers();

                if (currentSceneId == SceneId.MissionLimboE && Core.data.randomizeSkulls)
                {
                    LevelManager.redDoor = GameObject.Find("Door (Large) With Controllers (3)/Door (Large)/").GetComponent<Door>();
                    if (!Core.data.unlockedSkulls.Contains("101_r")) LevelManager.redDoor.Close(true);
                }

                if ((currentSceneId.IsMission() || currentSceneId == SceneId.CyberGrind)
                    && currentSceneId != SceneId.MissionWrathS)
                    Core.ValidateArms();

                if (currentSceneId == SceneId.MissionWrathS) LevelManager.ForceBlueArm();

                if (Core.CurrentLevelHasInfo && Core.CurrentLevelInfo.Skulls >= SkullsType.Normal && Core.data.randomizeSkulls)
                    LevelManager.FindSkulls();

                if (Core.data.deathLink && Core.uim.deathLinkMessage == null) Core.uim.CreateDeathLinkMessage();
            }
            //if (LocationManager.messages.Count > 0 && !UIManager.displayingMessage) Core.uim.StartCoroutine("DisplayMessage");
        }
    }
}
