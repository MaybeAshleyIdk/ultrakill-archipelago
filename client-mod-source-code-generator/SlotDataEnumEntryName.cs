/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

using System;
using System.Text.RegularExpressions;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal readonly struct SlotDataEnumEntryName : IEquatable<SlotDataEnumEntryName>
	{
		private static readonly Regex NamePattern = new Regex("^[a-z](_?[a-z0-9]+)*$");

		private readonly string nameString;
		private SlotDataEnumEntryName(string nameString) => this.nameString = nameString;

		public bool Equals(SlotDataEnumEntryName other) => this.nameString == other.nameString;

		public override bool Equals(object obj) =>
			(obj is SlotDataEnumEntryName otherEnumName) && this.Equals(otherEnumName);

		public override int GetHashCode() => this.nameString.GetHashCode();
		public override string ToString() => this.nameString;

		public static bool operator ==(SlotDataEnumEntryName left, SlotDataEnumEntryName right) => left.Equals(right);

		public static bool operator !=(SlotDataEnumEntryName left, SlotDataEnumEntryName right) =>
			!(left.Equals(right));

		public static SlotDataEnumEntryName? OfString(string nameString)
		{
			return NamePattern.IsMatch(nameString)
				? (new SlotDataEnumEntryName(nameString) as SlotDataEnumEntryName?)
				: null;
		}
	}

	internal static class EnumEntryNameExtensions
	{
		public static SlotDataEnumEntryName? ToEnumEntryNameOrNull(this string nameString) =>
			SlotDataEnumEntryName.OfString(nameString);
	}
}
