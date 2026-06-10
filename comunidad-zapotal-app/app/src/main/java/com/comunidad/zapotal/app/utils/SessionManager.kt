package com.comunidad.zapotal.app.utils

import android.content.Context
import android.content.SharedPreferences
import com.comunidad.zapotal.app.data.model.Usuario
import com.google.gson.Gson

class SessionManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("user_session", Context.MODE_PRIVATE)
    private val gson = Gson()

    fun saveUser(usuario: Usuario) {
        val editor = prefs.edit()
        editor.putString("usuario", gson.toJson(usuario))
        editor.putLong("user_id", usuario.id)
        editor.putBoolean("is_logged_in", true)
        editor.apply()
    }

    fun getUser(): Usuario? {
        val userJson = prefs.getString("usuario", null)
        return if (userJson != null) {
            gson.fromJson(userJson, Usuario::class.java)
        } else {
            null
        }
    }

    fun getUserId(): Long {
        return prefs.getLong("user_id", -1L)
    }

    fun isLoggedIn(): Boolean {
        return prefs.getBoolean("is_logged_in", false)
    }

    fun logout() {
        val editor = prefs.edit()
        editor.clear()
        editor.apply()
    }
}
