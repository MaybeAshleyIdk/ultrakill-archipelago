/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

using System;
using UnityEngine;

namespace ArchipelagoULTRAKILL.Structures
{
    public class ItemDefinition
    {
        public string Name { get; }
        public UKType Type { get; }
        public Func<Color> Color { get; }
        public string Image { get; }

        public ItemDefinition(string name, UKType type, Func<Color> color, string image)
        {
            Name = name;
            Type = type;
            Color = color;
            Image = image;
        }
    }
}
