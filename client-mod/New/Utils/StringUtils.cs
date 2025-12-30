/*
 * Copyright (c) 2025 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

namespace ArchipelagoULTRAKILL.New.Utils
{
	public static class StringUtils
	{
		public static string Quoted(this string str)
		{
			string escaped = str.Replace(@"\", @"\\").Replace("\"", "\\\"");
			return $"\"{escaped}\"";
		}
	}
}
