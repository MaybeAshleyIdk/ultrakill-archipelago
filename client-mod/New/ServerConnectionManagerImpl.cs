#nullable enable

using Archipelago.MultiClient.Net;
using Archipelago.MultiClient.Net.Enums;
using Archipelago.MultiClient.Net.Helpers;
using BepInEx.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace ArchipelagoULTRAKILL.New
{
	internal sealed class ServerConnectionManagerImpl : ServerConnectionManager
	{
		private sealed class ServerConnectionImpl : ServerConnection
		{
			private ArchipelagoSession? session = null;
			// private

			public CombinedSlotData SlotData { get; }

			public ServerConnectionImpl(ArchipelagoSession session, CombinedSlotData slotData)
			{
				this.session = session;
				this.SlotData = slotData;
			}

			public void Initialize()
			{

			}

			public bool IsOpen()
			{
				return this.session?.Socket?.Connected ?? false;
			}

			public async Task CloseAsync()
			{
				ArchipelagoSession? session = Interlocked.Exchange(ref this.session, null);
				if (session is null) return;

				session

				try
				{
					await session.Socket.DisconnectAsync();
				}
				catch
				{
					Interlocked.CompareExchange(ref this.session, session, null);
					throw;
				}
			}
		}

		private readonly ManualLogSource logger;

		private ServerConnectionImpl? connection = null;

		public ServerConnectionManagerImpl(ManualLogSource logger)
		{
			this.logger = logger;
		}

		public ServerConnection? Connection => this.connection;

		public async Task<ServerConnectionManager.ConnectResult> ConnectAsync(
			string hostname,
			ushort port,
			string slotName,
			string? password
		)
		{
			await this.DisconnectAsync();

			ArchipelagoSession session = ArchipelagoSessionFactory.CreateSession(hostname, port);
			session.Socket.SocketClosed += (string reason) => { };
			session.Socket.ErrorReceived += (Exception e, string message) => { };
			session.Socket.PacketReceived += (ArchipelagoPacketBase packet) => { };
			session.Items.ItemReceived += (ReceivedItemsHelper helper) => { };

			LoginResult result =
				session.TryConnectAndLogin(
					game: "ULTRAKILL",
					name: slotName,
					itemsHandlingFlags: ItemsHandlingFlags.AllItems,
					version: new Version(0, 6, 1),
					tags: null,
					uuid: null,
					password: password,
					requestSlotData: true
				);

			if (!(result is LoginSuccessful successfulResult))
			{
				if (result is LoginFailure failureResult)
				{
					// TODO
				}

				return new ServerConnectionManager.ConnectResult.Failure();
			}

			CombinedSlotData slotData = CombinedSlotData.FromLoginResult(successfulResult, Core.Logger);

			var connection = new ServerConnectionImpl(session, slotData);

			await (Interlocked.Exchange(ref this.connection, connection)?.CloseAsync() ?? Task.CompletedTask);

			return new ServerConnectionManager.ConnectResult.Success(connection);
		}

		public Task DisconnectAsync()
		{
			ServerConnectionImpl? connection = Interlocked.Exchange(ref this.connection, null);
			return connection?.CloseAsync() ?? Task.CompletedTask;
		}
	}
}
