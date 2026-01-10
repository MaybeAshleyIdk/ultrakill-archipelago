#nullable enable

using Archipelago.MultiClient.Net;
using BepInEx.Logging;

namespace ArchipelagoULTRAKILL.New
{
	internal readonly struct CombinedSlotData
	{
		public readonly SlotData Primitives;
		public readonly StructuredSlotData Structured;

		private CombinedSlotData(SlotData primitives, StructuredSlotData structured)
		{
			this.Primitives = primitives;
			this.Structured = structured;
		}

		public static CombinedSlotData FromLoginResult(LoginSuccessful result, ManualLogSource logger)
		{
			SlotData primitives = SlotData.FromLoginResult(result, logger);
			StructuredSlotData structured = StructuredSlotData.FromLoginResult(result, logger);

			return new CombinedSlotData(primitives, structured);
		}
	}
}
