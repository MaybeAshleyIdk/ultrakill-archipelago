/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using Archipelago.MultiClient.Net;
using Archipelago.MultiClient.Net.BounceFeatures.DeathLink;
using ArchipelagoULTRAKILL.Components;
using ArchipelagoULTRAKILL.New.Utils;
using BepInEx.Logging;
using System;
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
			public readonly int DeathLinkThreshold;

			public DeathLinkWrapper? QueuedDeathLink = null;
			public int NonDeathLinkPlayerDeathsCount = 0;

			public StartedState(int deathLinkThreshold)
			{
				this.DeathLinkThreshold = deathLinkThreshold;
			}
		}

		private readonly DeathLinkService deathLinkService;
		private readonly CanPlayerBeKilledPredicate canPlayerBeKilled;
		private readonly ManualLogSource logger;

		private StartedState? startedState;

		private DeathLinkManagerImpl(
			DeathLinkService deathLinkService,
			CanPlayerBeKilledPredicate canPlayerBeKilled,
			int deathLinkThreshold,
			ManualLogSource logger
		)
		{
			this.deathLinkService = deathLinkService;
			this.canPlayerBeKilled = canPlayerBeKilled;
			this.logger = logger;

			this.startedState = new StartedState(deathLinkThreshold);
		}

		public static DeathLinkManager CreateStarted(
			ArchipelagoSession session,
			CanPlayerBeKilledPredicate canPlayerBeKilled,
			int deathLinkThreshold,
			ManualLogSource logger
		)
		{
			if (deathLinkThreshold < 1)
			{
				throw new ArgumentException(
					message: "Death link threshold must be greater than or equal to 1",
					paramName: nameof(deathLinkThreshold)
				);
			}

			DeathLinkService deathLinkService = session.CreateDeathLinkService();

			var manager =
				new DeathLinkManagerImpl(
					deathLinkService,
					canPlayerBeKilled,
					deathLinkThreshold,
					logger
				);

			deathLinkService.OnDeathLinkReceived += manager.QueueDeathLink;
			deathLinkService.EnableDeathLink();

			return manager;
		}

		public DeathLinkManager.Status? GetStatus()
		{
			StartedState? startedState = this.startedState;
			if (startedState is null) return null;

			return new DeathLinkManager.Status(
				deathLinkThreshold: startedState.DeathLinkThreshold,
				nonDeathLinkPlayerDeathsCount: startedState.NonDeathLinkPlayerDeathsCount
			);
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
				this.UpdateNonDeathLinkPlayerDeathsCount(startedState);
			}
		}

		public void ResetAndStop()
		{
			StartedState? prevState = Interlocked.Exchange(ref this.startedState, null);
			if (!(prevState is null))
			{
				this.deathLinkService.DisableDeathLink();
			}
		}

		public void Start(int deathLinkThreshold)
		{
			if (deathLinkThreshold < 1)
			{
				throw new ArgumentException(
					message: "Death link threshold must be greater than or equal to 1",
					paramName: nameof(deathLinkThreshold)
				);
			}

			StartedState? prevState = Interlocked.Exchange(ref this.startedState, new StartedState(deathLinkThreshold));
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

		private void UpdateNonDeathLinkPlayerDeathsCount(StartedState startedState)
		{
			int nonDeathLinkPlayerDeathsCount =
				Interlocked.Increment(ref startedState.NonDeathLinkPlayerDeathsCount);

			if (nonDeathLinkPlayerDeathsCount < startedState.DeathLinkThreshold)
			{
				return;
			}

			while (true)
			{
				int prevValue =
					Interlocked.CompareExchange(
						ref startedState.NonDeathLinkPlayerDeathsCount,
						nonDeathLinkPlayerDeathsCount % startedState.DeathLinkThreshold,
						nonDeathLinkPlayerDeathsCount
					);

				if (prevValue == nonDeathLinkPlayerDeathsCount)
				{
					break;
				}
			}

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

		private static string? DetermineDeathLinkCause()
		{
			// ???
			if (Core.uim.deathLinkMessage is null)
			{
				return null;
			}

			List<string> messages =
				DeathLinkMessage.specialMessages.TryGetValue(CurrentScene.Id, out List<string> missionMessages)
					? missionMessages
					: DeathLinkMessage.deathMessages;

			return string.Format(messages.GetRandomItem(), Core.data.slot_name);
		}
	}
}
