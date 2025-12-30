/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using UnityEngine;

namespace ArchipelagoULTRAKILL.Components
{
    public class ChapterSelectState : MonoBehaviour
    {
        private void OnDisable()
        {
            if (Core.DataExists())
            {
                Core.Logger.LogInfo("Chapter Select inactive. Updating levels.");
                UIManager.UpdateLevels();
            }
            UIManager.actStats?.gameObject.SetActive(false);
        }
    }
}
