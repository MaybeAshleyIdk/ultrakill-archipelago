/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

using System;
using System.Collections.Generic;
using System.Linq;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal readonly struct Line
	{
		public readonly string Text;
		public readonly EolType? EolType;

		public Line(string text, EolType? eolType)
		{
			if (text.IndexOfAny(new[] { '\n', '\r' }) != -1)
			{
				throw new ArgumentException(
					message: "Line text must not contain newline characters",
					paramName: nameof(text)
				);
			}

			this.Text = text;
			this.EolType = eolType;
		}

		public override bool Equals(object obj)
		{
			return !(obj is null) && (this.ToString() == obj.ToString());
		}

		public override int GetHashCode()
		{
			return this.ToString().GetHashCode();
		}

		public override string ToString()
		{
			return this.Text + this.EolType.DetermineEolString();
		}
	}

	internal static class LineExtensions
	{
		public static IEnumerable<Line> SplitLines(this string str)
		{
			var currentLine = "";

			for (var i = 0; i < str.Length; ++i)
			{
				bool isPrevCharCr = (i >= 1) && (str[i - 1] == '\r');
				char ch = str[i];

				switch (ch)
				{
					case '\n':
					{
						EolType eolType = isPrevCharCr ? EolType.CrLf : EolType.Lf;
						yield return new Line(currentLine, eolType);
						currentLine = "";

						continue;
					}
					case '\r':
					{
						if (isPrevCharCr)
						{
							yield return new Line(currentLine, EolType.Cr);
							currentLine = "";
						}

						continue;
					}
					default:
					{
						currentLine += ch;
						break;
					}
				}
			}

			if (currentLine != "")
			{
				EolType? eolType = (str[str.Length - 1] == '\r') ? EolType.Cr : (null as EolType?);
				yield return new Line(currentLine, eolType);
			}
		}

		public static string PrependLinesWith(this string str, string prefix)
		{
			return str.SplitLines()
				.Aggregate(seed: "", (string acc, Line line) => $"{acc}{prefix}{line}");
		}

		public static string IndentWith(this string str, string indent)
		{
			return str.SplitLines()
				.Aggregate(seed: "", (string acc, Line line) =>
				{
					string lineText = line.Text;

					if (lineText != "")
					{
						lineText = indent + lineText;
					}

					return acc + lineText + line.EolType.DetermineEolString();
				});
		}
	}
}
