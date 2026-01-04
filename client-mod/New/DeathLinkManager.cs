/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using Archipelago.MultiClient.Net.BounceFeatures.DeathLink;
using System;

namespace ArchipelagoULTRAKILL.New
{
	public interface DeathLinkManager
	{
		public readonly struct Status
		{
			public readonly int DeathLinkThreshold;
			public readonly int NonDeathLinkPlayerDeathsCount;

			public Status(int deathLinkThreshold, int nonDeathLinkPlayerDeathsCount)
			{
				if (deathLinkThreshold < 1)
				{
					throw new ArgumentException(
						message: "Death link threshold must be greater than or equal to 1",
						paramName: nameof(deathLinkThreshold)
					);
				}

				if (nonDeathLinkPlayerDeathsCount < 0)
				{
					throw new ArgumentException(
						message: "Non-death link player deaths count must be greater than or equal to zero",
						paramName: nameof(nonDeathLinkPlayerDeathsCount)
					);
				}

				this.DeathLinkThreshold = deathLinkThreshold;
				this.NonDeathLinkPlayerDeathsCount = nonDeathLinkPlayerDeathsCount;
			}
		}

		/// <summary>
		/// Returns <c>null</c> if the manager is currently stopped.
		/// </summary>
		public Status? GetStatus();

		public DeathLink? ConsumeQueuedDeathLink();
		public void RemoveQueuedDeathLink();

		public void NotifyOfPlayerDeath();

		public void ResetAndStop();
		public void Start(int deathLinkThreshold);
	}
}
