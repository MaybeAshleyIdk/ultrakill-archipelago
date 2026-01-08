/*
 * Copyright (c) 2026 MaybeAshleyIdk
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#nullable enable

using System.Text.RegularExpressions;

namespace ArchipelagoULTRAKILL.New
{
	public enum SceneId
	{
		MainMenu,

		DeveloperMuseum,

		CyberGrind,
		Sandbox,

		#region missions

		#region Prelude

		/// 0-1: INTO THE FIRE
		MissionPrelude1,

		/// 0-2: THE MEATGRINDER
		MissionPrelude2,

		/// 0-3: DOUBLE DOWN
		MissionPrelude3,

		/// 0-4: A ONE-MACHINE ARMY
		MissionPrelude4,

		/// 0-5: CERBERUS
		MissionPrelude5,

		/// 0-S: SOMETHING WICKED
		MissionPreludeS,

		/// 0-E: THIS HEAT, AN EVIL HEAT
		MissionPreludeE,

		#endregion

		#region Act I

		#region Limbo

		/// 1-1: HEART OF THE SUNRISE
		MissionLimbo1,

		/// 1-2: THE BURNING WORLD
		MissionLimbo2,

		/// 1-3: HALLS OF SACRED REMAINS
		MissionLimbo3,

		/// 1-4: CLAIR DE LUNE
		MissionLimbo4,

		/// 1-S: THE WITLESS
		MissionLimboS,

		/// 1-E: ...THEN FELL THE ASHES
		MissionLimboE,

		#endregion

		#region Lust

		/// 2-1: BRIDGEBURNER
		MissionLust1,

		/// 2-2: DEATH AT 20,000 VOLTS
		MissionLust2,

		/// 2-3: SHEER HEART ATTACK
		MissionLust3,

		/// 2-4: COURT OF THE CORPSE KING
		MissionLust4,

		/// 2-S: ALL-IMPERFECT LOVE SONG
		MissionLustS,

		// /// 2-S: ???
		// LustE,

		#endregion

		#region Gluttony

		/// 3-1: BELLY OF THE BEAST
		MissionGluttony1,

		/// 3-2: IN THE FLESH
		MissionGluttony2,

		// /// 3-E: ???
		// GluttonyE,

		#endregion

		#endregion

		#region Act 2

		#region Greed

		/// 4-1: SLAVES TO POWER
		MissionGreed1,

		/// 4-2: GOD DAMN THE SUN
		MissionGreed2,

		/// 4-3: A SHOT IN THE DARK
		MissionGreed3,

		/// 4-4: CLAIR THE SOLEIL
		MissionGreed4,

		/// 4-S: CLASH OF THE BRANDICOOT
		MissionGreedS,

		// /// 4-E: ???
		// MissionGreedE,

		#endregion

		#region Wrath

		/// 5-1: IN THE WAKE OF POSEIDON
		MissionWrath1,

		/// 5-2: WAVES OF THE STARLESS SEA
		MissionWrath2,

		/// 5-3: SHIP OF FOOLS
		MissionWrath3,

		/// 5-4: LEVIATHAN
		MissionWrath4,

		/// 5-S: I ONLY SAY MORNING
		MissionWrathS,

		// /// 5-E: ???
		// MissionWrathE,

		#endregion

		#region Heresy

		/// 6-1: CRY FOR THE WEEPER
		MissionHeresy1,

		/// 6-2: AESTHETICS OF HATE
		MissionHeresy2,

		// /// 6-E: ???
		// MissionHeresyE,

		#endregion

		#endregion

		#region Act 3

		#region Violence

		/// 7-1: GARDEN OF FORKING PATHS
		MissionViolence1,

		/// 7-2: LIGHT UP THE NIGHT
		MissionViolence2,

		/// 7-3: NO SOUND, NO MEMORY
		MissionViolence3,

		/// 7-4: ...LIKE ANTENNAS TO HEAVEN
		MissionViolence4,

		/// 7-S: HELL BATH NO FURY
		MissionViolenceS,

		// /// 7-E: ???
		// MissionViolenceE,

		#endregion

		#region Fraud

		// /// 8-1: HURTBREAK WONDERLAND
		// MissionFraud1,
		//
		// /// 8-2: ???
		// MissionFraud2,
		//
		// /// 8-3: ???
		// MissionFraud3,
		//
		// /// 8-4: ???
		// MissionFraud4,
		//
		// /// 8-S: ???
		// MissionFraudS,
		//
		// /// 8-E: ???
		// MissionFraudE,

		#endregion

		#region Treachery

		// // 9-1: ???
		// MissionTreachery1,
		//
		// // 9-2: ???
		// MissionTreachery2,
		//
		// // 9-E: ???
		// MissionTreacheryE,

		#endregion

		#endregion

		#region Prime Sanctums

		/// P-1: SOUL SURVIVOR
		MissionP1,

		/// P-2: WAIT OF THE WORLD
		MissionP2,

		// /// P-3: ???
		// MissionP3,

		#endregion

		#endregion

		Unknown,
	}

	public static class SceneIdExtensions
	{
		public static bool IsMission(this SceneId sceneId)
		{
			return (sceneId >= SceneId.MissionPrelude1) && (sceneId <= SceneId.MissionP2);
		}

		public static bool IsSecretMission(this SceneId sceneId)
		{
			return sceneId switch
			{
				SceneId.MissionPreludeS => true,
				SceneId.MissionLimboS => true,
				SceneId.MissionLustS => true,
				SceneId.MissionGreedS => true,
				SceneId.MissionWrathS => true,
				SceneId.MissionViolenceS => true,
				_ => false,
			};
		}
	}

	public static class SceneIdUtils
	{
		private static readonly Regex MissionPattern = new Regex("^Level (.)-(.)$");

		public static SceneId ParseSceneNameToId(string sceneName)
		{
			return sceneName switch
			{
				"Main Menu" => SceneId.MainMenu,
				"CreditsMuseum2" => SceneId.DeveloperMuseum,
				"Endless" => SceneId.CyberGrind,
				"uk_construct" => SceneId.Sandbox,
				_ => ParseMissionSceneNameToId(sceneName),
			};
		}

		private static SceneId ParseMissionSceneNameToId(string sceneName)
		{
			Match match = MissionPattern.Match(sceneName);
			if (match == Match.Empty) return SceneId.Unknown;

			string firstPart = match.Groups[1].Value;
			string secondPart = match.Groups[2].Value;

			return firstPart switch
			{
				"0" => secondPart switch
				{
					"1" => SceneId.MissionPrelude1,
					"2" => SceneId.MissionPrelude2,
					"3" => SceneId.MissionPrelude3,
					"4" => SceneId.MissionPrelude4,
					"5" => SceneId.MissionPrelude5,
					"S" => SceneId.MissionPreludeS,
					"E" => SceneId.MissionPreludeE,
					_ => SceneId.Unknown,
				},

				#region Act 1

				"1" => secondPart switch
				{
					"1" => SceneId.MissionLimbo1,
					"2" => SceneId.MissionLimbo2,
					"3" => SceneId.MissionLimbo3,
					"4" => SceneId.MissionLimbo4,
					"S" => SceneId.MissionLimboS,
					"E" => SceneId.MissionLimboE,
					_ => SceneId.Unknown,
				},

				"2" => secondPart switch
				{
					"1" => SceneId.MissionLust1,
					"2" => SceneId.MissionLust2,
					"3" => SceneId.MissionLust3,
					"4" => SceneId.MissionLust4,
					"S" => SceneId.MissionLustS,
					// "E" => SceneId.MissionLustE,
					_ => SceneId.Unknown,
				},

				"3" => secondPart switch
				{
					"1" => SceneId.MissionGluttony1,
					"2" => SceneId.MissionGluttony2,
					// "E" => SceneId.MissionGluttonyE,
					_ => SceneId.Unknown,
				},

				#endregion

				#region Act 2

				"4" => secondPart switch
				{
					"1" => SceneId.MissionGreed1,
					"2" => SceneId.MissionGreed2,
					"3" => SceneId.MissionGreed3,
					"4" => SceneId.MissionGreed4,
					"S" => SceneId.MissionGreedS,
					// "E" => SceneId.MissionGreedE,
					_ => SceneId.Unknown,
				},

				"5" => secondPart switch
				{
					"1" => SceneId.MissionWrath1,
					"2" => SceneId.MissionWrath2,
					"3" => SceneId.MissionWrath3,
					"4" => SceneId.MissionWrath4,
					"S" => SceneId.MissionWrathS,
					// "E" => SceneId.MissionWrathE,
					_ => SceneId.Unknown,
				},

				"6" => secondPart switch
				{
					"1" => SceneId.MissionHeresy1,
					"2" => SceneId.MissionHeresy2,
					// "E" => SceneId.MissionHeresyE,
					_ => SceneId.Unknown,
				},

				#endregion

				#region Act 3

				"7" => secondPart switch
				{
					"1" => SceneId.MissionViolence1,
					"2" => SceneId.MissionViolence2,
					"3" => SceneId.MissionViolence3,
					"4" => SceneId.MissionViolence4,
					"S" => SceneId.MissionViolenceS,
					// "E" => SceneId.MissionViolenceE,
					_ => SceneId.Unknown,
				},

				// "8" => secondPart switch
				// {
				// 	"1" => SceneId.MissionFraud1,
				// 	"2" => SceneId.MissionFraud2,
				// 	"3" => SceneId.MissionFraud3,
				// 	"4" => SceneId.MissionFraud4,
				// 	"S" => SceneId.MissionFraudS,
				// 	"E" => SceneId.MissionFraudE,
				// 	_ => SceneId.Unknown,
				// },
				//
				// "9" => secondPart switch
				// {
				//  "1" => SceneId.MissionTreachery1,
				//  "2" => SceneId.MissionTreachery2,
				//  "E" => SceneId.MissionTreacheryE,
				// 	_ => SceneId.Unknown,
				// },

				#endregion

				"P" => secondPart switch
				{
					"1" => SceneId.MissionP1,
					"2" => SceneId.MissionP2,
					// "3" => SceneId.MissionP3,
					_ => SceneId.Unknown,
				},

				_ => SceneId.Unknown,
			};
		}
	}

	public static class CurrentScene
	{
		public static SceneId Id
		{
			get
			{
				string? currentSceneName = SceneHelper.CurrentScene;
				return !(currentSceneName is null)
					? SceneIdUtils.ParseSceneNameToId(currentSceneName)
					: SceneId.Unknown;
			}
		}

		public static bool IsCurrent(this SceneId sceneId)
		{
			return Id == sceneId;
		}
	}
}
