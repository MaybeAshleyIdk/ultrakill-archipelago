/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

using System;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal enum EolType
	{
		/// Unix-like and modern macOS
		Lf,

		/// Windows
		CrLf,

		/// Classic Mac OS
		Cr,
	}

	internal static class EolTypeUtils
	{
		public static string DetermineEolString(this EolType? eolType)
		{
			return eolType.HasValue ? eolType.Value.DetermineEolString() : "";
		}

		private static string DetermineEolString(this EolType eolType)
		{
			switch (eolType)
			{
				case EolType.Lf: return "\n";
				case EolType.CrLf: return "\r\n";
				case EolType.Cr: return "\r";
				default: throw new ArgumentOutOfRangeException(nameof(eolType), eolType, null);
			}
		}
	}
}
