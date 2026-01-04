/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using UnityEngine;

namespace ArchipelagoULTRAKILL.New.UI
{
	internal interface UiElementData<out TElement>
	{
		TElement CreateElementAndAddTo(
			GameObject parent,
			string name,
			float relativeX,
			float relativeY
		);
	}

	internal static class UiElementDataExtensions
	{
		public static TElement AddChild<TElement>(
			this GameObject parent,
			string name,
			float relativeX,
			float relativeY,
			UiElementData<TElement> childData
		)
		{
			return childData.CreateElementAndAddTo(parent, name, relativeX, relativeY);
		}
	}
}
