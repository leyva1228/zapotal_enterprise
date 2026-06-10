package com.comunidad.zapotal.app.data.model

data class RegisterResponse(

    val ok: Boolean,

    val mensaje: String,

    val usuario: Usuario?
)