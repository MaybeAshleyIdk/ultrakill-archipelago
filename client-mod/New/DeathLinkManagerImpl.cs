/*
 * Copyright (c) 2025 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using Archipelago.MultiClient.Net;
using Archipelago.MultiClient.Net.BounceFeatures.DeathLink;
using ArchipelagoULTRAKILL.Components;
using ArchipelagoULTRAKILL.New.Utils;
using BepInEx.Logging;
using System.Collections.Generic;
using System.Threading;

namespace ArchipelagoULTRAKILL.New
{
	internal delegate bool CanPlayerBeKilledPredicate();

	internal sealed class DeathLinkManagerImpl : DeathLinkManager
	{
		private sealed class DeathLinkWrapper
		{
			private DeathLink? unwrapped;

			public DeathLinkWrapper(DeathLink unwrapped)
			{
				this.unwrapped = unwrapped;
			}

			public DeathLink? Consume()
			{
				return Interlocked.Exchange(ref this.unwrapped, null);
			}

			public bool IsConsumed()
			{
				return (this.unwrapped is null);
			}
		}

		private sealed class StartedState
		{
			public DeathLinkWrapper? QueuedDeathLink = null;

			public static readonly StartedState Initial = new StartedState();
		}

		private readonly DeathLinkService deathLinkService;
		private readonly CanPlayerBeKilledPredicate canPlayerBeKilled;
		private readonly ManualLogSource logger;

		private StartedState? startedState = StartedState.Initial;

		private DeathLinkManagerImpl(
			DeathLinkService deathLinkService,
			CanPlayerBeKilledPredicate canPlayerBeKilled,
			ManualLogSource logger
		)
		{
			this.deathLinkService = deathLinkService;
			this.canPlayerBeKilled = canPlayerBeKilled;
			this.logger = logger;
		}

		public static DeathLinkManager CreateStarted(
			ArchipelagoSession session,
			CanPlayerBeKilledPredicate canPlayerBeKilled,
			ManualLogSource logger
		)
		{
			DeathLinkService deathLinkService = session.CreateDeathLinkService();

			var manager =
				new DeathLinkManagerImpl(
					deathLinkService,
					canPlayerBeKilled,
					logger
				);

			deathLinkService.OnDeathLinkReceived += manager.QueueDeathLink;
			deathLinkService.EnableDeathLink();

			return manager;
		}

		public DeathLink? ConsumeQueuedDeathLink()
		{
			return this.startedState?.QueuedDeathLink?.Consume();
		}

		public void RemoveQueuedDeathLink()
		{
			StartedState? startedState = this.startedState;
			if (startedState is null) return;

			startedState.QueuedDeathLink = null;
		}

		public void NotifyOfPlayerDeath()
		{
			StartedState? startedState = this.startedState;
			if (startedState is null) return;

			DeathLinkWrapper? queuedDeathLink = startedState.QueuedDeathLink;

			if (!(queuedDeathLink is null) && queuedDeathLink.IsConsumed())
			{
				startedState.QueuedDeathLink = null;
			}
			else
			{
				var deathLink =
					new DeathLink(
						sourcePlayer: Core.data.slot_name,
						cause: DetermineDeathLinkCause()
					);

				string logMsg = "Sending death link " +
					((deathLink.Cause is null) ? "without a cause" : $"with cause {deathLink.Cause.Quoted()}");
				this.logger.LogInfo(logMsg);

				this.deathLinkService.SendDeathLink(deathLink);
			}
		}

		public void Stop()
		{
			StartedState? prevState = Interlocked.Exchange(ref this.startedState, null);
			if (!(prevState is null))
			{
				this.deathLinkService.DisableDeathLink();
			}
		}

		public void Start()
		{
			StartedState? prevState = Interlocked.CompareExchange(ref this.startedState, StartedState.Initial, null);
			if (prevState is null)
			{
				this.deathLinkService.EnableDeathLink();
			}
		}

		private void QueueDeathLink(DeathLink deathLink)
		{
			StartedState? startedState = this.startedState;
			if (startedState is null) return;

			if (!(this.canPlayerBeKilled()))
			{
				string msg = "Received death link (" +
					$"cause={deathLink.Cause.Quoted()}, " +
					$"source={deathLink.Source.Quoted()}, " +
					$"timestamp={deathLink.Timestamp}), " +
					"but the player cannot be killed right now";
				this.logger.LogInfo(msg);

				return;
			}

			if (startedState.QueuedDeathLink?.IsConsumed() == true)
			{
				// Previous death link was consumed but has not yet been removed.
				// Ignore the incoming death link as killing the player two times right after another would be weird.
				return;
			}

			startedState.QueuedDeathLink = new DeathLinkWrapper(unwrapped: deathLink);
		}

		private static string? DetermineDeathLinkCause()
		{
			// ???
			if (Core.uim.deathLinkMessage is null)
			{
				return null;
			}

			List<string> messages =
				DeathLinkMessage.specialMessages.TryGetValue(SceneHelper.CurrentScene, out List<string> missionMessages)
					? missionMessages
					: DeathLinkMessage.deathMessages;

			return string.Format(messages.GetRandomItem(), Core.data.slot_name);
		}
	}
}
