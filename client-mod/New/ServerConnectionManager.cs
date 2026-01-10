#nullable enable

using Archipelago.MultiClient.Net.Helpers;
using System;
using System.Threading.Tasks;

namespace ArchipelagoULTRAKILL.New
{
	internal interface ServerConnection
	{
		CombinedSlotData SlotData { get; }

		event ReceivedItemsHelper.ItemReceivedHandler ItemReceived;
		event ArchipelagoSocketHelperDelagates.PacketReceivedHandler PacketReceived;

		bool IsOpen();

		Task CloseAsync();
	}

	internal interface ServerConnectionManager
	{
		public interface ConnectResult
		{
			void Visit(Action<ServerConnection> ifSuccess, Action ifFailure);

			public readonly struct Success : ConnectResult
			{
				public readonly ServerConnection ServerConnection;

				public Success(ServerConnection serverConnection)
				{
					this.ServerConnection = serverConnection;
				}

				public void Visit(Action<ServerConnection> ifSuccess, Action ifFailure) =>
					ifSuccess(this.ServerConnection);
			}

			public readonly struct Failure : ConnectResult
			{
				public void Visit(Action<ServerConnection> ifSuccess, Action ifFailure) => ifFailure();
			}
		}

		ServerConnection? Connection { get; }

		Task<ConnectResult> ConnectAsync(string hostname, ushort port, string slotName, string? password);

		Task DisconnectAsync();
	}

	internal static class ServerConnectionManagerExtensions
	{
		public static bool IsConnected(this ServerConnectionManager manager)
		{
			return manager.Connection?.IsOpen() ?? false;
		}
	}
}
