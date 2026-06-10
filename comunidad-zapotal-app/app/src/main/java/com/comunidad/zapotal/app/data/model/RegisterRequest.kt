package com.comunidad.zapotal.app.data.model

import com.google.gson.annotations.SerializedName

data class RegisterRequest(
    @SerializedName("nombres")
    val nombres: String,
    @SerializedName("apellidos")
    val apellidos: String,
    @SerializedName("email")
    val email: String,
    @SerializedName("password")
    val password: String,
    @SerializedName("dni")
    val dni: String
)
