/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using UnityEngine;
using UnityEngine.UI;

namespace ArchipelagoULTRAKILL.New.UI
{
	internal sealed class SecondaryPauseMenuSurface
	{
		public readonly GameObject GameObject;

		private SecondaryPauseMenuSurface(GameObject gameObject)
		{
			this.GameObject = gameObject;
		}

		public readonly struct Data : UiElementData<SecondaryPauseMenuSurface>
		{
			private readonly float width;
			private readonly float height;

			public Data(float width, float height)
			{
				this.width = width;
				this.height = height;
			}

			public SecondaryPauseMenuSurface CreateElementAndAddTo(
				GameObject parent,
				string name,
				float relativeX,
				float relativeY
			)
			{
				var gameObject = new GameObject(name: name);
				gameObject.transform.SetParent(parent.transform);
				gameObject.transform.localPosition = new Vector3(relativeX, relativeY, 0.0f);
				gameObject.transform.localScale = Vector3.one;

				RectTransform rectTransform = gameObject.AddComponent<RectTransform>();
				rectTransform.sizeDelta = new Vector2(this.width, this.height);

				Image image = gameObject.AddComponent<Image>();
				image.sprite = UIManager.menuSprite1;
				image.color = new Color(0.0f, 0.0f, 0.0f, 0.7843f);
				image.pixelsPerUnitMultiplier = 5.0f;
				image.type = Image.Type.Sliced;

				return new SecondaryPauseMenuSurface(gameObject);
			}
		}
	}
}
