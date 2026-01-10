#nullable enable

using Archipelago.MultiClient.Net;
using ArchipelagoULTRAKILL.Structures;
using BepInEx.Logging;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;

namespace ArchipelagoULTRAKILL.New
{
	internal readonly struct StructuredSlotData
	{
		// TODO

		private StructuredSlotData()
		{
			// TODO
		}

		public static StructuredSlotData FromLoginResult(LoginSuccessful result, ManualLogSource logger)
		{
			Dictionary<string, object> slotData = result.SlotData;

			TryGetStart(ref Core.data.unlockedLevels, slotData, "0-1");
			TryGetGoal(ref Core.data.goal, slotData, "6-2");

			TryGetEnemyOption(ref Core.data.enemyRewards, slotData, "enemy_rewards", EnemyOptions.Disabled);
			TryGetFire2(ref Core.data.randomizeFire2, slotData, "randomize_secondary_fire", Fire2Options.Disabled);
			TryGetSlotDataValue(ref Core.data.revForm, slotData, "revolver_form", WeaponForm.Standard);
			TryGetSlotDataValue(ref Core.data.shoForm, slotData, "shotgun_form", WeaponForm.Standard);
			TryGetSlotDataValue(ref Core.data.naiForm, slotData, "nailgun_form", WeaponForm.Standard);

			if (Core.data.musicRandomizer)
			{
				Core.data.music =
					JsonConvert.DeserializeObject<Dictionary<string, string>>(slotData["music"].ToString());
			}

			try
			{
				ConfigManager.uiColorRandomizer.value = (ColorOptions)Enum.Parse(typeof(ColorOptions),
					slotData["ui_color_randomizer"].ToString());
			}
			catch (KeyNotFoundException)
			{
				ConfigManager.uiColorRandomizer.value = ColorOptions.Off;
			}

			try
			{
				ConfigManager.gunColorRandomizer.value = (ColorOptions)Enum.Parse(typeof(ColorOptions),
					slotData["gun_color_randomizer"].ToString());
			}
			catch (KeyNotFoundException)
			{
				ConfigManager.gunColorRandomizer.value = ColorOptions.Off;
			}

			LocationManager.locations = ((JObject)slotData["locations"]).ToObject<Dictionary<string, long>>();

			return new StructuredSlotData();
		}


		private static void TryGetStart(ref HashSet<string> unlockedLevels, Dictionary<string, object> slotData,
			string defaultValue)
		{
			try
			{
				unlockedLevels.Add(slotData["start"].ToString());
				Core.data.start = slotData["start"].ToString();
			}
			catch (KeyNotFoundException)
			{
				Core.Logger.LogWarning($"No key found for start level. Using default value ({defaultValue})");
				unlockedLevels.Add(defaultValue);
				Core.data.start = defaultValue;
			}
		}


		private static void TryGetGoal(ref string goal, Dictionary<string, object> slotData, string defaultValue)
		{
			if (int.TryParse(slotData["goal"].ToString(), out int goalNum))
			{
				Core.Logger.LogWarning("Using legacy goal option.");
				switch (goalNum)
				{
					case 0:
						goal = "1-4";
						break;
					case 1:
						goal = "2-4";
						break;
					case 2:
						goal = "3-2";
						break;
					case 3:
						goal = "4-4";
						break;
					case 4:
						goal = "5-4";
						break;
					case 6:
						goal = "P-1";
						break;
					case 7:
						goal = "P-2";
						break;
					case 8:
						goal = "7-4";
						break;
					case 5:
					default:
						goal = "6-2";
						break;
				}
			}
			else
			{
				goal = slotData["goal"].ToString();
			}
		}

		private static void TryGetEnemyOption(ref EnemyOptions option, Dictionary<string, object> slotData, string key,
			EnemyOptions defaultValue)
		{
			try
			{
				option = (EnemyOptions)int.Parse(slotData[key].ToString());
			}
			catch (KeyNotFoundException)
			{
				try
				{
					option = (EnemyOptions)int.Parse(slotData["boss_rewards"].ToString());
					Core.Logger.LogInfo("Using legacy enemy reward option.");
				}
				catch (KeyNotFoundException)
				{
					Core.Logger.LogWarning($"No key found for enemy rewards. Using default value ({defaultValue})");
					option = defaultValue;
				}
			}
		}

		private static void TryGetFire2(ref Fire2Options option, Dictionary<string, object> slotData, string key,
			Fire2Options defaultValue)
		{
			if (bool.TryParse(slotData[key].ToString(), out bool value))
			{
				Core.Logger.LogInfo("Using legacy secondary fire option.");
				if (value) option = Fire2Options.Split;
				else option = Fire2Options.Disabled;
			}
			else
			{
				try
				{
					option = (Fire2Options)int.Parse(slotData[key].ToString());
				}
				catch (KeyNotFoundException)
				{
					Core.Logger.LogWarning($"No key found for option \"{key}\". Using default value ({defaultValue})");
					option = defaultValue;
				}
			}
		}

		private static void TryGetSlotDataValue(ref WeaponForm option, Dictionary<string, object> slotData, string key,
			WeaponForm defaultValue)
		{
			try
			{
				option = (WeaponForm)int.Parse(slotData[key].ToString());
			}
			catch (KeyNotFoundException)
			{
				Core.Logger.LogWarning($"No key found for option \"{key}\". Using default value ({defaultValue})");
				option = defaultValue;
			}
		}
	}
}
