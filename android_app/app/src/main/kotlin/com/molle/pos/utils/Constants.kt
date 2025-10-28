package com.molle.pos.utils

object Constants {
    const val API_BASE_URL = "http://localhost:8000/api/v1/"
    const val SYNC_INTERVAL = 5 * 60 * 1000 // 5 دقائق
    const val OFFLINE_MODE_ENABLED = true
    const val DATABASE_NAME = "molle_pos.db"
    
    // Preferences
    const val PREF_NAME = "molle_pos_prefs"
    const val PREF_USER_ID = "user_id"
    const val PREF_BRANCH_ID = "branch_id"
    const val PREF_TOKEN = "auth_token"
    const val PREF_LAST_SYNC = "last_sync"
}
