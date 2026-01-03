/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using Archipelago.MultiClient.Net.BounceFeatures.DeathLink;

namespace ArchipelagoULTRAKILL.New
{
	public interface DeathLinkManager
	{
		public DeathLink? ConsumeQueuedDeathLink();
		public void RemoveQueuedDeathLink();

		public void NotifyOfPlayerDeath();

		public void ResetAndStop();
		public void Start(int deathLinkThreshold);
	}
}
