package com.comunidad_zapotal.comunidad_zapotal.data.model
import java.io.Serializable

data class Multimedia(
    val id: Int,
    val archivo_url: String,
    val tipo: String,
    val orden: Int
) : Serializable