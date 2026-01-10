/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

using System;
using System.Collections.Immutable;
using System.Linq;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal readonly struct SlotDataEnum : IEquatable<SlotDataEnum>
	{
		public readonly SlotDataEnumName Name;
		public readonly ImmutableList<SlotDataEnumEntryName> EntryNames;

		public SlotDataEnum(SlotDataEnumName name, ImmutableList<SlotDataEnumEntryName> entryNames)
		{
			if (entryNames is null)
			{
				throw new ArgumentNullException(paramName: nameof(entryNames));
			}

			if (entryNames.Count < 1)
			{
				throw new ArgumentException(
					message: "Enum must have at least one entry",
					paramName: nameof(entryNames)
				);
			}

			if (entryNames.ToImmutableHashSet().Count != entryNames.Count)
			{
				throw new ArgumentException(message: "Duplicate enum entries", paramName: nameof(entryNames));
			}

			this.Name = name;
			this.EntryNames = entryNames;
		}

		public bool Equals(SlotDataEnum other)
		{
			return (this.Name == other.Name) && this.EntryNames.SequenceEqual(other.EntryNames);
		}

		public override bool Equals(object obj) => (obj is SlotDataEnum other) && this.Equals(other);

		public override int GetHashCode()
		{
			int hashCode = this.Name.GetHashCode();

			foreach (SlotDataEnumEntryName entryName in this.EntryNames)
			{
				unchecked
				{
					hashCode = (hashCode * 397) ^ entryName.GetHashCode();
				}
			}

			return hashCode;
		}

		public static bool operator ==(SlotDataEnum left, SlotDataEnum right) => left.Equals(right);
		public static bool operator !=(SlotDataEnum left, SlotDataEnum right) => !(left.Equals(right));
	}
}
