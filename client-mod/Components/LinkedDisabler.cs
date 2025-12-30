/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using System.Collections.Generic;
using UnityEngine;

namespace ArchipelagoULTRAKILL.Components
{
    public class LinkedDisabler : MonoBehaviour
    {
        public List<GameObject> objects = new List<GameObject>();

        public void OnDisable()
        {
            foreach (GameObject obj in objects)
            {
                obj.SetActive(false);
            }
        }
    }
}
