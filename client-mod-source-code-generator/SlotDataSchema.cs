/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Linq;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal readonly struct SlotDataSchema
	{
		public readonly ImmutableList<SlotDataEnum> Enums;
		public readonly ImmutableDictionary<string, SlotDataSchemaEntry> Entries;

		public SlotDataSchema(
			ImmutableList<SlotDataEnum> enums,
			ImmutableDictionary<string, SlotDataSchemaEntry> entries
		)
		{
			this.Enums = enums ?? throw new ArgumentNullException(paramName: nameof(enums));
			this.Entries = entries ?? throw new ArgumentNullException(paramName: nameof(entries));
		}
	}
}
