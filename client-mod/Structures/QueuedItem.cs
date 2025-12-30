/*
 * Copyright (c) 2023-2025 Trevor L
 * SPDX-License-Identifier: MIT
 */

namespace ArchipelagoULTRAKILL.Structures
{
    public class QueuedItem
    {
        public UKItem item;
        public string sendingPlayer;
        public bool silent;

        public QueuedItem(UKItem item, string sendingPlayer, bool silent = false)
        {
            this.item = item;
            this.sendingPlayer = sendingPlayer;
            this.silent = silent;
        }
    }
}
