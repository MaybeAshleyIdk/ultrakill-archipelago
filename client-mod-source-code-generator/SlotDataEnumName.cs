/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

using System;
using System.Text.RegularExpressions;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal readonly struct SlotDataEnumName : IEquatable<SlotDataEnumName>
	{
		private static readonly Regex NamePattern = new Regex("^[A-Z][a-zA-Z0-9]*$");

		private readonly string nameString;
		private SlotDataEnumName(string nameString) => this.nameString = nameString;

		public bool Equals(SlotDataEnumName other) => this.nameString == other.nameString;

		public override bool Equals(object obj) =>
			(obj is SlotDataEnumName otherEnumName) && this.Equals(otherEnumName);

		public override int GetHashCode() => this.nameString.GetHashCode();
		public override string ToString() => this.nameString;

		public static bool operator ==(SlotDataEnumName left, SlotDataEnumName right) => left.Equals(right);
		public static bool operator !=(SlotDataEnumName left, SlotDataEnumName right) => !(left.Equals(right));

		public static SlotDataEnumName? OfString(string nameString)
		{
			return NamePattern.IsMatch(nameString) ? (new SlotDataEnumName(nameString) as SlotDataEnumName?) : null;
		}
	}

	internal static class EnumNameExtensions
	{
		public static SlotDataEnumName? ToEnumNameOrNull(this string nameString) =>
			SlotDataEnumName.OfString(nameString);
	}
}
