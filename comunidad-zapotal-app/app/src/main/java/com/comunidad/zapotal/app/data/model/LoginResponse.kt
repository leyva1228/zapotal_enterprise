package com.comunidad.zapotal.app.data.model

data class LoginResponse(

    val ok: Boolean,

    val mensaje: String,

    val usuario: Usuario?
)