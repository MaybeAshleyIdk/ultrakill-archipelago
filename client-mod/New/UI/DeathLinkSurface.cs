/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using UnityEngine;

namespace ArchipelagoULTRAKILL.New.UI
{
	internal sealed class DeathLinkSurface
	{
		public const float Height = 48;

		private sealed class Component : MonoBehaviour
		{
			private DeathLinkManager? deathLinkManager = null;
			private Label? label = null;

			public void SetFields(DeathLinkManager? deathLinkManager, Label label)
			{
				this.deathLinkManager = deathLinkManager;
				this.label = label;
			}

			public void SetDeathLinkManager(DeathLinkManager? deathLinkManager)
			{
				this.deathLinkManager = deathLinkManager;
			}

			private void OnEnable()
			{
				Label? label = this.label;
				if (label is null) return;

				DeathLinkManager.Status? status = this.deathLinkManager?.GetStatus();
				label.SetText(DetermineTextFromStatus(status));
			}
		}

		public readonly GameObject GameObject;

		private DeathLinkSurface(GameObject gameObject)
		{
			this.GameObject = gameObject;
		}

		public void SetDeathLinkManager(DeathLinkManager? deathLinkManager)
		{
			Component component = this.GameObject.GetOrAddComponent<Component>();
			component.SetDeathLinkManager(deathLinkManager);
		}

		private static string DetermineTextFromStatus(DeathLinkManager.Status? status)
		{
			string nonDeathLinkPlayerDeathsCount;
			string deathLinkThreshold;
			if (!(status is null))
			{
				nonDeathLinkPlayerDeathsCount = status.Value.NonDeathLinkPlayerDeathsCount.ToString();
				deathLinkThreshold = status.Value.DeathLinkThreshold.ToString();
			}
			else
			{
				nonDeathLinkPlayerDeathsCount = "?";
				deathLinkThreshold = "?";
			}

			return $"DEATH LINK: {nonDeathLinkPlayerDeathsCount} / {deathLinkThreshold}";
		}

		public readonly struct Data : UiElementData<DeathLinkSurface>
		{
			private readonly DeathLinkManager? deathLinkManager;

			public Data(DeathLinkManager? deathLinkManager)
			{
				this.deathLinkManager = deathLinkManager;
			}

			public DeathLinkSurface CreateElementAndAddTo(
				GameObject parent,
				string name,
				float relativeX,
				float relativeY
			)
			{
				SecondaryPauseMenuSurface surface = parent
					.AddChild(
						name: name,
						relativeX: relativeX,
						relativeY: relativeY,
						new SecondaryPauseMenuSurface.Data(
							width: 224,
							height: Height
						)
					);

				Label label = surface.GameObject
					.AddChild(
						name: $"{name} - Label",
						relativeX: 0.0f,
						relativeY: 0.0f,
						new Label.Data(
							fontSize: 18.0f,
							initialText: DetermineTextFromStatus(this.deathLinkManager?.GetStatus())
						)
					);

				Component component = surface.GameObject.AddComponent<Component>();
				component.SetFields(this.deathLinkManager, label);

				return new DeathLinkSurface(surface.GameObject);
			}
		}
	}
}
