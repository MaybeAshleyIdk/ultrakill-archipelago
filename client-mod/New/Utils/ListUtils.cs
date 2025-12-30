/*
 * Copyright (c) 2025 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using System.Collections.Generic;
using UnityEngine;

namespace ArchipelagoULTRAKILL.New.Utils
{
	public static class ListUtils
	{
		public static T GetRandomItem<T>(this List<T> list)
		{
			int index = Random.Range(0, list.Count);
			return list[index];
		}
	}
}
