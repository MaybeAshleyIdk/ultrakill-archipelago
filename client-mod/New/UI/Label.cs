/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using TMPro;
using UnityEngine;

namespace ArchipelagoULTRAKILL.New.UI
{
	internal sealed class Label
	{
		private readonly TextMeshProUGUI component;

		private Label(TextMeshProUGUI component)
		{
			this.component = component;
		}

		public void SetText(string text)
		{
			this.component.text = text;
		}

		public readonly struct Data : UiElementData<Label>
		{
			private readonly float fontSize;
			private readonly string initialText;

			public Data(float fontSize, string initialText)
			{
				this.fontSize = fontSize;
				this.initialText = initialText;
			}

			public Label CreateElementAndAddTo(GameObject parent, string name, float relativeX, float relativeY)
			{
				var gameObject = new GameObject(name);
				gameObject.transform.SetParent(parent.transform);
				gameObject.transform.localPosition = new Vector3(relativeX, relativeY, 0.0f);
				gameObject.transform.localScale = Vector3.one;

				TextMeshProUGUI component = gameObject.AddComponent<TextMeshProUGUI>();
				component.font = UIManager.fontMain;
				component.fontSize = this.fontSize;
				component.alignment = TextAlignmentOptions.Center;
				component.text = this.initialText;

				return new Label(component);
			}
		}
	}
}
