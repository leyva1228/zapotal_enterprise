package com.comunidad_zapotal.comunidad_zapotal.data.model

data class Autoridad(
    val id: Int = 0,
    val nombres: String? = null,
    val apellidos: String? = null,
    val cargo: String? = null,
    val descripcion: String? = null,
    val telefono: String? = null,
    val correo: String? = null,
    val foto_url: String? = null,
    val estado: String? = null
)