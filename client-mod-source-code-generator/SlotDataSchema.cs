/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

using Microsoft.CodeAnalysis.Text;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal static class SlotDataSchema
	{
		private static class PropertyNames
		{
			public const string MinValue = "min";
			public const string MaxValue = "max";
			public const string FallbackValue = "fallback";
		}

		private abstract class PartialEntry
		{
			public readonly string Key;

			/// <summary>
			/// May be <c>null</c>.
			/// </summary>
			public string Description { get; private set; } = null;

			protected PartialEntry(string key)
			{
				this.Key = key;
			}

			public abstract bool InitProperty(string name, string value);

			public abstract SlotDataSchemaEntryTypeData ToTypeDataOrNull();

			public void AddDescriptionLine(string line)
			{
				if (this.Description is null)
				{
					this.Description = "";
				}
				else
				{
					this.Description += "\n";
				}

				this.Description += line;
			}
		}

		#region types

		private sealed class PartialBoolEntry : PartialEntry
		{
			private bool? fallbackValue = null;

			public PartialBoolEntry(string key) : base(key)
			{
			}

			public override bool InitProperty(string name, string value)
			{
				if (name != PropertyNames.FallbackValue)
				{
					return false;
				}

				if (!(this.fallbackValue is null)) return false;

				switch (value)
				{
					case "true":
					{
						this.fallbackValue = true;
						return true;
					}
					case "false":
					{
						this.fallbackValue = false;
						return true;
					}
					default: return false;
				}
			}

			public override SlotDataSchemaEntryTypeData ToTypeDataOrNull()
			{
				if (this.fallbackValue is null) return null;

				return new SlotDataSchemaEntryTypes.Bool(this.fallbackValue.Value);
			}
		}

		private sealed class PartialInt32Entry : PartialEntry
		{
			private int? minValue = null;
			private int? maxValue = null;
			private int? fallbackValue = null;

			public PartialInt32Entry(string key) : base(key)
			{
			}

			public override bool InitProperty(string name, string value)
			{
				switch (name)
				{
					case PropertyNames.MinValue: return this.InitMinValue(value);
					case PropertyNames.MaxValue: return this.InitMaxValue(value);
					case PropertyNames.FallbackValue: return this.InitFallbackValue(value);
					default: return false;
				}
			}

			public override SlotDataSchemaEntryTypeData ToTypeDataOrNull()
			{
				if (this.fallbackValue is null) return null;

				return new SlotDataSchemaEntryTypes.Int32(
					minValue: this.minValue ?? int.MinValue,
					maxValue: this.maxValue ?? int.MaxValue,
					fallbackValue: this.fallbackValue.Value
				);
			}

			private bool InitMinValue(string minValueStr)
			{
				if (!(this.minValue is null)) return false;

				int? minValue = ParseString(minValueStr);
				if (minValue is null) return false;

				if (!(this.maxValue is null) && (minValue > this.maxValue.Value)) return false;
				if (!(this.fallbackValue is null) && (this.fallbackValue.Value < minValue)) return false;

				this.minValue = minValue;
				return true;
			}

			private bool InitMaxValue(string maxValueStr)
			{
				if (!(this.maxValue is null)) return false;

				int? maxValue = ParseString(maxValueStr);
				if (maxValue is null) return false;

				if (!(this.minValue is null) && (maxValue < this.minValue.Value)) return false;
				if (!(this.fallbackValue is null) && (this.fallbackValue.Value > maxValue)) return false;

				this.maxValue = maxValue;
				return true;
			}

			private bool InitFallbackValue(string fallbackValueStr)
			{
				if (!(this.fallbackValue is null)) return false;

				int? fallbackValue = ParseString(fallbackValueStr);
				if (fallbackValue is null) return false;

				if (!(this.minValue is null) && (fallbackValue < this.minValue.Value)) return false;
				if (!(this.maxValue is null) && (fallbackValue > this.maxValue.Value)) return false;

				this.fallbackValue = fallbackValue;
				return true;
			}

			private static int? ParseString(string valueStr)
			{
				if (valueStr.StartsWith("+")) valueStr = valueStr.Substring(1);

				valueStr = valueStr.Replace("_", "");

				if (int.TryParse(valueStr, out int value))
				{
					return value;
				}

				return null;
			}
		}

		private sealed class PartialStringEntry : PartialEntry
		{
			public PartialStringEntry(string key) : base(key)
			{
			}

			public override bool InitProperty(string name, string value) => false;

			public override SlotDataSchemaEntryTypeData ToTypeDataOrNull()
			{
				return new SlotDataSchemaEntryTypes.String();
			}
		}

		#endregion

		public static Dictionary<string, SlotDataSchemaEntry> Parse(TextLineCollection textLines)
		{
			var schema = new Dictionary<string, SlotDataSchemaEntry>();

			PartialEntry currentEntry = null;

			foreach (TextLine line in textLines)
			{
				bool isValidLine = ProcessLine(line.ToString(), ref currentEntry, ref schema);
				if (!isValidLine)
				{
					return null;
				}
			}

			return schema;
		}

		private static bool ProcessLine(
			string line,
			ref PartialEntry currentEntry,
			ref Dictionary<string, SlotDataSchemaEntry> schema
		)
		{
			int commentCharIndex = line.IndexOf('#');
			if (commentCharIndex >= 0)
			{
				line = line.Remove(startIndex: commentCharIndex);
			}

			line = line.Trim();
			if (line == "") return true;

			if (currentEntry is null)
			{
				PartialEntry entry = ProcessEntryHeadLine(line);

				if (!(entry is null))
				{
					currentEntry = entry;
				}

				return !(entry is null);
			}

			Match descriptionMatch = Regex.Match(line, @"^\(i\)(.*)$");
			if (descriptionMatch != Match.Empty)
			{
				string descriptionLine = descriptionMatch.Groups[1].Value.Trim();

				if (descriptionLine == "") return false;

				currentEntry.AddDescriptionLine(descriptionLine);

				return true;
			}

			Match propertyMatch = Regex.Match(line, @"^([a-z][a-z0-9_]*)\s*=\s*(.+)$");
			if (propertyMatch != Match.Empty)
			{
				string propertyName = propertyMatch.Groups[1].Value;
				string propertyValue = propertyMatch.Groups[2].Value.Trim();

				return currentEntry.InitProperty(propertyName, propertyValue);
			}

			if (line == "}")
			{
				SlotDataSchemaEntryTypeData typeData = currentEntry.ToTypeDataOrNull();
				if (typeData is null) return false;

				schema[currentEntry.Key] = new SlotDataSchemaEntry(typeData, currentEntry.Description);
				currentEntry = null;

				return true;
			}

			return false;
		}

		private static PartialEntry ProcessEntryHeadLine(string line)
		{
			Match headMatch = Regex.Match(line, @"^([a-z0-9_]+)\s*:\s*([a-z0-9_]+)\s*\{$");

			if (headMatch == Match.Empty)
			{
				return null;
			}

			string key = headMatch.Groups[1].Value;
			string typeName = headMatch.Groups[2].Value;

			switch (typeName)
			{
				case "bool": return new PartialBoolEntry(key);
				case "int32": return new PartialInt32Entry(key);
				case "string": return new PartialStringEntry(key);
				default: return null;
			}
		}
	}
}
