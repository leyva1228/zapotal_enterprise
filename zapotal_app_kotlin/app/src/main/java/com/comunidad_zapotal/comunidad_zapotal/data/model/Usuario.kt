package com.comunidad_zapotal.comunidad_zapotal.data.model

data class Usuario(
    val id: Int,
    val nombres: String,
    val apellidos: String,
    val foto_perfil_url: String?
)