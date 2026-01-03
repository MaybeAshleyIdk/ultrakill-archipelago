/*
 * SPDX-License-Identifier: CC0-1.0
 */

using System;
using System.Collections.Generic;
using System.Linq;

namespace UltrakillArchipelago.SourceCodeGenerator
{
	internal static class EnumerableUtils
	{
		public static string JoinToString<T>(this IEnumerable<T> values, string separator) =>
			string.Join(separator, values);

		public static IEnumerable<TResult> Select<TSourceKey, TSourceValue, TResult>(
			this IDictionary<TSourceKey, TSourceValue> source,
			Func<TSourceKey, TSourceValue, TResult> selector
		)
		{
			return source.Select((KeyValuePair<TSourceKey, TSourceValue> pair) =>
				selector.Invoke(pair.Key, pair.Value));
		}
	}
}
