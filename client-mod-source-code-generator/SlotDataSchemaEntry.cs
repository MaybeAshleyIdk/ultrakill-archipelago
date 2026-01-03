/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

using System;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal interface SlotDataSchemaEntryTypeData
	{
		string DotNetTypeName { get; }
	}

	internal readonly struct SlotDataSchemaEntry
	{
		public readonly SlotDataSchemaEntryTypeData TypeData;

		/// <summary>
		/// May be <c>null</c>.
		/// </summary>
		public readonly string Description;

		public SlotDataSchemaEntry(SlotDataSchemaEntryTypeData typeData, string description)
		{
			if (description == "")
			{
				throw new ArgumentException(
					message: "Slot data schema entry description must not be empty",
					paramName: nameof(description)
				);
			}

			this.TypeData = typeData;
			this.Description = description;
		}
	}

	namespace SlotDataSchemaEntryTypes
	{
		internal readonly struct Bool : SlotDataSchemaEntryTypeData
		{
			public string DotNetTypeName => "bool";
			public readonly bool FallbackValue;

			public Bool(bool fallbackValue)
			{
				this.FallbackValue = fallbackValue;
			}
		}

		internal readonly struct Int32 : SlotDataSchemaEntryTypeData
		{
			public string DotNetTypeName => "int";
			public readonly int MinValue;
			public readonly int MaxValue;
			public readonly int FallbackValue;

			public Int32(int minValue, int maxValue, int fallbackValue)
			{
				this.MinValue = minValue;
				this.MaxValue = maxValue;
				this.FallbackValue = fallbackValue;
			}
		}

		internal readonly struct String : SlotDataSchemaEntryTypeData
		{
			public string DotNetTypeName => "string";
		}
	}
}
