/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using ArchipelagoULTRAKILL.New.Utils;
using UnityEngine;

namespace ArchipelagoULTRAKILL.New.UI
{
	internal static class PauseMenuElementsManager
	{
		private sealed class Component : MonoBehaviour
		{
			private DeathLinkManager? deathLinkManager = null;
			private DeathLinkSurface? deathLinkSurface = null;

			public void SetFields(DeathLinkManager? deathLinkManager, DeathLinkSurface deathLinkSurface)
			{
				this.deathLinkManager = deathLinkManager;
				this.deathLinkSurface = deathLinkSurface;
			}

			private void OnEnable()
			{
				DeathLinkManager.Status? deathLinkManagerStatus = this.deathLinkManager?.GetStatus();
				this.deathLinkSurface?.GameObject.SetActive(MustShowDeathLinkSurface(deathLinkManagerStatus));
			}

			private static bool MustShowDeathLinkSurface(DeathLinkManager.Status? deathLinkManagerStatus)
			{
				if (deathLinkManagerStatus is null) return false;
				return deathLinkManagerStatus.Value.DeathLinkThreshold > 1;
			}
		}

		private static DeathLinkSurface? globalDeathLinkSurface = null;

		public static void InitializeElements(DeathLinkManager? deathLinkManager, GameObject pauseMenu)
		{
			RectTransform? pauseMenuRectTransform = pauseMenu.GetComponent<RectTransform>();
			float pauseMenuHeight = !(pauseMenuRectTransform is null) ? (pauseMenuRectTransform.sizeDelta.y) : 400.0f;

			DeathLinkSurface? deathLinkSurface = globalDeathLinkSurface;
			if (deathLinkSurface?.GameObject.IsNotNullAndAttached() != true)
			{
				float y = 0;
				y += pauseMenuHeight / 2.0f;
				y += DeathLinkSurface.Height / 2.0f;
				y += 15.0f;

				deathLinkSurface = pauseMenu
					.AddChild(
						name: "Death Link Surface",
						relativeX: 0,
						relativeY: y,
						new DeathLinkSurface.Data(
							deathLinkManager: deathLinkManager
						)
					);

				globalDeathLinkSurface = deathLinkSurface;
			}
			else
			{
				deathLinkSurface.SetDeathLinkManager(deathLinkManager);
			}

			Component component = pauseMenu.GetOrAddComponent<Component>();
			component.SetFields(deathLinkManager, deathLinkSurface);
		}
	}
}
