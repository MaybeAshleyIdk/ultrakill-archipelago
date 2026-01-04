/*
 * SPDX-License-Identifier: CC0-1.0
 */

#nullable enable

using System.Diagnostics.CodeAnalysis;
using UnityEngine;

namespace ArchipelagoULTRAKILL.New.Utils
{
	internal static class UnityObjectLifetimeUtils
	{
		public static bool IsNotNullAndAttached([NotNullWhen(returnValue: true)] this Object? obj)
		{
			return !(obj is null) && obj.IsAttached();
		}

		private static bool IsAttached(this Object obj)
		{
			// <https://docs.unity3d.com/ScriptReference/Object.html>
			// > Detached objects retain their InstanceID, but the object can't be used to call methods or access
			// > properties. Comparing objects in this state with `null` evaluates `true`, because of Unity's custom
			// > implementation of the equality (`==`) and inequality (`!=`) operators and Object.bool. However,
			// > because the managed object is not truly null, a call to `Object.ReferenceEquals(myobject, null)`
			// > returns `false`.
			// This is fucking horrible why would you do this.
			return obj != null;
		}
	}
}
