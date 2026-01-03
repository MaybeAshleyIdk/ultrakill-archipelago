/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

using System;
using System.Linq;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal static class StringUtils
	{
		public static string Replace(this string str, string oldValue, Func<string> getNewValue)
		{
			int oldValueIndex = str.IndexOf(oldValue, StringComparison.Ordinal);
			if (oldValueIndex < 0)
			{
				return str;
			}

			string newValue = getNewValue();

			return str.Substring(startIndex: 0, length: oldValueIndex) +
				newValue +
				str.Substring(startIndex: oldValueIndex + oldValue.Length);
		}

		public static string ExtractLeadingWhiteSpace(this string str)
		{
			var leadingWhiteSpace = "";

			foreach (char ch in str)
			{
				if (char.IsWhiteSpace(ch))
				{
					leadingWhiteSpace += ch.ToString();
				}
				else
				{
					break;
				}
			}

			return leadingWhiteSpace;
		}

		public static string TurnSnakeCaseIntoCamelCase(string snakeCaseString)
		{
			return snakeCaseString.Split('_')
				.Aggregate(seed: "", (string camelCaseString, string word) =>
				{
					if (camelCaseString != "")
					{
						word = word.ToTitle();
					}

					return camelCaseString + word;
				});
		}

		public static string TurnSnakeCaseIntoPascalCase(string snakeCaseString)
		{
			return snakeCaseString.Split('_')
				.Aggregate(
					seed: "",
					(string pascalCaseString, string word) => pascalCaseString + word.ToTitle()
				);
		}

		private static string ToTitle(this string str)
		{
			if (str == "")
			{
				return str;
			}

			return char.ToUpper(str[0]) + str.Substring(startIndex: 1).ToLower();
		}
	}
}
