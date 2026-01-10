/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

using System;
using System.Collections.Immutable;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal readonly struct SlotDataSchema
	{
		public readonly ImmutableDictionary<string, SlotDataSchemaEntry> Entries;

		public SlotDataSchema(ImmutableDictionary<string, SlotDataSchemaEntry> entries)
		{
			this.Entries = entries ?? throw new ArgumentNullException(paramName: nameof(entries));
		}
	}
}
