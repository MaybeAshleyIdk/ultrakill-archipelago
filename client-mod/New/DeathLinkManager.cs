/*
 * Copyright (c) 2025 MaybeAshleyIdk
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

		public void Stop();
		public void Start();
	}
}
